#!/usr/bin/env python3
"""Builds the static pages (index, login, account, monitor, privacy, legal, contact, 404) with a shared header and footer.
Run:  python3 _tools/build.py   (from the project folder)"""
import datetime as _dt
import os, html

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITE = 'https://siteupdown.com'

INVADER = ["..#.....#..", "...#...#...", "..#######..", ".##.###.##.", "###########", "#.#######.#", "#.#.....#.#", "...##.##..."]
def invader():
    r = ''
    for y, row in enumerate(INVADER):
        for x, ch in enumerate(row):
            if ch == '#':
                eye = (y == 3 and x in (3, 7))
                r += '<rect x="%d" y="%d" width="1" height="1"%s/>' % (x, y, ' fill="var(--bg)"' if False else '')
    # eyes: draw as dark squares on top
    r += '<rect x="3" y="3" width="1" height="1" fill="var(--bg)"/><rect x="7" y="3" width="1" height="1" fill="var(--bg)"/>'
    return '<svg viewBox="0 0 11 8" fill="currentColor" shape-rendering="crispEdges" aria-hidden="true">%s</svg>' % r
INV = invader()
LOGO = 'arrow'   # 'robot' or 'arrow': which logo files in assets/ the header and footer use
LOGO_ASPECT = {'robot': 2.0, 'arrow': 1.5}[LOGO]
BRAND = ('<img class="lf lf-d" src="/assets/logo-%s-dark.png" alt="siteupdown.com" width="%d" height="56"><img class="lf lf-l" src="/assets/logo-%s-light.png" alt="" width="%d" height="56">' % (LOGO, round(56 * LOGO_ASPECT), LOGO, round(56 * LOGO_ASPECT)))

def ico(path, extra=''):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"%s>%s</svg>' % (extra, path)
I_GLOBE = ico('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>')
I_RADIO = ico('<circle cx="12" cy="12" r="2"/><path d="M16.2 7.8a6 6 0 0 1 0 8.4M7.8 16.2a6 6 0 0 1 0-8.4M19 5a10 10 0 0 1 0 14M5 19A10 10 0 0 1 5 5"/>')
I_SHIELD = ico('<path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>')
I_ARROW = ico('<path d="M5 12h14M13 6l6 6-6 6"/>')
I_MAIL = ico('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>')
I_LOCK = ico('<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>')
I_USER = ico('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>')
I_REFRESH = ico('<path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7"/>')
I_LINK = ico('<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>')
I_WA = ico('<path d="M21 11.5a8.4 8.4 0 0 1-12.3 7.4L3 21l2.2-5.5A8.4 8.4 0 1 1 21 11.5z"/><path d="M9 9.5c.3 2.6 2.9 5.2 5.5 5.5l1.3-1.3-2-1-.8.8c-1-.4-1.9-1.300-2.300-2.300l.8-.8-1-2z" fill="currentColor" stroke="none"/>')
I_SHARE = ico('<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="m8.2 10.8 7.600-3.600M8.200 13.200l7.600 3.600"/>')
I_SEARCH = ico('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>')
I_FB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8V6.5c0-.7.3-1 1-1h2V2h-3a4 4 0 0 0-4 4.2V8H7.5v3.5H10V22h4V11.5h2.7L17 8z"/></svg>'
I_IG = ico('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>')
I_X = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.9-6.3L5.3 21H2.2l7.2-8.3L2 3h6.4l4.4 5.8zm-1.1 16.2h1.7L7.3 4.7H5.5z"/></svg>'
I_TT = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 3a5 5 0 0 0 4 4.4v3.3a8 8 0 0 1-4-1.2v6.2a6 6 0 1 1-6-6c.3 0 .7 0 1 .1v3.4a2.7 2.7 0 1 0 1.8 2.5V3z"/></svg>'
I_YT = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3z"/></svg>'

NAV = [('Regional map', '/#global-pulse'), ('Top websites', '/#top-sites'), ('Gaming', '/#online-gaming'), ('Tools', '/tools/'), ('Monitor', '/monitor'), ('Account', '/account'), ('Help', '/help/'), ('How it works', '/#how-it-works')]


MENU = [
 ('Check', [('Website checker', '/', 'Is it down, or just you?'), ('All apps &amp; sites', '/is-it-down/', ''), ('Outage map', '/outage-map', 'Reachability around the world'), ('Outage history', '/outage-history', 'What happened on past days'), ('State of the internet', '/state-of-the-internet', 'This week in outages'), ('Compare sites', '/compare', 'Two services side by side'), ('Monitor &amp; alerts', '/monitor', 'Watch up to 25 sites')]),
 ('Tools', [('Internet speed test', '/internet-speed-test', ''), ('Website speed test', '/speed', ''), ('What is my IP?', '/what-is-my-ip', ''), ('Game ping test', '/game-ping-test', ''), ('All tools', '/tools/', '')]),
 ('Learn', [('Help centre', '/help/', 'Plain-English guides'), ('How we check', '/how-we-check', ''), ('FAQ', '/faq', '')]),
 ('More', [('Account', '/account', ''), ('About', '/about', ''), ('For business', '/business', ''), ('Contact', '/contact', '')]),
]
DRAWER_HTML = '<button class="nl-close" id="nl-close" type="button" aria-label="Close menu">&times;</button>' + ''.join('<h2>%s</h2>%s' % (g, ''.join('<a href="%s"%s>%s%s</a>' % (h, '' if g != 'More' else ' class="nl-sub"', l, ('<small>%s</small>' % sm) if sm else '') for l, h, sm in items)) for g, items in MENU)

def fit_title(t, limit=60):
    """Search results cut titles at about 60 characters: drop the brand suffix first, then trim at a word."""
    if len(t) <= limit: return t
    for suf in (' \u2014 siteupdown.com', ' | siteupdown.com'):
        if t.endswith(suf):
            t = t[:-len(suf)]
            break
    if len(t) <= limit: return t
    cut = t[:limit].rsplit(' ', 1)[0].rstrip(' ,:;-\u2014|')
    return cut

def fit_desc(d, limit=158):
    """Descriptions are cut at about 160 characters: end on a sentence or word instead."""
    if len(d) <= limit: return d
    cut = d[:limit]
    if '. ' in cut[80:]: return cut[:cut.rindex('. ') + 1]
    return cut.rsplit(' ', 1)[0].rstrip(' ,;:-') + '\u2026'

def head(title, desc, path, extra_head='', noindex=False):
    t = html.escape(fit_title(title))
    d = html.escape(fit_desc(desc))
    canon = SITE + path
    drawer = DRAWER_HTML
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">'
    return f'''<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
{robots}
<meta name="google-adsense-account" content="ca-pub-6517978259411056">
<link rel="canonical" href="{canon}"><link rel="alternate" hreflang="en-gb" href="{canon}"><link rel="alternate" hreflang="x-default" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="siteupdown.com">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{SITE}/assets/og.png">
<link rel="alternate" type="application/rss+xml" title="siteupdown.com guides" href="/feed.xml"><meta name="application-name" content="siteupdown.com"><meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#ffde59">
<link rel="icon" href="/favicon.ico?v=3" sizes="any"><link rel="icon" href="/favicon-32.png?v=3" type="image/png" sizes="32x32"><link rel="icon" href="/favicon-64.png?v=3" type="image/png" sizes="64x64"><link rel="manifest" href="/site.webmanifest"><link rel="icon" href="/favicon-192.png?v=3" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="/apple-touch-icon.png?v=3">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/app.css">
<link rel="stylesheet" href="/assets/newlook.css">
{extra_head}
</head>
<body{{BODYATTR}}>
<a class="skip" href="#main">Skip to content</a>
<header class="nl-head"><div class="nl-bar">
<a class="nl-logo" href="/" aria-label="siteupdown.com home"><img src="/assets/nl-logo.png" alt="Site up down?" width="831" height="391"></a>
<div class="nl-tools"><div id="auth"></div><button class="nl-menu-btn" id="nl-menu-btn" type="button" aria-expanded="false" aria-controls="nl-drawer" aria-label="Open menu"><span></span><span></span><span></span></button></div>
</div></header>
<div class="nl-scrim" id="nl-scrim" hidden></div>
<nav class="nl-drawer" id="nl-drawer" aria-label="Main menu">{drawer}</nav>
<main id="main">
'''

SHOW_SOCIALS = False  # set True once the social profiles exist and ad approval is done
def foot(scripts):
    groups = [('Check', [('Website checker', '/'), ('Is it down?', '/is-it-down/'), ('Outage map', '/outage-map'), ('Outage history', '/outage-history'), ('State of the internet', '/state-of-the-internet'), ('Compare sites', '/compare'), ('Monitor', '/monitor')]), ('Tools', [('Internet speed test', '/internet-speed-test'), ('Website speed test', '/speed'), ('What is my IP?', '/what-is-my-ip'), ('Game ping test', '/game-ping-test'), ('All tools', '/tools/')]), ('Learn', [('Help centre', '/help/'), ('How we check', '/how-we-check'), ('FAQ', '/faq')]), ('Company', [('Account', '/account'), ('About', '/about'), ('For business', '/business'), ('Contact', '/contact')]), ('Legal', [('Terms &amp; legal', '/legal'), ('Privacy', '/privacy'), ('Editorial &amp; ad policy', '/editorial-policy')])]
    fgrid = ''.join('<div class="nl-fg"><h3>%s</h3>%s%s</div>' % (g, ''.join('<a href="%s">%s</a>' % (h, l) for l, h in items), '<button type="button" data-cookie-settings>Cookie settings</button>' if g == 'Legal' else '') for g, items in groups)
    SOCIALS_HTML = f'''<div class="socials" aria-label="Social media">
<a href="#" title="Facebook" aria-label="Facebook">{I_FB}</a><a href="#" title="Instagram" aria-label="Instagram">{I_IG}</a><a href="#" title="X" aria-label="X">{I_X}</a><a href="#" title="TikTok" aria-label="TikTok">{I_TT}</a><a href="#" title="YouTube" aria-label="YouTube">{I_YT}</a>
</div>'''
    return f'''</main>
<footer class="site-foot"><div class="wrap nl-foot">
<img src="/assets/nl-logo-light.png" alt="Site up down?" width="831" height="391">
<p class="note">Less refreshing. More knowing.</p>
{SOCIALS_HTML if SHOW_SOCIALS else ''}
<nav class="nl-fgrid nl-fcard" aria-label="All pages">{fgrid}</nav>
<p class="fine">&copy; <span data-year>2026</span> siteupdown.com. An independent website checker, not affiliated with the sites it checks. Regional probes use the public <a href="https://globalping.io" rel="noopener">Globalping</a> network.</p>
</div></footer>
{scripts}
<script src="/assets/newlook.js"></script>
</body>
</html>
'''

import hashlib, re as _re
def _ver():
    h = hashlib.md5()
    for n in ('app.css', 'app.js', 'home.js', 'pages.js', 'worldmap.js', 'landmask.js', 'live.js', 'sitepage.js', 'tools.js', 'sla.js', 'speedtest.js', 'heatmap.js', 'localmap.js', 'history.js', 'ip.js', 'gameping.js', 'embed.js', 'state.js', 'newlook.js', 'newlook.css'):
        try: h.update(open(os.path.join(ROOT, 'assets', n), 'rb').read())
        except OSError: pass
    return h.hexdigest()[:8]
import html as _html
_ICO = {
 '\u26a1': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 '\U0001F514': '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21a2 2 0 0 0 4 0"/>',
 '\U0001F512': '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 '\U0001F4C8': '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 '\U0001F9ED': '<circle cx="12" cy="12" r="10"/><path d="m16 8-2 6-6 2 2-6z"/>',
 '\U0001F6E0': '<path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-3 3-2.4-.6-.6-2.4z"/>',
 '\U0001F4DA': '<path d="M4 4h5v16H4zM9 4h5v16H9z"/><path d="m14 6 5-1 2 15-5 1z"/>',
 '\U0001F310': '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20"/>',
 '\U0001F4CB': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9zM9 12h6M9 16h6"/>',
 '\U0001F4C5': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 '\u2709': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
 '\U0001F916': '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 4v4M9 14h.01M15 14h.01M9 18h6"/>',
 '\U0001F6E1': '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
}
_ICO['\u21aa'] = '<path d="M5 12h11l-4-4M16 12l-4 4"/><path d="M19 5v14"/>'
_ICO['\U0001F4E1'] = '<path d="M5 19a9 9 0 0 1 0-12"/><path d="M8.5 15.5a4.5 4.5 0 0 1 0-5"/><circle cx="12" cy="12.5" r="1.5"/><path d="M15.5 15.5a4.5 4.5 0 0 0 0-5"/><path d="M19 19a9 9 0 0 0 0-12"/>'
_ICO['\U0001F5FA'] = '<path d="m3 6 6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/>'
_ICO['\U0001F4D0'] = '<path d="M4 20 20 4v16z"/><path d="M8 20v-3M12 20v-6M16 20v-9"/>'
_ICO['\U0001F50D'] = '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>'
_ICO['\U0001F4F6'] = '<path d="M5 20v-4M10 20v-8M15 20V8M20 20V4"/>'
_ICO['\U0001F3AE'] = '<rect x="2" y="7" width="20" height="11" rx="5"/><path d="M7 10.5v4M5 12.5h4M16 11h.01M18.5 14h.01"/>'
_ICO['\U0001F50C'] = '<path d="M9 2v5M15 2v5"/><path d="M6 7h12v4a6 6 0 0 1-12 0z"/><path d="M12 17v5"/>'
_ICO['\U0001F4CD'] = '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'
def _svgicons(c):
    def r(m):
        e = _html.unescape(m.group(1)).rstrip('\ufe0f')
        return '<span class="ti"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg></span>' % _ICO[e] if e in _ICO else m.group(0)
    return _re.sub(r'<span class="ti">([^<]{1,9})</span>', r, c)

def build_newlook_css():
    src = open(os.path.join(ROOT, '_tools', 'newlook.src.css'), encoding='utf-8').read()
    out = src.replace('@@', ':root[data-theme=light] body')
    open(os.path.join(ROOT, 'assets', 'newlook.css'), 'w', encoding='utf-8').write(out)

def seo_extras(name, content):
    """Per-page share image and (when the page has none of its own) breadcrumb + page structured data."""
    if 'content="noindex' in content or name in ('index.html', '404.html', '403.html', '500.html'): return content
    m = _re.search(r'<title>(.*?)</title>', content)
    if not m: return content
    title = html.unescape(m.group(1)); short = _re.split(r'\s[|\u2014\u2013-]\s(?=siteupdown)', title)[0].strip()
    stem = name[:-5]; slug = stem.replace('/', '-')
    label = 'Guide' if stem.startswith('help/') else 'Free tool' if stem.startswith('tools/') else 'Is it down?' if _re.match(r'is-.*-down$', stem) else 'siteupdown.com'
    try:
        import make_og
        img = SITE + make_og.make(slug, short, label)
        content = content.replace(SITE + '/assets/og.png', img)
    except Exception as e:
        print('og image skipped for', name, e)
    if '"BreadcrumbList"' not in content:
        parts = [('Home', SITE + '/')]
        segs = stem.split('/')
        if len(segs) > 1: parts.append((segs[0].capitalize() if segs[0] != 'help' else 'Help centre', SITE + '/' + segs[0] + '/'))
        parts.append((short, SITE + '/' + stem))
        kind = 'AboutPage' if stem == 'about' else 'ContactPage' if stem == 'contact' else 'CollectionPage' if stem.endswith('index') or stem in ('outage-history', 'outage-map', 'state-of-the-internet', 'compare') else 'WebPage'
        d = {'@context': 'https://schema.org', '@graph': [
            {'@type': kind, '@id': SITE + '/' + stem + '#page', 'url': SITE + '/' + stem, 'name': short, 'isPartOf': {'@type': 'WebSite', 'name': 'siteupdown.com', 'url': SITE + '/'}, 'inLanguage': 'en-GB',
             'dateModified': _dt.date.today().isoformat(), 'publisher': {'@type': 'Organization', 'name': 'siteupdown.com', 'url': SITE + '/'}},
            {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(parts)]}]}
        content = content.replace('</head>', '<script type="application/ld+json">' + _json.dumps(d, ensure_ascii=False) + '</script>\n</head>', 1)
    return content

def write(name, content):
    if name.endswith('.html'):
        content = seo_extras(name, content)
        content = _svgicons(content)
        v = _ver()
        content = _re.sub(r'(/assets/(?:app\.css|newlook\.css|newlook\.js|app\.js|home\.js|pages\.js|worldmap\.js|live\.js|sitepage\.js|tools\.js|sla\.js|speedtest\.js|heatmap\.js|state\.js|localmap\.js|history\.js|ip\.js|gameping\.js|embed\.js))(?=")', r'\1?v=' + v, content)
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
        f.write(content)
    print('wrote', name, len(content), 'bytes')

# ---------------------------------------------------------------- home
ADS_ON = False
def ADS_OFF_GUARD(): return ADS_ON  # switch to True once AdSense is approved and the ad code is added
def ad(label, text):
    if not ADS_OFF_GUARD(): return ''
    return f'<aside class="ad" aria-label="Advertisement"><small>{label}</small><span>{text}</span></aside>'

def home():
    jsonld = '<script type="application/ld+json">{"@context": "https://schema.org", "@graph": [{"@type": "WebSite", "@id": "https://siteupdown.com/#website", "name": "siteupdown.com", "url": "https://siteupdown.com/", "description": "Check whether a website is down for everyone or just you, with probes in fifteen places around the world.", "inLanguage": "en-GB"}, {"@type": "Organization", "@id": "https://siteupdown.com/#org", "name": "siteupdown.com", "url": "https://siteupdown.com/", "logo": "https://siteupdown.com/android-chrome-512.png", "email": "hello@siteupdown.com"}, {"@type": "WebApplication", "name": "siteupdown.com website checker", "url": "https://siteupdown.com/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}}]}</script>'
    h = head('siteupdown.com — Is the website down, or just you?', 'Paste any website address to see if it is down for everyone or only for you. We check from our server and from fifteen probes in different countries, at the same time.', '/', jsonld)
    h = h.replace('{BODYATTR}', ' data-page="home"')
    report_kinds = ''.join('<button type="button" class="rk" data-kind="%s">%s</button>' % (k, l) for k, l in SP.KIND_LABELS)
    order = [k for k in ['social', 'video', 'gaming', 'ai', 'finance', 'payments', 'trading', 'shopping', 'delivery', 'news', 'government', 'health', 'betting', 'telecom', 'travel', 'search', 'work'] if sum(1 for _, _, c, _ in SP.SITES if c == k) >= 4]
    short = {'social': 'Social', 'video': 'Streaming', 'gaming': 'Gaming', 'ai': 'AI', 'finance': 'Banks', 'payments': 'Payments', 'trading': 'Trading & crypto', 'shopping': 'Shopping', 'delivery': 'Delivery', 'news': 'News', 'government': 'Government', 'health': 'Health', 'betting': 'Betting', 'telecom': 'Broadband & mobile', 'travel': 'Travel', 'search': 'Search & email', 'work': 'Work & cloud'}
    topchips = '<button class="chip" type="button" data-cat="" aria-pressed="true">Popular</button>' + ''.join('<button class="chip" type="button" data-cat="%s" aria-pressed="false" data-full="%s">%s</button>' % (k, html.escape(SP.CATS[k][0]), html.escape(short[k])) for k in order if k in SP.CATS)
    share_btns = ''.join(f'<button class="sb{" wide" if k=="copy" else ""}" type="button" data-share="{k}" title="{t}" aria-label="{t}"{" hidden" if k=="native" else ""}>{i}{("<span>"+t+"</span>") if k=="copy" else ""}</button>' for k, t, i in [('copy', 'Copy link', I_LINK), ('x', 'Share on X', I_X), ('fb', 'Share on Facebook', I_FB), ('wa', 'Share on WhatsApp', I_WA), ('native', 'More share options', I_SHARE)])
    body = f'''
<section class="nl-hero"><div class="wrap">
<h1>Is it down, or is it just you?</h1>
<p class="lead">Paste any website. We check it from our server and from around the world.</p>
<form class="card checker" id="chk-form" aria-labelledby="checker-title" novalidate>
<div class="nl-wbar" aria-hidden="true"><span>&lsaquo;</span><i></i><span>&rsaquo;</span></div><div class="nl-wbody">
<div class="top"><span id="checker-title"><img class="nl-ant" src="/assets/nl-antenna.png?v=1" alt="" width="25" height="26">Check a website</span><span class="nl-live"><svg class="nl-beacon" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle class="bb" cx="12" cy="12" r="6" fill="none" stroke="#22c55e" stroke-width="2"/><circle cx="12" cy="12" r="6.5" fill="#22c55e" stroke="#0b0b0b" stroke-width="2.2"/><circle cx="10" cy="10" r="1.8" fill="#fff"/></svg><em>Live Check</em></span></div>
<div class="chk-row">
<div class="field">{I_GLOBE}<input id="chk-input" name="address" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="e.g. netflix.com" maxlength="300" aria-label="Website address"></div>
<button class="btn" id="chk-btn" type="submit"><span>Check website</span>{I_ARROW}</button></div>
<p class="err" id="chk-err" role="alert"></p>
<div class="chk-foot"><p class="assure">{I_SHIELD}No sign-up. Just answers.</p></div>
</div></form>
<div class="recent-row" id="recent-wrap" hidden><div class="eyebrow">Your recent searches</div><div class="chips" id="recent-chips"></div></div>
<div class="nl-try"><span class="eyebrow">Try one</span>
<button class="chip" type="button" data-h="google.com">google.com</button><button class="chip" type="button" data-h="youtube.com">youtube.com</button><a class="chip" href="/is-whatsapp-down">WhatsApp</a><a class="chip" href="/is-instagram-down">Instagram</a><a class="chip" href="/is-roblox-down">Roblox</a><a class="chip" href="/is-facebook-down">Facebook</a><a class="chip" href="/is-netflix-down">Netflix</a><a class="chip" href="/is-tiktok-down">TikTok</a><a class="chip" href="/is-amazon-down">Amazon</a><a class="chip" href="/is-discord-down">Discord</a><a class="chip" href="/is-chatgpt-down">ChatGPT</a></div>
</div></section>

<section class="nl-tiles"><div class="wrap"><div class="nl-grid">
<a class="nl-tile" href="/internet-speed-test"><b>Speed test</b><span>How fast is your internet?</span><img src="/assets/nl-tile-speed.svg?v=4" alt="" width="200" height="140" loading="lazy"></a>
<a class="nl-tile map" href="/outage-map"><b>Outage map</b><span>What is down around the world</span><img src="/assets/nl-map.png" alt="" width="580" height="437" loading="lazy"></a>
<a class="nl-tile mon" href="/monitor"><b>Monitor</b><span>Email alerts for up to 25 sites</span><img src="/assets/nl-tile-monitor.svg" alt="" width="200" height="150" loading="lazy"></a>
<a class="nl-tile help" href="/help/"><b>Help</b><span>Plain-English guides</span><img src="/assets/nl-tile-help.svg" alt="" width="160" height="160" loading="lazy"></a>
</div></div></section>

<section id="global-pulse" class="nl-pulse"><div class="wrap">
<div class="card pulse-card" aria-live="polite">
<div class="pc-head"><div><span class="eyebrow"><i></i>Global pulse · worldwide probes</span>
<h2>Down for everyone — or just you<span class="dot">?</span></h2>
<p class="lead">One run asks machines in different countries to fetch the same address at the same time. If they can all reach it, the problem is probably on your side.</p></div>
<div class="pc-actions"><span class="statchip" hidden><i></i><span id="pulse-status">Standby</span></span><button class="btn small ghost" type="button" id="run-again" hidden>Run again</button></div></div>
<div class="strip">
<div class="cell wide"><span class="k">Verdict</span><b id="v-big">Waiting for probes</b><small id="v-sub">No address checked yet</small><small class="v-ip" id="v-ip" hidden></small><span id="v-pill"></span></div>
<div class="cell"><span class="k">Reachable</span><b id="s-reach">0/12</b><small>probes that answered</small></div>
<div class="cell"><span class="k">Median response</span><b id="s-med">—</b><small>across responding probes</small></div>
<div class="cell"><span class="k">Measured at</span><b id="s-at">—</b><small>Not run yet</small></div>
</div>
<div class="cantsure" id="cs-home" hidden></div>
<div class="hsum" id="hsum" hidden aria-live="polite"><p class="hs-line" id="hs-line"></p><div class="hs-chips"><span class="hs-c"><i class="hs-dot"></i><b id="hs-ms">&mdash;</b><small>live response</small><svg id="hs-spark" viewBox="0 0 60 18" preserveAspectRatio="none" aria-hidden="true"></svg></span><span class="hs-c"><b id="hs-up">&mdash;</b><small>up, last 24 hours</small></span><span class="hs-c"><b id="hs-rep">&mdash;</b><small>reports, last 3 hours</small></span><span class="hs-c"><b id="hs-pr">&mdash;</b><small>regions reached</small></span></div></div>
<div class="map-card"><div class="map-wrap" id="map"><svg id="map-svg" role="img" aria-label="World map of probe results" preserveAspectRatio="xMidYMid meet"></svg>
<div class="map-empty" id="map-empty"><span>No regional run yet. Check a website and the map lights up.</span></div><div class="tip" id="tip" hidden></div></div>
<div class="legend" aria-label="Map legend"><span><i style="background:var(--green)"></i>Responded</span><span><i style="background:var(--amber)"></i>Blocked</span><span><i style="background:var(--red)"></i>Server error</span><span><i style="border:2px solid var(--grey)"></i>No connection</span></div>
<p class="fine" style="margin-top:10px">Hover or tap a marker for details. Regions without a probe are not claimed. Each run is a snapshot, not continuous monitoring. Probe network: <a href="https://globalping.io" rel="noopener">Globalping</a>.</p></div>
<div class="details">
<div class="row-actions"><button class="btn small ghost" type="button" id="wl-add" hidden>Add to my watchlist</button><a class="btn small ghost" id="open-site" target="_blank" rel="noopener noreferrer" hidden>Open website ↗</a><a class="btn small ghost" id="speed-link" hidden>Test speed ⚡</a></div>
<div id="lv-home" hidden></div>
<div class="sp-card rep-box" id="rep-box" hidden><div class="sp-rhead"><b id="rb-title">Problems reported by visitors</b><span id="rb-level" class="sp-level"></span></div><div class="sp-ranges" id="rb-ranges" role="group" aria-label="Time range"><button type="button" class="rg on" data-range="24h" aria-pressed="true">24 hours</button><button type="button" class="rg" data-range="7d" aria-pressed="false">7 days</button><button type="button" class="rg" data-range="30d" aria-pressed="false">30 days</button><button type="button" class="rg" data-range="1y" aria-pressed="false">1 year</button></div><div class="sp-rdate" id="rb-date"></div><div class="sp-chart small" id="rb-chart"></div><div class="sp-axis" id="rb-axis"><span>24 hours ago</span><span>Now</span></div><p class="sp-rdetail" id="rb-detail"></p><div class="sp-kinds" id="rb-kinds"></div><h3 class="rf-h">Latest reports</h3><ul class="rf" id="rb-feed"></ul><div class="sp-report"><button type="button" class="btn small ghost" id="rb-btn"><span>Report a problem</span></button> <button type="button" class="btn small ghost" id="rb-fix"><span>It is working for me now</span></button><div class="sp-rpick" id="rb-pick" hidden><p>What is going wrong? Pick everything that applies.</p><div class="sp-rbtns">{report_kinds}</div><label class="rloc"><input type="checkbox"> <span>Also add my approximate area to the local outage map <small>Optional. Your browser will ask first. Rounded to about 10 km, never your exact spot.</small></span></label><p class="sp-rsendrow"><button type="button" class="btn small rsend" disabled><span>Send report</span></button></p></div><p class="sp-rmsg" id="rb-msg" role="status"></p></div></div>
<div class="share" id="share" hidden><span class="eyebrow">Share this check</span><div class="sbtns">{share_btns}</div></div></div>
</div>

<div class="charts" id="charts">
<div class="card chart"><h3>Response time by region</h3><p class="fine">Lower is faster. Colour shows the outcome. The two-letter codes are countries: hover or tap one for its name.</p><div id="ch-bars" class="ch-empty">Run a check to see this chart.</div></div>
<div class="card chart"><h3>Probe outcomes</h3><p class="fine">How the fifteen probes fared.</p><div id="ch-donut" class="ch-empty">Run a check to see this chart.</div></div>
<div class="card chart"><h3>Speed range</h3><p class="fine">Our server against the worldwide spread.</p><div id="ch-range" class="ch-empty">Run a check to see this chart.</div></div>
</div>
<div class="card more-det" id="more-det" hidden><h3>Technical details</h3><p class="fine">Certificate, DNS and what we saw when we fetched the page.</p><div id="ssl" hidden></div><div id="dns" hidden></div><div class="facts" id="facts" hidden></div></div>
</div></section>

<section class="nl-acc"><div class="wrap">
<div class="nl-d nl-fixed" id="recent-outages"><h2 class="nl-sum">Outages right now</h2><div class="nl-dbody"><div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Live · updates every minute</span><h2 id="ro-h">Outages right now<span class="dot">.</span></h2>
<p class="lead" id="ro-lead">Popular sites that are down at this moment, with any that came back in the last 24 hours underneath.</p></div></div>
<ul class="ro-list" id="ro-list"><li class="skeleton">Loading&hellip;</li></ul>
<h3 class="ro-sub">Running slower than usual</h3><ul class="ro-list" id="ro-slow"><li class="skeleton">Loading&hellip;</li></ul>
<h3 class="ro-sub">More reports</h3>
<div class="seg2 ins-tabs" id="ins-tabs" role="tablist"><button type="button" data-t="today" aria-pressed="true">Today</button><button type="button" data-t="rel" aria-pressed="false">Reliability</button><button type="button" data-t="speed" aria-pressed="false">Speed</button><button type="button" data-t="out" aria-pressed="false">Outages</button><button type="button" data-t="rep" aria-pressed="false">Visitor reports</button><button type="button" data-t="trend" aria-pressed="false">Trends</button></div>
<div id="ins-body" class="ins-body"><p class="ro-none">Loading&hellip;</p></div>
<p class="fine" style="margin-top:14px">A site counts as down after two failed checks in a row, so times are approximate and shown in your time zone. These reports use our own checks of the sites we watch and the problem reports visitors send us.</p>
</div></div></div>
<details class="nl-d" id="top-sites"><summary>Top websites</summary><div class="nl-dbody"><div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Watchlist · real requests</span><h2>Top websites<span class="dot">.</span></h2>
<p class="lead">A rolling sweep of the sites people ask about most. Every line is a real request from this server — a red entry is one that answered with an error or not at all.</p></div>
<div class="pc-actions col"><div class="seg2"><button type="button" data-f="all" aria-pressed="true">All sites</button><button type="button" data-f="issues" aria-pressed="false" id="f-issues">Issues</button></div>
<span class="fine" id="top-count"></span><button class="btn small ghost" type="button" id="top-refresh">{I_REFRESH}Refresh</button></div></div>
<div class="rows" id="top-grid"><div class="skeleton">Sweeping the watchlist…</div></div>
<p class="fine" id="top-updated" style="margin-top:14px">A snapshot, not continuous uptime monitoring.</p>
</div></div></details>
<details class="nl-d" id="online-gaming"><summary>Online gaming</summary><div class="nl-dbody">
<div class="sec-head"><span class="eyebrow"><i></i>Games &amp; services</span><h2>Online gaming<span class="dot">.</span></h2>
<p class="lead">Is the game down, or is it your connection? Search a service or browse by type.</p></div>
<div class="tools"><div class="field" style="flex:1;min-width:240px;max-width:420px">{I_SEARCH}<input id="g-q" type="search" placeholder="Search gaming services" aria-label="Search gaming services" autocomplete="off"></div><span class="fine" id="g-count"></span></div>
<div class="chips" id="g-cats" style="margin-bottom:16px"></div>
<div class="rows" id="g-grid"><div class="skeleton">Loading gaming services…</div></div>
<div class="pager"><button class="btn small ghost" type="button" id="g-prev">Prev</button><button class="btn small ghost" type="button" id="g-next">Next</button></div>
</div></details>
<details class="nl-d" id="recent"><summary>Recently checked websites</summary><div class="nl-dbody">
<div class="sec-head"><span class="eyebrow"><i></i>Live feed</span><h2>Recently checked websites<span class="dot">.</span></h2>
<p class="lead">What people have just checked. A snapshot in time, not a promise of uptime.</p></div>
<div class="card table-wrap"><table class="feed"><thead><tr><th>Website</th><th>Status</th><th>Last checked</th></tr></thead><tbody id="feed-body"><tr><td colspan="3" class="skeleton">Loading recently checked websites…</td></tr></tbody></table></div>
</div></details>
</div></section>
'''
    scripts = '<script src="/assets/worldmap.js"></script>\n<script src="/assets/app.js"></script>\n<script src="/assets/home.js"></script><script src="/assets/live.js"></script>'
    write('index.html', h + body + foot(scripts))

# ---------------------------------------------------------------- login
def login():
    h = head('Sign in — siteupdown.com', 'Sign in or create a free siteupdown.com account to save your checks and build a watchlist.', '/login', noindex=True).replace('{BODYATTR}', ' data-page="login"')
    body = f'''
<section class="page"><div class="wrap narrow">
<div class="lg-head"><h1 id="t-h">Sign in<span class="dot">.</span></h1><p class="lead" id="t-p">Sign in to save your checks and watchlist and take them to any device. The checker is free to use without an account.</p></div>
<p class="card" id="off" hidden>Accounts are not switched on yet. Please check back soon.</p>
<div class="lg-card" id="card">
<div class="seg" hidden id="seg" role="tablist"><button type="button" role="tab" data-v="signin" aria-selected="true">Sign in</button><button type="button" role="tab" data-v="create" aria-selected="false">Create account</button></div>
<div class="stack" id="gwrap"><div id="gbtn"></div><p class="err" id="g-err" role="alert"></p><div class="or">or use your email</div></div>

<form class="stack" id="v-signin" novalidate>
<label class="fl"><span>Email</span><div class="field"><input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div></label>
<label class="fl"><span>Password</span><div class="field"><input name="password" type="password" autocomplete="current-password" placeholder="Your password" aria-label="Password" required></div></label>
<button class="btn block" type="submit"><span>Sign in</span></button><p class="err" role="alert"></p>
<div class="links"><a href="#" data-go="forgot">Forgot your password?</a></div><p class="alt">New here? <a href="#" data-go="create">Create an account</a></p></form>

<form class="stack" id="v-create" hidden novalidate>
<label class="fl"><span>Your name</span><div class="field"><input name="name" type="text" autocomplete="name" placeholder="What should we call you?" aria-label="Name" maxlength="60" required></div></label>
<label class="fl"><span>Email</span><div class="field"><input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div></label>
<label class="fl"><span>Password</span><div class="field"><input name="password" type="password" autocomplete="new-password" placeholder="Password (8+ characters)" aria-label="Password" minlength="8" required></div></label>
<div class="cf-slot" data-cf></div><button class="btn block" type="submit"><span>Create account</span></button><p class="err" role="alert"></p>
<p class="note">By creating an account you agree to our <a href="/legal">legal notice</a> and <a href="/privacy">privacy policy</a>.</p>
<p class="alt">Already have an account? <a href="#" data-go="signin">Sign in</a></p></form>

<form class="stack" id="v-code" hidden novalidate>
<p class="note" style="margin:0">We emailed a six-digit code to <b id="tf-email"></b>. It works for 10 minutes.</p>
<label class="fl"><span>Code</span><div class="field"><input name="code" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="6-digit code" aria-label="Six-digit code" required></div></label>
<button class="btn block" type="submit"><span>Confirm</span></button><p class="err" role="alert"></p>
<p class="alt"><a href="#" data-go="signin">Back to sign in</a></p></form>

<form class="stack" id="v-forgot" hidden novalidate>
<label class="fl"><span>Email</span><div class="field"><input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div></label>
<div class="cf-slot" data-cf></div><button class="btn block" type="submit"><span>Send reset link</span></button><p class="err" role="alert"></p>
<p class="alt"><a href="#" data-go="signin">Back to sign in</a></p></form>

<form class="stack" id="v-reset" hidden novalidate>
<label class="fl"><span>Password</span><div class="field"><input name="password" type="password" autocomplete="new-password" placeholder="New password (8+ characters)" aria-label="New password" minlength="8" required></div></label>
<button class="btn block" type="submit"><span>Save new password</span></button><p class="err" role="alert"></p></form>

<div class="stack" id="v-sent" hidden><p class="note">Check your inbox, and your spam folder just in case.</p><p class="alt"><a href="#" data-go="signin">Back to sign in</a></p></div>
</div></div></section>
'''
    scripts = '<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'
    write('login.html', h + body + foot(scripts))

# ---------------------------------------------------------------- account
def account():
    h = head('Your account — siteupdown.com', 'Your saved checks and account settings.', '/account', noindex=True).replace('{BODYATTR}', ' data-page="account"')
    body = f'''
<section class="page"><div class="wrap" id="acct" hidden>
<div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Your account</span><h2>Account<span class="dot">.</span></h2><p class="note" id="a-since" style="margin:8px 0 0"></p></div></div>
<div class="tabs" id="tabs" role="tablist"><button type="button" role="tab" data-t="checks" aria-selected="true">My checks</button><button type="button" role="tab" data-t="settings" aria-selected="false">Settings</button></div>

<div id="p-checks" class="pad"><div class="tools"><p class="note" style="margin:0">Your last 100 checks, saved while you were signed in. Only you can see them.</p><button class="btn small ghost" type="button" id="clear-checks" hidden>Clear all</button></div>
<div class="list" id="checks-list"><div class="skeleton">Loading your checks…</div></div></div>

<div id="p-settings" hidden class="stack pad" style="max-width:680px">
<form class="card stack" id="f-name" novalidate><h3>Profile</h3><p class="note" style="margin:0">Signed in as <b id="a-email"></b></p>
<div><label class="lbl" for="a-name">Display name</label><div class="field">{I_USER}<input id="a-name" type="text" maxlength="60" autocomplete="name"></div></div>
<button class="btn small" type="submit" style="justify-self:start">Save name</button><p class="err" role="alert"></p></form>
<div id="pw-card"><form class="card stack" id="f-pw" novalidate><h3>Change password</h3>
<div class="field">{I_LOCK}<input name="cur" type="password" autocomplete="current-password" placeholder="Current password" aria-label="Current password"></div>
<div class="field">{I_LOCK}<input name="nw" type="password" autocomplete="new-password" placeholder="New password (8+)" aria-label="New password" minlength="8"></div>
<button class="btn small" type="submit" style="justify-self:start">Change password</button><p class="err" role="alert"></p></form></div>
<div class="card stack" id="tf-card"><h3>Two-step sign-in</h3><p class="note" style="margin:0" id="tf-state">Add a second lock: after your password we email you a six-digit code.</p>
<button class="btn small" type="button" id="tf-btn" style="justify-self:start">Turn on</button>
<form class="stack" id="tf-form" hidden novalidate><div class="field">{I_LOCK}<input name="code" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="6-digit code from your email" aria-label="Six-digit code"></div>
<button class="btn small" type="submit" style="justify-self:start">Confirm</button><p class="err" role="alert"></p></form></div>
<div class="card stack"><h3>Reset my data</h3><p class="note" style="margin:0">Clears your saved checks and your watchlist. Your account stays.</p><button class="btn small ghost" type="button" id="reset-data" style="justify-self:start">Reset my data</button></div>
<div class="card stack danger-zone"><h3>Delete account</h3><p class="note" style="margin:0">Permanently deletes your account and everything saved with it. This cannot be undone.</p>
<button class="btn small danger" type="button" id="del-open" style="justify-self:start">Delete my account</button>
<form class="stack" id="del-form" hidden novalidate><div class="field">{I_LOCK}<input name="confirm" type="text" placeholder="Type DELETE to confirm" aria-label="Type DELETE to confirm" autocomplete="off"></div>
<div id="del-pw-wrap"><div class="field">{I_LOCK}<input name="password" type="password" placeholder="Your password" aria-label="Your password" autocomplete="current-password"></div></div>
<button class="btn small danger" type="submit" style="justify-self:start">Permanently delete</button><p class="err" role="alert"></p></form></div>
</div>
</div></div></section>
'''
    scripts = '<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'
    write('account.html', h + body + foot(scripts))

# ---------------------------------------------------------------- monitor
def monitor():
    h = head('Monitor your websites — siteupdown.com', 'Build a personal watchlist and see at a glance which of your websites are up.', '/monitor').replace('{BODYATTR}', ' data-page="monitor"')
    body = f'''
<section class="page"><div class="wrap">
<div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Your watchlist</span><h1>Monitor<span class="dot">.</span></h1>
<p class="lead">Keep an eye on the websites you care about. We re-check them every few minutes, keep their uptime history, and email you if one goes down.</p></div></div>
<div class="pad">
<div class="card" id="m-out" hidden><h3 style="margin-bottom:8px">Sign in to build your watchlist</h3><p class="note">A free account lets you save up to 25 sites and see their status at a glance. The checker on the home page stays free without one.</p>
<div class="row-actions" style="margin-top:14px"><a class="btn" href="/login?next=%2Fmonitor"><span>Sign in</span>{I_ARROW}</a><a class="btn ghost" href="/login?next=%2Fmonitor#create">Create account</a></div></div>
<div id="m-in" hidden>
<form class="stack" id="m-add" novalidate style="max-width:640px;margin-bottom:22px"><label class="lbl" for="m-input">Add a website</label>
<div class="row-actions" style="flex-wrap:nowrap"><div class="field" style="flex:1">{I_GLOBE}<input id="m-input" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="example.com" maxlength="300"></div><button class="btn" type="submit"><span>Add</span></button></div><p class="err" id="m-err" role="alert"></p></form>
<div class="tools"><span class="fine" id="m-count"></span><span class="fine">Updates every minute while this page is open.</span></div>
<div class="list" id="m-list"><div class="skeleton">Loading your watchlist…</div></div></div>
<div class="card" id="xc-card" style="margin-top:26px" hidden><h3 style="margin-bottom:6px">Extra checks</h3>
<p class="note">Go beyond &ldquo;is it up?&rdquo;. Check that a word is still on a page (for example your shop&rsquo;s &ldquo;Add to basket&rdquo; button), or that a port such as email or a database is answering. These run every minute, and we alert you after two fails in a row, the same way as your watchlist.</p>
<div class="list" id="xc-list" style="margin:14px 0"></div>
<form class="stack" id="xc-form" novalidate style="max-width:640px">
<div class="field"><select id="xc-kind" aria-label="Check type"><option value="kw">A word must be on the page</option><option value="port">A port must be open</option></select></div>
<div class="field"><input id="xc-host" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="example.com" maxlength="253" aria-label="Website address"></div>
<div class="field" id="xc-wordf"><input id="xc-word" type="text" autocomplete="off" placeholder="Word or phrase on the page" maxlength="100" aria-label="Word or phrase"></div>
<div class="field" id="xc-portf" hidden><select id="xc-port" aria-label="Port"><option value="443">443 &ndash; secure website</option><option value="80">80 &ndash; website</option><option value="22">22 &ndash; SSH</option><option value="25">25 &ndash; email (SMTP)</option><option value="465">465 &ndash; email (SMTPS)</option><option value="587">587 &ndash; email (submission)</option><option value="993">993 &ndash; email (IMAP)</option><option value="995">995 &ndash; email (POP3)</option><option value="143">143 &ndash; IMAP</option><option value="110">110 &ndash; POP3</option><option value="53">53 &ndash; DNS</option><option value="21">21 &ndash; FTP</option><option value="3306">3306 &ndash; MySQL</option><option value="5432">5432 &ndash; PostgreSQL</option><option value="8080">8080 &ndash; alternate web</option><option value="8443">8443 &ndash; alternate secure web</option></select></div>
<div><button class="btn small" type="submit"><span>Add check</span></button> <span class="fine" id="xc-count"></span></div>
<p class="err" id="xc-err" role="alert"></p></form>
<p class="fine">Word checks read the first 600 KB of the page and ignore capital letters. Only check sites and servers you own or look after.</p></div>
<div class="card" id="ch-card" style="margin-top:26px" hidden><h3 style="margin-bottom:6px">Alert channels</h3>
<p class="note">We always email you. You can also get an instant message in Telegram, Slack or Discord when a site on your watchlist goes down or comes back up. Use the Alerts button on each site to switch alerts on or off.</p>
<div class="list" id="ch-list" style="margin:14px 0"></div>
<div id="ch-tg-box" hidden><button class="btn small" type="button" id="ch-tg"><span>Connect Telegram</span></button> <a class="btn small ghost" id="ch-tg-open" href="#" target="_blank" rel="noopener" hidden><span>Open Telegram</span></a> <span class="fine" id="ch-tg-msg"></span></div>
<form class="stack" id="ch-wh" novalidate style="max-width:640px;margin-top:16px"><label class="lbl" for="ch-url">Slack or Discord webhook address</label>
<div class="row-actions" style="flex-wrap:nowrap"><div class="field" style="flex:1"><input id="ch-url" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="https://hooks.slack.com/services/..." maxlength="300" aria-label="Webhook address"></div><button class="btn small" type="submit"><span>Add</span></button></div>
<p class="err" id="ch-err" role="alert"></p></form>
<details class="faq-mini"><summary>How do I get a webhook address?</summary>
<p><b>Slack:</b> in Slack, open the Apps menu, add &ldquo;Incoming Webhooks&rdquo;, pick a channel and copy the Webhook URL. <b>Discord:</b> open the channel settings, choose Integrations, then Webhooks, create one and copy its URL. Paste the address above and we will send a test message straight away.</p></details>
<p class="note">Webhook addresses are private, so keep them to yourself. You can remove a channel at any time, and deleting your account removes them all.</p></div>
</div></div></div></section>
'''
    scripts = '<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'
    write('monitor.html', h + body + foot(scripts))

# ---------------------------------------------------------------- speed test
def speed():
    h = head('Website speed test — siteupdown.com', 'Free website speed test: how fast a page responds and loads, with a timing breakdown, page weight, a grade and tips.', '/speed').replace('{BODYATTR}', ' data-page="speed"')
    body = f'''
<section class="page"><div class="wrap">
<div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Speed test</span><h1 style="margin:10px 0 6px">How fast is it<span class="dot">?</span></h1>
<p class="lead">Loads a page three times from our server and shows where the time goes: finding the server, connecting, securing the connection, waiting, and downloading.</p></div></div>
<div class="pad">
<form class="stack" id="sp-form" novalidate style="max-width:640px;margin-bottom:22px"><label class="lbl" for="sp-input">Website address</label>
<div class="row-actions" style="flex-wrap:nowrap"><div class="field" style="flex:1">{I_GLOBE}<input id="sp-input" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="example.com" maxlength="300"></div><button class="btn" id="sp-btn" type="submit"><span>Test speed</span></button></div><p class="err" id="sp-err" role="alert"></p></form>
<div id="sp-out" hidden></div>
</div></div></div><div class="prose" style="margin-top:34px;max-width:760px">
<h2>What this speed test measures</h2>
<p>The test loads the page you enter three times from our server and reports the middle result, so one slow moment does not skew the answer. It breaks the total into the stages every web request goes through, which shows you <em>where</em> the time is going rather than just how long it took.</p>
<ul>
<li><b>Finding the server (DNS).</b> Turning the name into an address. Slow DNS usually points to the domain&rsquo;s name servers.</li>
<li><b>Connecting.</b> Opening a connection to the server. This depends mostly on distance between us and the site.</li>
<li><b>Securing the connection (TLS).</b> The HTTPS handshake that encrypts traffic.</li>
<li><b>Waiting for the first byte.</b> How long the site takes to start replying. This is the best sign of how busy or slow the server or application is.</li>
<li><b>Downloading.</b> How long the page itself takes to arrive, which grows with page weight.</li>
</ul>
<h2>How to read your grade</h2>
<p>Under about 300&nbsp;ms to the first byte is quick, 300 to 800&nbsp;ms is fine for most sites, and above that it is worth looking at hosting, caching or heavy pages. Our measurement is from one data centre, so someone far away will see longer times. For a wider view use the <a href="/outage-map">outage map</a>, which shows response times from places around the world, and read <a href="/help/speed-up-your-website">how to speed up your website</a> and <a href="/help/what-is-a-good-response-time">what is a good response time</a>.</p>
<p class="note">This is a server-side test of one page. It does not run scripts like a full browser lab test, so it will not match tools that measure rendering. Use it as a quick, honest first check.</p>
</div>
</section>
'''
    write('speed.html', h + body + foot('<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'))

# ---------------------------------------------------------------- status page
def status():
    h = head('Website status — siteupdown.com', 'Live status, uptime and recent outages for a website, checked every few minutes by siteupdown.com.', '/status', noindex=True).replace('{BODYATTR}', ' data-page="status"')
    body = f'''
<section class="page"><div class="wrap">
<div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Status page</span><h1 id="st-h" style="margin:10px 0 6px">Website status<span class="dot">.</span></h1><p class="lead" id="st-p">Loading…</p></div><div id="st-pill"></div></div>
<div class="pad" id="st-body"><div class="skeleton">Loading status…</div></div>
</div></div></section>
'''
    write('status.html', h + body + foot('<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'))

# ---------------------------------------------------------------- legal pages
SEO_PROSE = {'About': ('About siteupdown.com: a free, independent website checker', 'About siteupdown.com: a free, independent website status, speed and uptime checker that tells you whether a site is down for everyone or just you.'),
 'Editorial policy': ('Editorial and advertising policy | siteupdown.com', 'How siteupdown.com writes its guides, checks its facts, corrects mistakes and keeps advertising separate from the results it shows.'),
 'Privacy': ('Privacy policy: how siteupdown.com handles your data', 'How siteupdown.com handles website checks, accounts, cookies and your data, in plain English, including what we keep and what we never collect.'),
 'Legal notice': ('Legal notice and terms of use | siteupdown.com', 'Legal notice and terms of use for siteupdown.com, an independent website status checker. Who we are, how to use the service and how to contact us.'),
 'Contact': ('Contact siteupdown.com: feedback, reports and questions', 'Get in touch with siteupdown.com: send feedback, report a problem, suggest a site to add or ask about your data. We read every message.')}
def prose(name, title, desc, path, inner):
    st, sd = SEO_PROSE.get(title, (title + ' — siteupdown.com', desc))
    h = head(st, sd, path).replace('{BODYATTR}', '')
    body = f'<section class="page"><div class="wrap prose"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 20px">{title}<span class="dot">.</span></h1>{inner}<p style="margin-top:34px"><a href="/">&larr; Back to the website checker</a></p></div></section>'
    write(name, h + body + foot('<script src="/assets/app.js"></script>'))

def static_pages():
    prose('about.html', 'About', 'About siteupdown.com: a free, independent website status, speed and uptime checker.', '/about', '''
<p class="lead">siteupdown.com answers one question quickly: is this website down for everyone, or is it just you?</p>
<h2>What we do</h2>
<p>When a page will not load, it is hard to tell whether the site is broken or something on your side is. You paste the address, and we load it from our own server and from fifteen probes in different countries at the same moment. If every probe reaches it, the site is up and the problem is probably your network, DNS, browser or device. If most fail, it is down for everyone.</p>
<h2>More than a status check</h2>
<p>Every check also shows the SSL certificate, DNS records, redirects and the domain&rsquo;s registration expiry. The <a href="/speed">speed test</a> times where a page&rsquo;s load goes. With a free account you can keep a <a href="/monitor">watchlist</a>, see uptime history and get an email when a site goes down or comes back, and each monitored site has a public status page.</p>
<h2>How we check, and how we try to be fair</h2>
<p>We would rather say &ldquo;not sure&rdquo; than be wrong. Here is what happens when you check a site:</p>
<ul>
<li><b>Our own server</b> asks the site for its page. If the address gets no reply, we also try the other form (with or without &ldquo;www&rdquo;), because some sites only answer on one.</li>
<li><b>Fifteen probes</b> in different countries ask the same thing at the same moment, so you can see whether it is down for everyone or only in some places.</li>
<li><b>We call a site down only on real evidence</b>, such as repeated server errors, or a site that was answering and then stops. Before we record an outage we ask probes in other countries as well, and if any of them can reach it, it is not counted as down.</li>
<li><b>Silence is not proof.</b> Some large sites quietly ignore automated checks. When nothing answers and we have not seen the site working lately, we say &ldquo;no answer&rdquo; and &ldquo;we can&rsquo;t be sure&rdquo;, and give you a link to try the site yourself, instead of showing a false red alert.</li>
<li><b>We use honest checks.</b> Our checker says who it is, and we do not disguise it as a browser to get past a site&rsquo;s protection.</li>
</ul>
<p>The live graph samples a site about every ten seconds while someone is watching it, and we keep daily records so you can see the last 24 hours, 7 days and 12 months, with a written summary of recent outages. Problem reports from visitors show what real people are seeing, and every result is a snapshot of one moment, which we say so.</p>
<h2>Independent</h2>
<p>siteupdown.com is not affiliated with the websites, games or services it checks. Regional probes run on the public <a href="https://globalping.io" rel="noopener">Globalping</a> network. The site is supported by advertising, so it stays free to use.</p>
''' + __import__('pages_extra').ABOUT_MORE)
    __import__('pages_extra').build(prose, head, write, foot, html, _json, _re)
    prose('editorial-policy.html', 'Editorial policy', 'How siteupdown.com writes, checks, corrects and funds its content.', '/editorial-policy', '''
<p class="lead">This page explains how the content on siteupdown.com is produced, how we keep it accurate, and how advertising fits in. We want you to be able to trust what you read here.</p>
<h2>What we publish</h2>
<p>siteupdown.com has three kinds of content. <b>Live results</b> come from our own automated checks of the sites on our public lists, repeated through the day from our own server and from probes around the world. <b>Guides</b> in the <a href="/help/">Help centre</a> explain how the internet works and how to fix common problems, such as DNS errors, certificate warnings and slow connections. <b>Site pages</b> (for example the &ldquo;Is YouTube down?&rdquo; pages) combine a live status with plain background on the service and recent history.</p>
<h2>How we write and check</h2>
<ul>
<li><b>Written for people.</b> Guides are written by the siteupdown.com team in plain English, from practical experience of running website checks and monitoring.</li>
<li><b>Numbers come from our own data.</b> Uptime figures, outage counts and response times are calculated from our own checks. We say how they are measured on <a href="/how-we-check">How we check</a> and we label them as guides, not official figures.</li>
<li><b>Honest checks.</b> Our checker identifies itself and never pretends to be a browser to get past a site&rsquo;s protection. If a site blocks automated visitors we say so instead of calling it down.</li>
<li><b>Dated and reviewed.</b> Guides show when they were last updated, and we review them when something they describe changes.</li>
</ul>
<h2>Corrections</h2>
<p>If you spot a mistake or a result that looks wrong, tell us through the <a href="/contact">contact form</a>. We check every report, fix confirmed errors promptly and update the &ldquo;last updated&rdquo; date on the page.</p>
<h2>Independence</h2>
<p>siteupdown.com is not affiliated with, endorsed by or paid by the websites, games or services it checks. A company cannot pay to change its status, its ranking or what we write about it.</p>
<h2>How advertising works</h2>
<p>The site is free to use and is supported by advertising. Adverts are always clearly separate from our results and guides, and never look like a status result or a button. Advertising cookies are optional and are only used if you allow them in <a href="/privacy">our cookie choices</a>. We do not sell personal data. Advertisers do not see or influence our content.</p>
<h2>Contact</h2>
<p>Questions about this policy? Write to <a href="mailto:hello@siteupdown.com">hello@siteupdown.com</a> or use the <a href="/contact">contact page</a>.</p>
''')
    prose('privacy.html', 'Privacy', 'How siteupdown.com handles checks, accounts, cookies and your data.', '/privacy', '''
<p>We keep this short and plain. siteupdown.com checks whether websites are reachable. We collect as little as we can to do that.</p>
<h2>Website checks</h2>
<p>When you check an address, our server fetches it. We store only the hostname, the result (status, HTTP code, response time) and the time in a public &ldquo;recently checked&rdquo; list. We do not publish who checked it. Regional checks send the hostname you entered to the Globalping probe network, which runs the request from machines around the world.</p>
<p>Share links keep a copy of the result so it can be shown to whoever you send it to. They expire after 30 days.</p>
<h2>Accounts</h2>
<p>Signing in is optional. If you create an account (with email and password, or with Google) we store your email address, display name and a hashed password (we never see or store your password itself). While you are signed in we also save your checks and your watchlist, and they are private to you. You can reset your data or delete your account at any time from the Account page; deleting removes everything saved with it.</p>
<h2>Extra checks</h2>
<p>If you add an extra check (a word that must appear on a page, or a port that must answer), we store the website address, the word or port, and the latest result, so we can check it every minute and email you if it fails. You can remove a check at any time on the Monitor page, and deleting your account removes them all.</p>
<h2>Browser extension</h2>
<p>The siteupdown.com browser extension reads the address of the tab you are on only when you click its toolbar button. It sends just the website name (for example example.com, never the full page address, search terms or page content) to siteupdown.com so we can check whether the site is up. It does not read or store your browsing history, and it does not run in the background. If you are signed in to siteupdown.com in the same browser, the extension uses that sign-in to add a site to your watchlist when you ask it to. Nothing is sold or shared for advertising.</p>
<h2>Alert channels</h2>
<p>If you connect Telegram, Slack or Discord alerts, we store the Telegram chat number or the webhook address you give us, so we can send you a short message when a site on your watchlist goes down or comes back up. These messages pass through Telegram, Slack or Discord, which have their own privacy policies. You can remove a channel at any time on the Monitor page, send /stop to our Telegram bot, or delete your account to remove them all.</p>
<p>If you sign in with Google, Google tells us your name and verified email address. We do not get access to anything else in your Google account.</p>
<h2>Problem reports</h2>
<p>After a check, and on the &ldquo;Is it down?&rdquo; pages, you can report a problem with a site. A report stores the site, the type of problem, the time, and a one-way hash of your network address, which is used only to limit repeat reports and is erased after two days. The report itself (site, type, time and the country you are in, worked out from your network or your device&rsquo;s time zone, with nothing that identifies you) is kept for up to three years so the report history can be shown. We do not ask for your name or email address for reports, and reports are shown as anonymous counts and as a list of the latest reports (the site, the type of problem, how long ago, and the country when several people reported from it), with no personal details.</p>
<p><strong>Local outage map (optional).</strong> When you send a report you can tick a box to add your approximate area. If you do, your browser asks for permission first. We then store only your position rounded to one decimal place of latitude and longitude, which is roughly a 10 km square, along with the report, and never your exact location. Reports with an area are shown on the local outage map only as counts in cells of about 20 km, never one by one. The local map loads its code from cdnjs.cloudflare.com and its map pictures from OpenStreetMap, only when you press &ldquo;Show the local map&rdquo;, so those services see your network address and the area you are looking at, as with any website.</p>
<p><strong>Outage history.</strong> Each day we keep a permanent record of how many reports each site received by type (for example website not loading or cannot log in), how many said it worked again, and how many outages our own checks detected, so anyone can read what happened on a past date. Only counts are kept. The record never contains who reported, network addresses or locations.</p>
<p><strong>Visit counts.</strong> To see how the site is used, we count page views without cookies and without keeping anyone&rsquo;s address. For each view we keep only the day, the page, the country (from the network or your time zone), the type of device, and the site you came from, as a number. To count visitors once a day, we turn your address and browser into a code that changes every day and is deleted after two days, and cannot be turned back into your address. We do not count anyone who declines analytics in the cookie settings or whose browser sends Do Not Track.</p>
<h2>Cookies and storage</h2>
<p>We use essential storage to run the site: your theme, your cookie choice, your recent searches (kept on your device) and a sign-in cookie if you are signed in. Analytics and advertising cookies are optional and off until you allow them in &ldquo;Cookie settings&rdquo;. Google&rsquo;s advertising script is only loaded if you allow advertising cookies.</p>
<h2>Advertising</h2>
<p>siteupdown.com is supported by advertising. Third-party vendors, including Google, may use cookies to serve ads based on a visitor&rsquo;s previous visits to this and other websites. Google&rsquo;s use of advertising cookies enables it and its partners to serve ads based on visits to this site and/or other sites on the internet. Advertising cookies are only used if you allow them in our cookie choices. You can opt out of personalised advertising at <a href="https://www.google.com/settings/ads" rel="noopener">Google Ads Settings</a>, or at <a href="https://www.aboutads.info" rel="noopener">aboutads.info</a>.</p>
<h2>Technical logs</h2>
<p>To keep the service safe from abuse we briefly keep a one-way hash of the visitor&rsquo;s network address for rate limiting. It cannot be turned back into an address and is removed within a day.</p>
<h2>Results are snapshots</h2>
<p>A check shows what happened at one moment. Timeouts, blocked requests and DNS problems are not reported as confirmed downtime.</p>
<h2>Contact</h2>
<p>Questions about your data? Use the <a href="/contact">contact page</a>.</p>''')
    prose('legal.html', 'Legal notice', 'Legal notice for siteupdown.com.', '/legal', '''
<p>siteupdown.com is an independent website status checker. It is not affiliated with, endorsed by or sponsored by any of the websites, games or services it checks, and all names and trademarks belong to their owners.</p>
<h2>No guarantees</h2>
<p>Results are provided as a convenience, as a snapshot at the moment of the check, and without any warranty. A result does not prove that a site is up or down for everyone, and should not be used as a service-level measurement or for critical decisions. We are not liable for loss arising from reliance on a result.</p>
<h2>Acceptable use</h2>
<p>Please do not use the checker to attack, overload or probe other people&rsquo;s systems. We limit how often one visitor can run checks, and we only fetch public web addresses on the standard web ports.</p>
<h2>Third parties</h2>
<p>The internet speed test sends test data between your browser and Cloudflare\'s public speed-test servers, so Cloudflare sees your address as it would for any website you visit. We do not store your speed results.</p>
<p>The what-is-my-IP page and the game ping test also run in your browser, and talk to Cloudflare and to public cloud servers, so those services see your address as any website would. We do not store your address or results. If you turn on browser notifications for a site, we store your browser\'s notification address and the site you chose, so we can send you an alert when it goes down or comes back. Turn it off on the same page and we delete it, and we also delete it automatically if your browser stops accepting notifications.</p>
<p>Regional probes run on the public <a href="https://globalping.io" rel="noopener">Globalping</a> network. Sign-in with Google uses Google&rsquo;s own sign-in service, and the site&rsquo;s fonts (Space Grotesk and JetBrains Mono) are loaded from Google Fonts.</p>
<h2>Content</h2>
<p>Site names shown in lists are used only to identify the services being checked.</p>''')
    prose('business.html', 'For business', 'siteupdown.com for business: planned monitoring for teams and companies, with status pages, more check types and shared alerts. Register your interest.', '/business', '''
<p class="lead">Free checks for everyone today. A paid plan for businesses is planned, and we would like to build it around what you actually need.</p>
<h2>What we are planning</h2>
<ul>
<li><b>Public status pages</b> for your own customers, showing live uptime for your site.</li>
<li><b>More check types</b>: website, keyword, port, SSL and domain expiry, from more locations.</li>
<li><b>Shared team alerts</b> by email, Telegram, Slack and Discord, plus SMS and WhatsApp.</li>
<li><b>Longer history and reports</b> you can share with clients.</li>
</ul>
<p>Nothing here is on sale yet. Today you can already <a href="/monitor">watch sites for free</a> with instant alerts and extra checks. Tell us what a business plan would need and we will email you once, when it is ready.</p>
<form id="cf" class="cform" novalidate>
<select id="cf-topic" hidden><option value="business" selected>business</option></select>
<input id="cf-site" type="hidden" value="">
<div class="cf-two">
<div><label for="cf-name">Your name <span class="opt">(optional)</span></label><div class="field"><input id="cf-name" type="text" maxlength="80" autocomplete="name"></div></div>
<div><label for="cf-email">Your email</label><div class="field"><input id="cf-email" type="email" maxlength="200" autocomplete="email" required></div></div>
</div>
<label for="cf-msg">What would you want from a business plan?</label>
<textarea id="cf-msg" rows="6" maxlength="4000" required placeholder="For example: how many sites you run, what you would monitor, and who needs the alerts."></textarea>
<div class="cf-hp" aria-hidden="true"><label>Leave this empty <input id="cf-hp" type="text" tabindex="-1" autocomplete="off"></label></div>
<p id="cf-err" class="cf-err" role="alert" hidden></p>
<p><button class="btn" type="submit" id="cf-btn"><span>Register interest</span></button></p>
<p class="note">We only use your email to reply about this. See our <a href="/privacy">privacy policy</a>.</p>
</form>
<div id="cf-ok" class="cf-ok" hidden role="status"><h2>Thank you</h2><p>We have your details and will email you once when the business plan is ready.</p></div>
<script src="/assets/contact.js"></script>''')
    prose('contact.html', 'Contact', 'Get in touch with siteupdown.com: send feedback, report a problem, suggest a site or ask about your data.', '/contact', '''
<p class="lead">Questions, feedback or something not working? Tell us below and we will reply by email.</p>
<form id="cf" class="cform" novalidate>
<label for="cf-topic">What is this about?</label>
<div class="field"><select id="cf-topic" required>
<option value="">Choose a topic&hellip;</option>
<option value="feedback">General feedback</option>
<option value="issue">Report a problem with the site</option>
<option value="wrong">A check gave the wrong result</option>
<option value="addsite">Suggest a site to add</option>
<option value="account">Account or sign-in help</option>
<option value="complaint">Complaint</option>
<option value="data">Data or privacy request</option>
<option value="business">Advertising or business enquiry</option>
<option value="other">Something else</option>
</select></div>
<div class="cf-two">
<div><label for="cf-name">Your name <span class="opt">(optional)</span></label><div class="field"><input id="cf-name" type="text" maxlength="80" autocomplete="name"></div></div>
<div><label for="cf-email">Your email</label><div class="field"><input id="cf-email" type="email" maxlength="200" autocomplete="email" required></div></div>
</div>
<div id="cf-siterow" hidden><label for="cf-site">Website address <span class="opt">(optional)</span></label><div class="field"><input id="cf-site" type="text" maxlength="253" placeholder="example.com" autocapitalize="none" autocorrect="off" spellcheck="false"></div></div>
<label for="cf-msg">Your message</label>
<textarea id="cf-msg" rows="6" maxlength="4000" required></textarea>
<div class="cf-hp" aria-hidden="true"><label>Leave this empty <input id="cf-hp" type="text" tabindex="-1" autocomplete="off"></label></div>
<p id="cf-err" class="cf-err" role="alert" hidden></p>
<p><button class="btn" type="submit" id="cf-btn"><span>Send message</span></button></p>
<p class="note">We only use your email to reply. See our <a href="/privacy">privacy policy</a>. Prefer email? Write to <a href="mailto:hello@siteupdown.com">hello@siteupdown.com</a>.</p>
</form>
<div id="cf-ok" class="cf-ok" hidden role="status"><h2>Message sent</h2><p>Thanks, we have it. We will reply to the email address you gave, usually within a few days.</p></div>
<h2>What to expect</h2>
<p>siteupdown.com is run by a small independent team. We read every message and usually reply within a few days. If you are reporting that a check gave the wrong result, include the website address and roughly when you ran it, which helps us reproduce it. For account or data requests, use the topic menu so the message reaches the right place. We never ask for your password and will not ask you to pay anything through this form.</p>
<h2>Other ways to reach us</h2>
<p>Email <a href="mailto:hello@siteupdown.com">hello@siteupdown.com</a>. For how we work and how we correct mistakes, read our <a href="/editorial-policy">editorial policy</a>, and for what we store about you read the <a href="/privacy">privacy policy</a>.</p>
<script src="/assets/contact.js"></script>''')
    h = head('Admin — siteupdown.com', 'Admin area.', '/admin', noindex=True).replace('{BODYATTR}', '')
    write('admin.html', h + '''<section class="page adm-page"><div class="wrap"><div id="adm-root"><p class="lead">Loading&hellip;</p></div></div></section>''' + foot('<script src="/assets/app.js"></script><script src="/assets/admin.js"></script>'))
    h = head('Page not found — siteupdown.com', 'That page could not be found.', '/404', noindex=True).replace('{BODYATTR}', '')
    write('404.html', h + '<section class="page"><div class="wrap narrow center"><img class="nl-404mon" src="/assets/nl-monster-blue.png" alt="" width="800" height="800"><span class="eyebrow"><i></i>Error 404</span><h1 style="margin:14px 0">Not found<span class="dot">.</span></h1><p class="lead">We checked everywhere. This page is down for everyone.</p><p style="margin-top:24px"><a class="btn" href="/"><span>Back to the checker</span></a></p></div></section>' + foot('<script src="/assets/app.js"></script>'))
    for code, ttl, big, msg in (('403', 'Access denied', 'No entry', 'You do not have permission to open this page.'), ('500', 'Something went wrong', 'Oops', 'That one is on us, not you. Please try again in a minute.')):
        h = head('%s — siteupdown.com' % ttl, 'An error occurred.', '/' + code, noindex=True).replace('{BODYATTR}', '')
        write(code + '.html', h + '<section class="page"><div class="wrap narrow center"><img class="nl-404mon" src="/assets/nl-monster-blue.png" alt="" width="800" height="800"><span class="eyebrow"><i></i>Error %s</span><h1 style="margin:14px 0">%s<span class="dot">.</span></h1><p class="lead">%s</p><p style="margin-top:24px"><a class="btn" href="/"><span>Back to the checker</span></a></p></div></section>' % (code, big, msg) + foot('<script src="/assets/app.js"></script>'))



# ---------------------------------------------------------------- "Is X down?" pages
import site_pages as SP
SENS = {'finance', 'payments', 'trading', 'government', 'betting'}      # banks, payments, trading, government, betting
HIDDEN = {n for n, _, c, _ in SP.SITES[SP.CORE:] if c in SENS}       # extended pages in those categories: kept, but not offered to search engines or listed publicly

def tile(name, host):
    return ''  # letter tiles removed; the name speaks for itself

def site_pages_build():
    hosts = [h for _, h, _, _ in SP.SITES]
    assert len(hosts) == len(set(hosts)), 'duplicate host in SITES'
    slugs = [SP.slug(n) for n, _, _, _ in SP.SITES]
    assert len(slugs) == len(set(slugs)), 'duplicate slug in SITES'
    # the list the PHP side reads (api/_ files are blocked from the web by .htaccess)
    with open(os.path.join(ROOT, 'api', '_sitepages.json'), 'w') as f:
        _json.dump({h: dict({'name': n, 'page': SP.page_path(n), 'cat': c}, **({'t': 2} if i >= SP.CORE else {}), **({'app': [list(x) for x in SP.APPS[n]]} if n in SP.APPS else {})) for i, (n, h, c, _) in enumerate(SP.SITES)}, f, separators=(',', ':'))
    kinds = ''.join('<button type="button" class="rk" data-kind="%s">%s</button>' % (k, l) for k, l in SP.KIND_LABELS)
    for name, host, cat, blurb in SP.SITES:
        n = html.escape(name); hh = html.escape(host)
        path = SP.page_path(name)
        catname, tips = SP.CATS[cat]
        title = 'Is %s down? Live status and outage reports' % name
        desc = 'Is %s down right now? Live status from our servers, response time, uptime and problems reported by other visitors.' % name
        faqs = [
            ('Is %s down right now?' % name, 'Look at the live status box at the top of this page. It shows the result of our latest automatic check of %s, repeated every few minutes. If it says the site is up but things still fail for you, the problem is probably on your side or limited to one feature or region.' % host),
            ('Why is %s not working for me when it works for others?' % name, 'A site can fail for some people and not others because of DNS caching, regional servers, your internet provider, a firewall or VPN, or a problem with your device or app. Our guide on why a website can be down for some people and not others explains how to tell which one it is.'),
            ('How do I report a problem with %s?' % name, 'Use the report buttons on this page and choose what is going wrong. Reports are anonymous and unverified, and each visitor can report each problem once every 30 minutes. They are shown as a chart so you can see whether other people are having the same problem.'),
            ('How does siteupdown.com check %s?' % name, 'Our server loads %s every few minutes, the way a browser would, and records the response code and how long it took. A site is only called down after two server errors in a row. Our page on how the checks work has the details.' % host),
        ]
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Is it down?", "item": SITE + "/is-it-down/"},
                {"@type": "ListItem", "position": 3, "name": 'Is %s down?' % name, "item": SITE + path}]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]}
        extra = '<script type="application/ld+json">' + _json.dumps(ld) + '</script>'
        h = head(title + ' — siteupdown.com', desc, path, extra, noindex=(name in HIDDEN)).replace('{BODYATTR}', '')
        same = [(n2, SP.page_path(n2)) for n2, h2, c2, _ in SP.SITES if c2 == cat and n2 != name][:8]
        rel = ''.join('<li><a href="%s">Is %s down?</a></li>' % (pth, html.escape(n2)) for n2, pth in same)
        tipsli = ''.join('<li>%s</li>' % t for t in tips)
        faqh = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(a)) for q, a in faqs)
        body = (
            '<section class="page"><div class="wrap prose sitepage" data-sp="site" data-host="%s" data-name="%s"%s>' % (hh, n, ' data-app="1"' if name in SP.APPS else '') +
            '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/is-it-down/">Is it down?</a> / %s</nav>' % n +
            '<h1 class="sp-h1" style="margin:14px 0 18px">%s<span>Is %s down?</span></h1>' % (tile(name, host), n) +
            '<div class="sp-card" id="sp-status" aria-live="polite"><div class="sp-head"><span class="sp-pill" id="sp-pill">Checking…</span><span class="sp-msg" id="sp-msg">Loading the latest result for %s.</span></div>' % hh +
            '<div class="sp-stats" id="sp-stats"></div><noscript><p>Turn on JavaScript to see the live status.</p></noscript></div>' +
            ('<div class="sp-card" id="sp-app" hidden><div class="sp-rhead"><b>%s app servers</b><span class="sp-level">Servers the app uses</span></div><ul class="sp-svc" id="sp-svc"></ul>'
             '<p class="note">These are the servers the %s app talks to. If they answer, the servers are reachable, but that does not prove everything inside the app is working, such as messages, feeds or logins. For in-app problems, see what other visitors are reporting below.</p></div>' % (n, n) if name in SP.APPS else '') +
            '<p class="sp-pushrow"><button type="button" class="btn small ghost" id="sp-push" hidden><span>Notify me when %s changes</span></button> <span class="note" id="sp-pushmsg"></span></p>' % n +
            '<div id="lv-slot" data-host="%s"></div>' % hh +
            '<p class="lead" style="margin-top:22px">%s</p>' % blurb +
            '<h2>Are other people having problems with %s?</h2>' % n +
            '<div class="sp-card" id="sp-reports"><div class="sp-rhead"><b id="sp-rtotal">Problem reports</b><span id="sp-rlevel" class="sp-level"></span></div>'
            '<div class="sp-ranges" id="sp-ranges" role="group" aria-label="Time range"><button type="button" class="rg on" data-range="24h" aria-pressed="true">24 hours</button><button type="button" class="rg" data-range="7d" aria-pressed="false">7 days</button><button type="button" class="rg" data-range="30d" aria-pressed="false">30 days</button><button type="button" class="rg" data-range="1y" aria-pressed="false">1 year</button></div><div class="sp-rdate" id="sp-date"></div><div class="sp-chart" id="sp-chart" role="group" aria-label="Problem reports per hour over the last 24 hours"></div>'
            '<div class="sp-axis"><span>24 hours ago</span><span>Now</span></div><p class="sp-rdetail" id="sp-detail">Tap or hover a bar to see what was reported.</p><div class="sp-kinds" id="sp-kinds"></div><h3 class="rf-h">Latest reports</h3><ul class="rf" id="sp-feed"></ul>'
            '<div class="sp-report"><button type="button" class="btn small" id="sp-rbtn"><span>I am having a problem with %s</span></button> <button type="button" class="btn small ghost" id="sp-fix"><span>It is working for me now</span></button>' % n +
            '<div class="sp-rpick" id="sp-rpick" hidden><p>What is going wrong? Pick everything that applies.</p><div class="sp-rbtns">%s</div><label class="rloc"><input type="checkbox"> <span>Also add my approximate area to the local outage map <small>Optional. Your browser will ask first. Rounded to about 10 km, never your exact spot.</small></span></label><p class="sp-rsendrow"><button type="button" class="btn small rsend" disabled><span>Send report</span></button></p></div><p class="sp-rmsg" id="sp-rmsg" role="status"></p></div>' % kinds +
            '<p class="note">Reports are anonymous and unverified, and each visitor can report each problem once every 30 minutes. They show how many people say they are affected, not why. <a href="/outage-history?host=' + hh + '">See what happened on past days</a>.</p></div>' +
            '<div id="sp-deep" hidden><h2>How reliable is %s?</h2><div class="sp-card sp-deepc" id="sp-deepc"></div></div>' % n +
            '<h2>If %s is not loading for you</h2><ul>%s</ul>' % (n, tipsli) +
            '<p>Still stuck? Work through our <a href="/help/website-not-loading-checklist">website not loading checklist</a>, or read <a href="/help/down-for-some-people-not-others">why a site can be down for some people and not others</a>.</p>'
            '<div class="sp-card" id="sp-world" hidden><div class="sp-rhead"><b>Seen from around the world</b><span class="sp-level" id="sp-wwhen"></span></div><p id="sp-wsum" class="note"></p><div class="sp-wmap"><svg id="sp-wsvg" role="img" aria-label="World map of where this site was reached" preserveAspectRatio="xMidYMid meet"></svg></div><div class="rt-wrap"><table class="rt" id="sp-wtab"><thead><tr><th>Place</th><th>Result</th><th>Time</th></tr></thead><tbody></tbody></table></div><p class="note">A snapshot from probes on the public Globalping network, refreshed every few hours. It shows whether the site answers from other countries, not what every visitor sees.</p></div>' +
            '<h2>Check %s from fifteen places</h2><p>This page shows our latest scheduled check. To test %s right now from our server and from fifteen countries, run a live check.</p>' % (n, hh) +
            '<p><a class="btn" href="/?q=%s"><span>Check %s now</span></a> <a class="btn ghost" href="/status/%s"><span>Full status page</span></a></p>' % (hh, n, hh) +
            '<h2>Show %s status on your own site</h2><div class="sp-card sp-embed"><p class="note" style="margin-top:0">Two ways to show whether %s is up on a forum, blog or community page. Both update by themselves.</p>' % (n, n) +
            '<h3>Live card</h3><p class="note">Shows the status, 24-hour uptime, response time and a small live graph. Move your cursor along the graph for each reading. It refreshes every few seconds while the page is open. Works on any normal web page that allows embeds.</p>' +
            '<p><iframe src="/widget/%s" title="%s live status" width="300" height="104" style="border:0;max-width:100%%" loading="lazy"></iframe></p>' % (hh, n) +
            '<textarea class="sp-code" id="sp-embed-code2" readonly rows="3" aria-label="Live card code">&lt;iframe src="https://siteupdown.com/widget/%s" title="%s live status" width="300" height="104" style="border:0;max-width:100%%" loading="lazy"&gt;&lt;/iframe&gt;</textarea>' % (hh, n) +
            '<p><button type="button" class="btn small ghost sp-embed-copy" data-for="sp-embed-code2"><span>Copy live card code</span></button></p>' +
            '<h3>Small badge</h3><p class="note">A tiny image for places that only allow pictures, such as forum signatures or GitHub pages. Hover for details. Other sites keep their own copy of images, so it can lag by a few minutes.</p>' +
            '<p><a href="%s"><img src="/badge/%s.svg" alt="%s status badge" title="Live status from siteupdown.com. Click for uptime and response details." height="22" loading="lazy"></a></p>' % (path, hh, n) +
            '<textarea class="sp-code" id="sp-embed-code" readonly rows="3" aria-label="Badge code">&lt;a href="https://siteupdown.com%s"&gt;&lt;img src="https://siteupdown.com/badge/%s.svg" alt="%s status" title="Live status from siteupdown.com. Click for uptime and response details." height="22"&gt;&lt;/a&gt;</textarea>' % (path, hh, n) +
            '<p><button type="button" class="btn small ghost sp-embed-copy" data-for="sp-embed-code"><span>Copy badge code</span></button></p></div>' +
            '<h2>Questions about %s</h2><div class="faq">%s</div>' % (n, faqh) +
            '<h2>Other %s checks</h2><ul>%s</ul>' % (html.escape(catname.lower()), rel) +
            '<p class="note">Category: %s. siteupdown.com is independent and is not affiliated with %s.</p>' % (html.escape(catname), n) +
            '<p style="margin-top:20px"><a href="/is-it-down/">&larr; All site status pages</a></p></div></section>')
        write(path.lstrip('/') + '.html', h + body + foot('<script src="/assets/worldmap.js"></script><script src="/assets/app.js"></script><script src="/assets/sitepage.js"></script><script src="/assets/live.js"></script>'))
    # directory
    groups = ''
    order = ['social', 'video', 'gaming', 'ai', 'finance', 'payments', 'trading', 'shopping', 'delivery', 'news', 'government', 'health', 'betting', 'telecom', 'travel', 'search', 'work']
    for cat in order:
        items = [(n, h, p) for n, h, c, p in SP.SITES if c == cat and n not in HIDDEN]
        if not items: continue
        li = ''.join('<li data-host="%s" data-name="%s"><i class="dot-s"></i>%s<a href="%s">%s</a><span class="rep"></span></li>' % (html.escape(h), html.escape(n.lower()), tile(n, h), SP.page_path(n), html.escape(n) + (' <em class="apptag">App</em>' if n in SP.APPS else '')) for n, h, p in items)
        groups += '<section class="dgroup" id="%s"><h2>%s</h2><ul>%s</ul></section>' % (cat, html.escape(SP.CATS[cat][0]), li)
    ld = '<script type="application/ld+json">' + _json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Is it down? Status of popular websites", "url": SITE + "/is-it-down/"}) + '</script>'
    h = head('Is it down? Live status of popular websites — siteupdown.com', 'Live status for popular websites, apps and games, checked every few minutes from our servers, with problem reports from other visitors.', '/is-it-down/', ld).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose sitedir" data-sp="dir"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 12px">Is it down<span class="dot">?</span></h1>'
            '<p class="lead">Live status for popular websites, apps and games. Each page shows our latest check, response time and uptime, and the problems other visitors have reported in the last 24 hours.</p>'
            '<div class="sp-card" id="sp-top" hidden><b>Most reported right now</b><ul id="sp-toplist"></ul></div>'
            '<label class="sr" for="sp-find">Find a site</label><input id="sp-find" class="sp-find" type="search" placeholder="Find a site, e.g. Netflix" autocomplete="off">'
            + groups +
            '<p>Not listed? <a href="/">Check any website</a> from fifteen places.</p></div></section>')
    write('is-it-down/index.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/sitepage.js"></script><script src="/assets/live.js"></script>'))

# ---------------------------------------------------------------- help centre
import json as _json
from help_content import CATS, ARTICLES, BY_SLUG
from tools_content import TOOLS, BY_SLUG as TOOL_BY

def help_pages():
    os.makedirs(os.path.join(ROOT, 'help'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'is-it-down'), exist_ok=True)
    catname = {c[0]: c[1] for c in CATS}
    # hub
    cards = ''
    for key, name, blurb in CATS:
        items = ''.join('<li><a href="/help/%s">%s</a></li>' % (a['slug'], html.escape(html.unescape(a['title']))) for a in ARTICLES if a['cat'] == key)
        cards += '<section class="hcat"><h2>%s</h2><p>%s</p><ul>%s</ul></section>' % (html.escape(name), html.escape(blurb), items)
    ld = '<script type="application/ld+json">' + _json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "siteupdown.com help centre", "url": SITE + "/help/"}) + '</script>'
    h = head('Help centre: website errors, DNS, SSL and uptime guides — siteupdown.com', 'Plain-English guides to website errors, DNS, SSL certificates, uptime and speed. Find out why a site will not load and how to fix it.', '/help/', ld).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose helphub"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 12px">Help centre<span class="dot">.</span></h1>'
            '<p class="lead">Plain-English answers about website errors, DNS, SSL, uptime and speed. Written to help you work out whether a site is down, and what to do next.</p>'
            '<div class="hgrid">' + cards + '</div>'
            '<p style="margin-top:34px"><a href="/">&larr; Back to the website checker</a></p></div></section>')
    write('help/index.html', h + body + foot('<script src="/assets/app.js"></script>'))
    for a in ARTICLES:
        path = '/help/' + a['slug']
        art = {"@context": "https://schema.org", "@type": "Article", "headline": a['title'], "description": a['desc'], "datePublished": "2026-11-02", "dateModified": "2026-11-02",
               "author": {"@type": "Organization", "name": "siteupdown.com", "url": SITE + "/"}, "publisher": {"@type": "Organization", "name": "siteupdown.com", "url": SITE + "/"},
               "mainEntityOfPage": SITE + path}
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Help centre", "item": SITE + "/help/"},
            {"@type": "ListItem", "position": 3, "name": a['title'], "item": SITE + path}]}
        extra = '<script type="application/ld+json">' + _json.dumps(art) + '</script><script type="application/ld+json">' + _json.dumps(crumbs) + '</script>'
        h = head(a['title'] + ' — siteupdown.com', a['desc'], path, extra).replace('{BODYATTR}', '')
        rel = ''.join('<li><a href="/help/%s">%s</a></li>' % (r, html.escape(BY_SLUG[r]['title'])) for r in a['related'])
        body = ('<section class="page"><div class="wrap prose article">'
                '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/help/">Help centre</a> / ' + html.escape(catname[a['cat']]) + '</nav>'
                '<h1 style="margin:14px 0 20px">' + html.escape(a['title']) + '</h1>' + a['body'] +
                '<div class="cta-box"><b>Check a website now</b><p>Is it down for everyone, or just you? Paste an address and we test it from fifteen places.</p><a class="btn" href="/"><span>Open the checker</span></a></div>'
                '<h2>Related guides</h2><ul>' + rel + '</ul>'
                '<p class="note">Last updated 2 November 2026. Written by the siteupdown.com team. <a href="/contact">Spotted a mistake?</a></p>'
                '<p style="margin-top:20px"><a href="/help/">&larr; All help guides</a></p></div></section>')
        write('help/' + a['slug'] + '.html', h + body + foot('<script src="/assets/app.js"></script>'))
    # sitemap
    urls = [('/', 'daily', '1.0'), ('/speed', 'monthly', '0.8'), ('/internet-speed-test', 'monthly', '0.8'), ('/what-is-my-ip', 'monthly', '0.8'), ('/game-ping-test', 'monthly', '0.8'), ('/outage-map', 'daily', '0.7'), ('/outage-history', 'daily', '0.6'), ('/state-of-the-internet', 'daily', '0.7'), ('/compare', 'weekly', '0.6'), ('/monitor', 'monthly', '0.7'), ('/help/', 'weekly', '0.8'), ('/editorial-policy', 'monthly', '0.4')] + [('/help/' + a['slug'], 'monthly', '0.7') for a in ARTICLES] + [('/is-it-down/', 'daily', '0.8'), ('/tools/', 'monthly', '0.8')] + [('/tools/' + t['slug'], 'monthly', '0.7') for t in TOOLS] + [('/tools/uptime-sla-calculator', 'monthly', '0.7'), ('/how-we-check', 'monthly', '0.6'), ('/faq', 'monthly', '0.6')] + [(SP.page_path(n), 'daily', '0.6') for n, _, _, _ in SP.SITES if n not in HIDDEN] + [('/about', 'monthly', '0.5'), ('/business', 'monthly', '0.5'), ('/contact', 'yearly', '0.3'), ('/privacy', 'yearly', '0.3'), ('/legal', 'yearly', '0.3')]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('<url><loc>%s%s</loc><lastmod>@@D@@</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>\n' % (SITE, u, c, p) for u, c, p in urls).replace('@@D@@', _dt.date.today().isoformat()) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
    # RSS feed of the help guides: lets readers, feed readers and aggregators follow new guides
    def _rss_item(a):
        link = SITE + '/help/' + a['slug']
        return '<item><title>%s</title><link>%s</link><guid isPermaLink="true">%s</guid><pubDate>%s</pubDate><description>%s</description></item>' % (
            html.escape(html.unescape(a['title'])), link, link, a.get('date', 'Mon, 02 Nov 2026 09:00:00 +0000'), html.escape(html.unescape(a['desc'])))
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>siteupdown.com guides</title><link>' + SITE + '/help/</link>'
           '<atom:link href="' + SITE + '/feed.xml" rel="self" type="application/rss+xml"/><description>Plain-English guides to website outages, error codes, DNS, speed and uptime.</description><language>en-gb</language>'
           + ''.join(_rss_item(a) for a in reversed(ARTICLES)) + '</channel></rss>\n')
    open(os.path.join(ROOT, 'feed.xml'), 'w', encoding='utf-8').write(rss)


# ---------------------------------------------------------------- tools
def tools_pages():
    os.makedirs(os.path.join(ROOT, 'tools'), exist_ok=True)
    # hub
    cards = ''.join('<a class="tool" href="/tools/%s"><span class="ti">%s</span><h3>%s</h3><p>%s</p><span class="tgo">Open the tool &rarr;</span></a>' % (t['slug'], t['icon'], html.escape(t['name']), t['short']) for t in TOOLS)
    extra_cards = ('<a class="tool" href="/"><span class="ti">&#128269;</span><h3>Is it down?</h3><p>Check any website from our server and fifteen places around the world.</p><span class="tgo">Open the checker &rarr;</span></a>'
                   '<a class="tool" href="/outage-map"><span class="ti">&#128506;</span><h3>Global outage map</h3><p>See where in the world websites are reachable right now.</p><span class="tgo">Open the map &rarr;</span></a>'
                   '<a class="tool" href="/internet-speed-test"><span class="ti">&#128246;</span><h3>Internet speed test</h3><p>Measure your download, upload, ping and jitter.</p><span class="tgo">Test your connection &rarr;</span></a>'
                   '<a class="tool" href="/what-is-my-ip"><span class="ti">&#128205;</span><h3>What is my IP address?</h3><p>See your public address, provider and approximate location.</p><span class="tgo">Show my IP &rarr;</span></a>'
                   '<a class="tool" href="/game-ping-test"><span class="ti">&#127918;</span><h3>Game ping test</h3><p>Check your ping to 17 regions that online games use.</p><span class="tgo">Test my ping &rarr;</span></a>'
                   '<a class="tool" href="/speed"><span class="ti">&#9889;</span><h3>Website speed test</h3><p>See how fast a page loads and where the time goes.</p><span class="tgo">Test a site &rarr;</span></a>'
                   '<a class="tool" href="/tools/uptime-sla-calculator"><span class="ti">&#128208;</span><h3>Uptime and SLA calculator</h3><p>Turn an uptime percentage into the downtime it allows, or the reverse.</p><span class="tgo">Open the calculator &rarr;</span></a>'
                   '<a class="tool" href="/monitor"><span class="ti">&#128276;</span><h3>Monitor and alerts</h3><p>Watch your sites and get an email when one goes down.</p><span class="tgo">Open Monitor &rarr;</span></a>')
    ld = '<script type="application/ld+json">' + _json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free website tools", "url": SITE + "/tools/"}) + '</script>'
    h = head('Free website tools: DNS, SSL, headers, redirects and more — siteupdown.com', 'Free website tools: DNS lookup, SSL certificate checker, HTTP header checker, redirect checker, WHOIS and domain expiry, MX lookup, robots.txt and security headers checks.', '/tools/', ld).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolhub"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 12px">Free website tools<span class="dot">.</span></h1>'
            '<p class="lead">Quick checks for the things that go wrong behind a website: DNS, certificates, redirects, headers, email and search settings. No sign-up, no downloads.</p>'
            '<h2>Look inside a website</h2><div class="tools-grid">' + cards + '</div>'
            '<h2>Is it working?</h2><div class="tools-grid">' + extra_cards + '</div>'
            '<p class="note">Each tool tests public websites only, from our servers, and we limit how often one visitor can run them. Results are a snapshot of the moment you ask. <a href="/help/how-our-checks-work">How our checks work</a>.</p>'
            '<p style="margin-top:30px"><a href="/">&larr; Back to the website checker</a></p></div></section>')
    write('tools/index.html', h + body + foot('<script src="/assets/app.js"></script>'))
    for t in TOOLS:
        path = '/tools/' + t['slug']
        faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), a) for q, a in t['faqs'])
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebApplication", "name": t['name'], "url": SITE + path, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Tools", "item": SITE + "/tools/"},
                {"@type": "ListItem", "position": 3, "name": t['name'], "item": SITE + path}]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _re.sub('<[^>]+>', '', a)}} for q, a in t['faqs']]}]}
        extra = '<script type="application/ld+json">' + _json.dumps(ld) + '</script>'
        h = head(t['h1'] + ' — free online tool | siteupdown.com', t['desc'], path, extra).replace('{BODYATTR}', '')
        others = ''.join('<li><a href="/tools/%s">%s</a></li>' % (o['slug'], html.escape(o['name'])) for o in TOOLS if o['slug'] != t['slug'])
        helps = ''.join('<li><a href="/help/%s">%s</a></li>' % (sl, html.escape(tt)) for sl, tt in t['help'])
        body = ('<section class="page"><div class="wrap prose toolpage" data-tool="%s">' % t['key'] +
                '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/tools/">Tools</a> / %s</nav>' % html.escape(t['name']) +
                '<h1 style="margin:14px 0 14px">%s</h1>' % html.escape(t['h1']) +
                '<form class="tool-form" id="tf" novalidate><div class="field"><input id="ti" type="text" inputmode="url" placeholder="%s" autocapitalize="none" autocorrect="off" spellcheck="false" aria-label="Website address"></div>' % t['ph'] +
                ('<select id="tq" class="tool-sel" aria-label="' + t.get('sel_label', 'Record type') + '">' + ''.join('<option value="%s">%s</option>' % o for o in t['sel']) + '</select>' if t.get('sel') else '') +
                '<button class="btn" type="submit" id="tb"><span>%s</span></button></form>' % t['btn'] +
                '<p class="tool-err" id="te" role="alert" hidden></p><div class="tool-out" id="tout" aria-live="polite"></div>' +
                ''.join('<p>%s</p>' % x for x in t['intro']) +
                '<h2>How to read the results</h2><ul>' + ''.join('<li>%s</li>' % x for x in t['read']) + '</ul>' +
                '<h2>Questions</h2><div class="faq">' + faq + '</div>' +
                '<h2>Related guides</h2><ul>' + helps + '</ul>' +
                '<h2>More free tools</h2><ul>' + others + '</ul>' +
                '<p class="note">Results are a snapshot taken from our servers at the moment you ask, and can differ from what you see elsewhere. siteupdown.com tests public websites only. <a href="/contact">Spotted a problem?</a></p>'
                '<p style="margin-top:20px"><a href="/tools/">&larr; All tools</a></p></div></section>')
        write('tools/' + t['slug'] + '.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/tools.js"></script>'))

def sla_page():
    path = '/tools/uptime-sla-calculator'
    faq = [('What does 99.9% uptime mean?', 'It allows about 8 hours 46 minutes of downtime a year, or 43 minutes a month. This is often called "three nines".'),
           ('Is 99.99% much better than 99.9%?', 'It is ten times stricter: about 52 minutes a year instead of nearly 9 hours. Each extra nine usually costs far more to achieve.'),
           ('Does planned maintenance count as downtime?', 'It depends on the agreement. Many service level agreements exclude announced maintenance, so read the small print.')]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": "Uptime and SLA calculator", "url": SITE + path, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}
    h = head('Uptime and SLA calculator — how much downtime is 99.9%? | siteupdown.com', 'Free uptime calculator: see how much downtime a 99%, 99.9% or 99.99% uptime guarantee allows per day, week, month and year, or work out your uptime from minutes of downtime.', path, '<script type="application/ld+json">' + _json.dumps(ld) + '</script>').replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" data-tool="sla"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/tools/">Tools</a> / Uptime and SLA calculator</nav>'
            '<h1 style="margin:14px 0 14px">Uptime and SLA calculator</h1>'
            '<div class="sp-card"><label for="sla-pct"><b>Uptime percentage</b></label><div class="tool-form"><div class="field"><input id="sla-pct" type="text" inputmode="decimal" value="99.9" aria-label="Uptime percentage"></div><span class="note" style="align-self:center">%</span></div>'
            '<div id="sla-out" aria-live="polite"></div></div>'
            '<div class="sp-card"><label for="sla-min"><b>Or: how much downtime did you have?</b></label><div class="tool-form"><div class="field"><input id="sla-min" type="text" inputmode="decimal" placeholder="Minutes of downtime" aria-label="Minutes of downtime"></div>'
            '<select id="sla-per" class="tool-sel" aria-label="Over this period"><option value="1440">in a day</option><option value="10080">in a week</option><option value="43200" selected>in a 30-day month</option><option value="525600">in a year</option></select></div><div id="sla-out2" aria-live="polite"></div></div>'
            '<h2>What the usual targets allow</h2><div class="rt-wrap"><table class="rt"><thead><tr><th>Uptime</th><th>Per day</th><th>Per month (30 days)</th><th>Per year</th></tr></thead><tbody id="sla-tab"></tbody></table></div>'
            '<p>Uptime is the share of time a service was working. The rest is downtime. Providers often promise a figure such as 99.9% in a service level agreement (SLA), and this page shows what that figure really allows. For how we measure uptime on this site, see <a href="/help/uptime-percentages-explained">uptime percentages explained</a>.</p>'
            '<h2>Questions</h2><div class="faq">' + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(a)) for q, a in faq) + '</div>'
            '<h2>More free tools</h2><ul>' + ''.join('<li><a href="/tools/%s">%s</a></li>' % (o['slug'], html.escape(o['name'])) for o in TOOLS) + '</ul>'
            '<p style="margin-top:20px"><a href="/tools/">&larr; All tools</a></p></div></section>')
    write('tools/uptime-sla-calculator.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/sla.js"></script>'))

def stopwatch_svg():
    import math
    cx, cy = 150, 185
    def pt(r, d):
        a = math.radians(d - 90); return cx + r * math.cos(a), cy + r * math.sin(a)
    def arc(r, d0, d1, col, w):
        x0, y0 = pt(r, d0); x1, y1 = pt(r, d1); big = 1 if d1 - d0 > 180 else 0
        return '<path d="M%.1f %.1f A%d %d 0 %d 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="%d"/>' % (x0, y0, r, r, big, x1, y1, col, w)
    sp = lambda f: -135 + f * 270
    ticks = ''
    for i in range(0, 33):
        d = -135 + i * 270 / 32.0; major = i % 4 == 0
        x0, y0 = pt(86 if major else 90, d); x1, y1 = pt(100, d)
        ticks += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#0b0b0b" stroke-width="%s" stroke-linecap="round"/>' % (x0, y0, x1, y1, 4 if major else 2.2)
    labels = ''
    for f, t in ((0, '0'), (2/8., '10'), (3/8., '50'), (4/8., '100'), (5/8., '250'), (6/8., '500'), (1, '1000')):
        x, y = pt(68, sp(f)); labels += '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12" font-weight="700" fill="#0b0b0b">%s</text>' % (x, y + 4, t)
    return ('<svg viewBox="0 0 300 330" aria-hidden="true">'
        '<rect x="128" y="6" width="44" height="26" rx="8" fill="#e84a4a" stroke="#0b0b0b" stroke-width="5"/><rect x="140" y="30" width="20" height="16" fill="#fbc531" stroke="#0b0b0b" stroke-width="5"/>'
        '<circle cx="150" cy="185" r="138" fill="#0b0b0b"/><circle cx="150" cy="185" r="130" fill="#fbc531"/><circle cx="150" cy="185" r="112" fill="#fffbea" stroke="#0b0b0b" stroke-width="5"/>'
        + arc(104, sp(0), sp(.25), '#e84a4a', 10) + arc(104, sp(.25), sp(.5), '#fbc531', 10) + arc(104, sp(.5), sp(1), '#7ed957', 10) + ticks + labels +
        '<path id="st-arc" class="st-arc" d="M36.4 163.6 A90 90 0 1 1 163.6 163.6" style="visibility:hidden"/>'
        '<g class="st-needle" id="st-needle"><path d="M143 185 L150 87 L157 185 Z" fill="#0b0b0b"/></g>'
        '<circle cx="150" cy="185" r="17" fill="#fbc531" stroke="#0b0b0b" stroke-width="5"/><circle cx="145" cy="180" r="4.5" fill="#fff"/></svg>')

def internet_speed_page():
    path = '/internet-speed-test'
    faq = [('How does the speed test work?', 'Your browser downloads and uploads test data to Cloudflare\'s public speed-test servers and times it. It also sends many tiny requests to measure ping and jitter. Nothing is installed.'),
           ('How much data does it use?', 'Usually 50 to 300 MB, more on a very fast connection. Avoid running it on a limited mobile data plan.'),
           ('Why is my result lower than what I pay for?', 'Wi-Fi, an old router, other devices using the connection, a VPN and a busy evening network all lower the result. For the most accurate number, use a cable and close other apps.'),
           ('What are ping and jitter?', 'Ping is how long a message takes to reach a server and return, in milliseconds. Jitter is how much that time varies. Low numbers matter most for gaming and video calls.'),
           ('What is a good speed?', 'About 10 Mbps is enough for HD video, 25 Mbps for 4K, and 5 Mbps down with 2 Mbps up for video calls. For several people at once, aim for 50 Mbps or more.'),
           ('Does a slow connection mean a website is down?', 'No. If one site will not load but others do, check it with our <a href="/">website checker</a>. If everything is slow, the problem is your connection.')]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": "Internet speed test", "url": SITE + path, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _re.sub('<[^>]+>', '', a)}} for q, a in faq]}]}
    h = head('Speed test — free internet speed test (download, upload, ping) | siteupdown.com', 'Free internet speed test: measure your download speed, upload speed, ping and jitter in about 20 seconds. No app and no sign-up.', path, '<script type="application/ld+json">' + _json.dumps(ld) + '</script>').replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" data-tool="speedtest"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/tools/">Tools</a> / Internet speed test</nav>'
            '<h1 style="margin:14px 0 8px">Internet speed test<span class="dot">.</span></h1>'
            '<div class="sp-card st-card"><div class="st-gauge">' + stopwatch_svg() + ''
            '<div class="st-read" aria-live="polite"><b id="st-num">0</b><span id="st-unit">Mbps</span><em id="st-phase">Ready</em></div></div>'
            '<div class="st-btn"><button class="btn" id="st-go" type="button"><span>Start test</span></button></div>'
            '<p class="tool-err" id="st-err" role="alert" hidden></p>'
            '<div class="st-grid"><div class="st-t"><i>Download</i><b id="st-dl">&ndash;</b></div><div class="st-t"><i>Upload</i><b id="st-ul">&ndash;</b></div><div class="st-t"><i>Ping</i><b id="st-ping">&ndash;</b></div><div class="st-t"><i>Jitter</i><b id="st-jit">&ndash;</b></div></div>'
            '<p class="note" id="st-conn"></p><p class="note" id="st-used"></p><p class="note" id="st-last"></p></div>'
            '<p class="st-inst"><button class="btn small" id="st-install" type="button" hidden><span>Install as an app</span></button></p>'
            '<div id="st-good" hidden></div>'
            '<p class="lead" style="margin-top:22px">How fast is your connection right now? Press start and we measure your download speed, upload speed, ping and jitter in about 20 seconds. No app and no sign-up.</p>'
            '<p class="note">The test uses roughly 50 to 300 MB of data, so avoid it on a limited mobile plan. It runs between your browser and Cloudflare\'s public speed-test network. We do not store your result or your address. Results depend on your device, Wi-Fi and what else is using your connection.</p>'
            '<h2>Use it like an app</h2><p>On Android, tap <b>Install as an app</b> below the test, or open your browser menu and choose Install app. On iPhone, tap Share and then Add to Home Screen. It opens straight to the speed test, with no app store needed.</p>'
            '<h2>Getting an accurate result</h2><ul><li>Use a cable if you can, or stand near the router.</li><li>Close streaming, downloads and other tabs first.</li><li>Turn off a VPN, which adds its own delay.</li><li>Run it two or three times and compare. Speeds vary from minute to minute.</li></ul>'
            '<h2>Questions</h2><div class="faq">' + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), a) for q, a in faq) + '</div>'
            '<h2>More free tools</h2><ul><li><a href="/">Is it down? website checker</a></li><li><a href="/speed">Website speed test</a></li>' + ''.join('<li><a href="/tools/%s">%s</a></li>' % (o['slug'], html.escape(o['name'])) for o in TOOLS) + '</ul>'
            '<p style="margin-top:20px"><a href="/tools/">&larr; All tools</a></p></div></section>')
    h = h.replace('href="/site.webmanifest"', 'href="/speedtest.webmanifest"')
    write('internet-speed-test.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/speedtest.js"></script>'))


def heatmap_page():
    path = '/outage-map'
    h = head('Global website outage map — where sites are reachable | siteupdown.com', 'A live world outage map showing how reachable popular websites and apps are from 15 places around the world, and how fast they respond.', path).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Outage map</nav>'
            '<h1 style="margin:14px 0 8px">Global outage map<span class="dot">.</span></h1>'
            '<p class="lead">Where in the world are websites and apps reachable right now? Each dot shows how the sites we watch look from that place.</p>'
            '<div class="hm-tabs" role="group" aria-label="Map layer"><button type="button" class="btn small" data-hm="reach" aria-pressed="true"><span>Reachability</span></button><button type="button" class="btn small" data-hm="speed" aria-pressed="false"><span>Response time</span></button></div>'
            '<div class="hm-world dg" id="hm-map"><div class="hm-scroll"><div class="hm-inner"><svg viewBox="0 0 2400 1221" role="img" aria-label="World map with a flag for each place we check from. The table below lists every place."><image href="/assets/nl-continents-comic.png?v=2" x="0" y="0" width="2400" height="1221"/><g id="hm-lay"></g></svg><div class="hm-bub" id="hm-bub" aria-live="polite"></div></div></div></div><p class="note hm-hint">Hover or tap a dot, or a country in the list, for details.</p><div class="hm-leg" id="hm-leg"></div><div class="sp-card"><div class="hm-card" id="hm-card" aria-live="polite"></div><p class="note" id="hm-sum">Loading the map&hellip;</p>'
            '<div class="rt-wrap"><table class="rt"><thead><tr><th>Place</th><th>Sites reached</th><th>Typical time</th></tr></thead><tbody id="hm-tab"></tbody></table></div></div>'
            '<section class="lm" id="lm"><h2>Local reports</h2><p class="lead">Where visitors say a site is not working for them. Glows fade as reports get older and dim when a site recovers. Reports are rounded to about 10 km and never show exactly who or where.</p><div class="card lm-card"><div class="lm-bar"><div class="hm-tabs" id="lm-win" role="group" aria-label="Time window"><button type="button" class="btn small" data-h="3" aria-pressed="true"><span>Last 3 hours</span></button><button type="button" class="btn small" data-h="24" aria-pressed="false"><span>Last 24 hours</span></button></div><button type="button" class="btn small" id="lm-go"><span>Show the local map</span></button><button type="button" class="btn small ghost" id="lm-me" hidden><span>Centre on me</span></button></div><div class="lm-map" id="lm-map" hidden role="region" aria-label="Local outage reports map"></div><p class="note" id="lm-note">The map loads street maps from OpenStreetMap when you open it.</p></div></section>'
            '<section class="lm" id="rf"><h2>Latest reports</h2><p class="lead">The newest problems visitors have reported across all sites. Each one is a choice they picked, with no personal details.</p><div class="card lm-card"><ul class="rf" id="rf-list"><li class="rf-none">Loading…</li></ul></div></section>'
            '<form class="card hm-mine" onsubmit="var v=this.q.value.trim();if(v)location.href=\'/?q=\'+encodeURIComponent(v);return false" novalidate><b>Is a site down in your country?</b><span>Type any website and we check it from all our places at once, so you can see where it works and where it does not.</span><div class="hm-mrow"><input name="q" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="e.g. netflix.com" aria-label="Website address"><button class="btn small" type="submit"><span>Check</span></button></div></form>'
            '<div id="hm-regions"></div>'
            '<div id="hm-sites"></div>'
            '<h2>How to read this map</h2><p>Each pin is one of the places we check from. For every place we ask how many of the websites and apps on our public lists answered, and how long a typical answer took.</p><ul><li><b>Colours:</b> green is 90% or more of sites reached, amber is 70 to 90%, red is under 70%. In response-time view, green is under 400 ms, amber is 400 to 900 ms and red is slower.</li><li>Green means almost every site we watch answered from that place. Amber and red mean more of them did not.</li><li>A whole place turning red can point to a problem with a network or country, not just one website.</li><li>Some sites deliberately block automated checks from certain countries, so a lower figure is a hint, not proof of an outage.</li><li>The data comes from probes on the public <a href="https://globalping.io" rel="noopener">Globalping</a> network, refreshed through the day. Read <a href="/how-we-check">how we check</a> for the details.</li></ul>'
            '<p style="margin-top:20px"><a href="/">&larr; Back to the website checker</a></p></div></section>')
    write('outage-map.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/heatmap.js"></script><script src="/assets/localmap.js"></script>'))


def insight_pages():
    """Compare two sites, the weekly state of the internet, and a printable per-site report. All data comes from the API at view time."""
    opts = ''
    for cat in ['social', 'video', 'gaming', 'ai', 'shopping', 'delivery', 'news', 'health', 'telecom', 'travel', 'search', 'work']:
        items = [(n, h) for n, h, c, _ in SP.SITES if c == cat and n not in HIDDEN]
        if items: opts += '<optgroup label="%s">%s</optgroup>' % (html.escape(SP.CATS[cat][0]), ''.join('<option value="%s">%s</option>' % (html.escape(h), html.escape(n)) for n, h in sorted(items)))
    # compare
    path = '/compare'
    h = head('Compare two websites: reliability, speed and outages | siteupdown.com', 'Put two popular websites side by side: uptime, outages, response time and reliability grade, measured by our own checks.', path).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" id="cmp"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Compare</nav>'
            '<h1 style="margin:14px 0 8px">Compare two sites<span class="dot">.</span></h1>'
            '<p class="lead">Pick two services and see which one has been more reliable and faster, based on our own checks over the last 30 days.</p>'
            '<form class="card cmp-pick" id="cmp-form"><label>First site<select id="cmp-a" aria-label="First site"><option value="">Choose a site</option>%s</select></label><span class="cmp-vs">vs</span><label>Second site<select id="cmp-b" aria-label="Second site"><option value="">Choose a site</option>%s</select></label></form>' % (opts, opts) +
            '<div id="cmp-out" aria-live="polite"><p class="note">Choose two sites above.</p></div>'
            '<p class="note">Measured from our own server. A site that blocks automated checks is never marked down for it, and uptime is a guide, not a service guarantee. Sites need a little history before they can be graded.</p>'
            '<p style="margin-top:20px"><a href="/is-it-down/">&larr; All site status pages</a></p></div></section>')
    write('compare.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/compare.js"></script>'))
    # weekly
    path = '/state-of-the-internet'
    h = head('State of the internet this week: outages, reliability and trends | siteupdown.com', 'A weekly summary of outages, the most and least reliable popular sites and how each category is doing, from our own checks.', path).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" id="st"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / State of the internet</nav>'
            '<h1 style="margin:14px 0 8px">State of the internet<span class="dot">.</span></h1>'
            '<p class="lead" id="st-lead">A summary of the last seven days across the popular sites we check, updated automatically.</p>'
            '<div id="st-out" aria-live="polite"><p class="note">Loading&hellip;</p></div>'
            '<h2>How we measure</h2><p>Every number here comes from our own checks of the sites on our public lists, repeated through the day, plus the problem reports visitors send us. We count a site as down only after repeated failed checks, and we never mark a site down just because it blocks automated visitors. These are guides, not official figures.</p>'
            '<p style="margin-top:20px"><a href="/outage-history">See the full outage history &rarr;</a></p></div></section>')
    write('state-of-the-internet.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/state.js"></script>'))
    # printable report
    path = '/site-report'
    h = head('Site reliability report | siteupdown.com', 'A printable reliability report for one website, from our own checks.', path, noindex=True).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" id="rp"><nav class="crumbs no-print" aria-label="Breadcrumb"><a href="/">Home</a> / Report</nav>'
            '<div id="rp-out" aria-live="polite"><p class="note">Loading&hellip;</p></div></div></section>')
    write('site-report.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/report.js"></script>'))

def history_page():
    path = '/outage-history'
    h = head('Outage history — what was reported and detected on any day | siteupdown.com', 'A permanent day-by-day record of the problems visitors reported and the outages our own checks detected, for popular websites and apps.', path).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" id="hs"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Outage history</nav>'
            '<h1 style="margin:14px 0 8px">Outage history<span class="dot">.</span></h1>'
            '<p class="lead">A permanent, day-by-day record of what visitors reported and what our own checks detected. Pick a date to see what happened, or look up one website.</p>'
            '<div class="card hs-card"><div class="hs-bar"><button type="button" class="btn small ghost" id="hs-prev" aria-label="Previous day"><span>&lsaquo;</span></button>'
            '<input type="date" id="hs-date" aria-label="Date">'
            '<button type="button" class="btn small ghost" id="hs-next" aria-label="Next day"><span>&rsaquo;</span></button>'
            '<button type="button" class="btn small" id="hs-today"><span>Today</span></button></div>'
            '<form class="hs-site" id="hs-form" novalidate><input type="text" id="hs-q" placeholder="Only one website? e.g. netflix.com" autocomplete="off" aria-label="Website"><button class="btn small" type="submit"><span>Show</span></button> <button class="btn small ghost" type="button" id="hs-all" hidden><span>All sites</span></button></form>'
            '<h2 id="hs-title" class="hs-title"></h2><div id="hs-out" aria-live="polite"><p class="note">Loading…</p></div></div>'
            '<h2>Days with activity</h2><div class="card hs-card"><ul class="rf hs-days" id="hs-days"><li class="rf-none">Loading…</li></ul></div>'
            '<p class="note">Dates are in UTC. Reports are anonymous visitor choices and are not verified. &ldquo;Detected down&rdquo; comes from our own automatic checks. Only counts are kept in this record, never who reported.</p>'
            '<p style="margin-top:20px"><a href="/outage-map">&larr; Back to the outage map</a></p></div></section>')
    write('outage-history.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/history.js"></script>'))

def _tool_page(path, fname, title, desc, tool_key, name, h1, inner, faq, script, extra_after=''):
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": name, "url": SITE + path, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Tools", "item": SITE + "/tools/"}, {"@type": "ListItem", "position": 3, "name": name, "item": SITE + path}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _re.sub('<[^>]+>', '', a)}} for q, a in faq]}]}
    h = head(title, desc, path, '<script type="application/ld+json">' + _json.dumps(ld) + '</script>').replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose toolpage" data-tool="%s"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/tools/">Tools</a> / %s</nav>' % (tool_key, html.escape(name)) +
            '<h1 style="margin:14px 0 8px">%s<span class="dot">.</span></h1>' % html.escape(h1) + inner +
            '<h2>Questions</h2><div class="faq">' + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), a) for q, a in faq) + '</div>' + extra_after +
            '<h2>More free tools</h2><ul><li><a href="/">Is it down? website checker</a></li><li><a href="/internet-speed-test">Internet speed test</a></li><li><a href="/what-is-my-ip">What is my IP address?</a></li><li><a href="/game-ping-test">Game ping test</a></li>' + ''.join('<li><a href="/tools/%s">%s</a></li>' % (o['slug'], html.escape(o['name'])) for o in TOOLS) + '</ul>'
            '<p style="margin-top:20px"><a href="/tools/">&larr; All tools</a></p></div></section>')
    write(fname, h + body + foot('<script src="/assets/app.js"></script><script src="/assets/%s"></script>' % script))


def ip_page():
    faq = [('What is an IP address?', 'It is the number that identifies your connection on the internet, a bit like a postal address for your router. Websites see it when you visit them, and it is how replies find their way back to you.'),
           ('What is the difference between IPv4 and IPv6?', 'IPv4 addresses look like 203.0.113.7 and the world is running out of them. IPv6 addresses are much longer, like 2001:db8::1, and there are plenty. Many connections now use IPv6, and some use both.'),
           ('Is the location shown accurate?', 'Only roughly. It usually points to your internet provider\'s nearest network hub, so it can be the right city or a nearby one. It does not show your street or your house.'),
           ('Why is my address different on my phone and my home Wi-Fi?', 'Each network gives you its own address. Your phone on mobile data shares an address with many other customers of that provider, and your home router has its own.'),
           ('Does a VPN change this?', 'Yes. With a VPN on, the address and location shown are the VPN\'s, not yours. That is a quick way to check the VPN is working.'),
           ('Do you store my address?', 'No. The lookup runs between your browser and Cloudflare\'s public network, so nothing about it is sent to or saved by siteupdown.com.')]
    inner = ('<div class="sp-card ip-card"><span class="ip-kind" id="ip-kind"></span><b class="ip-big" id="ip-big" aria-live="polite">Looking&hellip;</b>'
             '<div class="ip-act"><button class="btn small" id="ip-copy" type="button" hidden><span>Copy address</span></button><button class="btn small ghost" id="ip-again" type="button"><span>Check again</span></button></div>'
             '<dl class="facts ip-facts" id="ip-facts" hidden></dl><p class="note" id="ip-note" hidden>Location comes from your provider\'s network records, so it is approximate. Nothing on this page is sent to or stored by us.</p></div>'
             '<p class="lead" style="margin-top:22px">Your public IP address is what every website and game server sees when you connect. This page shows it, along with your provider and approximate location.</p>'
             '<h2>What you can do with it</h2><ul><li>Check that a VPN is on, or off.</li><li>Give your address to a game host or a firewall rule that asks for it.</li><li>Compare the address on your phone and your home network.</li><li>Test whether a port is open on it with the <a href="/tools/port-checker">port checker</a>.</li></ul>'
             '<p class="note">Looking for the speed of this connection? Try the <a href="/internet-speed-test">internet speed test</a>.</p>')
    _tool_page('/what-is-my-ip', 'what-is-my-ip.html', 'What is my IP address? — free IP lookup | siteupdown.com', 'See your public IP address, internet provider and approximate location in one tap. Free, no sign-up, and nothing is stored.', 'ip', 'What is my IP address?', 'What is my IP address?', inner, faq, 'ip.js')


def gameping_page():
    faq = [('What does this test?', 'It times how long your connection takes to reach cloud data centres in 17 regions around the world. Many online games and game services run their servers in the same regions, so it shows roughly what ping you could expect there.'),
           ('Is this the same as the ping in my game?', 'Not exactly. It is a browser test, which usually reads about 15 to 20 ms higher than a game does, and it is not the game\'s own server. Use it to compare regions and spot a problem, not as an exact in-game number.'),
           ('What is a good ping for gaming?', 'Under about 50 ms feels instant, up to about 100 ms is fine for most games, and over 150 ms is noticeable. Fast competitive shooters feel best under about 40 ms.'),
           ('Why is my nearest region still slow?', 'Wi-Fi, a busy network, other devices downloading and a VPN all add delay. Try a cable, pause downloads and run the test again. Mobile data is also less steady than a home line.'),
           ('What does steadiness mean?', 'It is how much the five measurements for a region varied. Steady connections feel smooth. Uneven ones cause rubber-banding even when the average looks fine.'),
           ('Why does a region show no answer?', 'An ad blocker, a work or school network, or a VPN can stop the test reaching it. Turn those off for this page and try again.')]
    inner = ('<div class="sp-card gp-card"><p class="note" style="margin-top:0">Press start and we time your connection to 17 cloud regions, closest first. It takes about 15 seconds and uses almost no data.</p>'
             '<div class="st-btn"><button class="btn" id="gp-go" type="button"><span>Start test</span></button></div><p class="tool-err" id="gp-err" role="alert" hidden></p>'
             '<div class="gp-best" id="gp-best" aria-live="polite" hidden></div>'
             '<div class="rt-wrap" id="gp-table" hidden><table class="rt"><thead><tr><th>Region</th><th>Ping</th><th>Rating</th></tr></thead><tbody id="gp-rows"></tbody></table></div></div>'
             '<p class="lead" style="margin-top:22px">Which part of the world gives you the best ping? This test measures your connection to cloud regions that many online games and game services use.</p>'
             '<p class="note">This is a browser test against cloud regions, not against any one game\'s own servers, and it reads a little higher than in-game ping. We do not store your results. For your download and upload speed use the <a href="/internet-speed-test">internet speed test</a>, and to see whether a game is down use <a href="/is-it-down/">Is it down?</a></p>'
             '<h2>Getting a fair result</h2><ul><li>Use a cable if you can, or stand near the router.</li><li>Pause downloads and streaming first.</li><li>Turn off a VPN, which adds its own delay.</li><li>Run it twice and compare, because a single run can catch a busy moment.</li></ul>')
    _tool_page('/game-ping-test', 'game-ping-test.html', 'Game ping test — check your ping to game regions | siteupdown.com', 'Free game ping test: see your ping and steadiness to 17 cloud regions around the world that many online games use. No app and no sign-up.', 'gameping', 'Game ping test', 'Game ping test', inner, faq, 'gameping.js')



def seo_audit():
    """Scan every built page for common search problems and write the result where the admin area can read it (not public)."""
    import glob as _g, re
    pages = []; titles = {}; descs = {}
    for f in sorted(_g.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
        if rel.startswith(('_tools/', 'node_modules/')) or rel in ('403.html', '404.html', '500.html'): continue
        t = open(f, encoding='utf-8').read()
        url = '/' if rel == 'index.html' else ('/' + rel[:-10] + '/' if rel.endswith('/index.html') else '/' + rel[:-5])
        m = re.search(r'<title>(.*?)</title>', t, re.S); title = html.unescape(m.group(1)).strip() if m else ''
        m = re.search(r'<meta name="description" content="(.*?)"', t); desc = html.unescape(m.group(1)) if m else ''
        body = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
        words = len(re.sub(r'<[^>]+>', ' ', body).split())
        imgs = re.findall(r'<img [^>]*>', t)
        noindex = 'noindex' in t[:4000]
        pg = {'url': url, 'title': title, 'tl': len(title), 'dl': len(desc), 'h1': len(re.findall(r'<h1[ >]', t)), 'words': words, 'noindex': noindex,
              'canon': 'rel="canonical"' in t, 'og': 'og:image' in t, 'ld': 'application/ld+json' in t, 'noalt': sum(1 for i in imgs if 'alt=' not in i),
              'links': len(re.findall(r'<a [^>]*href="/', t))}
        titles.setdefault(title, []).append(url); descs.setdefault(desc, []).append(url)
        pages.append((pg, title, desc))
    out_pages = []
    for pg, title, desc in pages:
        iss = []
        if not pg['noindex']:
            if pg['tl'] == 0: iss.append('Missing title')
            elif pg['tl'] > 62: iss.append('Title too long (may be cut off)')
            elif pg['tl'] < 25: iss.append('Title very short')
            if len(titles[title]) > 1: iss.append('Same title as %d other page%s' % (len(titles[title]) - 1, '' if len(titles[title]) == 2 else 's'))
            if pg['dl'] == 0: iss.append('Missing description')
            elif pg['dl'] > 165: iss.append('Description too long (may be cut off)')
            elif pg['dl'] < 70: iss.append('Description very short')
            if desc and len(descs[desc]) > 1: iss.append('Same description as %d other page%s' % (len(descs[desc]) - 1, '' if len(descs[desc]) == 2 else 's'))
            if pg['h1'] != 1: iss.append('Needs exactly one main heading (has %d)' % pg['h1'])
            if pg['words'] < 250: iss.append('Thin content (%d words)' % pg['words'])
            if pg['noalt']: iss.append('%d image%s without alt text' % (pg['noalt'], '' if pg['noalt'] == 1 else 's'))
            if not pg['canon']: iss.append('No canonical link')
            if not pg['og']: iss.append('No social preview image')
        pg['issues'] = iss; out_pages.append(pg)
    idx = [p_ for p_ in out_pages if not p_['noindex']]
    clean = sum(1 for p_ in idx if not p_['issues'])
    sm = open(os.path.join(ROOT, 'sitemap.xml')).read() if os.path.exists(os.path.join(ROOT, 'sitemap.xml')) else ''
    res = {'built': _dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), 'indexable': len(idx), 'noindex': len(out_pages) - len(idx), 'clean': clean,
           'score': round(100 * clean / max(1, len(idx))), 'in_sitemap': sm.count('<url>'),
           'site': {'robots': os.path.exists(os.path.join(ROOT, 'robots.txt')), 'sitemap': bool(sm), 'ads_txt': os.path.exists(os.path.join(ROOT, 'ads.txt')), 'https_canonical': True},
           'pages': out_pages}
    with open(os.path.join(ROOT, 'api', '_seo.json'), 'w') as fh: _json.dump(res, fh, separators=(',', ':'))
    print('seo audit: %d indexable, %d clean (%d%%)' % (len(idx), clean, res['score']))

if __name__ == '__main__':
    build_newlook_css(); home(); login(); account(); monitor(); speed(); status(); static_pages(); help_pages(); tools_pages(); sla_page(); internet_speed_page(); heatmap_page(); history_page(); insight_pages(); ip_page(); gameping_page(); site_pages_build(); seo_audit()
