<?php
// Keeps the result history, outages and "down / back up" emails for watched sites.
declare(strict_types=1);
require_once __DIR__ . '/_mail.php';
require_once __DIR__ . '/_notify.php';

const SUD_FAILS_TO_ALERT = 2; // two failed checks in a row before we say a site is down

/** True when independent probes recently reached a site our server could not (so a failed check means "blocked", not "down"). */
function corroborated_alive_cached(PDO $pdo, string $host): bool {
    $c = $pdo->prepare('SELECT alive FROM corroboration WHERE host=? AND ts > ?'); $c->execute([$host, time() - 1800]);
    return (bool)$c->fetchColumn();
}

/** Did the latest worldwide check (fifteen places, under 12 hours old) reach this site from at least 80% of them? Then our own server being blocked or unanswered does not mean the site is down. */
function world_says_up(PDO $pdo, string $host): bool {
    $q = $pdo->prepare('SELECT data, ts FROM world_checks WHERE host=?'); $q->execute([$host]);
    $r = $q->fetch();
    if (!$r || $r['data'] === '' || (int)$r['ts'] < time() - 43200) return false;
    $d = json_decode($r['data'], true);
    if (!is_array($d) || empty($d['probes']) || count($d['probes']) < 10) return false;
    $ok = 0; foreach ($d['probes'] as $p) if (($p['state'] ?? '') === 'ok') $ok++;
    return $ok / count($d['probes']) >= 0.8;
}

/** Has this site answered one of our checks in the last 24 hours? */
function seen_up_recently(PDO $pdo, string $host): bool {
    $q = $pdo->prepare("SELECT 1 FROM site_log WHERE host=? AND verdict='up' AND ts > ? LIMIT 1");
    $q->execute([$host, gmdate('Y-m-d H:i:s', time() - 86400)]);
    return (bool)$q->fetchColumn();
}

function track_result(PDO $pdo, string $host, string $verdict, ?int $ms): void {
    if (in_array($verdict, ['down', 'timeout'], true) && corroborated_alive_cached($pdo, $host)) $verdict = 'inconclusive';
    if ($verdict === 'timeout' && !seen_up_recently($pdo, $host)) $verdict = 'inconclusive';     // silence from a site we have not seen answer lately is not an outage
    $now = sql_now();
    // One history row per host per five minutes (the worst result in that window wins), so one-minute checks do not bloat the history.
    $lg = $pdo->prepare('SELECT ts, verdict FROM site_log WHERE host=? ORDER BY ts DESC LIMIT 1');
    $lg->execute([$host]);
    $last = $lg->fetch();
    if ($last && intdiv(strtotime($last['ts'] . ' UTC'), 300) === intdiv(time(), 300)) {
        if ($last['verdict'] === 'up' && $verdict !== 'up') $pdo->prepare('UPDATE site_log SET verdict=?, ms=? WHERE host=? AND ts=?')->execute([$verdict, $ms, $host, $last['ts']]);
    } else {
        $pdo->prepare('INSERT INTO site_log (host, ts, verdict, ms) VALUES (?,?,?,?)')->execute([$host, $now, $verdict, $ms]);
    }
    if ($verdict === 'inconclusive') return; // blocked or unverifiable: neither proves up nor down
    $bad = in_array($verdict, ['down', 'timeout'], true);
    $s = $pdo->prepare('SELECT state, fails, since FROM alert_state WHERE host=?');
    $s->execute([$host]);
    $st = $s->fetch() ?: ['state' => 'up', 'fails' => 0, 'since' => null];
    if ($bad) {
        $fails = (int)$st['fails'] + 1;
        if ($st['state'] !== 'down' && $fails >= SUD_FAILS_TO_ALERT) {
            // Before calling it an outage, ask probes in other countries. If any can reach the site, it is blocking us, not down.
            require_once __DIR__ . '/_gp.php';
            if (corroborate_alive($host)) { $pdo->prepare('REPLACE INTO alert_state (host, state, fails, since) VALUES (?,?,?,?)')->execute([$host, $st['state'], SUD_FAILS_TO_ALERT - 1, $st['since']]); return; }
            $pdo->prepare('REPLACE INTO alert_state (host, state, fails, since) VALUES (?,?,?,?)')->execute([$host, 'down', $fails, $now]);
            $pdo->prepare('INSERT INTO incidents (host, started_at) VALUES (?,?)')->execute([$host, $now]);
            notify_watchers($pdo, $host, true, $now, null);
            return;
        }
        $pdo->prepare('REPLACE INTO alert_state (host, state, fails, since) VALUES (?,?,?,?)')->execute([$host, $st['state'], $fails, $st['since']]);
        return;
    }
    // Reachable again (or never failed).
    if ($st['state'] === 'down') {
        $pdo->prepare('UPDATE incidents SET ended_at=? WHERE host=? AND ended_at IS NULL')->execute([$now, $host]);
        $pdo->prepare('REPLACE INTO alert_state (host, state, fails, since) VALUES (?,?,?,?)')->execute([$host, 'up', 0, $now]);
        notify_watchers($pdo, $host, false, $now, $st['since']);
    } elseif ((int)$st['fails'] > 0) {
        $pdo->prepare('REPLACE INTO alert_state (host, state, fails, since) VALUES (?,?,?,?)')->execute([$host, 'up', 0, $st['since']]);
    }
}

function human_span(int $sec): string {
    if ($sec < 90) return 'about a minute';
    if ($sec < 5400) return round($sec / 60) . ' minutes';
    if ($sec < 172800) return round($sec / 3600, 1) . ' hours';
    return round($sec / 86400, 1) . ' days';
}

function notify_watchers(PDO $pdo, string $host, bool $down, string $now, ?string $since): void {
    $q = $pdo->prepare('SELECT u.id, u.email, u.name FROM watchlist w JOIN users u ON u.id = w.user_id WHERE w.host=? AND w.alerts=1');
    $q->execute([$host]);
    $site = rtrim((config()['site'] ?? 'https://siteupdown.com'), '/');
    $page = $site . '/status/' . rawurlencode($host);
    $h = htmlspecialchars($host, ENT_QUOTES, 'UTF-8');
    foreach ($q->fetchAll() as $u) {
        $name = htmlspecialchars($u['name'], ENT_QUOTES, 'UTF-8');
        if ($down) {
            sud_email($u['email'], $host . ' looks down', $host . ' looks down',
                "<p>Hi $name,</p><p>We could not reach <b>$h</b> on two checks in a row, so we think it is down. We will email you again as soon as it answers.</p>",
                "Hi {$u['name']},\n\nWe could not reach $host on two checks in a row, so we think it is down. We will email you again as soon as it answers.",
                'See live status', $page, '', 'down');
            push_user($pdo, (int)$u['id'], "\u{1F534} $host looks down. We could not reach it on two checks in a row.", $page);
        } else {
            $for = $since ? human_span(max(0, strtotime($now . ' UTC') - strtotime($since . ' UTC'))) : '';
            $ex = $for ? " It was down for $for." : '';
            sud_email($u['email'], $host . ' is back up', $host . ' is back up',
                "<p>Hi $name,</p><p>Good news: <b>$h</b> is answering again.$ex</p>",
                "Hi {$u['name']},\n\nGood news: $host is answering again.$ex",
                'See live status', $page, '', 'up');
            push_user($pdo, (int)$u['id'], "\u{1F7E2} $host is back up." . $ex, $page);
        }
    }
}
