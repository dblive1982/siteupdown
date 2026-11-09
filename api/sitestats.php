<?php
// TEST SITE ONLY: sample numbers for the deeper-insight section. Not real results.
header('Content-Type: application/json');
$h = strtolower((string)($_GET['host'] ?? 'example.com')); $t = time(); $d = fn($ago) => gmdate('Y-m-d\\TH:i:s\\Z', $t - $ago);
$bad = in_array($h, ['discord.com', 'roblox.com'], true);
$hours = [210,205,198,190,185,180,190,230,260,280,270,260,255,250,260,270,290,330,420,470,440,380,300,240];
echo json_encode(['host' => $h, 'name' => ucfirst(explode('.', $h)[0]), 'page' => '/is-' . explode('.', $h)[0] . '-down', 'cat' => 'video',
 'u7' => ['checks' => 2000, 'pct' => $bad ? 99.4 : 99.98, 'outages' => $bad ? 2 : 0, 'down' => $bad ? 3600 : 0, 'avg' => 250],
 'u30' => ['checks' => 8000, 'pct' => $bad ? 99.2 : 99.96, 'outages' => $bad ? 5 : 1, 'down' => $bad ? 9000 : 900, 'avg' => 262],
 'grade' => $bad ? 'C' : 'A', 'rank' => ['n' => 3, 'of' => 11], 'timing' => ['dns' => 12, 'conn' => 31, 'tls' => 58, 'ttfb' => 164, 'n' => 288],
 'hours' => $hours, 'outages' => [['started' => $d(400000), 'ended' => $d(396400), 'seconds' => 3600], ['started' => $d(1200000), 'ended' => $d(1198800), 'seconds' => 1200], ['started' => $d(3000000), 'ended' => $d(2995000), 'seconds' => 5000]],
 'outages_90' => 3, 'mtbf_h' => 612.0, 'provider' => 'Cloudflare', 'now' => $d(0)]);
