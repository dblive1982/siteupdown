<?php
// GET ?host=example.com -> visitor problem reports for the last 24 hours (hourly bars), split by type.
// GET ?top=1            -> the sites with the most reports in the last 3 hours.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_probe.php';
$pdo = db();
$sites = site_pages();
$now = time();
header('Cache-Control: public, max-age=30');

if (!empty($_GET['top'])) {
    $q = $pdo->prepare("SELECT host, COUNT(*) AS n FROM reports WHERE ts > ? AND kind <> 'fixed' GROUP BY host ORDER BY n DESC LIMIT 8");
    $q->execute([gmdate('Y-m-d H:i:s', $now - 3 * 3600)]);
    $items = [];
    foreach ($q->fetchAll() as $r) {
        if ((int)$r['n'] < 3 || !isset($sites[$r['host']])) continue;     // a couple of reports is just noise
        $items[] = ['host' => $r['host'], 'name' => $sites[$r['host']]['name'], 'page' => $sites[$r['host']]['page'], 'count' => (int)$r['n']];
    }
    out(200, ['items' => $items]);
}

if (!empty($_GET['recent'])) {
    // Latest reports as a list: site, type, how long ago, and the country only when at least 3 reports came from it today.
    $since = gmdate('Y-m-d H:i:s', $now - 24 * 3600);
    $h = strtolower(trim((string)($_GET['host'] ?? '')));
    if ($h !== '' && !isset($sites[$h]) && !parse_target($h)) out(404, ['error' => 'No reports are collected for that address.']);
    $cc = $pdo->prepare('SELECT country, COUNT(*) AS n FROM reports WHERE ts > ? AND country IS NOT NULL GROUP BY country');
    $cc->execute([$since]); $busy = [];
    foreach ($cc->fetchAll() as $r) if ((int)$r['n'] >= 3) $busy[$r['country']] = true;
    $q = $h !== '' ? $pdo->prepare('SELECT host, kind, ts, country FROM reports WHERE ts > ? AND host = ? ORDER BY ts DESC LIMIT 15')
                   : $pdo->prepare('SELECT host, kind, ts, country FROM reports WHERE ts > ? ORDER BY ts DESC LIMIT 15');
    $q->execute($h !== '' ? [$since, $h] : [$since]);
    $items = [];
    foreach ($q->fetchAll() as $r) {
        if (!in_array($r['kind'], ['site', 'login', 'app', 'slow', 'fixed'], true)) continue;
        $items[] = ['host' => $r['host'], 'name' => $sites[$r['host']]['name'] ?? $r['host'], 'page' => $sites[$r['host']]['page'] ?? null,
                    'kind' => $r['kind'], 'ts' => iso($r['ts']), 'country' => ($r['country'] && isset($busy[$r['country']])) ? $r['country'] : null];
    }
    out(200, ['items' => $items]);
}

$host = strtolower(trim((string)($_GET['host'] ?? '')));
if (!isset($sites[$host])) {
    $t = parse_target($host);
    if (!$t || filter_var($t[0], FILTER_VALIDATE_IP) || $t[0] !== $host) out(404, ['error' => 'No reports are collected for that address.']);
}
$name = $sites[$host]['name'] ?? $host;

$range = (string)($_GET['range'] ?? '24h');
if (!in_array($range, ['24h', '7d', '30d', '1y'], true)) $range = '24h';
$K = ['site', 'login', 'app', 'slow'];
$empty = fn() => ['site' => 0, 'login' => 0, 'app' => 0, 'slow' => 0];
$since = $now - 24 * 3600;
// Buckets for the chosen range: hourly for 24h, daily for 7d and 30d, weekly for 1y (UTC).
$buckets = []; $unit = 'hour';
if ($range === '24h') {
    $b0 = (int)(floor($now / 3600) * 3600) - 23 * 3600;
    for ($i = 0; $i < 24; $i++) $buckets[gmdate('Y-m-d H', $b0 + $i * 3600)] = ['t' => gmdate('Y-m-d\TH:00:00\Z', $b0 + $i * 3600), 'n' => 0, 'k' => $empty()];
    $from = $b0; $fmt = 13;
} else {
    $unit = $range === '1y' ? 'week' : 'day';
    $days = $range === '7d' ? 7 : ($range === '30d' ? 30 : 364);
    $d0 = (int)(floor($now / 86400) * 86400) - ($days - 1) * 86400;
    if ($range === '1y') { for ($i = 0; $i < 52; $i++) { $t = $d0 + $i * 7 * 86400; $buckets['w' . $i] = ['t' => gmdate('Y-m-d\T00:00:00\Z', $t), 'n' => 0, 'k' => $empty(), 's' => $t]; } }
    else for ($i = 0; $i < $days; $i++) $buckets[gmdate('Y-m-d', $d0 + $i * 86400)] = ['t' => gmdate('Y-m-d\T00:00:00\Z', $d0 + $i * 86400), 'n' => 0, 'k' => $empty()];
    $from = $d0; $fmt = 10;
}
$q = $pdo->prepare("SELECT substr(ts,1,$fmt) AS d, kind, COUNT(*) AS n FROM reports WHERE host=? AND ts >= ? GROUP BY substr(ts,1,$fmt), kind");
$q->execute([$host, gmdate('Y-m-d H:i:s', $from)]);
$total = 0; $kinds = $empty();
foreach ($q->fetchAll() as $r) {
    $key = $r['d'];
    if ($range === '1y') { $ts = strtotime($r['d'] . ' UTC'); $key = 'w' . min(51, max(0, (int)floor(($ts - $d0) / (7 * 86400)))); }
    if (!isset($buckets[$key]) || !in_array($r['kind'], $K, true)) continue;
    $c = (int)$r['n'];
    $buckets[$key]['n'] += $c; $buckets[$key]['k'][$r['kind']] += $c; $total += $c; $kinds[$r['kind']] += $c;
}
foreach ($buckets as &$bk) unset($bk['s']); unset($bk);
$cq = $pdo->prepare('SELECT country, COUNT(*) AS n FROM reports WHERE host=? AND kind <> \'fixed\' AND ts >= ? AND country IS NOT NULL AND country <> \'\' GROUP BY country ORDER BY n DESC LIMIT 6');
$cq->execute([$host, gmdate('Y-m-d H:i:s', $from)]);
$countries = array_map(fn($r) => ['cc' => $r['country'], 'n' => (int)$r['n']], $cq->fetchAll());
// Last three hours and what is normal for this site (average per hour over the previous 6 days) drive the "more than usual" label.
$l3 = $pdo->prepare("SELECT COUNT(*), MAX(ts) FROM reports WHERE host=? AND kind <> 'fixed' AND ts > ?");
$l3->execute([$host, gmdate('Y-m-d H:i:s', $now - 3 * 3600)]);
[$last3, $lastTs] = array_map(fn($v) => $v, $l3->fetch(PDO::FETCH_NUM)); $last3 = (int)$last3;
$b = $pdo->prepare("SELECT COUNT(*) FROM reports WHERE host=? AND kind <> 'fixed' AND ts > ? AND ts <= ?");
$b->execute([$host, gmdate('Y-m-d H:i:s', $now - 7 * 86400), gmdate('Y-m-d H:i:s', $since)]);
$base = round(((int)$b->fetchColumn()) / (6 * 24), 2);
$t24 = $pdo->prepare("SELECT COUNT(*) FROM reports WHERE host=? AND kind <> 'fixed' AND ts > ?"); $t24->execute([$host, gmdate('Y-m-d H:i:s', $since)]); $total24 = (int)$t24->fetchColumn();
$level = 'none';
if ($total24 > 0) $level = 'low';
if ($last3 >= 12 && $last3 > 4 * $base * 3) $level = 'high';
elseif ($last3 >= 5 && $last3 > 2 * $base * 3) $level = 'raised';
out(200, ['host' => $host, 'name' => $name, 'page' => $sites[$host]['page'] ?? null, 'range' => $range, 'unit' => $unit, 'buckets' => array_values($buckets),
          'total' => $total, 'total24' => $total24, 'kinds' => $kinds, 'countries' => $countries, 'last3h' => $last3, 'usual_per_hour' => $base, 'level' => $level, 'last' => iso($lastTs), 'now' => gmdate('Y-m-d\TH:i:s\Z', $now)]);
