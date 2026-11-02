<?php
// Keeps the result history, outages and "down / back up" emails for watched sites.
declare(strict_types=1);
require_once __DIR__ . '/_mail.php';

const SUD_FAILS_TO_ALERT = 2; // two failed checks in a row before we say a site is down

function track_result(PDO $pdo, string $host, string $verdict, ?int $ms): void {
    $now = sql_now();
    $pdo->prepare('INSERT INTO site_log (host, ts, verdict, ms) VALUES (?,?,?,?)')->execute([$host, $now, $verdict, $ms]);
    if ($verdict === 'inconclusive') return; // blocked or unverifiable: neither proves up nor down
    $bad = in_array($verdict, ['down', 'timeout'], true);
    $s = $pdo->prepare('SELECT state, fails, since FROM alert_state WHERE host=?');
    $s->execute([$host]);
    $st = $s->fetch() ?: ['state' => 'up', 'fails' => 0, 'since' => null];
    if ($bad) {
        $fails = (int)$st['fails'] + 1;
        if ($st['state'] !== 'down' && $fails >= SUD_FAILS_TO_ALERT) {
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
    $q = $pdo->prepare('SELECT u.email, u.name FROM watchlist w JOIN users u ON u.id = w.user_id WHERE w.host=? AND w.alerts=1');
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
                'See live status', $page);
        } else {
            $for = $since ? human_span(max(0, strtotime($now . ' UTC') - strtotime($since . ' UTC'))) : '';
            $ex = $for ? " It was down for $for." : '';
            sud_email($u['email'], $host . ' is back up', $host . ' is back up',
                "<p>Hi $name,</p><p>Good news: <b>$h</b> is answering again.$ex</p>",
                "Hi {$u['name']},\n\nGood news: $host is answering again.$ex",
                'See live status', $page);
        }
    }
}
