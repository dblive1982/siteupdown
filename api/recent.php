<?php
// GET -> the latest checked websites (one row per site).
require __DIR__ . '/_boot.php';
$rows = db()->query('SELECT host, verdict, http_code, ms, checked_at FROM checks ORDER BY id DESC LIMIT 80')->fetchAll();
$seen = []; $items = [];
foreach ($rows as $r) {
    if (isset($seen[$r['host']])) continue;
    $seen[$r['host']] = 1;
    $items[] = ['host' => $r['host'], 'verdict' => $r['verdict'], 'code' => $r['http_code'] !== null ? (int)$r['http_code'] : null, 'ms' => $r['ms'] !== null ? (int)$r['ms'] : null, 'at' => iso($r['checked_at'])];
    if (count($items) >= 10) break;
}
header('Cache-Control: public, max-age=10');
out(200, ['items' => $items]);
