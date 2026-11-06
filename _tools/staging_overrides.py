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
