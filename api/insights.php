<?php
// TEST SITE ONLY: sample data for the More reports tabs. Not real results.
header('Content-Type: application/json');
$n = fn($name, $slug, $x = []) => array_merge(['host' => $slug . '.com', 'name' => $name, 'page' => '/is-' . $slug . '-down'], $x);
$t = time(); $d = fn($ago) => gmdate('Y-m-d\\TH:i:s\\Z', $t - $ago);
$trend = []; for ($i = 29; $i >= 0; $i--) $trend[] = ['day' => gmdate('Y-m-d', $t - $i * 86400), 'n' => [0,2,1,0,3,1,0,0,4,2,1,0,1,5,2,0,1,1,3,0,2,1,0,6,2,1,0,1,3,2][29 - $i]];
$hours = array_fill(0, 24, 0); foreach ([[7,2],[8,5],[9,3],[13,2],[18,4],[19,6],[20,3],[22,2]] as $h) $hours[$h[0]] = $h[1];
echo json_encode([
 'reliable' => [$n('Google','google',['pct'=>100,'ms'=>96]), $n('Wikipedia','wikipedia',['pct'=>100,'ms'=>121]), $n('Amazon','amazon',['pct'=>99.99,'ms'=>180]), $n('BBC','bbc',['pct'=>99.98,'ms'=>210])],
 'perfect' => 87, 'tracked' => 132,
 'unreliable' => [$n('Discord','discord',['pct'=>98.9,'outages'=>4,'down'=>7200]), $n('Roblox','roblox',['pct'=>99.3,'outages'=>2,'down'=>4300]), $n('Snapchat','snapchat',['pct'=>99.6,'outages'=>1,'down'=>1500])],
 'fastest' => [$n('Google','google',['ms'=>88]), $n('Cloudflare','cloudflare',['ms'=>94]), $n('Wikipedia','wikipedia',['ms'=>110])],
 'slowest' => [$n('Atlassian','atlassian',['ms'=>1870]), $n('Trello','trello',['ms'=>1320]), $n('Zoom','zoom',['ms'=>990])],
 'recovered' => [$n('Netflix','netflix',['started'=>$d(9000),'ended'=>$d(5400),'seconds'=>3600]), $n('Spotify','spotify',['started'=>$d(40000),'ended'=>$d(38000),'seconds'=>2000])],
 'longest' => [$n('Discord','discord',['started'=>$d(900000),'ended'=>$d(892000),'seconds'=>8000]), $n('Roblox','roblox',['started'=>$d(1500000),'ended'=>$d(1495000),'seconds'=>5000])],
 'hours' => $hours, 'hours_total' => array_sum($hours),
 'certs' => [$n('Example Shop','shop',['days'=>3]), $n('Demo Bank','bank',['days'=>11])],
 'reported' => [$n('Instagram','instagram',['count'=>14]), $n('WhatsApp','whatsapp',['count'=>8]), $n('Netflix','netflix',['count'=>5])],
 'by_cat' => [['cat'=>'social','count'=>61],['cat'=>'streaming','count'=>34],['cat'=>'gaming','count'=>19]],
 'by_area' => [['country'=>'GB','count'=>48],['country'=>'US','count'=>31],['country'=>'IN','count'=>12]],
 'glance' => ['checked'=>132,'outages'=>3,'avg'=>312,'avg_prev'=>287], 'trend' => $trend, 'now' => $d(0)
]);
