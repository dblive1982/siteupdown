<?php
// Re-probes the watched sites. Run every 5 minutes from hPanel > Advanced > Cron Jobs:
//   */5 * * * *  /usr/bin/php /home/USER/domains/siteupdown.com/public_html/api/cron.php
// If you cannot use cron, call https://siteupdown.com/api/cron.php?key=YOUR_CRON_KEY from a free uptime pinger.
declare(strict_types=1);
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_tls.php';
require __DIR__ . '/_track.php';
require __DIR__ . '/_sites.php';
$c = config();
if (PHP_SAPI !== 'cli') {
    $key = (string)($_GET['key'] ?? '');
    if (!$c || empty($c['cron_key']) || !hash_equals((string)$c['cron_key'], $key)) out(403, ['error' => 'Forbidden.']);
    @set_time_limit(100);
    ignore_user_abort(true);
}
$pdo = db();
$batch = (int)($c['cron_batch'] ?? 40);
$hosts = [];
foreach (top_sites() as $s) $hosts[$s[0]] = 1;
foreach (gaming_sites() as $s) $hosts[$s[0]] = 1;
foreach ($pdo->query('SELECT DISTINCT host FROM watchlist')->fetchAll() as $r) $hosts[$r['host']] = 1;
$st = [];
foreach ($pdo->query('SELECT host, checked_at FROM site_status')->fetchAll() as $r) $st[$r['host']] = $r['checked_at'];
$list = array_keys($hosts);
usort($list, fn($a, $b) => strcmp($st[$a] ?? '', $st[$b] ?? '')); // never-checked first, then the stalest
$list = array_slice($list, 0, $batch);
$up = $pdo->prepare('REPLACE INTO site_status (host, verdict, http_code, ms, checked_at) VALUES (?,?,?,?,?)');
$n = 0; $t0 = time();
foreach ($list as $h) {
    if (time() - $t0 > 85) break;
    $r = check_site($h, '/', false, true);
    $up->execute([$h, $r['verdict'], $r['http_code'], $r['ms'], sql_now()]);
    track_result($pdo, $h, $r['verdict'], $r['ms']);
    $n++;
}
// Certificates: each host once a day, a few per run (top sites and gaming services).
$certAt = [];
foreach ($pdo->query('SELECT host, checked_at FROM site_cert')->fetchAll() as $r) $certAt[$r['host']] = $r['checked_at'];
$certHosts = [];
foreach (top_sites() as $s2) $certHosts[$s2[0]] = 1;
foreach (gaming_sites() as $s2) $certHosts[$s2[0]] = 1;
$certList = array_keys($certHosts);
$cut = gmdate('Y-m-d H:i:s', time() - 22 * 3600);
$certList = array_values(array_filter($certList, fn($h) => ($certAt[$h] ?? '') < $cut));
usort($certList, fn($a, $b) => strcmp($certAt[$a] ?? '', $certAt[$b] ?? ''));
$certList = array_slice($certList, 0, (int)($c['cert_batch'] ?? 8));
$cu = $pdo->prepare('REPLACE INTO site_cert (host, status, days_left, expires, checked_at) VALUES (?,?,?,?,?)');
$nc = 0;
foreach ($certList as $h) {
    if (time() - $t0 > 90) break;
    $rp = resolve_public($h);
    $t = (!$rp['error'] && $rp['ips']) ? tls_inspect($h, $rp['ips'][0], 5) : ['status' => 'none'];
    $cu->execute([$h, $t['status'], $t['days_left'] ?? null, $t['to'] ?? null, sql_now()]);
    $nc++;
}
// Housekeeping: drop old feed rows and expired share links.
$pdo->prepare('DELETE FROM checks WHERE checked_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 3 * 86400)]);
$pdo->prepare('DELETE FROM site_log WHERE ts < ?')->execute([gmdate('Y-m-d H:i:s', time() - 35 * 86400)]);
$pdo->prepare('DELETE FROM incidents WHERE started_at < ? AND ended_at IS NOT NULL')->execute([gmdate('Y-m-d H:i:s', time() - 95 * 86400)]);
$pdo->prepare('DELETE FROM shares WHERE created_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 30 * 86400)]);
$pdo->prepare('DELETE FROM resets WHERE expires_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 86400)]);
if (PHP_SAPI === 'cli') echo "Probed $n sites, $nc certificates\n"; else out(200, ['probed' => $n, 'certs' => $nc]);
