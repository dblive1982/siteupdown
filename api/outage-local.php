<?php
// TEST SITE ONLY: fixed sample data so the local outage map can be styled. Not real reports.
header('Content-Type: application/json');
$s = [[51.5,-0.1,14,'Netflix',6,'Instagram',5,'WhatsApp',3],[53.5,-2.3,6,'Netflix',4,'Facebook',2],[52.5,-1.9,4,'Instagram',4],[48.9,2.3,9,'WhatsApp',5,'Facebook',4],[40.7,-74.0,12,'Instagram',7,'Netflix',5],[34.1,-118.3,5,'YouTube',5],[19.1,72.9,8,'WhatsApp',8],[-33.9,151.2,3,'Netflix',3],[-23.5,-46.6,7,'Instagram',4,'WhatsApp',3],[35.7,139.7,4,'YouTube',4],[41.9,12.5,5,'Netflix',3,'Facebook',2],[52.5,13.4,4,'WhatsApp',4]];
$cells = []; $total = 0;
foreach ($s as $r) { $sites = []; for ($i = 3; $i < count($r); $i += 2) $sites[] = ['name' => $r[$i], 'n' => $r[$i + 1]]; $k = count($cells); $cells[] = ['lat' => $r[0], 'lon' => $r[1], 'cell' => 0.2, 'n' => $r[2], 'w' => round(max(0.15, 1 - $k * 0.08), 2), 'newest' => gmdate('Y-m-d\TH:i:s\Z', time() - (5 + $k * 12) * 60), 'sites' => array_map(function($x) use ($k) { if ($k % 4 === 2) $x['rec'] = 'checks'; return $x; }, $sites)]; $total += $r[2]; }
echo json_encode(['hours' => (int)($_GET['hours'] ?? 3), 'total' => $total, 'cells' => $cells]);
