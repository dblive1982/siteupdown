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
    // Browser notifications for anyone who asked to hear about this site (separate from the watchlist emails below).
    try {
        require_once __DIR__ . '/_push.php'; require_once __DIR__ . '/_sitepages.php';
        $sp = site_pages()[$host] ?? null;
        if ($sp) {
            $url = 'https://siteupdown.com' . $sp['page'];
            if ($down) push_host($pdo, $host, "\u{1F534} " . $sp['name'] . ' looks down', 'We could not reach it on two checks in a row.', $url);
            else { $for = $since ? human_span(max(0, strtotime($now . ' UTC') - strtotime($since . ' UTC'))) : ''; push_host($pdo, $host, "\u{1F7E2} " . $sp['name'] . ' is back up', $for ? 'It was down for about ' . $for . '.' : 'It is answering again.', $url); }
        }
    } catch (Throwable $e) {}
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
            push_user($pdo, (int)$u['id'], "\u{1F534} $host looks down. We could not reach it on two checks in a row.", $page, 'down', $host);
        } else {
            $for = $since ? human_span(max(0, strtotime($now . ' UTC') - strtotime($since . ' UTC'))) : '';
            $ex = $for ? " It was down for $for." : '';
            sud_email($u['email'], $host . ' is back up', $host . ' is back up',
                "<p>Hi $name,</p><p>Good news: <b>$h</b> is answering again.$ex</p>",
                "Hi {$u['name']},\n\nGood news: $host is answering again.$ex",
                'See live status', $page, '', 'up');
            push_user($pdo, (int)$u['id'], "\u{1F7E2} $host is back up." . $ex, $page, 'up', $host);
        }
    }
}


/** Keep the timing breakdown and the detected provider from a check (one timing row per host per five minutes). */
function save_timing(PDO $pdo, string $host, array $r): void {
    try {
        if (!empty($r['prov'])) $pdo->prepare('REPLACE INTO site_prov (host, provider, seen) VALUES (?,?,?)')->execute([$host, $r['prov'], sql_now()]);
        $t = $r['timing'] ?? null; if (!$t || ($r['verdict'] ?? '') !== 'up') return;
        $q = $pdo->prepare('SELECT ts FROM site_timing WHERE host=? ORDER BY ts DESC LIMIT 1'); $q->execute([$host]); $last = $q->fetchColumn();
        if ($last && intdiv(strtotime($last . ' UTC'), 300) === intdiv(time(), 300)) return;
        $pdo->prepare('INSERT INTO site_timing (host, ts, dns_ms, conn_ms, tls_ms, ttfb_ms) VALUES (?,?,?,?,?,?)')->execute([$host, sql_now(), (int)$t['dns'], (int)$t['conn'], (int)$t['tls'], (int)$t['ttfb']]);
    } catch (Throwable $e) { /* extra detail only, never break a check */ }
}
