<?php
// GET -> the "Top websites" list with the latest result from cron.php.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sites.php';
require __DIR__ . '/_sitepages.php';
$pg = site_pages();
$pdo = db();
$st = [];
foreach ($pdo->query('SELECT host, verdict, http_code, ms, checked_at FROM site_status')->fetchAll() as $r) $st[$r['host']] = $r;
$cert = [];
foreach ($pdo->query('SELECT host, status, days_left FROM site_cert')->fetchAll() as $r) $cert[$r['host']] = $r;
$items = []; $latest = null;
foreach (top_sites() as [$host, $name]) {
    $r = $st[$host] ?? null;
    if ($r && (!$latest || $r['checked_at'] > $latest)) $latest = $r['checked_at'];
    $items[] = ['host' => $host, 'name' => $name, 'page' => $pg[$host]['page'] ?? null, 'verdict' => $r['verdict'] ?? null, 'code' => isset($r['http_code']) ? (int)$r['http_code'] : null,
                'ms' => isset($r['ms']) ? (int)$r['ms'] : null, 'at' => $r ? iso($r['checked_at']) : null,
                'ssl' => $cert[$host]['status'] ?? null, 'ssl_days' => isset($cert[$host]['days_left']) ? (int)$cert[$host]['days_left'] : null];
}
header('Cache-Control: public, max-age=30');
out(200, ['items' => $items, 'updated' => $latest ? iso($latest) : null]);
