<?php
// GET -> the numbers behind the weekly "state of the internet" page, from our own checks and visitor report counts. Cached for ten minutes.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$cache = sys_get_temp_dir() . '/sud_weekly.json';
header('Cache-Control: public, max-age=300');
if (is_file($cache) && filemtime($cache) > time() - 600) { header('Content-Type: application/json'); readfile($cache); exit; }
$pdo = db(); $pg = site_pages(); $now = time(); $ts = fn(int $t) => gmdate('Y-m-d H:i:s', $t);
$R = ['from' => gmdate('Y-m-d', $now - 6 * 86400), 'to' => gmdate('Y-m-d', $now)];
$q = $pdo->prepare('SELECT day, SUM(outages) o, SUM(down_s) d FROM site_daily WHERE day >= ? GROUP BY day');
$q->execute([gmdate('Y-m-d', $now - 13 * 86400)]);
$cur = 0; $prev = 0; $down = 0; $days = [];
foreach ($q->fetchAll() as $r) { if ($r['day'] >= $R['from']) { $cur += (int)$r['o']; $down += (int)$r['d']; $days[$r['day']] = (int)$r['o']; } else $prev += (int)$r['o']; }
$R['outages'] = $cur; $R['outages_prev'] = $prev; $R['down_s'] = $down;
arsort($days); $R['worst_day'] = $days && reset($days) > 0 ? ['day' => key($days), 'n' => reset($days)] : null;

$q = $pdo->prepare('SELECT host, SUM(up_n) u, SUM(bad_n) b, SUM(outages) o, SUM(down_s) d, SUM(ms_sum) ms, SUM(ms_n) mn FROM site_daily WHERE day >= ? GROUP BY host');
$q->execute([$R['from']]); $sites = [];
foreach ($q->fetchAll() as $r) {
    $h = $r['host']; $n = (int)$r['u'] + (int)$r['b'];
    if (!isset($pg[$h]) || $n < 100) continue;
    $sites[$h] = ['host' => $h, 'name' => $pg[$h]['name'], 'page' => $pg[$h]['page'], 'cat' => $pg[$h]['cat'] ?? 'other', 'pct' => round(100 * (int)$r['u'] / $n, 2), 'outages' => (int)$r['o'], 'down' => (int)$r['d'], 'ms' => (int)$r['mn'] ? (int)round($r['ms'] / $r['mn']) : null];
}
$R['tracked'] = count($sites);
$R['perfect'] = count(array_filter($sites, fn($v) => $v['outages'] === 0 && $v['pct'] >= 99.99));
$byUp = $sites; uasort($byUp, fn($a, $b) => [$b['pct'], $a['ms'] ?? 9e9] <=> [$a['pct'], $b['ms'] ?? 9e9]);
$R['best'] = array_values(array_slice($byUp, 0, 5));
$worst = array_filter($sites, fn($v) => $v['outages'] > 0); uasort($worst, fn($a, $b) => [$a['pct'], -$a['outages']] <=> [$b['pct'], -$b['outages']]);
$R['worst'] = array_values(array_slice($worst, 0, 5));
$cat = [];
foreach ($sites as $v) { $cat[$v['cat']]['p'][] = $v['pct']; $cat[$v['cat']]['o'] = ($cat[$v['cat']]['o'] ?? 0) + $v['outages']; }
$R['cats'] = [];
foreach ($cat as $c => $d) if (count($d['p']) >= 3) $R['cats'][] = ['cat' => $c, 'sites' => count($d['p']), 'pct' => round(array_sum($d['p']) / count($d['p']), 2), 'outages' => $d['o']];
usort($R['cats'], fn($a, $b) => $b['pct'] <=> $a['pct']);

$q = $pdo->prepare('SELECT host, started_at, ended_at FROM incidents WHERE started_at > ? AND ended_at IS NOT NULL');
$q->execute([$ts($now - 7 * 86400)]); $long = null;
foreach ($q->fetchAll() as $r) {
    if (!isset($pg[$r['host']])) continue;
    $sec = strtotime($r['ended_at'] . ' UTC') - strtotime($r['started_at'] . ' UTC');
    if (!$long || $sec > $long['seconds']) $long = ['name' => $pg[$r['host']]['name'], 'page' => $pg[$r['host']]['page'], 'started' => iso($r['started_at']), 'seconds' => $sec];
}
$R['longest'] = $long;
try {
    $q = $pdo->prepare('SELECT SUM(rep_site+rep_login+rep_app+rep_slow) n FROM history_days WHERE day >= ?'); $q->execute([$R['from']]);
    $R['reports'] = (int)$q->fetchColumn();
} catch (Throwable $e) { $R['reports'] = 0; }
$R['now'] = gmdate('Y-m-d\TH:i:s\Z');
$json = json_encode($R); @file_put_contents($cache, $json);
header('Content-Type: application/json'); echo $json;
