<?php
// TEST SITE ONLY: sample day-by-day history. Not real data.
header('Content-Type: application/json');
$today = gmdate('Y-m-d'); $h = strtolower((string)($_GET['host'] ?? ''));
if (!empty($_GET['days'])) {
    $days = []; foreach ([0,1,3,4,8,12,19] as $i => $o) $days[] = ['day' => gmdate('Y-m-d', time() - $o * 86400), 'reports' => 140 - $i * 17, 'outages' => $i % 3, 'down_min' => ($i % 3) * 22];
    echo json_encode(['host' => $h ?: null, 'name' => null, 'today' => $today, 'days' => $days]); exit;
}
$date = (string)($_GET['date'] ?? $today);
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date) || $date > $today) { http_response_code(422); echo json_encode(['error' => 'Please pick a valid date that is not in the future.']); exit; }
$rows = [['netflix.com','Netflix','/is-netflix-down',54,['site'=>10,'login'=>38,'app'=>4,'slow'=>2],9,1,26],['instagram.com','Instagram','/is-instagram-down',31,['site'=>20,'login'=>5,'app'=>4,'slow'=>2],4,0,0],['whatsapp.com','WhatsApp','/is-whatsapp-down',12,['site'=>3,'login'=>0,'app'=>2,'slow'=>7],1,0,0]];
$out = []; foreach ($rows as $r) { if ($h !== '' && $h !== $r[0]) continue; $out[] = ['host'=>$r[0],'name'=>$r[1],'page'=>$r[2],'reports'=>$r[3],'kinds'=>$r[4],'fixed'=>$r[5],'outages'=>$r[6],'down_min'=>$r[7]]; }
echo json_encode(['date' => $date, 'today' => $today, 'host' => $h ?: null, 'total_reports' => array_sum(array_column($out, 'reports')), 'total_outages' => array_sum(array_column($out, 'outages')), 'rows' => $out]);
