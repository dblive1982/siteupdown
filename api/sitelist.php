<?php
// GET -> the latest status of every site that has an "Is X down?" page (used by the directory page).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$pdo = db();
$st = [];
foreach ($pdo->query('SELECT host, verdict, ms, checked_at FROM site_status')->fetchAll() as $r) $st[$r['host']] = $r;
$rep = [];
$q = $pdo->prepare('SELECT host, COUNT(*) AS n FROM reports WHERE ts > ? GROUP BY host');
$q->execute([gmdate('Y-m-d H:i:s', time() - 3 * 3600)]);
foreach ($q->fetchAll() as $r) $rep[$r['host']] = (int)$r['n'];
$items = [];
foreach (site_pages() as $host => $p) {
    $r = $st[$host] ?? null;
    $items[$host] = ['v' => $r['verdict'] ?? null, 'ms' => isset($r['ms']) ? (int)$r['ms'] : null, 'at' => $r ? iso($r['checked_at']) : null, 'rep' => $rep[$host] ?? 0];
}
header('Cache-Control: public, max-age=30');
out(200, ['items' => $items]);
