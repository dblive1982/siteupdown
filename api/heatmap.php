<?php
// GET -> how the sites we list look from each of our worldwide probe places, from the background sweep snapshots.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$pages = site_pages();
$rows = db()->query("SELECT host, data, ts FROM world_checks WHERE data <> ''")->fetchAll();
$places = []; $sites = []; $oldest = null; $newest = null; $n = 0;
foreach ($rows as $r) {
    $h = $r['host'];
    if (!isset($pages[$h])) continue;
    $d = json_decode($r['data'], true);
    if (!is_array($d) || empty($d['probes'])) continue;
    $n++; $ts = (int)$r['ts'];
    $oldest = $oldest === null ? $ts : min($oldest, $ts); $newest = $newest === null ? $ts : max($newest, $ts);
    $ok = 0; $tot = 0;
    foreach ($d['probes'] as $p) {
        $k = ($p['country'] ?? '') . '|' . ($p['city'] ?? '');
        if (!isset($places[$k])) $places[$k] = ['country' => $p['country'] ?? '', 'city' => $p['city'] ?? '', 'lat' => $p['lat'] ?? null, 'lon' => $p['lon'] ?? null, 'n' => 0, 'ok' => 0, 'error' => 0, 'blocked' => 0, 'none' => 0, 'ms' => []];
        $pl = &$places[$k]; $pl['n']++;
        $st = in_array($p['state'] ?? '', ['ok', 'error', 'blocked', 'none'], true) ? $p['state'] : 'none';
        $pl[$st]++;
        if ($st === 'ok' && is_numeric($p['ms'] ?? null)) $pl['ms'][] = (int)$p['ms'];
        unset($pl);
        $tot++; if (($p['state'] ?? '') === 'ok') $ok++;
    }
    if ($tot && $ok < $tot) $sites[] = ['name' => $pages[$h]['name'], 'page' => $pages[$h]['page'], 'ok' => $ok, 'total' => $tot];
}
foreach ($places as &$p) {
    sort($p['ms']); $c = count($p['ms']);
    $p['median_ms'] = $c ? ($c % 2 ? $p['ms'][intdiv($c, 2)] : (int)round(($p['ms'][$c / 2 - 1] + $p['ms'][$c / 2]) / 2)) : null;
    unset($p['ms']);
}
unset($p);
usort($sites, fn($a, $b) => ($a['ok'] / $a['total']) <=> ($b['ok'] / $b['total']));
header('Cache-Control: public, max-age=300');
out(200, ['places' => array_values($places), 'sites_count' => $n, 'oldest' => $oldest, 'newest' => $newest, 'unreachable' => array_slice($sites, 0, 8)]);
