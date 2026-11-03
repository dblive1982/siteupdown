#!/usr/bin/env python3
"""Builds the static pages (index, login, account, monitor, privacy, legal, contact, 404) with a shared header and footer.
Run:  python3 _tools/build.py   (from the project folder)"""
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
BRAND = '<img class="lf lf-d" src="/assets/logo-full-dark.png" alt="siteupdown.com" width="116" height="48"><img class="lf lf-l" src="/assets/logo-full-light.png" alt="" width="116" height="48">'

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

def head(title, desc, path, extra_head='', noindex=False):
    t = html.escape(title)
    d = html.escape(desc)
    canon = SITE + path
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">'
    return f'''<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
{robots}
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="siteupdown.com">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{SITE}/assets/og.png">
<meta name="application-name" content="siteupdown.com"><meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#130228">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32"><link rel="icon" href="/favicon-64.png" type="image/png" sizes="64x64"><link rel="manifest" href="/site.webmanifest"><link rel="icon" href="/favicon-192.png" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/app.css">
{extra_head}
</head>
<body{{BODYATTR}}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap head-in">
<a class="brand" href="/" aria-label="siteupdown.com home">{BRAND}</a>
<nav class="nav" aria-label="Main">{''.join('<a href="%s">%s</a>' % (h, l) for l, h in NAV)}</nav>
<div class="head-tools"><button class="icon-btn" id="theme" type="button" aria-label="Switch theme"></button><div id="auth"></div></div>
</div></header>
<main id="main">
'''

def foot(scripts):
    links = [('Regional map', '/#global-pulse'), ('How it works', '/#how-it-works'), ('Help centre', '/help/'), ('Tools', '/tools/'), ('Is it down?', '/is-it-down/'), ('Speed test', '/speed'), ('Monitor', '/monitor'), ('Account', '/account'), ('About', '/about'), ('For business', '/business'), ('Contact', '/contact'), ('Terms &amp; legal', '/legal'), ('Privacy', '/privacy')]
    return f'''</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-brand">{BRAND}</div>
<p class="note">Less refreshing. More knowing.</p>
<div class="socials" aria-label="Social media">
<a href="#" title="Facebook" aria-label="Facebook">{I_FB}</a><a href="#" title="Instagram" aria-label="Instagram">{I_IG}</a><a href="#" title="X" aria-label="X">{I_X}</a><a href="#" title="TikTok" aria-label="TikTok">{I_TT}</a><a href="#" title="YouTube" aria-label="YouTube">{I_YT}</a>
</div>
<div class="foot-links">{''.join('<a href="%s">%s</a>' % (h, l) for l, h in links)}<button type="button" data-cookie-settings>Cookie settings</button></div>
<p class="fine">&copy; <span data-year>2026</span> siteupdown.com. An independent website checker, not affiliated with the sites it checks. Regional probes use the public <a href="https://globalping.io" rel="noopener">Globalping</a> network.</p>
</div></footer>
{scripts}
</body>
</html>
'''

import hashlib, re as _re
def _ver():
    h = hashlib.md5()
    for n in ('app.css', 'app.js', 'home.js', 'pages.js', 'worldmap.js', 'live.js', 'sitepage.js'):
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
_ICO['\U0001F50D'] = '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>'
def _svgicons(c):
    def r(m):
        e = _html.unescape(m.group(1)).rstrip('\ufe0f')
        return '<span class="ti"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg></span>' % _ICO[e] if e in _ICO else m.group(0)
    return _re.sub(r'<span class="ti">([^<]{1,9})</span>', r, c)

def write(name, content):
    if name.endswith('.html'):
        content = _svgicons(content)
        v = _ver()
        content = _re.sub(r'(/assets/(?:app\.css|app\.js|home\.js|pages\.js|worldmap\.js|live\.js|sitepage\.js))(?=")', r'\1?v=' + v, content)
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
    jsonld = '<script type="application/ld+json">{"@context": "https://schema.org", "@graph": [{"@type": "WebSite", "@id": "https://siteupdown.com/#website", "name": "siteupdown.com", "url": "https://siteupdown.com/", "description": "Check whether a website is down for everyone or just you, with probes in twelve places around the world.", "inLanguage": "en-GB"}, {"@type": "Organization", "@id": "https://siteupdown.com/#org", "name": "siteupdown.com", "url": "https://siteupdown.com/", "logo": "https://siteupdown.com/android-chrome-512.png", "email": "hello@siteupdown.com"}, {"@type": "WebApplication", "name": "siteupdown.com website checker", "url": "https://siteupdown.com/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"}}]}</script>\n<script type="application/ld+json">{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "How do I know if a website is down for everyone or just me?", "acceptedAnswer": {"@type": "Answer", "text": "Paste the address into the checker. We load it from our own server and from twelve probes in different countries at the same moment. If every probe reaches it, the site is up and the problem is probably on your side (your network, DNS, browser or device). If most fail, it is down for everyone."}}, {"@type": "Question", "name": "Why does it say Timeout or Inconclusive instead of Down?", "acceptedAnswer": {"@type": "Answer", "text": "A slow or blocked response is not proof that a site is down. We only call a site Confirmed down when the server returns errors on two attempts. Timeouts and blocked requests are reported as such so you are never told something we cannot be sure of."}}, {"@type": "Question", "name": "Is siteupdown.com free to use?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. The checker, speed test and status pages are free and need no sign-up. A free account lets you keep a watchlist of up to 25 sites, see their uptime history and get an email when one goes down or comes back."}}, {"@type": "Question", "name": "How does the website speed test work?", "acceptedAnswer": {"@type": "Answer", "text": "It loads the page three times from our server and reports the median. You see how long finding the server, connecting, securing the connection, waiting and downloading each took, plus page size, compression, protocol and a grade with plain-English tips."}}, {"@type": "Question", "name": "Can I check an SSL certificate or a domain\'s expiry date?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. Every check shows the SSL certificate (who issued it, when it expires, whether it covers the address) as well as DNS records, redirects and the domain registration expiry date."}}, {"@type": "Question", "name": "How often are monitored sites checked?", "acceptedAnswer": {"@type": "Answer", "text": "Sites on a watchlist are re-checked about every minute. A site is only reported as down after two failed checks in a row, which avoids false alarms."}}]}</script>'
    h = head('siteupdown.com — Is the website down, or just you?', 'Paste any website address to see if it is down for everyone or only for you. We check from our server and from twelve probes in different countries, at the same time.', '/', jsonld)
    h = h.replace('{BODYATTR}', ' data-page="home"')
    report_kinds = ''.join('<button type="button" class="rk" data-kind="%s">%s</button>' % (k, l) for k, l in SP.KIND_LABELS)
    share_btns = ''.join(f'<button class="sb{" wide" if k=="copy" else ""}" type="button" data-share="{k}" title="{t}" aria-label="{t}"{" hidden" if k=="native" else ""}>{i}{("<span>"+t+"</span>") if k=="copy" else ""}</button>' for k, t, i in [('copy', 'Copy link', I_LINK), ('x', 'Share on X', I_X), ('fb', 'Share on Facebook', I_FB), ('wa', 'Share on WhatsApp', I_WA), ('native', 'More share options', I_SHARE)])
    body = f'''
<section class="hero"><div class="wrap">
<svg class="rings" viewBox="0 0 400 400" aria-hidden="true"><circle cx="200" cy="200" r="60"/><circle cx="200" cy="200" r="130"/><circle cx="200" cy="200" r="198"/><rect x="262" y="52" width="9" height="9" fill="var(--green)"/></svg>
<span class="eyebrow"><i></i>A little clarity. In one click.</span>
<h1>Is it down — or <span class="hl">just you?</span></h1>
<p class="lead">Paste any address for a clear answer in seconds, then watch real probes on six continents show whether a site is down for everyone — or just you.</p>
<form class="card checker" id="chk-form" aria-labelledby="checker-title" novalidate>
<div class="top"><span id="checker-title">{I_RADIO}Check a website <em>· Live from our server</em></span><span class="live">Live check</span></div>
<div class="chk-row">
<div class="field">{I_GLOBE}<input id="chk-input" name="address" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="Website address, e.g. example.com" maxlength="300" aria-label="Website address"></div>
<button class="btn" id="chk-btn" type="submit"><span>Check website</span>{I_ARROW}</button></div>
<p class="err" id="chk-err" role="alert"></p>
<div class="chk-foot">
<p class="assure">{I_SHIELD}No sign-up. Just answers.</p></div>
</form>
<div class="recent-row" id="recent-wrap" hidden><div class="eyebrow">Your recent searches</div><div class="chips" id="recent-chips"></div></div>
<div class="try-row"><span class="eyebrow">Try a website</span><div class="chips">
<button class="chip" type="button" data-h="google.com">google.com<span class="ne">↗</span></button><button class="chip" type="button" data-h="youtube.com">youtube.com<span class="ne">↗</span></button><button class="chip" type="button" data-h="github.com">github.com<span class="ne">↗</span></button></div></div>
<div class="try-row app-row"><span class="eyebrow">Checking an app?</span><div class="chips">
<a class="chip" href="/is-whatsapp-down">WhatsApp</a><a class="chip" href="/is-instagram-down">Instagram</a><a class="chip" href="/is-spotify-down">Spotify</a><a class="chip" href="/is-roblox-down">Roblox</a><a class="chip" href="/is-it-down/">All apps &amp; sites<span class="ne">→</span></a>
</div></div>
<p class="rule-note"><span>One server check, twelve regional probes. No sign-up, no guesswork.</span></p>
</div></section>

<section id="global-pulse"><div class="wrap">
<div class="card pulse-card" aria-live="polite">
<div class="pc-head"><div><span class="eyebrow"><i></i>Global pulse · worldwide probes</span>
<h2>Down for everyone — or just you<span class="dot">?</span></h2>
<p class="lead">One run asks machines in different countries to fetch the same address at the same time. If they can all reach it, the problem is probably on your side.</p></div>
<div class="pc-actions"><span class="statchip"><i></i><span id="pulse-status">Standby</span></span><button class="btn small ghost" type="button" id="run-again" hidden>Run again</button></div></div>
<div class="strip">
<div class="cell wide"><span class="k">Verdict</span><b id="v-big">Waiting for probes</b><small id="v-sub">No address checked yet</small><span id="v-pill"></span></div>
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
<div class="sp-card rep-box" id="rep-box" hidden><div class="sp-rhead"><b id="rb-title">Problems reported by visitors</b><span id="rb-level" class="sp-level"></span></div><div class="sp-ranges" id="rb-ranges" role="group" aria-label="Time range"><button type="button" class="rg on" data-range="24h" aria-pressed="true">24 hours</button><button type="button" class="rg" data-range="7d" aria-pressed="false">7 days</button><button type="button" class="rg" data-range="30d" aria-pressed="false">30 days</button><button type="button" class="rg" data-range="1y" aria-pressed="false">1 year</button></div><div class="sp-rdate" id="rb-date"></div><div class="sp-chart small" id="rb-chart"></div><div class="sp-axis" id="rb-axis"><span>24 hours ago</span><span>Now</span></div><p class="sp-rdetail" id="rb-detail"></p><div class="sp-kinds" id="rb-kinds"></div><div class="sp-report"><button type="button" class="btn small ghost" id="rb-btn"><span>Report a problem</span></button><div class="sp-rpick" id="rb-pick" hidden><p>What is going wrong? Pick everything that applies.</p><div class="sp-rbtns">{report_kinds}</div><p class="sp-rsendrow"><button type="button" class="btn small rsend" disabled><span>Send report</span></button></p></div><p class="sp-rmsg" id="rb-msg" role="status"></p></div></div>
<div class="share" id="share" hidden><span class="eyebrow">Share this check</span><div class="sbtns">{share_btns}</div></div></div>
</div>

<div class="charts" id="charts">
<div class="card chart"><h3>Response time by region</h3><p class="fine">Lower is faster. Colour shows the outcome. The two-letter codes are countries: hover or tap one for its name.</p><div id="ch-bars" class="ch-empty">Run a check to see this chart.</div></div>
<div class="card chart"><h3>Probe outcomes</h3><p class="fine">How the twelve probes fared.</p><div id="ch-donut" class="ch-empty">Run a check to see this chart.</div></div>
<div class="card chart"><h3>Speed range</h3><p class="fine">Our server against the worldwide spread.</p><div id="ch-range" class="ch-empty">Run a check to see this chart.</div></div>
</div>
<div class="card more-det" id="more-det" hidden><h3>Technical details</h3><p class="fine">Certificate, DNS and what we saw when we fetched the page.</p><div id="ssl" hidden></div><div id="dns" hidden></div><div class="facts" id="facts" hidden></div></div>
</div></section>

<section id="recent-outages"><div class="wrap"><div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Live · updates every minute</span><h2 id="ro-h">Outages right now<span class="dot">.</span></h2>
<p class="lead" id="ro-lead">Popular sites that are down at this moment, with any that came back in the last 24 hours underneath.</p></div></div>
<ul class="ro-list" id="ro-list"><li class="skeleton">Loading&hellip;</li></ul>
<p class="fine" style="margin-top:14px">A site counts as down after two failed checks in a row, so times are approximate and shown in your time zone.</p>
</div></div></section>

<section id="top-sites"><div class="wrap"><div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Watchlist · real requests</span><h2>Top websites<span class="dot">.</span></h2>
<p class="lead">A rolling sweep of the sites people ask about most. Every line is a real request from this server — a red entry is one that answered with an error or not at all.</p></div>
<div class="pc-actions col"><div class="seg2"><button type="button" data-f="all" aria-pressed="true">All sites</button><button type="button" data-f="issues" aria-pressed="false" id="f-issues">Issues</button></div>
<span class="fine" id="top-count"></span><button class="btn small ghost" type="button" id="top-refresh">{I_REFRESH}Refresh</button></div></div>
<div class="rows" id="top-grid"><div class="skeleton">Sweeping the watchlist…</div></div>
<p class="fine" id="top-updated" style="margin-top:14px">A snapshot, not continuous uptime monitoring.</p>
</div></div></section>

<section id="online-gaming"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Games &amp; services</span><h2>Online gaming<span class="dot">.</span></h2>
<p class="lead">Is the game down, or is it your connection? Search a service or browse by type.</p></div>
<div class="tools"><div class="field" style="flex:1;min-width:240px;max-width:420px">{I_SEARCH}<input id="g-q" type="search" placeholder="Search gaming services" aria-label="Search gaming services" autocomplete="off"></div><span class="fine" id="g-count"></span></div>
<div class="chips" id="g-cats" style="margin-bottom:16px"></div>
<div class="rows" id="g-grid"><div class="skeleton">Loading gaming services…</div></div>
<div class="pager"><button class="btn small ghost" type="button" id="g-prev">Prev</button><button class="btn small ghost" type="button" id="g-next">Next</button></div>
</div></section>

<div class="wrap">{ad('ADVERTISEMENT', 'A little space that keeps siteupdown.com free.')}</div>

<section id="recent"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Live feed</span><h2>Recently checked websites<span class="dot">.</span></h2>
<p class="lead">What people have just checked. A snapshot in time, not a promise of uptime.</p></div>
<div class="card table-wrap"><table class="feed"><thead><tr><th>Website</th><th>Status</th><th>Last checked</th></tr></thead><tbody id="feed-body"><tr><td colspan="3" class="skeleton">Loading recently checked websites…</td></tr></tbody></table></div>
</div></section>

<section><div class="wrap">
<div class="sec-head"><h2>Clear signals. No false alarms<span class="dot">.</span></h2></div>
<div class="defs">
<div class="def"><span class="pill up">Up</span><p class="note" style="margin:0">The site responded to our server.</p></div>
<div class="def"><span class="pill down">Confirmed down</span><p class="note" style="margin:0">Repeated server errors, verified on two attempts.</p></div>
<div class="def"><span class="pill timeout">Timeout</span><p class="note" style="margin:0">A slow or missing response. That isn't proof of downtime.</p></div>
<div class="def"><span class="pill inconclusive">Inconclusive</span><p class="note" style="margin:0">The check was blocked or couldn't verify the connection.</p></div>
</div></div></section>

<div class="wrap">{ad('ADVERTISEMENT', 'Space for a little support.')}</div>

<section id="tools"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>More than a status check</span><h2>Tools for every website<span class="dot">.</span></h2></div>
<div class="tools-grid">
<a class="tool" href="/speed"><span class="ti">⚡</span><h3>Website speed test</h3><p>See how fast a page loads, where the time goes, and what to fix. Free, no sign-up.</p><span class="tgo">Test a site →</span></a>
<a class="tool" href="/monitor"><span class="ti">🔔</span><h3>Monitor &amp; email alerts</h3><p>Watch up to 25 sites and get an email when one goes down and when it is back.</p><span class="tgo">Open Monitor →</span></a>
<a class="tool" href="#checker-title" onclick="document.getElementById('chk-input').focus()"><span class="ti">🔒</span><h3>SSL, DNS &amp; domain expiry</h3><p>Every check shows the certificate, DNS records, redirects and when the domain expires.</p><span class="tgo">Run a check →</span></a>
<a class="tool" href="/monitor"><span class="ti">📈</span><h3>Uptime history &amp; status pages</h3><p>Uptime over 24 hours, 7 and 30 days, with a public status page you can share.</p><span class="tgo">Start tracking →</span></a>
</div>
<p class="tools-more"><a class="btn ghost" href="/tools/"><span>See all free tools</span></a></p></div></section>

<section id="help-teaser"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Help centre</span><h2>Plain-English guides<span class="dot">.</span></h2></div>
<div class="tools-grid">
<a class="tool" href="/help/website-not-loading-checklist"><span class="ti">🧭</span><h3>Website not loading?</h3><p>A step-by-step checklist to find out whether it is the site or you.</p><span class="tgo">Read the guide →</span></a>
<a class="tool" href="/help/server-errors-500-502-503-504"><span class="ti">🛠</span><h3>500, 502, 503, 504 errors</h3><p>What each server error means and what to try.</p><span class="tgo">Read the guide →</span></a>
<a class="tool" href="/help/ssl-certificate-errors"><span class="ti">🔒</span><h3>SSL certificate errors</h3><p>Why browsers warn that a connection is not private, and how to fix it.</p><span class="tgo">Read the guide →</span></a>
<a class="tool" href="/help/"><span class="ti">📚</span><h3>All help guides</h3><p>Error codes, fixes, DNS, uptime and speed, in one place.</p><span class="tgo">Open the help centre →</span></a>
</div></div></section>

<section id="faq"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Questions</span><h2>Frequently asked questions<span class="dot">.</span></h2></div>
<div class="faq">
<details><summary>How do I know if a website is down for everyone or just me?</summary><p>Paste the address into the checker. We load it from our own server and from twelve probes in different countries at the same moment. If every probe reaches it, the site is up and the problem is probably on your side (your network, DNS, browser or device). If most fail, it is down for everyone.</p></details>
<details><summary>Why does it say Timeout or Inconclusive instead of Down?</summary><p>A slow or blocked response is not proof that a site is down. We only call a site Confirmed down when the server returns errors on two attempts. Timeouts and blocked requests are reported as such so you are never told something we cannot be sure of.</p></details>
<details><summary>Is siteupdown.com free to use?</summary><p>Yes. The checker, speed test and status pages are free and need no sign-up. A free account lets you keep a watchlist of up to 25 sites, see their uptime history and get an email, a Telegram message or a Slack or Discord message when one goes down or comes back.</p></details>
<details><summary>How does the website speed test work?</summary><p>It loads the page three times from our server and reports the median. You see how long finding the server, connecting, securing the connection, waiting and downloading each took, plus page size, compression, protocol and a grade with plain-English tips.</p></details>
<details><summary>Can I check an SSL certificate or a domain's expiry date?</summary><p>Yes. Every check shows the SSL certificate (who issued it, when it expires, whether it covers the address) as well as DNS records, redirects and the domain registration expiry date.</p></details>
<details><summary>How often are monitored sites checked?</summary><p>Sites on a watchlist are re-checked about every minute. A site is only reported as down after two failed checks in a row, which avoids false alarms.</p></details>
</div></div></section>

<section id="how-it-works"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Behind the signal</span><h2>Less guesswork. More peace of mind<span class="dot">.</span></h2></div>
<div class="steps">
<div class="step"><span class="n">01</span><h3>We dispatch probes</h3><p>Machines in different countries fetch the address at the same moment and report back status codes and timings.</p></div>
<div class="step"><span class="n">02</span><h3>We compare regions</h3><p>If every region responds, the site is up for the wider internet. If only some do, the map shows where it stops.</p></div>
<div class="step"><span class="n">03</span><h3>You get the full picture</h3><p>Status codes, timings, a cautious verdict and a share link you can send to someone.</p></div>
</div>
<p class="center" style="margin-top:28px"><a class="btn" href="#checker-title" onclick="document.getElementById('chk-input').focus()"><span>Check a website</span>{I_ARROW}</a></p>
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
<button class="btn block" type="submit"><span>Create account</span></button><p class="err" role="alert"></p>
<p class="note">By creating an account you agree to our <a href="/legal">legal notice</a> and <a href="/privacy">privacy policy</a>.</p>
<p class="alt">Already have an account? <a href="#" data-go="signin">Sign in</a></p></form>

<form class="stack" id="v-forgot" hidden novalidate>
<label class="fl"><span>Email</span><div class="field"><input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div></label>
<button class="btn block" type="submit"><span>Send reset link</span></button><p class="err" role="alert"></p>
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
<div class="pc-head"><div><span class="eyebrow"><i></i>Your watchlist</span><h2>Monitor<span class="dot">.</span></h2>
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
</div></div></div></section>
'''
    write('speed.html', h + body + foot('<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'))

# ---------------------------------------------------------------- status page
def status():
    h = head('Website status — siteupdown.com', 'Live status, uptime and recent outages for a website, checked every few minutes by siteupdown.com.', '/status').replace('{BODYATTR}', ' data-page="status"')
    body = f'''
<section class="page"><div class="wrap">
<div class="card toplist">
<div class="pc-head"><div><span class="eyebrow"><i></i>Status page</span><h1 id="st-h" style="margin:10px 0 6px">Website status<span class="dot">.</span></h1><p class="lead" id="st-p">Loading…</p></div><div id="st-pill"></div></div>
<div class="pad" id="st-body"><div class="skeleton">Loading status…</div></div>
</div></div></section>
'''
    write('status.html', h + body + foot('<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'))

# ---------------------------------------------------------------- legal pages
def prose(name, title, desc, path, inner):
    h = head(title + ' — siteupdown.com', desc, path).replace('{BODYATTR}', '')
    body = f'<section class="page"><div class="wrap prose"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 20px">{title}<span class="dot">.</span></h1>{inner}<p style="margin-top:34px"><a href="/">&larr; Back to the website checker</a></p></div></section>'
    write(name, h + body + foot('<script src="/assets/app.js"></script>'))

def static_pages():
    prose('about.html', 'About', 'About siteupdown.com: a free, independent website status, speed and uptime checker.', '/about', '''
<p class="lead">siteupdown.com answers one question quickly: is this website down for everyone, or is it just you?</p>
<h2>What we do</h2>
<p>When a page will not load, it is hard to tell whether the site is broken or something on your side is. You paste the address, and we load it from our own server and from twelve probes in different countries at the same moment. If every probe reaches it, the site is up and the problem is probably your network, DNS, browser or device. If most fail, it is down for everyone.</p>
<h2>More than a status check</h2>
<p>Every check also shows the SSL certificate, DNS records, redirects and the domain&rsquo;s registration expiry. The <a href="/speed">speed test</a> times where a page&rsquo;s load goes. With a free account you can keep a <a href="/monitor">watchlist</a>, see uptime history and get an email when a site goes down or comes back, and each monitored site has a public status page.</p>
<h2>How we check, and how we try to be fair</h2>
<p>We would rather say &ldquo;not sure&rdquo; than be wrong. Here is what happens when you check a site:</p>
<ul>
<li><b>Our own server</b> asks the site for its page. If the address gets no reply, we also try the other form (with or without &ldquo;www&rdquo;), because some sites only answer on one.</li>
<li><b>Twelve probes</b> in different countries ask the same thing at the same moment, so you can see whether it is down for everyone or only in some places.</li>
<li><b>We call a site down only on real evidence</b>, such as repeated server errors, or a site that was answering and then stops. Before we record an outage we ask probes in other countries as well, and if any of them can reach it, it is not counted as down.</li>
<li><b>Silence is not proof.</b> Some large sites quietly ignore automated checks. When nothing answers and we have not seen the site working lately, we say &ldquo;no answer&rdquo; and &ldquo;we can&rsquo;t be sure&rdquo;, and give you a link to try the site yourself, instead of showing a false red alert.</li>
<li><b>We use honest checks.</b> Our checker says who it is, and we do not disguise it as a browser to get past a site&rsquo;s protection.</li>
</ul>
<p>The live graph samples a site about every ten seconds while someone is watching it, and we keep daily records so you can see the last 24 hours, 7 days and 12 months, with a written summary of recent outages. Problem reports from visitors show what real people are seeing, and every result is a snapshot of one moment, which we say so.</p>
<h2>Independent</h2>
<p>siteupdown.com is not affiliated with the websites, games or services it checks. Regional probes run on the public <a href="https://globalping.io" rel="noopener">Globalping</a> network. The site is supported by advertising, so it stays free to use.</p>
<h2>Get in touch</h2>
<p>Found a bug or want a site added to the lists? <a href="/contact">Contact us</a>.</p>''')
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
<p>After a check, and on the &ldquo;Is it down?&rdquo; pages, you can report a problem with a site. A report stores the site, the type of problem, the time, and a one-way hash of your network address, which is used only to limit repeat reports and is erased after two days. The report itself (site, type, time and the country you are in, worked out from your network or your device&rsquo;s time zone, with nothing that identifies you) is kept for up to three years so the report history can be shown. We do not ask for your name or email address for reports, and reports are shown only as anonymous counts.</p>
<h2>Cookies and storage</h2>
<p>We use essential storage to run the site: your theme, your cookie choice, your recent searches (kept on your device) and a sign-in cookie if you are signed in. Analytics and advertising cookies are optional and off until you allow them in &ldquo;Cookie settings&rdquo;. No advertising script is connected at the moment.</p>
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
<script src="/assets/contact.js"></script>''')
    h = head('Admin — siteupdown.com', 'Admin area.', '/admin', noindex=True).replace('{BODYATTR}', '')
    write('admin.html', h + '''<section class="page adm-page"><div class="wrap"><div id="adm-root"><p class="lead">Loading&hellip;</p></div></div></section>''' + foot('<script src="/assets/app.js"></script><script src="/assets/admin.js"></script>'))
    h = head('Page not found — siteupdown.com', 'That page could not be found.', '/404', noindex=True).replace('{BODYATTR}', '')
    write('404.html', h + '<section class="page"><div class="wrap narrow center"><span class="eyebrow"><i></i>Error 404</span><h1 style="margin:14px 0">Not found<span class="dot">.</span></h1><p class="lead">We checked everywhere. This page is down for everyone.</p><p style="margin-top:24px"><a class="btn" href="/"><span>Back to the checker</span></a></p></div></section>' + foot('<script src="/assets/app.js"></script>'))



# ---------------------------------------------------------------- "Is X down?" pages
import site_pages as SP

def tile(name, host):
    return ''  # letter tiles removed; the name speaks for itself

def site_pages_build():
    hosts = [h for _, h, _, _ in SP.SITES]
    assert len(hosts) == len(set(hosts)), 'duplicate host in SITES'
    slugs = [SP.slug(n) for n, _, _, _ in SP.SITES]
    assert len(slugs) == len(set(slugs)), 'duplicate slug in SITES'
    # the list the PHP side reads (api/_ files are blocked from the web by .htaccess)
    with open(os.path.join(ROOT, 'api', '_sitepages.json'), 'w') as f:
        _json.dump({h: dict({'name': n, 'page': SP.page_path(n), 'cat': c}, **({'app': [list(x) for x in SP.APPS[n]]} if n in SP.APPS else {})) for n, h, c, _ in SP.SITES}, f, separators=(',', ':'))
    kinds = ''.join('<button type="button" class="rk" data-kind="%s">%s</button>' % (k, l) for k, l in SP.KIND_LABELS)
    for name, host, cat, blurb in SP.SITES:
        n = html.escape(name); hh = html.escape(host)
        path = SP.page_path(name)
        catname, tips = SP.CATS[cat]
        title = 'Is %s down? Live status and outage reports' % name
        desc = 'Is %s (%s) down right now? See the live status checked from our servers, response time, uptime and problems reported by other visitors in the last 24 hours.' % (name, host)
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
        h = head(title + ' — siteupdown.com', desc, path, extra).replace('{BODYATTR}', '')
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
            '<div id="lv-slot" data-host="%s"></div>' % hh +
            '<p class="lead" style="margin-top:22px">%s</p>' % blurb +
            '<h2>Are other people having problems with %s?</h2>' % n +
            '<div class="sp-card" id="sp-reports"><div class="sp-rhead"><b id="sp-rtotal">Problem reports</b><span id="sp-rlevel" class="sp-level"></span></div>'
            '<div class="sp-ranges" id="sp-ranges" role="group" aria-label="Time range"><button type="button" class="rg on" data-range="24h" aria-pressed="true">24 hours</button><button type="button" class="rg" data-range="7d" aria-pressed="false">7 days</button><button type="button" class="rg" data-range="30d" aria-pressed="false">30 days</button><button type="button" class="rg" data-range="1y" aria-pressed="false">1 year</button></div><div class="sp-rdate" id="sp-date"></div><div class="sp-chart" id="sp-chart" role="group" aria-label="Problem reports per hour over the last 24 hours"></div>'
            '<div class="sp-axis"><span>24 hours ago</span><span>Now</span></div><p class="sp-rdetail" id="sp-detail">Tap or hover a bar to see what was reported.</p><div class="sp-kinds" id="sp-kinds"></div>'
            '<div class="sp-report"><button type="button" class="btn small" id="sp-rbtn"><span>I am having a problem with %s</span></button>' % n +
            '<div class="sp-rpick" id="sp-rpick" hidden><p>What is going wrong? Pick everything that applies.</p><div class="sp-rbtns">%s</div><p class="sp-rsendrow"><button type="button" class="btn small rsend" disabled><span>Send report</span></button></p></div><p class="sp-rmsg" id="sp-rmsg" role="status"></p></div>' % kinds +
            '<p class="note">Reports are anonymous and unverified, and each visitor can report each problem once every 30 minutes. They show how many people say they are affected, not why.</p></div>'
            '<h2>If %s is not loading for you</h2><ul>%s</ul>' % (n, tipsli) +
            '<p>Still stuck? Work through our <a href="/help/website-not-loading-checklist">website not loading checklist</a>, or read <a href="/help/down-for-some-people-not-others">why a site can be down for some people and not others</a>.</p>'
            '<h2>Check %s from twelve places</h2><p>This page shows our latest scheduled check. To test %s right now from our server and from twelve countries, run a live check.</p>' % (n, hh) +
            '<p><a class="btn" href="/?q=%s"><span>Check %s now</span></a> <a class="btn ghost" href="/status/%s"><span>Full status page</span></a></p>' % (hh, n, hh) +
            '<h2>Questions about %s</h2><div class="faq">%s</div>' % (n, faqh) +
            '<h2>Other %s checks</h2><ul>%s</ul>' % (html.escape(catname.lower()), rel) +
            '<p class="note">Category: %s. siteupdown.com is independent and is not affiliated with %s.</p>' % (html.escape(catname), n) +
            '<p style="margin-top:20px"><a href="/is-it-down/">&larr; All site status pages</a></p></div></section>')
        write(path.lstrip('/') + '.html', h + body + foot('<script src="/assets/app.js"></script><script src="/assets/sitepage.js"></script><script src="/assets/live.js"></script>'))
    # directory
    groups = ''
    order = ['social', 'video', 'search', 'work', 'shopping', 'news', 'gaming']
    for cat in order:
        items = [(n, h, p) for n, h, c, p in SP.SITES if c == cat]
        li = ''.join('<li data-host="%s" data-name="%s"><i class="dot-s"></i>%s<a href="%s">%s</a><span class="rep"></span></li>' % (html.escape(h), html.escape(n.lower()), tile(n, h), SP.page_path(n), html.escape(n) + (' <em class="apptag">App</em>' if n in SP.APPS else '')) for n, h, p in items)
        groups += '<section class="dgroup"><h2>%s</h2><ul>%s</ul></section>' % (html.escape(SP.CATS[cat][0]), li)
    ld = '<script type="application/ld+json">' + _json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Is it down? Status of popular websites", "url": SITE + "/is-it-down/"}) + '</script>'
    h = head('Is it down? Live status of popular websites — siteupdown.com', 'Live status for popular websites, apps and games, checked every few minutes from our servers, with problem reports from other visitors.', '/is-it-down/', ld).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose sitedir" data-sp="dir"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 12px">Is it down<span class="dot">?</span></h1>'
            '<p class="lead">Live status for popular websites, apps and games. Each page shows our latest check, response time and uptime, and the problems other visitors have reported in the last 24 hours.</p>'
            '<div class="sp-card" id="sp-top" hidden><b>Most reported right now</b><ul id="sp-toplist"></ul></div>'
            '<label class="sr" for="sp-find">Find a site</label><input id="sp-find" class="sp-find" type="search" placeholder="Find a site, e.g. Netflix" autocomplete="off">'
            + groups +
            '<p>Not listed? <a href="/">Check any website</a> from twelve places.</p></div></section>')
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
        items = ''.join('<li><a href="/help/%s">%s</a></li>' % (a['slug'], html.escape(a['title'])) for a in ARTICLES if a['cat'] == key)
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
                '<div class="cta-box"><b>Check a website now</b><p>Is it down for everyone, or just you? Paste an address and we test it from twelve places.</p><a class="btn" href="/"><span>Open the checker</span></a></div>'
                '<h2>Related guides</h2><ul>' + rel + '</ul>'
                '<p class="note">Last updated 2 November 2026. Written by the siteupdown.com team. <a href="/contact">Spotted a mistake?</a></p>'
                '<p style="margin-top:20px"><a href="/help/">&larr; All help guides</a></p></div></section>')
        write('help/' + a['slug'] + '.html', h + body + foot('<script src="/assets/app.js"></script>'))
    # sitemap
    urls = [('/', 'daily', '1.0'), ('/speed', 'monthly', '0.8'), ('/monitor', 'monthly', '0.7'), ('/help/', 'weekly', '0.8')] + [('/help/' + a['slug'], 'monthly', '0.7') for a in ARTICLES] + [('/is-it-down/', 'daily', '0.8'), ('/tools/', 'monthly', '0.8')] + [('/tools/' + t['slug'], 'monthly', '0.7') for t in TOOLS] + [(SP.page_path(n), 'daily', '0.6') for n, _, _, _ in SP.SITES] + [('/about', 'monthly', '0.5'), ('/business', 'monthly', '0.5'), ('/contact', 'yearly', '0.3'), ('/privacy', 'yearly', '0.3'), ('/legal', 'yearly', '0.3')]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('<url><loc>%s%s</loc><lastmod>2026-11-02</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>\n' % (SITE, u, c, p) for u, c, p in urls) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)


# ---------------------------------------------------------------- tools
def tools_pages():
    os.makedirs(os.path.join(ROOT, 'tools'), exist_ok=True)
    # hub
    cards = ''.join('<a class="tool" href="/tools/%s"><span class="ti">%s</span><h3>%s</h3><p>%s</p><span class="tgo">Open the tool &rarr;</span></a>' % (t['slug'], t['icon'], html.escape(t['name']), t['short']) for t in TOOLS)
    extra_cards = ('<a class="tool" href="/"><span class="ti">&#128269;</span><h3>Is it down?</h3><p>Check any website from our server and twelve places around the world.</p><span class="tgo">Open the checker &rarr;</span></a>'
                   '<a class="tool" href="/speed"><span class="ti">&#9889;</span><h3>Website speed test</h3><p>See how fast a page loads and where the time goes.</p><span class="tgo">Test a site &rarr;</span></a>'
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

if __name__ == '__main__':
    home(); login(); account(); monitor(); speed(); status(); static_pages(); help_pages(); tools_pages(); site_pages_build()
