<?php
// TEST SITE ONLY: sample weekly summary. Not real results.
header('Content-Type: application/json');
$n = fn($name, $slug, $x) => array_merge(['host' => $slug . '.com', 'name' => $name, 'page' => '/is-' . $slug . '-down', 'cat' => 'social', 'ms' => 200], $x);
$t = time();
echo json_encode(['from' => gmdate('Y-m-d', $t - 6 * 86400), 'to' => gmdate('Y-m-d', $t), 'outages' => 14, 'outages_prev' => 19, 'down_s' => 31200, 'worst_day' => ['day' => gmdate('Y-m-d', $t - 2 * 86400), 'n' => 6], 'tracked' => 132, 'perfect' => 91,
 'best' => [$n('Google','google',['pct'=>100,'outages'=>0,'down'=>0]), $n('Wikipedia','wikipedia',['pct'=>100,'outages'=>0,'down'=>0]), $n('Amazon','amazon',['pct'=>99.99,'outages'=>0,'down'=>0])],
 'worst' => [$n('Discord','discord',['pct'=>98.9,'outages'=>4,'down'=>7200]), $n('Roblox','roblox',['pct'=>99.3,'outages'=>2,'down'=>4300])],
 'cats' => [['cat'=>'search','sites'=>6,'pct'=>99.98,'outages'=>0],['cat'=>'video','sites'=>11,'pct'=>99.9,'outages'=>2],['cat'=>'gaming','sites'=>20,'pct'=>99.5,'outages'=>8]],
 'longest' => ['name' => 'Discord', 'page' => '/is-discord-down', 'started' => gmdate('Y-m-d\\TH:i:s\\Z', $t - 3 * 86400), 'seconds' => 5400], 'reports' => 412, 'now' => gmdate('Y-m-d\\TH:i:s\\Z')]);
