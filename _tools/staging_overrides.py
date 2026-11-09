#!/usr/bin/env python3
"""TEST SITE ONLY (lives on the staging branch). Run after copying the restyle build over:
   git checkout restyle -- . && python3 _tools/staging_overrides.py
Makes the copy safe: hidden from search engines, no ads, no backend, sample heat-map data, TEST SITE tag."""
import os, re, glob, shutil
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def p(*a): return os.path.join(R, *a)
# no backend: drop api/, keep one sample endpoint for the heat map
shutil.rmtree(p('api'), ignore_errors=True); os.makedirs(p('api'))
open(p('api', 'heatmap.php'), 'w').write('''<?php
// TEST SITE ONLY: fixed sample data so the heat map globe can be styled. Not real results.
header('Content-Type: application/json');
$p = [['London','GB',51.5,-0.1,128,132,60,1,2,1],['Frankfurt','DE',50.1,8.7,124,132,77,3,3,2],['Dubai','AE',25.2,55.3,123,132,462,4,3,2],['Buenos Aires','AR',-34.6,-58.4,124,132,257,3,3,2],['Sydney','AU',-33.9,151.2,123,132,247,4,3,2],['Sao Paulo','BR',-23.5,-46.6,123,132,228,4,3,2],['Montreal','CA',45.5,-73.6,121,132,107,5,4,2],['Tokyo','JP',35.7,139.7,100,132,150,20,8,4],['Johannesburg','ZA',-26.2,28.0,123,132,300,4,3,2],['Dallas','US',32.8,-96.8,126,132,90,3,2,1],['Mumbai','IN',19.1,72.9,120,132,210,6,4,2],['Singapore','SG',1.3,103.8,125,132,140,3,2,2]];
$places = [];
foreach ($p as $r) $places[] = ['city'=>$r[0],'country'=>$r[1],'lat'=>$r[2],'lon'=>$r[3],'ok'=>$r[4],'n'=>$r[5],'median_ms'=>$r[6],'error'=>$r[7],'blocked'=>$r[8],'none'=>$r[9]];
echo json_encode(['places'=>$places,'sites_count'=>132,'newest'=>time()-300,'oldest'=>time()-7200,'unreachable'=>[]]);
''')
# Test site only: sample local reports + a report stub (nothing is stored here).
open(p('api', 'outage-local.php'), 'w').write('''<?php
// TEST SITE ONLY: fixed sample data so the local outage map can be styled. Not real reports.
header('Content-Type: application/json');
$s = [[51.5,-0.1,14,'Netflix',6,'Instagram',5,'WhatsApp',3],[53.5,-2.3,6,'Netflix',4,'Facebook',2],[52.5,-1.9,4,'Instagram',4],[48.9,2.3,9,'WhatsApp',5,'Facebook',4],[40.7,-74.0,12,'Instagram',7,'Netflix',5],[34.1,-118.3,5,'YouTube',5],[19.1,72.9,8,'WhatsApp',8],[-33.9,151.2,3,'Netflix',3],[-23.5,-46.6,7,'Instagram',4,'WhatsApp',3],[35.7,139.7,4,'YouTube',4],[41.9,12.5,5,'Netflix',3,'Facebook',2],[52.5,13.4,4,'WhatsApp',4]];
$cells = []; $total = 0;
foreach ($s as $r) { $sites = []; for ($i = 3; $i < count($r); $i += 2) $sites[] = ['name' => $r[$i], 'n' => $r[$i + 1]]; $k = count($cells); $cells[] = ['lat' => $r[0], 'lon' => $r[1], 'cell' => 0.2, 'n' => $r[2], 'w' => round(max(0.15, 1 - $k * 0.08), 2), 'newest' => gmdate('Y-m-d\\TH:i:s\\Z', time() - (5 + $k * 12) * 60), 'sites' => array_map(function($x) use ($k) { if ($k % 4 === 2) $x['rec'] = 'checks'; return $x; }, $sites)]; $total += $r[2]; }
echo json_encode(['hours' => (int)($_GET['hours'] ?? 3), 'total' => $total, 'cells' => $cells]);
''')
open(p('api', 'report.php'), 'w').write('''<?php
// TEST SITE ONLY: accepts a report but stores nothing.
header('Content-Type: application/json');
$b = json_decode(file_get_contents('php://input'), true); $fx = !empty($b['kinds']) && $b['kinds'] === ['fixed'];
echo json_encode(['ok' => true, 'added' => 1, 'message' => $fx ? 'Thanks. This is the test site, so nothing was saved.' : 'Thanks. This is the test site, so nothing was saved.']);
''')
open(p('api', 'reports.php'), 'w').write('''<?php
// TEST SITE ONLY: sample latest-reports list. Not real reports.
header('Content-Type: application/json');
if (empty($_GET['recent'])) { http_response_code(404); echo json_encode(['error' => 'Sample site']); exit; }
$h = strtolower((string)($_GET['host'] ?? ''));
$s = [['netflix.com','Netflix','/is-netflix-down','login',3,'GB'],['instagram.com','Instagram','/is-instagram-down','site',9,null],['whatsapp.com','WhatsApp','/is-whatsapp-down','slow',22,'IN'],['netflix.com','Netflix','/is-netflix-down','site',41,'GB'],['facebook.com','Facebook','/is-facebook-down','app',75,'US'],['instagram.com','Instagram','/is-instagram-down','login',130,'GB'],['youtube.com','YouTube','/is-youtube-down','slow',260,null],['netflix.com','Netflix','/is-netflix-down','fixed',12,'GB']];
$items = [];
foreach ($s as $r) { if ($h !== '' && $h !== $r[0]) continue; $items[] = ['host'=>$r[0],'name'=>$r[1],'page'=>$r[2],'kind'=>$r[3],'ts'=>gmdate('Y-m-d\\TH:i:s\\Z', time() - $r[4] * 60),'country'=>$r[5]]; }
echo json_encode(['items' => $items]);
''')
open(p('api', 'history-day.php'), 'w').write('''<?php
// TEST SITE ONLY: sample day-by-day history. Not real data.
header('Content-Type: application/json');
$today = gmdate('Y-m-d'); $h = strtolower((string)($_GET['host'] ?? ''));
if (!empty($_GET['days'])) {
    $days = []; foreach ([0,1,3,4,8,12,19] as $i => $o) $days[] = ['day' => gmdate('Y-m-d', time() - $o * 86400), 'reports' => 140 - $i * 17, 'outages' => $i % 3, 'down_min' => ($i % 3) * 22];
    echo json_encode(['host' => $h ?: null, 'name' => null, 'today' => $today, 'days' => $days]); exit;
}
$date = (string)($_GET['date'] ?? $today);
if (!preg_match('/^\\d{4}-\\d{2}-\\d{2}$/', $date) || $date > $today) { http_response_code(422); echo json_encode(['error' => 'Please pick a valid date that is not in the future.']); exit; }
$rows = [['netflix.com','Netflix','/is-netflix-down',54,['site'=>10,'login'=>38,'app'=>4,'slow'=>2],9,1,26],['instagram.com','Instagram','/is-instagram-down',31,['site'=>20,'login'=>5,'app'=>4,'slow'=>2],4,0,0],['whatsapp.com','WhatsApp','/is-whatsapp-down',12,['site'=>3,'login'=>0,'app'=>2,'slow'=>7],1,0,0]];
$out = []; foreach ($rows as $r) { if ($h !== '' && $h !== $r[0]) continue; $out[] = ['host'=>$r[0],'name'=>$r[1],'page'=>$r[2],'reports'=>$r[3],'kinds'=>$r[4],'fixed'=>$r[5],'outages'=>$r[6],'down_min'=>$r[7]]; }
echo json_encode(['date' => $date, 'today' => $today, 'host' => $h ?: null, 'total_reports' => array_sum(array_column($out, 'reports')), 'total_outages' => array_sum(array_column($out, 'outages')), 'rows' => $out]);
''')
open(p('api', 'insights.php'), 'w').write('''<?php
// TEST SITE ONLY: sample data for the More reports tabs. Not real results.
header('Content-Type: application/json');
$n = fn($name, $slug, $x = []) => array_merge(['host' => $slug . '.com', 'name' => $name, 'page' => '/is-' . $slug . '-down'], $x);
$t = time(); $d = fn($ago) => gmdate('Y-m-d\\\\TH:i:s\\\\Z', $t - $ago);
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
 'cats_rel' => [['cat'=>'search','sites'=>6,'pct'=>99.98,'outages'=>0],['cat'=>'video','sites'=>11,'pct'=>99.9,'outages'=>2],['cat'=>'gaming','sites'=>20,'pct'=>99.5,'outages'=>8]],
 'cascade' => [['provider'=>'Cloudflare','count'=>4,'sites'=>[['name'=>'Discord','page'=>'/is-discord-down','state'=>'slow'],['name'=>'Roblox','page'=>'/is-roblox-down','state'=>'slow'],['name'=>'Canva','page'=>'/is-canva-down','state'=>'down'],['name'=>'Medium','page'=>'/is-medium-down','state'=>'slow']]]],
 'cal' => array_map(fn($i) => ['day' => gmdate('Y-m-d', $t - (90 - $i) * 86400), 'n' => ($i * 7) % 5 === 0 ? ($i % 6) : 0], range(0, 90)),
 'glance' => ['checked'=>132,'outages'=>3,'avg'=>312,'avg_prev'=>287], 'trend' => $trend, 'now' => $d(0)
]);
''')
open(p('api', 'sitestats.php'), 'w').write('''<?php
// TEST SITE ONLY: sample numbers for the deeper-insight section. Not real results.
header('Content-Type: application/json');
$h = strtolower((string)($_GET['host'] ?? 'example.com')); $t = time(); $d = fn($ago) => gmdate('Y-m-d\\\\TH:i:s\\\\Z', $t - $ago);
$bad = in_array($h, ['discord.com', 'roblox.com'], true);
$hours = [210,205,198,190,185,180,190,230,260,280,270,260,255,250,260,270,290,330,420,470,440,380,300,240];
echo json_encode(['host' => $h, 'name' => ucfirst(explode('.', $h)[0]), 'page' => '/is-' . explode('.', $h)[0] . '-down', 'cat' => 'video',
 'u7' => ['checks' => 2000, 'pct' => $bad ? 99.4 : 99.98, 'outages' => $bad ? 2 : 0, 'down' => $bad ? 3600 : 0, 'avg' => 250],
 'u30' => ['checks' => 8000, 'pct' => $bad ? 99.2 : 99.96, 'outages' => $bad ? 5 : 1, 'down' => $bad ? 9000 : 900, 'avg' => 262],
 'grade' => $bad ? 'C' : 'A', 'rank' => ['n' => 3, 'of' => 11], 'timing' => ['dns' => 12, 'conn' => 31, 'tls' => 58, 'ttfb' => 164, 'n' => 288],
 'hours' => $hours, 'outages' => [['started' => $d(400000), 'ended' => $d(396400), 'seconds' => 3600], ['started' => $d(1200000), 'ended' => $d(1198800), 'seconds' => 1200], ['started' => $d(3000000), 'ended' => $d(2995000), 'seconds' => 5000]],
 'outages_90' => 3, 'mtbf_h' => 612.0, 'provider' => 'Cloudflare', 'now' => $d(0)]);
''')
open(p('api', 'weekly.php'), 'w').write('''<?php
// TEST SITE ONLY: sample weekly summary. Not real results.
header('Content-Type: application/json');
$n = fn($name, $slug, $x) => array_merge(['host' => $slug . '.com', 'name' => $name, 'page' => '/is-' . $slug . '-down', 'cat' => 'social', 'ms' => 200], $x);
$t = time();
echo json_encode(['from' => gmdate('Y-m-d', $t - 6 * 86400), 'to' => gmdate('Y-m-d', $t), 'outages' => 14, 'outages_prev' => 19, 'down_s' => 31200, 'worst_day' => ['day' => gmdate('Y-m-d', $t - 2 * 86400), 'n' => 6], 'tracked' => 132, 'perfect' => 91,
 'best' => [$n('Google','google',['pct'=>100,'outages'=>0,'down'=>0]), $n('Wikipedia','wikipedia',['pct'=>100,'outages'=>0,'down'=>0]), $n('Amazon','amazon',['pct'=>99.99,'outages'=>0,'down'=>0])],
 'worst' => [$n('Discord','discord',['pct'=>98.9,'outages'=>4,'down'=>7200]), $n('Roblox','roblox',['pct'=>99.3,'outages'=>2,'down'=>4300])],
 'cats' => [['cat'=>'search','sites'=>6,'pct'=>99.98,'outages'=>0],['cat'=>'video','sites'=>11,'pct'=>99.9,'outages'=>2],['cat'=>'gaming','sites'=>20,'pct'=>99.5,'outages'=>8]],
 'longest' => ['name' => 'Discord', 'page' => '/is-discord-down', 'started' => gmdate('Y-m-d\\\\TH:i:s\\\\Z', $t - 3 * 86400), 'seconds' => 5400], 'reports' => 412, 'now' => gmdate('Y-m-d\\\\TH:i:s\\\\Z')]);
''')
open(p('api', 'export.php'), 'w').write('''<?php
// TEST SITE ONLY: sample CSV.
header('Content-Type: text/csv; charset=utf-8'); header('Content-Disposition: attachment; filename="sample-uptime.csv"');
echo "site,date_utc,checks,successful_checks,uptime_percent,average_response_ms,outages,minutes_down\\nSample,2026-11-01,288,288,100,250,0,0\\nSample,2026-11-02,288,286,99.31,262,1,10\\n";
''')
open(p('robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
for f in ('sitemap.xml', 'ads.txt'):
    if os.path.exists(p(f)): os.remove(p(f))
h = open(p('.htaccess')).read()
if 'X-Robots-Tag' not in h:
    h = h.replace('<IfModule mod_headers.c>', '<IfModule mod_headers.c>\n  Header always set X-Robots-Tag "noindex, nofollow, noarchive"', 1); open(p('.htaccess'), 'w').write(h)
for f in glob.glob(p('**', '*.html'), recursive=True):
    s = open(f, encoding='utf-8').read(); o = s
    s = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,nofollow,noarchive">', s)
    s = s.replace('<meta name="google-adsense-account" content="ca-pub-6517978259411056">\n', '')
    if s != o: open(f, 'w', encoding='utf-8').write(s)
j = open(p('assets', 'app.js'), encoding='utf-8').read()
if 'ads never load' not in j:
    j = j.replace('function loadAds() {', 'function loadAds() {\n    return; /* test site: ads never load */', 1); open(p('assets', 'app.js'), 'w', encoding='utf-8').write(j)
c = open(p('assets', 'newlook.css'), encoding='utf-8').read()
if 'TEST SITE' not in c:
    c += '\nbody:after{content:"TEST SITE";position:fixed;right:10px;bottom:10px;background:#f59e0b;color:#000;font:700 12px/1 system-ui,sans-serif;letter-spacing:.08em;padding:7px 10px;border:2px solid #000;border-radius:6px;z-index:90;pointer-events:none}\n'
    open(p('assets', 'newlook.css'), 'w', encoding='utf-8').write(c)
print('staging overrides applied')

# Test site only: let /layout, /heatmap-plain etc. open the matching .html mock-up without the extension.
h = open(p('.htaccess')).read()
if 'TEST-CLEAN-URLS' not in h:
    h = h.replace('RewriteEngine On\n', 'RewriteEngine On\n# TEST-CLEAN-URLS\nRewriteCond %{REQUEST_FILENAME}.html -f\nRewriteRule ^([A-Za-z0-9_-]+)/?$ $1.html [L]\n', 1)
    open(p('.htaccess'), 'w').write(h)
