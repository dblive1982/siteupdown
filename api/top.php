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
$cat = preg_replace('/[^a-z]/', '', strtolower((string)($_GET['cat'] ?? '')));
$list = [];
if ($cat !== '') { foreach ($pg as $h0 => $p0) if (($p0['cat'] ?? '') === $cat) $list[] = [$h0, $p0['name']]; }
else $list = top_sites();
foreach ($list as [$host, $name]) {
    $r = $st[$host] ?? null;
    if ($r && (!$latest || $r['checked_at'] > $latest)) $latest = $r['checked_at'];
    $items[] = ['host' => $host, 'name' => $name, 'page' => $pg[$host]['page'] ?? null, 'verdict' => $r['verdict'] ?? null, 'code' => isset($r['http_code']) ? (int)$r['http_code'] : null,
                'ms' => isset($r['ms']) ? (int)$r['ms'] : null, 'at' => $r ? iso($r['checked_at']) : null,
                'ssl' => $cert[$host]['status'] ?? null, 'ssl_days' => isset($cert[$host]['days_left']) ? (int)$cert[$host]['days_left'] : null];
}
header('Cache-Control: public, max-age=30');
out(200, ['cat' => $cat, 'items' => $items, 'updated' => $latest ? iso($latest) : null]);
