<?php
// GET ?host=example.com&days=30 -> CSV of one listed site's daily uptime and outages, for people who need a record. Own checks only.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$pg = site_pages(); $host = strtolower(trim((string)($_GET['host'] ?? '')));
if (!isset($pg[$host])) out(404, ['error' => 'We only keep records for the sites on our public lists.']);
$days = max(7, min(365, (int)($_GET['days'] ?? 30)));
$pdo = db();
$q = $pdo->prepare('SELECT day, up_n, bad_n, ms_sum, ms_n, outages, down_s FROM site_daily WHERE host = ? AND day >= ? ORDER BY day');
$q->execute([$host, gmdate('Y-m-d', time() - $days * 86400)]);
header_remove('Content-Type'); header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="' . preg_replace('/[^a-z0-9.-]/', '_', $host) . '-uptime-' . $days . 'd.csv"');
header('Cache-Control: public, max-age=300');
$o = fopen('php://output', 'w');
fputcsv($o, ['site', 'date_utc', 'checks', 'successful_checks', 'uptime_percent', 'average_response_ms', 'outages', 'minutes_down']);
foreach ($q->fetchAll() as $r) {
    $n = (int)$r['up_n'] + (int)$r['bad_n'];
    fputcsv($o, [$pg[$host]['name'], $r['day'], $n, (int)$r['up_n'], $n ? round(100 * $r['up_n'] / $n, 2) : '', (int)$r['ms_n'] ? round($r['ms_sum'] / $r['ms_n']) : '', (int)$r['outages'], round($r['down_s'] / 60)]);
}
fputcsv($o, []); fputcsv($o, ['Measured by siteupdown.com from our own server. Times are UTC. Uptime counts our own checks only, so it is a guide and not a service guarantee.']);
fclose($o);
