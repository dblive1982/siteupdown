<?php
// GET -> extra reports for the Outages tab, all built from our own checks and visitor report counts. Cached for two minutes.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$cache = sys_get_temp_dir() . '/sud_insights.json';
if (is_file($cache) && filemtime($cache) > time() - 120) { header('Content-Type: application/json'); header('Cache-Control: public, max-age=60'); readfile($cache); exit; }
$pdo = db();
$pg = site_pages();
$now = time();
$ts = fn(int $t) => gmdate('Y-m-d H:i:s', $t);
$item = fn(string $h, array $x = []) => array_merge(['host' => $h, 'name' => $pg[$h]['name'], 'page' => $pg[$h]['page']], $x);
$R = [];

// Uptime over the last 7 days, from the daily record plus today's checks.
$q = $pdo->prepare('SELECT host, SUM(up_n) u, SUM(bad_n) b, SUM(outages) o, SUM(down_s) d, SUM(ms_sum) ms, SUM(ms_n) mn FROM site_daily WHERE day >= ? GROUP BY host');
$q->execute([gmdate('Y-m-d', $now - 7 * 86400)]);
$up7 = [];
foreach ($q->fetchAll() as $r) {
    $h = $r['host']; $n = (int)$r['u'] + (int)$r['b'];
    if (!isset($pg[$h]) || $n < 100) continue;          // not enough checks yet to judge fairly
    $up7[$h] = ['pct' => round(100 * (int)$r['u'] / $n, 2), 'out' => (int)$r['o'], 'down' => (int)$r['d'], 'avg' => (int)$r['mn'] ? (int)round($r['ms'] / $r['mn']) : null];
}
$rel = $up7; uasort($rel, fn($a, $b) => [$b['pct'], $a['out'], $a['avg'] ?? 9e9] <=> [$a['pct'], $b['out'], $b['avg'] ?? 9e9]);
$R['reliable'] = []; foreach (array_slice($rel, 0, 6, true) as $h => $v) $R['reliable'][] = $item($h, ['pct' => $v['pct'], 'ms' => $v['avg']]);
$R['perfect'] = count(array_filter($up7, fn($v) => $v['out'] === 0 && $v['pct'] >= 99.99));
$R['tracked'] = count($up7);
$bad = array_filter($up7, fn($v) => $v['out'] > 0); uasort($bad, fn($a, $b) => [$a['pct'], -$a['out']] <=> [$b['pct'], -$b['out']]);
$R['unreliable'] = []; foreach (array_slice($bad, 0, 6, true) as $h => $v) $R['unreliable'][] = $item($h, ['pct' => $v['pct'], 'outages' => $v['out'], 'down' => $v['down']]);

// Fastest and slowest right now (latest successful check, no older than 3 hours).
$q = $pdo->prepare("SELECT host, ms FROM site_status WHERE verdict='up' AND ms IS NOT NULL AND checked_at > ?");
$q->execute([$ts($now - 10800)]);
$sp = [];
foreach ($q->fetchAll() as $r) if (isset($pg[$r['host']])) $sp[$r['host']] = (int)$r['ms'];
asort($sp); $R['fastest'] = []; foreach (array_slice($sp, 0, 6, true) as $h => $ms) $R['fastest'][] = $item($h, ['ms' => $ms]);
arsort($sp); $R['slowest'] = []; foreach (array_slice($sp, 0, 6, true) as $h => $ms) $R['slowest'][] = $item($h, ['ms' => $ms]);

// Outages: recovered in the last day, longest in the last 30 days, and the time of day they tend to start.
$q = $pdo->prepare('SELECT host, started_at, ended_at FROM incidents WHERE started_at > ? ORDER BY started_at DESC LIMIT 4000');
$q->execute([$ts($now - 30 * 86400)]);
$rec = []; $long = []; $hours = array_fill(0, 24, 0); $nOut = 0;
foreach ($q->fetchAll() as $r) {
    $h = $r['host']; if (!isset($pg[$h])) continue;
    $st = strtotime($r['started_at'] . ' UTC'); $en = $r['ended_at'] ? strtotime($r['ended_at'] . ' UTC') : null;
    $hours[(int)gmdate('G', $st)]++; $nOut++;
    if ($en) {
        $x = $item($h, ['started' => iso($r['started_at']), 'ended' => iso($r['ended_at']), 'seconds' => max(0, $en - $st)]);
        if ($en > $now - 86400) $rec[] = $x;
        $long[] = $x;
    }
}
usort($rec, fn($a, $b) => strcmp($b['ended'], $a['ended'])); $R['recovered'] = array_slice($rec, 0, 8);
usort($long, fn($a, $b) => $b['seconds'] <=> $a['seconds']); $R['longest'] = array_slice($long, 0, 6);
$R['hours'] = $hours; $R['hours_total'] = $nOut;

// Certificates that run out soon.
$cert = [];
foreach ($pdo->query("SELECT host, days_left FROM site_cert WHERE status='ok' AND days_left IS NOT NULL AND days_left <= 14 ORDER BY days_left ASC LIMIT 60")->fetchAll() as $r)
    if (isset($pg[$r['host']])) $cert[] = $item($r['host'], ['days' => (int)$r['days_left']]);
$R['certs'] = array_slice($cert, 0, 8);

// Visitor reports: busiest sites in the last 3 hours, then by category and by country over 24 hours.
$q = $pdo->prepare("SELECT host, COUNT(*) n FROM reports WHERE ts > ? AND kind <> 'fixed' GROUP BY host ORDER BY n DESC LIMIT 12");
$q->execute([$ts($now - 3 * 3600)]);
$R['reported'] = [];
foreach ($q->fetchAll() as $r) if ((int)$r['n'] >= 3 && isset($pg[$r['host']])) $R['reported'][] = $item($r['host'], ['count' => (int)$r['n']]);
$R['reported'] = array_slice($R['reported'], 0, 6);
$q = $pdo->prepare("SELECT host, COUNT(*) n FROM reports WHERE ts > ? AND kind <> 'fixed' GROUP BY host");
$q->execute([$ts($now - 86400)]);
$cat = [];
foreach ($q->fetchAll() as $r) if (isset($pg[$r['host']])) { $c = $pg[$r['host']]['cat'] ?? 'other'; $cat[$c] = ($cat[$c] ?? 0) + (int)$r['n']; }
arsort($cat); $R['by_cat'] = []; foreach (array_slice($cat, 0, 8, true) as $c => $n) $R['by_cat'][] = ['cat' => $c, 'count' => $n];
$q = $pdo->prepare("SELECT country, COUNT(*) n FROM reports WHERE ts > ? AND kind <> 'fixed' AND country IS NOT NULL GROUP BY country ORDER BY n DESC LIMIT 10");
$q->execute([$ts($now - 86400)]);
$R['by_area'] = [];
foreach ($q->fetchAll() as $r) if ((int)$r['n'] >= 3) $R['by_area'][] = ['country' => $r['country'], 'count' => (int)$r['n']];   // small groups are never shown

// Today at a glance and the 30-day outage trend.
$q = $pdo->prepare("SELECT COUNT(*) c FROM site_status WHERE checked_at > ?"); $q->execute([$ts($now - 86400)]); $checked = (int)$q->fetch()['c'];
$q = $pdo->prepare("SELECT AVG(ms) a FROM site_log WHERE ts > ? AND ts <= ? AND verdict='up' AND ms IS NOT NULL"); 
$q->execute([$ts($now - 86400), $ts($now)]); $a1 = $q->fetch()['a'];
$q->execute([$ts($now - 172800), $ts($now - 86400)]); $a0 = $q->fetch()['a'];
$q = $pdo->prepare('SELECT COUNT(*) c FROM incidents WHERE started_at > ?'); $q->execute([$ts($now - 86400)]); $o24 = (int)$q->fetch()['c'];
$R['glance'] = ['checked' => $checked, 'outages' => $o24, 'avg' => $a1 !== null ? (int)round($a1) : null, 'avg_prev' => $a0 !== null ? (int)round($a0) : null];
$q = $pdo->prepare('SELECT day, SUM(outages) o FROM site_daily WHERE day >= ? GROUP BY day ORDER BY day');
$q->execute([gmdate('Y-m-d', $now - 29 * 86400)]);
$m = []; foreach ($q->fetchAll() as $r) $m[$r['day']] = (int)$r['o'];
$R['trend'] = []; for ($i = 29; $i >= 0; $i--) { $d = gmdate('Y-m-d', $now - $i * 86400); $R['trend'][] = ['day' => $d, 'n' => $m[$d] ?? 0]; }
// Reliability by category (7 days) and a 13-week outage calendar.
$cr = [];
foreach ($up7 as $h => $v) { $c = $pg[$h]['cat'] ?? 'other'; $cr[$c]['pct'][] = $v['pct']; $cr[$c]['out'] = ($cr[$c]['out'] ?? 0) + $v['out']; }
$R['cats_rel'] = [];
foreach ($cr as $c => $d) if (count($d['pct']) >= 3) $R['cats_rel'][] = ['cat' => $c, 'sites' => count($d['pct']), 'pct' => round(array_sum($d['pct']) / count($d['pct']), 2), 'outages' => $d['out']];
usort($R['cats_rel'], fn($a, $b) => $b['pct'] <=> $a['pct']);
$q = $pdo->prepare('SELECT day, SUM(outages) o FROM site_daily WHERE day >= ? GROUP BY day ORDER BY day');
$q->execute([gmdate('Y-m-d', $now - 90 * 86400)]);
$m2 = []; foreach ($q->fetchAll() as $r) $m2[$r['day']] = (int)$r['o'];
$R['cal'] = []; for ($i = 90; $i >= 0; $i--) { $d = gmdate('Y-m-d', $now - $i * 86400); $R['cal'][] = ['day' => $d, 'n' => $m2[$d] ?? 0]; }

// Shared-provider trouble: three or more sites behind the same provider down or unusually slow at the same time.
$prov = [];
foreach ($pdo->query('SELECT host, provider FROM site_prov')->fetchAll() as $r) if (isset($pg[$r['host']])) $prov[$r['host']] = $r['provider'];
$avg = []; $q = $pdo->prepare("SELECT host, AVG(ms) a FROM site_log WHERE ts > ? AND verdict='up' AND ms IS NOT NULL GROUP BY host HAVING COUNT(*) >= 12"); $q->execute([$ts($now - 86400)]);
foreach ($q->fetchAll() as $r) $avg[$r['host']] = (float)$r['a'];
$flag = [];
foreach ($pdo->query('SELECT host, verdict, ms, checked_at FROM site_status')->fetchAll() as $r) {
    $h = $r['host']; if (!isset($prov[$h]) || strtotime($r['checked_at'] . ' UTC') < $now - 3600) continue;
    $bad = in_array($r['verdict'], ['down', 'timeout'], true);
    $slow = $r['verdict'] === 'up' && isset($avg[$h]) && (int)$r['ms'] >= 2 * $avg[$h] && (int)$r['ms'] - $avg[$h] >= 300;
    if ($bad || $slow) $flag[$prov[$h]][] = ['name' => $pg[$h]['name'], 'page' => $pg[$h]['page'], 'state' => $bad ? 'down' : 'slow'];
}
$R['cascade'] = [];
foreach ($flag as $p => $list) if (count($list) >= 3) $R['cascade'][] = ['provider' => $p, 'count' => count($list), 'sites' => array_slice($list, 0, 5)];
usort($R['cascade'], fn($a, $b) => $b['count'] <=> $a['count']);
$R['now'] = gmdate('Y-m-d\TH:i:s\Z');

$json = json_encode($R);
@file_put_contents($cache, $json);
header('Content-Type: application/json'); header('Cache-Control: public, max-age=60');
echo $json;
