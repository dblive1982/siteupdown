<?php
// GET -> the latest checked websites (one row per site).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sites.php';
require __DIR__ . '/_sitepages.php';
// Only well-known sites are listed publicly. Addresses people type in (which could be anything, including scam sites) are never shown or linked.
$known = [];
foreach (site_pages() as $h0 => $x) $known[$h0] = 1;
foreach (top_sites() as $x) $known[$x[0]] = 1;
foreach (gaming_sites() as $x) $known[$x[0]] = 1;
$rows = db()->query('SELECT host, verdict, http_code, ms, checked_at FROM checks ORDER BY id DESC LIMIT 400')->fetchAll();
$seen = []; $items = [];
foreach ($rows as $r) {
    if (isset($seen[$r['host']]) || !isset($known[$r['host']])) continue;
    $seen[$r['host']] = 1;
    $items[] = ['host' => $r['host'], 'verdict' => $r['verdict'], 'code' => $r['http_code'] !== null ? (int)$r['http_code'] : null, 'ms' => $r['ms'] !== null ? (int)$r['ms'] : null, 'at' => iso($r['checked_at'])];
    if (count($items) >= 10) break;
}
header('Cache-Control: public, max-age=10');
out(200, ['items' => $items]);
