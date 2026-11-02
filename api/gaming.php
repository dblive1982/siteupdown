<?php
// GET ?q=&cat=&page= -> gaming services with their latest status (24 per page).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sites.php';
require __DIR__ . '/_sitepages.php';
$pg = site_pages();
$pdo = db();
$st = [];
foreach ($pdo->query('SELECT host, verdict, http_code, ms, checked_at FROM site_status')->fetchAll() as $r) $st[$r['host']] = $r;
$cert = [];
foreach ($pdo->query('SELECT host, status, days_left FROM site_cert')->fetchAll() as $r) $cert[$r['host']] = $r;
$q = mb_strtolower(trim((string)($_GET['q'] ?? '')));
$cat = (string)($_GET['cat'] ?? 'All');
$page = max(1, (int)($_GET['page'] ?? 1));
$per = 24;
$all = []; $seen = [];
foreach (gaming_sites() as [$host, $name, $c]) {
    $key = mb_strtolower($name);
    if (isset($seen[$key])) continue;
    $seen[$key] = 1;
    $all[] = [$host, $name, $c];
}
usort($all, fn($a, $b) => strcasecmp($a[1], $b[1]));
$cats = ['All', 'Multiplayer', 'Shooters', 'Platforms', 'Casual', 'Services', 'MMO'];
$f = array_values(array_filter($all, fn($x) => ($cat === 'All' || $x[2] === $cat) && ($q === '' || str_contains(mb_strtolower($x[1]), $q))));
$total = count($f);
$pages = max(1, (int)ceil($total / $per));
$page = min($page, $pages);
$items = [];
foreach (array_slice($f, ($page - 1) * $per, $per) as [$host, $name, $c]) {
    $r = $st[$host] ?? null;
    $items[] = ['host' => $host, 'name' => $name, 'page' => $pg[$host]['page'] ?? null, 'cat' => $c, 'verdict' => $r['verdict'] ?? null,
                'ms' => isset($r['ms']) ? (int)$r['ms'] : null, 'at' => $r ? iso($r['checked_at']) : null,
                'ssl' => $cert[$host]['status'] ?? null, 'ssl_days' => isset($cert[$host]['days_left']) ? (int)$cert[$host]['days_left'] : null];
}
header('Cache-Control: public, max-age=30');
out(200, ['items' => $items, 'total' => $total, 'all_total' => count($all), 'page' => $page, 'pages' => $pages, 'cats' => $cats]);
