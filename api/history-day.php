<?php
// GET ?date=YYYY-MM-DD       -> what was reported and detected that day, per site (permanent record, counts only).
// GET ?days=1[&host=x.com]   -> days with activity, newest first (all sites, or one site).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$pdo = db();
$pages = site_pages();
$nm = fn($h) => $pages[$h]['name'] ?? $h;
header('Cache-Control: public, max-age=120');
$today = gmdate('Y-m-d');
$host = strtolower(trim((string)($_GET['host'] ?? '')));
if ($host !== '' && !preg_match('/^[a-z0-9.-]{1,253}$/', $host)) out(404, ['error' => 'Unknown site.']);

if (!empty($_GET['days'])) {
    if ($host !== '') {
        $q = $pdo->prepare('SELECT day, rep_site + rep_login + rep_app + rep_slow AS reports, outages, down_s FROM history_days WHERE host=? AND (rep_site + rep_login + rep_app + rep_slow + outages) > 0 ORDER BY day DESC LIMIT 400');
        $q->execute([$host]);
    } else {
        $q = $pdo->query('SELECT day, SUM(rep_site + rep_login + rep_app + rep_slow) AS reports, SUM(outages) AS outages, SUM(down_s) AS down_s FROM history_days GROUP BY day HAVING SUM(rep_site + rep_login + rep_app + rep_slow + outages) > 0 ORDER BY day DESC LIMIT 120');
    }
    $days = [];
    foreach ($q->fetchAll() as $r) $days[] = ['day' => $r['day'], 'reports' => (int)$r['reports'], 'outages' => (int)$r['outages'], 'down_min' => (int)round(((int)$r['down_s']) / 60)];
    out(200, ['host' => $host ?: null, 'name' => $host ? $nm($host) : null, 'today' => $today, 'days' => $days]);
}

$date = (string)($_GET['date'] ?? $today);
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date) || !checkdate((int)substr($date, 5, 2), (int)substr($date, 8, 2), (int)substr($date, 0, 4)) || $date > $today) out(422, ['error' => 'Please pick a valid date that is not in the future.']);
$q = $pdo->prepare('SELECT host, rep_site, rep_login, rep_app, rep_slow, rep_fixed, outages, down_s FROM history_days WHERE day=?' . ($host !== '' ? ' AND host=?' : ''));
$q->execute($host !== '' ? [$date, $host] : [$date]);
$rows = []; $tr = 0; $to = 0;
foreach ($q->fetchAll() as $r) {
    $rep = (int)$r['rep_site'] + (int)$r['rep_login'] + (int)$r['rep_app'] + (int)$r['rep_slow'];
    if ($rep + (int)$r['outages'] === 0) continue;
    $tr += $rep; $to += (int)$r['outages'];
    $rows[] = ['host' => $r['host'], 'name' => $nm($r['host']), 'page' => $pages[$r['host']]['page'] ?? null, 'reports' => $rep,
               'kinds' => ['site' => (int)$r['rep_site'], 'login' => (int)$r['rep_login'], 'app' => (int)$r['rep_app'], 'slow' => (int)$r['rep_slow']],
               'fixed' => (int)$r['rep_fixed'], 'outages' => (int)$r['outages'], 'down_min' => (int)round(((int)$r['down_s']) / 60)];
}
usort($rows, fn($a, $b) => ($b['reports'] + 5 * $b['outages']) <=> ($a['reports'] + 5 * $a['outages']));
out(200, ['date' => $date, 'today' => $today, 'host' => $host ?: null, 'total_reports' => $tr, 'total_outages' => $to, 'rows' => array_slice($rows, 0, 60)]);
