<?php
// Re-probes watched sites every minute and public pages about every five. Run every minute from hPanel > Advanced > Cron Jobs:
//   * * * * *  /usr/bin/php /home/USER/domains/siteupdown.com/public_html/api/cron.php
// If you cannot use cron, call https://siteupdown.com/api/cron.php?key=YOUR_CRON_KEY from a free uptime pinger.
declare(strict_types=1);
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_tls.php';
require __DIR__ . '/_track.php';
require __DIR__ . '/_sites.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_xcheck.php';
$c = config();
if (PHP_SAPI !== 'cli') {
    $key = (string)($_GET['key'] ?? '');
    if (!$c || empty($c['cron_key']) || !hash_equals((string)$c['cron_key'], $key)) out(403, ['error' => 'Forbidden.']);
    @set_time_limit(100);
    ignore_user_abort(true);
}
$pdo = db();
// One run at a time: if the previous minute's run is still going, skip this one.
$lock = @fopen(sys_get_temp_dir() . '/sud-cron.lock', 'c');
if ($lock && !flock($lock, LOCK_EX | LOCK_NB)) { if (PHP_SAPI === 'cli') echo "Already running\n"; else out(200, ['skipped' => true]); exit; }
$t0 = time();
$now = sql_now();
$st = [];
foreach ($pdo->query('SELECT host, checked_at FROM site_status')->fetchAll() as $r) $st[$r['host']] = $r['checked_at'];
$up = $pdo->prepare('REPLACE INTO site_status (host, verdict, http_code, ms, checked_at) VALUES (?,?,?,?,?)');
$n = 0;
$probe = function (string $h) use ($pdo, $up, &$n) {
    $r = check_site($h, '/', false, true);
    if (in_array($r['verdict'], ['down', 'timeout'], true) && corroborated_alive_cached($pdo, $h)) { $r['verdict'] = 'inconclusive'; $r['note'] = 'The site answers other countries but not our server, so we cannot be sure.'; }
    $up->execute([$h, $r['verdict'], $r['http_code'], $r['ms'], sql_now()]);
    track_result($pdo, $h, $r['verdict'], $r['ms']);
    $n++;
};
// 1) Sites on someone's watchlist: every minute, stalest first. If there are more than fit in a minute, the stalest simply wait their turn.
$watched = [];
foreach ($pdo->query('SELECT DISTINCT host FROM watchlist')->fetchAll() as $r) $watched[$r['host']] = 1;
$due = array_values(array_filter(array_keys($watched), fn($h) => ($st[$h] ?? '') < gmdate('Y-m-d H:i:s', time() - 55)));
usort($due, fn($a, $b) => strcmp($st[$a] ?? '', $st[$b] ?? ''));
foreach ($due as $h) { if (time() - $t0 > 40) break; $probe($h); }
// 2) Extra checks (keyword on page, open port), also every minute.
$nx = 0;
$xr = $pdo->prepare('SELECT * FROM extra_checks WHERE checked_at IS NULL OR checked_at < ? ORDER BY checked_at');
$xr->execute([gmdate('Y-m-d H:i:s', time() - 55)]);
foreach ($xr->fetchAll() as $row) { if (time() - $t0 > 48) break; xcheck_track($pdo, $row, xcheck_run($row)); $nx++; }
// 3) Public pages (top sites, games, apps): about every five minutes, a few per run, while there is time left.
$pubBatch = (int)($c['cron_batch'] ?? 8);
$pub = [];
foreach (top_sites() as $s) $pub[$s[0]] = 1;
foreach (gaming_sites() as $s) $pub[$s[0]] = 1;
foreach (site_pages() as $h0 => $sp0) { $pub[$h0] = 1; foreach ($sp0['app'] ?? [] as $ap) $pub[$ap[1]] = 1; }
foreach ($pdo->query('SELECT host FROM tracked_hosts')->fetchAll() as $r) $pub[$r['host']] = 1;     // other sites people have looked at lately
$pl = array_values(array_filter(array_keys($pub), fn($h) => !isset($watched[$h]) && ($st[$h] ?? '') < gmdate('Y-m-d H:i:s', time() - 270)));
usort($pl, fn($a, $b) => strcmp($st[$a] ?? '', $st[$b] ?? ''));
foreach (array_slice($pl, 0, $pubBatch) as $h) { if (time() - $t0 > 52) break; $probe($h); }
// 4) Certificates: each host once a day, a few per run (public pages and every watched site).
$certAt = [];
foreach ($pdo->query('SELECT host, checked_at FROM site_cert')->fetchAll() as $r) $certAt[$r['host']] = $r['checked_at'];
$certHosts = $watched;
foreach (top_sites() as $s2) $certHosts[$s2[0]] = 1;
foreach (gaming_sites() as $s2) $certHosts[$s2[0]] = 1;
foreach (array_keys(site_pages()) as $h0) $certHosts[$h0] = 1;
$certList = array_keys($certHosts);
$cut = gmdate('Y-m-d H:i:s', time() - 22 * 3600);
$certList = array_values(array_filter($certList, fn($h) => ($certAt[$h] ?? '') < $cut));
usort($certList, fn($a, $b) => strcmp($certAt[$a] ?? '', $certAt[$b] ?? ''));
$certList = array_slice($certList, 0, (int)($c['cert_batch'] ?? 8));
$cu = $pdo->prepare('REPLACE INTO site_cert (host, status, days_left, expires, checked_at) VALUES (?,?,?,?,?)');
$nc = 0;
foreach ($certList as $h) {
    if (time() - $t0 > 56) break;
    $rp = resolve_public($h);
    $t = (!$rp['error'] && $rp['ips']) ? tls_inspect($h, $rp['ips'][0], 5) : ['status' => 'none'];
    $cu->execute([$h, $t['status'], $t['days_left'] ?? null, $t['to'] ?? null, sql_now()]);
    if (isset($watched[$h]) && isset($t['days_left'], $t['to']) && $t['status'] !== 'none') expiry_check($pdo, $h, 'ssl', (int)$t['days_left'], (string)$t['to']);
    $nc++;
}
// 5) Domain registration dates for watched sites, hourly (RDAP answers are cached for a week).
$sw = $pdo->prepare('SELECT ts FROM expiry_state WHERE host=? AND kind=?'); $sw->execute(['*', 'sweep']);
$lastSweep = $sw->fetchColumn();
if (!$lastSweep || $lastSweep < gmdate('Y-m-d H:i:s', time() - 3600)) {
    $pdo->prepare('DELETE FROM expiry_state WHERE host=? AND kind=?')->execute(['*', 'sweep']);
    $pdo->prepare('INSERT INTO expiry_state (host, kind, level, ts) VALUES (?,?,?,?)')->execute(['*', 'sweep', 0, sql_now()]);
    $doms = [];
    foreach (array_keys($watched) as $h) { $d = registrable_domain($h); if ($d !== '' && !filter_var($d, FILTER_VALIDATE_IP)) $doms[$d] = 1; }
    $k = 0;
    foreach (array_keys($doms) as $d) {
        if (time() - $t0 > 56 || $k >= 6) break;
        $w = domain_whois($d);
        if ($w && isset($w['days_left'], $w['expires'])) expiry_check($pdo, $d, 'domain', (int)$w['days_left'], (string)$w['expires']);
        $k++;
    }
}
// Housekeeping (about every ten minutes): drop old feed rows and expired share links.
if ((int)gmdate('i') % 10 === 3) {
$pdo->prepare('DELETE FROM tracked_hosts WHERE last_seen < ?')->execute([gmdate('Y-m-d H:i:s', time() - 7 * 86400)]);
$pdo->prepare('DELETE FROM live_viewer WHERE ts < ?')->execute([time() - 3600]);
// One-off clean-up (runs once): callofduty.com was wrongly shown as down because only its www address answers our server.
$m1 = $pdo->prepare('SELECT 1 FROM corroboration WHERE host=?'); $m1->execute(['*cleanup-cod-1']);
if (!$m1->fetchColumn()) {
    $pdo->prepare('DELETE FROM incidents WHERE host=?')->execute(['callofduty.com']);
    $pdo->prepare("UPDATE site_log SET verdict='inconclusive' WHERE host=? AND verdict IN ('down','timeout')")->execute(['callofduty.com']);
    $pdo->prepare('DELETE FROM alert_state WHERE host=?')->execute(['callofduty.com']);
    $pdo->prepare('INSERT INTO corroboration (host, alive, ts) VALUES (?,?,?)')->execute(['*cleanup-cod-1', 0, time()]);
    $needDailyFix = true;
}
// Daily record for the 12-month view: first run back-fills what site_log still holds, later runs refresh today and yesterday.
try {
    require_once __DIR__ . '/_daily.php';
    $hasDaily = $pdo->query('SELECT 1 FROM site_daily LIMIT 1')->fetchColumn();
    rollup_daily($pdo, $hasDaily ? (!empty($needDailyFix) ? 4 : 2) : 34);
    $pdo->prepare('DELETE FROM site_daily WHERE day < ?')->execute([gmdate('Y-m-d', time() - 400 * 86400)]);
} catch (Throwable $e) { error_log('daily rollup: ' . $e->getMessage()); }
$pdo->prepare('DELETE FROM checks WHERE checked_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 3 * 86400)]);
$pdo->prepare('DELETE FROM site_log WHERE ts < ?')->execute([gmdate('Y-m-d H:i:s', time() - 35 * 86400)]);
// Problem reports are kept for three years; the one-way address hash is only needed for the 30-minute duplicate check, so it is wiped after two days.
$pdo->prepare('DELETE FROM reports WHERE ts < ?')->execute([gmdate('Y-m-d H:i:s', time() - 1095 * 86400)]);
$pdo->prepare("UPDATE reports SET ip_hash='' WHERE ts < ? AND ip_hash <> ''")->execute([gmdate('Y-m-d H:i:s', time() - 2 * 86400)]);
$pdo->prepare('DELETE FROM incidents WHERE started_at < ? AND ended_at IS NOT NULL')->execute([gmdate('Y-m-d H:i:s', time() - 95 * 86400)]);
$pdo->prepare('DELETE FROM shares WHERE created_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 30 * 86400)]);
$pdo->prepare('DELETE FROM resets WHERE expires_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 86400)]);
}
if (PHP_SAPI === 'cli') echo "Probed $n sites, $nx extra checks, $nc certificates\n"; else out(200, ['probed' => $n, 'extra' => $nx, 'certs' => $nc]);
