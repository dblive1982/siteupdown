<?php
// GET -> listed sites that are answering much slower than their own recent normal. Uses only our own checks.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sites.php';
require __DIR__ . '/_sitepages.php';
$cache = sys_get_temp_dir() . '/sud_slow.json';
if (is_file($cache) && filemtime($cache) > time() - 120) { header('Content-Type: application/json'); header('Cache-Control: public, max-age=60'); readfile($cache); exit; }
$pdo = db();
$names = [];
foreach (site_pages() as $h => $sp) $names[$h] = ['name' => $sp['name'], 'page' => $sp['page']];
$now = time();
// Normal: average of successful checks between 24 hours and 90 minutes ago (needs at least 12 samples).
$base = [];
$q = $pdo->prepare("SELECT host, AVG(ms) a, COUNT(*) n FROM site_log WHERE ts > ? AND ts < ? AND verdict='up' AND ms IS NOT NULL GROUP BY host HAVING COUNT(*) >= 12");
$q->execute([gmdate('Y-m-d H:i:s', $now - 86400), gmdate('Y-m-d H:i:s', $now - 5400)]);
foreach ($q->fetchAll() as $r) $base[$r['host']] = (float)$r['a'];
// Now: average of the last 90 minutes (needs at least 3 samples), so one slow check does not count.
$q = $pdo->prepare("SELECT host, AVG(ms) a, COUNT(*) n FROM site_log WHERE ts > ? AND verdict='up' AND ms IS NOT NULL GROUP BY host HAVING COUNT(*) >= 3");
$q->execute([gmdate('Y-m-d H:i:s', $now - 5400)]);
$items = [];
foreach ($q->fetchAll() as $r) {
    $h = $r['host'];
    if (!isset($names[$h]) || !isset($base[$h])) continue;
    $cur = (float)$r['a']; $norm = $base[$h];
    if ($cur >= $norm * 1.8 && $cur - $norm >= 250) $items[] = ['host' => $h, 'name' => $names[$h]['name'], 'page' => $names[$h]['page'], 'now' => (int)round($cur), 'usual' => (int)round($norm), 'x' => round($cur / max($norm, 1), 1)];
}
usort($items, fn($a, $b) => $b['x'] <=> $a['x']);
$json = json_encode(['items' => array_slice($items, 0, 5)]);
@file_put_contents($cache, $json);
header('Content-Type: application/json'); header('Cache-Control: public, max-age=60');
echo $json;
