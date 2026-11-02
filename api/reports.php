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
    $q = $pdo->prepare('SELECT host, COUNT(*) AS n FROM reports WHERE ts > ? GROUP BY host ORDER BY n DESC LIMIT 8');
    $q->execute([gmdate('Y-m-d H:i:s', $now - 3 * 3600)]);
    $items = [];
    foreach ($q->fetchAll() as $r) {
        if ((int)$r['n'] < 3 || !isset($sites[$r['host']])) continue;     // a couple of reports is just noise
        $items[] = ['host' => $r['host'], 'name' => $sites[$r['host']]['name'], 'page' => $sites[$r['host']]['page'], 'count' => (int)$r['n']];
    }
    out(200, ['items' => $items]);
}

$host = strtolower(trim((string)($_GET['host'] ?? '')));
if (!isset($sites[$host])) {
    $t = parse_target($host);
    if (!$t || filter_var($t[0], FILTER_VALIDATE_IP) || $t[0] !== $host) out(404, ['error' => 'No reports are collected for that address.']);
}
$name = $sites[$host]['name'] ?? $host;

$since = $now - 24 * 3600;
$q = $pdo->prepare('SELECT kind, ts FROM reports WHERE host=? AND ts > ? ORDER BY ts');
$q->execute([$host, gmdate('Y-m-d H:i:s', $since)]);
$bars = array_fill(0, 24, 0);
$kinds = ['site' => 0, 'login' => 0, 'app' => 0, 'slow' => 0];
$total = 0; $last3 = 0; $last = null;
foreach ($q->fetchAll() as $r) {
    $t = strtotime($r['ts'] . ' UTC');
    $i = min(23, max(0, (int)floor(($t - $since) / 3600)));
    $bars[$i]++; $total++;
    if (isset($kinds[$r['kind']])) $kinds[$r['kind']]++;
    if ($t > $now - 3 * 3600) $last3++;
    $last = $r['ts'];
}
// What is normal for this site: the average number of reports per hour over the previous 6 days.
$b = $pdo->prepare('SELECT COUNT(*) FROM reports WHERE host=? AND ts > ? AND ts <= ?');
$b->execute([$host, gmdate('Y-m-d H:i:s', $now - 7 * 86400), gmdate('Y-m-d H:i:s', $since)]);
$base = round(((int)$b->fetchColumn()) / (6 * 24), 2);
$level = 'none';
if ($total > 0) $level = 'low';
if ($last3 >= 12 && $last3 > 4 * $base * 3) $level = 'high';
elseif ($last3 >= 5 && $last3 > 2 * $base * 3) $level = 'raised';
out(200, ['host' => $host, 'name' => $name, 'page' => $sites[$host]['page'] ?? null, 'hours' => $bars, 'total' => $total, 'kinds' => $kinds,
          'last3h' => $last3, 'usual_per_hour' => $base, 'level' => $level, 'last' => iso($last), 'start' => gmdate('Y-m-d\TH:i:s\Z', $since)]);
