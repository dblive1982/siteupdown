<?php
// GET ?host=example.com&range=24h|7d|30d -> uptime %, response-time series and outages for the public status page.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
$t = parse_target((string)($_GET['host'] ?? ''));
if (!$t || filter_var($t[0], FILTER_VALIDATE_IP)) out(422, ['error' => 'That is not a website address we can show.']);
$host = $t[0];
$pdo = db();
$cur = $pdo->prepare('SELECT verdict, http_code, ms, checked_at FROM site_status WHERE host=?');
$cur->execute([$host]);
$cur = $cur->fetch();
$has = $pdo->prepare('SELECT 1 FROM site_log WHERE host=? LIMIT 1');
$has->execute([$host]);
if (!$cur || !$has->fetch()) out(404, ['error' => 'We are not monitoring ' . $host . ' yet. Sign in and add it to your watchlist on the Monitor page to start its history.', 'host' => $host]);

$range = in_array($_GET['range'] ?? '', ['24h', '48h', '7d', '30d', '1y'], true) ? $_GET['range'] : '24h';
$spans = ['24h' => [86400, 48], '48h' => [2 * 86400, 48], '1y' => [30 * 86400, 30], '7d' => [7 * 86400, 56], '30d' => [30 * 86400, 30]];
[$span, $n] = $spans[$range];
$now = time();
$q = $pdo->prepare('SELECT ts, verdict, ms FROM site_log WHERE host=? AND ts > ? ORDER BY ts');
$q->execute([$host, gmdate('Y-m-d H:i:s', $now - 30 * 86400)]);
$rows = $q->fetchAll();

$win = ['24h' => [0, 0], '48h' => [0, 0], '7d' => [0, 0], '30d' => [0, 0]];
$buckets = array_fill(0, $n, ['ok' => 0, 'bad' => 0, 'sum' => 0, 'n' => 0]);
$bw = $span / $n;
foreach ($rows as $r) {
    $ts = strtotime($r['ts'] . ' UTC');
    $age = $now - $ts;
    $isOk = $r['verdict'] === 'up';
    $isBad = in_array($r['verdict'], ['down', 'timeout'], true);
    if (!$isOk && !$isBad) continue;
    foreach (['24h' => 86400, '48h' => 172800, '7d' => 7 * 86400, '30d' => 30 * 86400] as $k => $s) if ($age <= $s) $win[$k][$isOk ? 0 : 1]++;
    if ($age <= $span) {
        $i = min($n - 1, max(0, (int)floor(($span - $age) / $bw)));
        if ($isOk) { $buckets[$i]['ok']++; if ($r['ms'] !== null) { $buckets[$i]['sum'] += (int)$r['ms']; $buckets[$i]['n']++; } } else $buckets[$i]['bad']++;
    }
}
$series = [];
foreach ($buckets as $i => $b) {
    $tot = $b['ok'] + $b['bad'];
    $series[] = ['t' => gmdate('Y-m-d\TH:i:s\Z', (int)($now - $span + $i * $bw)),
        'state' => $tot === 0 ? 'none' : ($b['bad'] === 0 ? 'up' : ($b['ok'] === 0 ? 'down' : 'partial')),
        'ms' => $b['n'] ? (int)round($b['sum'] / $b['n']) : null];
}
$pct = fn($a) => ($a[0] + $a[1]) > 0 ? round(100 * $a[0] / ($a[0] + $a[1]), 2) : null;
$inc = $pdo->prepare('SELECT started_at, ended_at FROM incidents WHERE host=? ORDER BY started_at DESC LIMIT 10');
$inc->execute([$host]);
$incidents = array_map(fn($i) => ['started' => iso($i['started_at']), 'ended' => $i['ended_at'] ? iso($i['ended_at']) : null,
    'seconds' => max(0, ($i['ended_at'] ? strtotime($i['ended_at'] . ' UTC') : $now) - strtotime($i['started_at'] . ' UTC'))], $inc->fetchAll());
// Written summary of outages in the last 7 days (start, end, length), newest first.
$r7 = $pdo->prepare('SELECT started_at, ended_at FROM incidents WHERE host=? AND (ended_at IS NULL OR ended_at >= ?) ORDER BY started_at DESC LIMIT 30');
$r7->execute([$host, gmdate('Y-m-d H:i:s', $now - 7 * 86400)]);
$recent = []; $down7 = 0;
foreach ($r7->fetchAll() as $i) {
    $st = strtotime($i['started_at'] . ' UTC'); $en = $i['ended_at'] ? strtotime($i['ended_at'] . ' UTC') : null;
    $down7 += max(0, ($en ?? $now) - max($st, $now - 7 * 86400));
    $recent[] = ['started' => iso($i['started_at']), 'ended' => $en ? iso($i['ended_at']) : null, 'seconds' => max(0, ($en ?? $now) - $st)];
}
// 12-month record from the daily table.
$year = ['days' => 0, 'uptime' => null, 'outages' => 0, 'down_s' => 0, 'since' => null];
$yq = $pdo->prepare('SELECT day, up_n, bad_n, ms_sum, ms_n, outages, down_s FROM site_daily WHERE host=? AND day >= ? ORDER BY day');
$yq->execute([$host, gmdate('Y-m-d', $now - 364 * 86400)]);
$yrows = $yq->fetchAll();
$yu = 0; $yb = 0;
foreach ($yrows as $d) { $yu += (int)$d['up_n']; $yb += (int)$d['bad_n']; $year['outages'] += (int)$d['outages']; $year['down_s'] += (int)$d['down_s']; }
if ($yrows) { $year['days'] = count($yrows); $year['since'] = $yrows[0]['day']; $year['uptime'] = ($yu + $yb) > 0 ? round(100 * $yu / ($yu + $yb), 2) : null; }
if ($range === '1y') {
    $series = array_map(function ($d) {
        $tot = (int)$d['up_n'] + (int)$d['bad_n'];
        return ['t' => $d['day'] . 'T12:00:00Z', 'state' => $tot === 0 ? 'none' : ((int)$d['bad_n'] === 0 ? 'up' : ((int)$d['up_n'] === 0 ? 'down' : 'partial')),
            'ms' => (int)$d['ms_n'] > 0 ? (int)round($d['ms_sum'] / $d['ms_n']) : null,
            'pct' => $tot ? round(100 * (int)$d['up_n'] / $tot, 2) : null, 'outages' => (int)$d['outages'], 'down_s' => (int)$d['down_s']];
    }, $yrows);
}
$ssl = $pdo->prepare('SELECT status, days_left, expires FROM site_cert WHERE host=?');
$ssl->execute([$host]);
$ssl = $ssl->fetch() ?: null;
$ms = array_values(array_filter(array_column($series, 'ms'), fn($x) => $x !== null));
header('Cache-Control: public, max-age=60');
out(200, ['host' => $host, 'range' => $range,
    'current' => ['verdict' => $cur['verdict'], 'code' => $cur['http_code'] !== null ? (int)$cur['http_code'] : null, 'ms' => $cur['ms'] !== null ? (int)$cur['ms'] : null, 'at' => iso($cur['checked_at'])],
    'uptime' => ['24h' => $pct($win['24h']), '7d' => $pct($win['7d']), '30d' => $pct($win['30d']), '48h' => $pct($win['48h']), '1y' => $year['uptime']],
    'avg_ms' => $ms ? (int)round(array_sum($ms) / count($ms)) : null, 'max_ms' => $ms ? max($ms) : null, 'min_ms' => $ms ? min($ms) : null,
    'series' => $series, 'incidents' => $incidents, 'recent' => $recent, 'recent_down_s' => $down7, 'year' => $year,
    'ssl' => $ssl ? ['status' => $ssl['status'], 'days' => $ssl['days_left'] !== null ? (int)$ssl['days_left'] : null, 'expires' => $ssl['expires']] : null]);
