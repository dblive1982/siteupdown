<?php
// GET ?host=example.com -> deeper numbers for one listed site: reliability grade, time breakdown, typical hours, outage timeline, provider.
// Built only from our own checks. Cached for five minutes per site.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$pg = site_pages();
$host = strtolower(trim((string)($_GET['host'] ?? '')));
if (!isset($pg[$host])) out(404, ['error' => 'We only keep detailed numbers for the sites on our public lists.']);
$cache = sys_get_temp_dir() . '/sud_ss_' . md5($host) . '.json';
header('Cache-Control: public, max-age=120');
if (is_file($cache) && filemtime($cache) > time() - 300) { header('Content-Type: application/json'); readfile($cache); exit; }
$pdo = db(); $now = time(); $ts = fn(int $t) => gmdate('Y-m-d H:i:s', $t);
$R = ['host' => $host, 'name' => $pg[$host]['name'], 'page' => $pg[$host]['page'], 'cat' => $pg[$host]['cat'] ?? null];

function ss_uptime(PDO $pdo, string $host, int $days): array {
    $q = $pdo->prepare('SELECT SUM(up_n) u, SUM(bad_n) b, SUM(outages) o, SUM(down_s) d, SUM(ms_sum) ms, SUM(ms_n) mn FROM site_daily WHERE host = ? AND day >= ?');
    $q->execute([$host, gmdate('Y-m-d', time() - $days * 86400)]); $r = $q->fetch();
    $n = (int)$r['u'] + (int)$r['b'];
    return ['checks' => $n, 'pct' => $n ? round(100 * (int)$r['u'] / $n, 3) : null, 'outages' => (int)$r['o'], 'down' => (int)$r['d'], 'avg' => (int)$r['mn'] ? (int)round($r['ms'] / $r['mn']) : null];
}
function ss_grade(?float $pct, int $n): ?string {
    if ($pct === null || $n < 150) return null;      // not enough history to judge fairly
    return $pct >= 99.9 ? 'A' : ($pct >= 99.5 ? 'B' : ($pct >= 99.0 ? 'C' : ($pct >= 97.0 ? 'D' : 'F')));
}
$u30 = ss_uptime($pdo, $host, 30); $u7 = ss_uptime($pdo, $host, 7);
$R['u7'] = $u7; $R['u30'] = $u30; $R['grade'] = ss_grade($u30['pct'], $u30['checks']);

// Rank within the category (30-day uptime, sites with enough history only).
if ($R['cat']) {
    $q = $pdo->prepare('SELECT host, SUM(up_n) u, SUM(bad_n) b FROM site_daily WHERE day >= ? GROUP BY host');
    $q->execute([gmdate('Y-m-d', $now - 30 * 86400)]); $peers = [];
    foreach ($q->fetchAll() as $r) { $n = (int)$r['u'] + (int)$r['b']; if ($n >= 150 && isset($pg[$r['host']]) && ($pg[$r['host']]['cat'] ?? '') === $R['cat']) $peers[$r['host']] = (int)$r['u'] / $n; }
    if (isset($peers[$host]) && count($peers) >= 3) { arsort($peers); $R['rank'] = ['n' => array_search($host, array_keys($peers)) + 1, 'of' => count($peers)]; }
}

// Where the time goes (average of the last 24 hours) and the latest check.
$q = $pdo->prepare('SELECT AVG(dns_ms) d, AVG(conn_ms) c, AVG(tls_ms) t, AVG(ttfb_ms) f, COUNT(*) n FROM site_timing WHERE host = ? AND ts > ?');
$q->execute([$host, $ts($now - 86400)]); $t = $q->fetch();
$R['timing'] = (int)$t['n'] >= 3 ? ['dns' => (int)round($t['d']), 'conn' => (int)round($t['c']), 'tls' => (int)round($t['t']), 'ttfb' => (int)round($t['f']), 'n' => (int)$t['n']] : null;

// Typical day: average response time per hour of the day (UTC) over the last 35 days.
$q = $pdo->prepare("SELECT ts, ms FROM site_log WHERE host = ? AND verdict = 'up' AND ms IS NOT NULL AND ts > ?");
$q->execute([$host, $ts($now - 35 * 86400)]);
$sum = array_fill(0, 24, 0); $cnt = array_fill(0, 24, 0);
foreach ($q->fetchAll() as $r) { $h = (int)gmdate('G', strtotime($r['ts'] . ' UTC')); $sum[$h] += (int)$r['ms']; $cnt[$h]++; }
$R['hours'] = []; for ($h = 0; $h < 24; $h++) $R['hours'][] = $cnt[$h] >= 5 ? (int)round($sum[$h] / $cnt[$h]) : null;

// Outage timeline: last 90 days, newest first, plus the typical gap between outages.
$q = $pdo->prepare('SELECT started_at, ended_at FROM incidents WHERE host = ? AND started_at > ? ORDER BY started_at DESC LIMIT 40');
$q->execute([$host, $ts($now - 90 * 86400)]); $inc = [];
foreach ($q->fetchAll() as $r) {
    $st = strtotime($r['started_at'] . ' UTC'); $en = $r['ended_at'] ? strtotime($r['ended_at'] . ' UTC') : null;
    $inc[] = ['started' => iso($r['started_at']), 'ended' => $en ? iso($r['ended_at']) : null, 'seconds' => max(0, ($en ?? $now) - $st)];
}
$R['outages'] = array_slice($inc, 0, 12); $R['outages_90'] = count($inc);
if (count($inc) >= 2) {
    $first = strtotime(end($inc)['started'] ?? 'now'); $span = max(86400, $now - $first);
    $R['mtbf_h'] = round($span / count($inc) / 3600, 1);
}
$q = $pdo->prepare('SELECT provider FROM site_prov WHERE host = ?'); $q->execute([$host]); $R['provider'] = $q->fetchColumn() ?: null;
$R['now'] = gmdate('Y-m-d\TH:i:s\Z');
$json = json_encode($R);
@file_put_contents($cache, $json);
header('Content-Type: application/json');
echo $json;
