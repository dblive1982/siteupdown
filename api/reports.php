<?php
// TEST SITE ONLY: sample latest-reports list. Not real reports.
header('Content-Type: application/json');
if (empty($_GET['recent'])) { http_response_code(404); echo json_encode(['error' => 'Sample site']); exit; }
$h = strtolower((string)($_GET['host'] ?? ''));
$s = [['netflix.com','Netflix','/is-netflix-down','login',3,'GB'],['instagram.com','Instagram','/is-instagram-down','site',9,null],['whatsapp.com','WhatsApp','/is-whatsapp-down','slow',22,'IN'],['netflix.com','Netflix','/is-netflix-down','site',41,'GB'],['facebook.com','Facebook','/is-facebook-down','app',75,'US'],['instagram.com','Instagram','/is-instagram-down','login',130,'GB'],['youtube.com','YouTube','/is-youtube-down','slow',260,null],['netflix.com','Netflix','/is-netflix-down','fixed',12,'GB']];
$items = [];
foreach ($s as $r) { if ($h !== '' && $h !== $r[0]) continue; $items[] = ['host'=>$r[0],'name'=>$r[1],'page'=>$r[2],'kind'=>$r[3],'ts'=>gmdate('Y-m-d\TH:i:s\Z', time() - $r[4] * 60),'country'=>$r[5]]; }
echo json_encode(['items' => $items]);
