<?php
// GET ?hours=24 -> where visitors reported problems, grouped into coarse cells (0.2 degree, about 20 km). Never individual reports.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$hours = max(1, min(72, (int)($_GET['hours'] ?? 24)));
$cut = gmdate('Y-m-d H:i:s', time() - $hours * 3600);
$st = db()->prepare('SELECT host, lat, lon FROM reports WHERE ts > ? AND lat IS NOT NULL AND lon IS NOT NULL');
$st->execute([$cut]);
$pages = site_pages();
$cell = 0.2; $cells = []; $total = 0;
foreach ($st->fetchAll() as $r) {
    $la = round(floor(((float)$r['lat']) / $cell) * $cell + $cell / 2, 2);
    $lo = round(floor(((float)$r['lon']) / $cell) * $cell + $cell / 2, 2);
    $k = $la . ',' . $lo;
    if (!isset($cells[$k])) $cells[$k] = ['lat' => $la, 'lon' => $lo, 'cell' => $cell, 'n' => 0, 'by' => []];
    $cells[$k]['n']++; $total++;
    $name = isset($pages[$r['host']]) ? $pages[$r['host']]['name'] : $r['host'];
    $cells[$k]['by'][$name] = ($cells[$k]['by'][$name] ?? 0) + 1;
}
$out = [];
foreach ($cells as $c) {
    arsort($c['by']); $sites = [];
    foreach (array_slice($c['by'], 0, 3, true) as $nm => $n) $sites[] = ['name' => (string)$nm, 'n' => $n];
    $out[] = ['lat' => $c['lat'], 'lon' => $c['lon'], 'cell' => $c['cell'], 'n' => $c['n'], 'sites' => $sites];
}
usort($out, fn($a, $b) => $b['n'] <=> $a['n']);
header('Cache-Control: public, max-age=60');
out(200, ['hours' => $hours, 'total' => $total, 'cells' => array_slice($out, 0, 400)]);
