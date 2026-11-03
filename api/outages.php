<?php
// GET -> the most recent outages (still going first) across the sites on our public lists. Five by default, last 24 hours, ?n= up to 10.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sites.php';
require __DIR__ . '/_sitepages.php';
$pdo = db();
$names = [];
foreach (top_sites() as $s) $names[$s[0]] = ['name' => $s[1], 'page' => null];
foreach (gaming_sites() as $s) $names[$s[0]] = ['name' => $s[1], 'page' => null];
foreach (site_pages() as $h => $sp) $names[$h] = ['name' => $sp['name'], 'page' => $sp['page']];
$n = max(1, min(10, (int)($_GET['n'] ?? 5)));
$q = $pdo->prepare('SELECT host, started_at, ended_at FROM incidents WHERE started_at > ? OR ended_at IS NULL ORDER BY (ended_at IS NULL) DESC, started_at DESC LIMIT 80');
$q->execute([gmdate('Y-m-d H:i:s', time() - 86400)]);
$items = []; $now = time();
foreach ($q->fetchAll() as $r) {
    if (!isset($names[$r['host']])) continue;
    $st = strtotime($r['started_at'] . ' UTC'); $en = $r['ended_at'] ? strtotime($r['ended_at'] . ' UTC') : null;
    $items[] = ['host' => $r['host'], 'name' => $names[$r['host']]['name'], 'page' => $names[$r['host']]['page'],
        'started' => iso($r['started_at']), 'ended' => $en ? iso($r['ended_at']) : null, 'seconds' => max(0, ($en ?? $now) - $st)];
    if (count($items) >= $n) break;
}
header('Cache-Control: public, max-age=60');
out(200, ['items' => $items, 'now' => gmdate('Y-m-d\TH:i:s\Z')]);
