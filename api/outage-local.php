<?php
// GET ?hours=3 (1 to 72) -> where visitors reported problems, grouped into coarse cells (0.2 degree, about 20 km). Never individual reports.
// Each cell has a weight that fades as its reports age, and sites are marked recovered when our own check passes again or visitors say it works.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$hours = max(1, min(72, (int)($_GET['hours'] ?? 3)));
$now = time();
$pdo = db();
$cut = gmdate('Y-m-d H:i:s', $now - $hours * 3600);
$st = $pdo->prepare('SELECT host, kind, ts, lat, lon FROM reports WHERE ts > ? AND lat IS NOT NULL AND lon IS NOT NULL');
$st->execute([$cut]);
$rows = $st->fetchAll();
$pages = site_pages();

// Which sites look recovered: visitors say it works again, or our latest check passes and the last problem report is not fresh.
$hosts = array_values(array_unique(array_column($rows, 'host')));
$rec = [];
if ($hosts) {
    $hr = gmdate('Y-m-d H:i:s', $now - 3600);
    $fx = $pdo->prepare("SELECT host, SUM(CASE WHEN kind='fixed' THEN 1 ELSE 0 END) AS f, SUM(CASE WHEN kind<>'fixed' THEN 1 ELSE 0 END) AS p, MAX(CASE WHEN kind<>'fixed' THEN ts END) AS last FROM reports WHERE ts > ? GROUP BY host");
    $fx->execute([$hr]);
    $info = [];
    foreach ($fx->fetchAll() as $r) $info[$r['host']] = $r;
    $ss = $pdo->prepare('SELECT verdict, checked_at FROM site_status WHERE host=?');
    foreach ($hosts as $h) {
        $why = null; $i = $info[$h] ?? null;
        if ($i && (int)$i['f'] >= 2 && (int)$i['f'] >= 0.5 * max(1, (int)$i['p'])) $why = 'visitors';
        $ss->execute([$h]); $s = $ss->fetch();
        if ($s && $s['verdict'] === 'up' && strtotime($s['checked_at'] . ' UTC') > $now - 1800) {
            $last = $i && $i['last'] ? strtotime($i['last'] . ' UTC') : 0;
            if ($now - $last > 900) $why = $why ? 'both' : 'checks';
        }
        $rec[$h] = $why;
    }
}

$cell = 0.2; $cells = []; $total = 0;
foreach ($rows as $r) {
    if ($r['kind'] === 'fixed') continue;
    $la = round(floor(((float)$r['lat']) / $cell) * $cell + $cell / 2, 2);
    $lo = round(floor(((float)$r['lon']) / $cell) * $cell + $cell / 2, 2);
    $k = $la . ',' . $lo;
    if (!isset($cells[$k])) $cells[$k] = ['lat' => $la, 'lon' => $lo, 'cell' => $cell, 'n' => 0, 'w' => 0.0, 'by' => [], 'newest' => 0];
    $age = max(0, $now - strtotime($r['ts'] . ' UTC'));
    $w = max(0.0, 1 - $age / ($hours * 3600));
    if ($rec[$r['host']] ?? null) $w *= 0.25;
    $cells[$k]['n']++; $cells[$k]['w'] += $w; $total++;
    $cells[$k]['newest'] = max($cells[$k]['newest'], strtotime($r['ts'] . ' UTC'));
    $name = isset($pages[$r['host']]) ? $pages[$r['host']]['name'] : $r['host'];
    $cells[$k]['by'][$name] = $cells[$k]['by'][$name] ?? ['n' => 0, 'rec' => $rec[$r['host']] ?? null];
    $cells[$k]['by'][$name]['n']++;
}
$out = [];
foreach ($cells as $c) {
    if ($c['w'] < 0.05) continue;
    uasort($c['by'], fn($a, $b) => $b['n'] <=> $a['n']); $sites = [];
    foreach (array_slice($c['by'], 0, 3, true) as $nm => $v) $sites[] = ['name' => (string)$nm, 'n' => $v['n'], 'rec' => $v['rec']];
    $out[] = ['lat' => $c['lat'], 'lon' => $c['lon'], 'cell' => $c['cell'], 'n' => $c['n'], 'w' => round($c['w'], 2), 'newest' => iso(gmdate('Y-m-d H:i:s', $c['newest'])), 'sites' => $sites];
}
usort($out, fn($a, $b) => $b['w'] <=> $a['w']);
header('Cache-Control: public, max-age=60');
out(200, ['hours' => $hours, 'total' => $total, 'cells' => array_slice($out, 0, 400)]);
