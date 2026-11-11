<?php
// Signed-in users only. GET -> my watchlist with latest status. POST {action: add|remove|check}.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_track.php';
require __DIR__ . '/_plan.php';
$pdo = db();
$uid = require_user();
$plan = user_plan($pdo, $uid);
$MAX = $plan['pro'] ? PRO_WATCH : FREE_WATCH;

function my_list(PDO $pdo, int $uid): array {
    $s = $pdo->prepare('SELECT w.host, w.added_at, w.alerts, s.verdict, s.http_code, s.ms, s.checked_at
        FROM watchlist w LEFT JOIN site_status s ON s.host = w.host WHERE w.user_id=? ORDER BY w.added_at DESC, w.id DESC');
    $s->execute([$uid]);
    $rows = $s->fetchAll();
    // Uptime over the last 24 hours, from the result history.
    $up = [];
    if ($rows) {
        $in = implode(',', array_fill(0, count($rows), '?'));
        $q = $pdo->prepare("SELECT host, SUM(CASE WHEN verdict='up' THEN 1 ELSE 0 END) AS ok, SUM(CASE WHEN verdict IN ('down','timeout') THEN 1 ELSE 0 END) AS bad
            FROM site_log WHERE ts > ? AND host IN ($in) GROUP BY host");
        $q->execute(array_merge([gmdate('Y-m-d H:i:s', time() - 86400)], array_column($rows, 'host')));
        foreach ($q->fetchAll() as $u) { $t = (int)$u['ok'] + (int)$u['bad']; if ($t > 0) $up[$u['host']] = round(100 * (int)$u['ok'] / $t, 2); }
    }
    return array_map(fn($r) => ['host' => $r['host'], 'alerts' => (int)$r['alerts'] === 1, 'uptime' => $up[$r['host']] ?? null, 'verdict' => $r['verdict'], 'code' => $r['http_code'] !== null ? (int)$r['http_code'] : null,
        'ms' => $r['ms'] !== null ? (int)$r['ms'] : null, 'at' => $r['checked_at'] ? iso($r['checked_at']) : null, 'added' => iso($r['added_at'])], $rows);
}
function probe_and_store(PDO $pdo, string $host): void {
    $r = check_site($host, '/', false, true);
    $pdo->prepare('REPLACE INTO site_status (host, verdict, http_code, ms, checked_at) VALUES (?,?,?,?,?)')->execute([$host, $r['verdict'], $r['http_code'], $r['ms'], sql_now()]);
    track_result($pdo, $host, $r['verdict'], $r['ms']);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') out(200, ['items' => my_list($pdo, $uid), 'max' => $MAX, 'pro' => $plan['pro']]);
$in = read_post();
$a = (string)($in['action'] ?? '');
if ($a === 'add') {
    $t = parse_target((string)($in['address'] ?? ''));
    if (!$t || filter_var($t[0], FILTER_VALIDATE_IP)) out(422, ['error' => 'Please enter a website address like example.com.']);
    $host = $t[0];
    $n = $pdo->prepare('SELECT COUNT(*) FROM watchlist WHERE user_id=?');
    $n->execute([$uid]);
    if ((int)$n->fetchColumn() >= $MAX) out(422, ['error' => 'Your watchlist is full (' . $MAX . ' sites).' . ($plan['pro'] ? ' Remove one to add another.' : ' Remove one, or upgrade to Pro for up to ' . PRO_WATCH . ' sites.'), 'upgrade' => !$plan['pro']]);
    $e = $pdo->prepare('SELECT id FROM watchlist WHERE user_id=? AND host=?');
    $e->execute([$uid, $host]);
    if (!$e->fetch()) {
        $pdo->prepare('INSERT INTO watchlist (user_id, host, added_at) VALUES (?,?,?)')->execute([$uid, $host, sql_now()]);
        // First status straight away if the cron has not seen this site yet.
        $s = $pdo->prepare('SELECT 1 FROM site_status WHERE host=?');
        $s->execute([$host]);
        if (!$s->fetch()) { throttle('watchprobe', 20, 10); note_attempt('watchprobe'); probe_and_store($pdo, $host); }
    }
    out(200, ['items' => my_list($pdo, $uid), 'max' => $MAX, 'pro' => $plan['pro']]);
}
if ($a === 'remove') {
    $pdo->prepare('DELETE FROM watchlist WHERE user_id=? AND host=?')->execute([$uid, strtolower((string)($in['host'] ?? ''))]);
    out(200, ['items' => my_list($pdo, $uid), 'max' => $MAX, 'pro' => $plan['pro']]);
}
if ($a === 'alerts') {
    $pdo->prepare('UPDATE watchlist SET alerts=? WHERE user_id=? AND host=?')->execute([!empty($in['on']) ? 1 : 0, $uid, strtolower((string)($in['host'] ?? ''))]);
    out(200, ['items' => my_list($pdo, $uid), 'max' => $MAX, 'pro' => $plan['pro']]);
}
if ($a === 'check') {
    $host = strtolower((string)($in['host'] ?? ''));
    $e = $pdo->prepare('SELECT 1 FROM watchlist WHERE user_id=? AND host=?');
    $e->execute([$uid, $host]);
    if (!$e->fetch()) out(404, ['error' => 'That site is not on your watchlist.']);
    throttle('watchprobe', 20, 10);
    note_attempt('watchprobe');
    probe_and_store($pdo, $host);
    out(200, ['items' => my_list($pdo, $uid), 'max' => $MAX, 'pro' => $plan['pro']]);
}
out(400, ['error' => 'Bad request.']);
