<?php
// Signed-in users. GET ?days=30 -> uptime report for the sites I watch. Free: last 30 days. Pro: up to 12 months, a chosen month, and CSV.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_plan.php';
require __DIR__ . '/_report.php';
$pdo = db();
$uid = require_user();
$pro = is_pro($pdo, $uid);
$today = gmdate('Y-m-d');
$month = (string)($_GET['month'] ?? '');
if ($month !== '') {
    if (!$pro) out(402, ['error' => 'Choosing a month needs siteupdown Pro.', 'upgrade' => true]);
    $b = month_bounds($month); if (!$b) out(422, ['error' => 'Bad month.']);
    if ($b[0] < gmdate('Y-m-d', time() - PRO_HISTORY_DAYS * 86400 - 31 * 86400)) out(422, ['error' => 'That is further back than we keep.']);
    [$from, $to] = $b; $days = null;
} else {
    $days = max(7, min($pro ? PRO_HISTORY_DAYS : FREE_HISTORY_DAYS, (int)($_GET['days'] ?? FREE_HISTORY_DAYS)));
    $from = gmdate('Y-m-d', time() - ($days - 1) * 86400); $to = $today;
}
$rows = report_rows($pdo, $uid, $from, $to);
if (!empty($_GET['csv'])) {
    pro_required($pdo, $uid, 'Downloading a report');
    header_remove('Content-Type'); header('Content-Type: text/csv; charset=utf-8'); header('Cache-Control: no-store');
    header('Content-Disposition: attachment; filename="siteupdown-report-' . $from . '-to-' . $to . '.csv"');
    $o = fopen('php://output', 'w');
    fputcsv($o, ['site', 'from_utc', 'to_utc', 'checks', 'uptime_percent', 'outages', 'minutes_down', 'average_response_ms']);
    foreach ($rows as $r) fputcsv($o, [$r['host'], $from, $to, $r['checks'], $r['uptime'] ?? '', $r['outages'], $r['down_min'], $r['avg_ms'] ?? '']);
    fputcsv($o, []); fputcsv($o, ['Measured by siteupdown.com from our own server. Times are UTC. A guide from our own checks, not a service-level guarantee.']);
    fclose($o); exit;
}
$months = [];
if ($pro) for ($i = 1; $i <= 12; $i++) $months[] = gmdate('Y-m', strtotime("first day of -$i month 00:00 UTC"));
out(200, ['pro' => $pro, 'from' => $from, 'to' => $to, 'days' => $days, 'month' => $month ?: null, 'rows' => $rows, 'months' => $months, 'free_days' => FREE_HISTORY_DAYS, 'pro_days' => PRO_HISTORY_DAYS]);
