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

def ico(path, extra=''):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"%s>%s</svg>' % (extra, path)
I_GLOBE = ico('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>')
I_RADIO = ico('<circle cx="12" cy="12" r="2"/><path d="M16.2 7.8a6 6 0 0 1 0 8.4M7.8 16.2a6 6 0 0 1 0-8.4M19 5a10 10 0 0 1 0 14M5 19A10 10 0 0 1 5 5"/>')
I_SHIELD = ico('<path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>')
I_ARROW = ico('<path d="M5 12h14M13 6l6 6-6 6"/>')
I_MAIL = ico('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>')
I_LOCK = ico('<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>')
I_USER = ico('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>')
I_SEARCH = ico('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>')
I_FB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8V6.5c0-.7.3-1 1-1h2V2h-3a4 4 0 0 0-4 4.2V8H7.5v3.5H10V22h4V11.5h2.7L17 8z"/></svg>'
I_IG = ico('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>')
I_X = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.9-6.3L5.3 21H2.2l7.2-8.3L2 3h6.4l4.4 5.8zm-1.1 16.2h1.7L7.3 4.7H5.5z"/></svg>'
I_TT = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 3a5 5 0 0 0 4 4.4v3.3a8 8 0 0 1-4-1.2v6.2a6 6 0 1 1-6-6c.3 0 .7 0 1 .1v3.4a2.7 2.7 0 1 0 1.8 2.5V3z"/></svg>'
I_YT = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3z"/></svg>'

NAV = [('Regional map', '/#global-pulse'), ('Top websites', '/#top-sites'), ('Gaming', '/#online-gaming'), ('Monitor', '/monitor'), ('Account', '/account'), ('How it works', '/#how-it-works')]

def head(title, desc, path, extra_head='', noindex=False):
    t = html.escape(title)
    d = html.escape(desc)
    canon = SITE + path
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ''
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
<meta property="og:image" content="{SITE}/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#060d0a">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/app.css">
{extra_head}
</head>
<body{{BODYATTR}}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap head-in">
<a class="brand" href="/" aria-label="siteupdown.com home">{INV}<span class="wordmark">siteupdown.com</span></a>
<nav class="nav" aria-label="Main">{''.join('<a href="%s">%s</a>' % (h, l) for l, h in NAV)}</nav>
<div class="head-tools"><button class="icon-btn" id="theme" type="button" aria-label="Switch theme"></button><div id="auth"></div></div>
</div></header>
<main id="main">
'''

def foot(scripts):
    links = [('Regional map', '/#global-pulse'), ('How it works', '/#how-it-works'), ('Monitor', '/monitor'), ('Account', '/account'), ('Contact', '/contact'), ('Legal notice', '/legal'), ('Privacy', '/privacy')]
    return f'''</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-brand">{INV}<span class="wordmark">siteupdown.com</span></div>
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

def write(name, content):
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
        f.write(content)
    print('wrote', name, len(content), 'bytes')

# ---------------------------------------------------------------- home
def ad(label, text):
    return f'<aside class="ad" aria-label="Advertisement"><small>{label}</small><span>{text}</span></aside>'

def home():
    jsonld = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"siteupdown.com","url":"https://siteupdown.com/","description":"Check whether a website is down for everyone or just you, with probes in twelve places around the world."}</script>'''
    h = head('siteupdown.com — Is the website down, or just you?', 'Paste any website address to see if it is down for everyone or only for you. We check from our server and from twelve probes in different countries, at the same time.', '/', jsonld)
    h = h.replace('{BODYATTR}', ' data-page="home"')
    share_btns = ''.join(f'<button class="btn small ghost" type="button" data-share="{k}"{" hidden" if k=="native" else ""}>{l}</button>' for k, l in [('copy', 'Copy link'), ('x', 'X'), ('fb', 'Facebook'), ('wa', 'WhatsApp'), ('native', 'Share…')])
    body = f'''
<section class="hero"><div class="wrap">
<span class="eyebrow"><i></i>A little clarity. In one click.</span>
<h1>Is it down — or just you<span class="dot">?</span></h1>
<p class="lead">Paste any address for a clear answer in seconds. Probes on six continents show whether a site is down for everyone or only for you.</p>
<form class="card checker" id="chk-form" aria-labelledby="checker-title" novalidate>
<div class="top"><span id="checker-title">{I_RADIO}Check a website</span><span class="live">Live from our server</span></div>
<div class="stack">
<div><label class="lbl" for="chk-input">Website address</label>
<div class="field">{I_GLOBE}<input id="chk-input" name="address" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="Type any website address, e.g. example.com" maxlength="300"></div></div>
<button class="btn block" id="chk-btn" type="submit"><span>Check website</span>{I_ARROW}</button>
<p class="err" id="chk-err" role="alert"></p>
<label class="check thorough"><input type="checkbox" id="chk-thorough"><span><b>Thorough check</b><small>Downloads part of the page and extracts the title, headers &amp; more</small></span></label>
<p class="assure">{I_SHIELD}No sign-up. No downloads. Just answers.</p>
</div></form>
<div class="recent-row" id="recent-wrap" hidden><div class="eyebrow">Your recent searches</div><div class="chips" id="recent-chips"></div></div>
<div class="recent-row"><div class="eyebrow">Try a website</div><div class="chips">
<button class="chip" type="button" data-h="google.com">google.com</button><button class="chip" type="button" data-h="youtube.com">youtube.com</button><button class="chip" type="button" data-h="github.com">github.com</button></div>
<p class="fine" style="margin-top:14px">Each check uses one server check plus twelve regional probes.</p></div>
</div></section>

<section id="global-pulse"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Global pulse · worldwide probes</span>
<h2>Down for everyone — or just you<span class="dot">?</span></h2>
<p class="lead">One run asks machines in different countries to fetch the same address at the same time. If they can all reach it, the problem is probably on your side.</p></div>
<div class="pulse-grid">
<div class="card map-card"><div class="map-wrap" id="map"><svg id="map-svg" role="img" aria-label="World map of probe results" preserveAspectRatio="xMidYMid meet"></svg>
<div class="map-empty" id="map-empty"><span>No regional run yet. Check a website and the map lights up.</span></div><div class="tip" id="tip" hidden></div></div>
<div class="legend" aria-label="Map legend"><span><i style="background:var(--green)"></i>Responded</span><span><i style="background:var(--amber)"></i>Blocked</span><span><i style="background:var(--red)"></i>Server error</span><span><i style="border:2px solid var(--grey)"></i>No connection</span></div>
<p class="fine" style="margin-top:10px">Hover or tap a marker for details. Regions without a probe are not claimed. Each run is a snapshot, not continuous monitoring. Probe network: <a href="https://globalping.io" rel="noopener">Globalping</a>.</p></div>
<div class="card verdict" aria-live="polite">
<div class="row-actions" style="justify-content:space-between;align-items:center"><span class="eyebrow" id="pulse-status">Standby</span><span id="v-pill"></span></div>
<div><div class="big" id="v-big">Waiting for probes</div><p class="note" id="v-sub" style="margin:6px 0 0">No address checked yet</p></div>
<dl class="stat" style="margin:0"><dt>Reachable</dt><dd id="s-reach">0/12</dd><dt>Median response</dt><dd id="s-med">—</dd><dt>Measured at</dt><dd id="s-at">—</dd></dl>
<div class="facts" id="facts" hidden></div>
<div class="row-actions"><button class="btn small" type="button" id="run-again" hidden>Run again</button><button class="btn small ghost" type="button" id="wl-add" hidden>Add to my watchlist</button></div>
<div class="share" id="share" hidden><span class="lbl eyebrow">Share</span>{share_btns}</div>
</div></div></div></section>

<section id="top-sites"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Watchlist · real requests</span><h2>Top websites<span class="dot">.</span></h2>
<p class="lead">The sites everyone checks first, probed every few minutes. Tap one to check it worldwide.</p></div>
<div class="tools"><div class="chips"><button class="chip" type="button" data-f="all" aria-pressed="true">All sites</button><button class="chip" type="button" data-f="issues" aria-pressed="false">Issues</button></div><span class="fine" id="top-updated"></span></div>
<div class="grid" id="top-grid"><div class="skeleton">Sweeping the watchlist…</div></div>
<p class="fine" style="margin-top:14px">A snapshot, not continuous uptime monitoring.</p>
</div></section>

<section id="online-gaming"><div class="wrap">
<div class="sec-head"><span class="eyebrow"><i></i>Games &amp; services</span><h2>Online gaming<span class="dot">.</span></h2>
<p class="lead">Is the game down, or is it your connection? Search a service or browse by type.</p></div>
<div class="tools"><div class="field" style="flex:1;min-width:240px;max-width:420px">{I_SEARCH}<input id="g-q" type="search" placeholder="Search gaming services" aria-label="Search gaming services" autocomplete="off"></div><span class="fine" id="g-count"></span></div>
<div class="chips" id="g-cats" style="margin-bottom:16px"></div>
<div class="grid" id="g-grid"><div class="skeleton">Loading gaming services…</div></div>
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
    scripts = '<script src="/assets/worldmap.js"></script>\n<script src="/assets/app.js"></script>\n<script src="/assets/home.js"></script>'
    write('index.html', h + body + foot(scripts))

# ---------------------------------------------------------------- login
def login():
    h = head('Sign in — siteupdown.com', 'Sign in or create a free siteupdown.com account to save your checks and build a watchlist.', '/login', noindex=True).replace('{BODYATTR}', ' data-page="login"')
    body = f'''
<section class="page"><div class="wrap narrow">
<div class="center"><span class="eyebrow"><i></i>Your account</span>
<h1 id="t-h" style="margin:14px 0">Sign in<span class="dot">.</span></h1><p class="lead" id="t-p" style="margin-bottom:26px">Save your checks, build a watchlist and keep your history across devices. The checker itself stays free and works without signing in.</p></div>
<p class="card" id="off" hidden>Accounts are not switched on yet. Please check back soon.</p>
<div class="card" id="card">
<div class="seg" id="seg" role="tablist"><button type="button" role="tab" data-v="signin" aria-selected="true">Sign in</button><button type="button" role="tab" data-v="create" aria-selected="false">Create account</button></div>
<div class="stack" id="gwrap" hidden><div id="gbtn"></div><p class="err" id="g-err" role="alert"></p><div class="or">or with email</div></div>

<form class="stack" id="v-signin" novalidate>
<div class="field">{I_MAIL}<input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div>
<div class="field">{I_LOCK}<input name="password" type="password" autocomplete="current-password" placeholder="Password" aria-label="Password" required></div>
<button class="btn block" type="submit"><span>Sign in</span>{I_ARROW}</button><p class="err" role="alert"></p>
<div class="links"><a href="#" data-go="forgot">Forgot password?</a><a href="#" data-go="create">Need an account? Create one</a></div></form>

<form class="stack" id="v-create" hidden novalidate>
<div class="field">{I_USER}<input name="name" type="text" autocomplete="name" placeholder="What should we call you?" aria-label="Name" maxlength="60" required></div>
<div class="field">{I_MAIL}<input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div>
<div class="field">{I_LOCK}<input name="password" type="password" autocomplete="new-password" placeholder="Password (8+ characters)" aria-label="Password" minlength="8" required></div>
<button class="btn block" type="submit"><span>Create account</span>{I_ARROW}</button><p class="err" role="alert"></p>
<p class="note">By creating an account you agree to our <a href="/legal">legal notice</a> and <a href="/privacy">privacy policy</a>.</p>
<div class="links"><a href="#" data-go="signin">Already have an account? Sign in</a></div></form>

<form class="stack" id="v-forgot" hidden novalidate>
<div class="field">{I_MAIL}<input name="email" type="email" autocomplete="email" placeholder="you@example.com" aria-label="Email" required></div>
<button class="btn block" type="submit"><span>Send reset link</span>{I_ARROW}</button><p class="err" role="alert"></p>
<div class="links"><a href="#" data-go="signin">Back to sign in</a></div></form>

<form class="stack" id="v-reset" hidden novalidate>
<div class="field">{I_LOCK}<input name="password" type="password" autocomplete="new-password" placeholder="New password (8+ characters)" aria-label="New password" minlength="8" required></div>
<button class="btn block" type="submit"><span>Save new password</span>{I_ARROW}</button><p class="err" role="alert"></p></form>

<div class="stack" id="v-sent" hidden><p class="note">Check your inbox, and your spam folder just in case.</p><div class="links"><a href="#" data-go="signin">Back to sign in</a></div></div>
</div></div></section>
'''
    scripts = '<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'
    write('login.html', h + body + foot(scripts))

# ---------------------------------------------------------------- account
def account():
    h = head('Your account — siteupdown.com', 'Your saved checks and account settings.', '/account', noindex=True).replace('{BODYATTR}', ' data-page="account"')
    body = f'''
<section class="page"><div class="wrap" id="acct" hidden>
<span class="eyebrow"><i></i>Your account</span>
<h1 style="margin:14px 0 6px">Account<span class="dot">.</span></h1><p class="note" id="a-since"></p>
<div class="tabs" id="tabs" role="tablist"><button type="button" role="tab" data-t="checks" aria-selected="true">My checks</button><button type="button" role="tab" data-t="settings" aria-selected="false">Settings</button></div>

<div id="p-checks"><div class="tools"><p class="note" style="margin:0">Your last 100 checks, saved while you were signed in. Only you can see them.</p><button class="btn small ghost" type="button" id="clear-checks" hidden>Clear all</button></div>
<div class="list" id="checks-list"><div class="skeleton">Loading your checks…</div></div></div>

<div id="p-settings" hidden class="stack" style="max-width:620px">
<form class="card stack" id="f-name" novalidate><h3>Profile</h3><p class="note" style="margin:0">Signed in as <b id="a-email"></b></p>
<div><label class="lbl" for="a-name">Display name</label><div class="field">{I_USER}<input id="a-name" type="text" maxlength="60" autocomplete="name"></div></div>
<button class="btn small" type="submit" style="justify-self:start">Save name</button><p class="err" role="alert"></p></form>
<div id="pw-card"><form class="card stack" id="f-pw" novalidate><h3>Change password</h3>
<div class="field">{I_LOCK}<input name="cur" type="password" autocomplete="current-password" placeholder="Current password" aria-label="Current password"></div>
<div class="field">{I_LOCK}<input name="nw" type="password" autocomplete="new-password" placeholder="New password (8+ characters)" aria-label="New password" minlength="8"></div>
<button class="btn small" type="submit" style="justify-self:start">Change password</button><p class="err" role="alert"></p></form></div>
<div class="card stack"><h3>Reset my data</h3><p class="note" style="margin:0">Clears your saved checks and your watchlist. Your account stays.</p><button class="btn small ghost" type="button" id="reset-data" style="justify-self:start">Reset my data</button></div>
<div class="card stack danger-zone"><h3>Delete account</h3><p class="note" style="margin:0">Permanently deletes your account and everything saved with it. This cannot be undone.</p>
<button class="btn small danger" type="button" id="del-open" style="justify-self:start">Delete my account</button>
<form class="stack" id="del-form" hidden novalidate><div class="field">{I_LOCK}<input name="confirm" type="text" placeholder="Type DELETE to confirm" aria-label="Type DELETE to confirm" autocomplete="off"></div>
<div id="del-pw-wrap"><div class="field">{I_LOCK}<input name="password" type="password" placeholder="Your password" aria-label="Your password" autocomplete="current-password"></div></div>
<button class="btn small danger" type="submit" style="justify-self:start">Permanently delete</button><p class="err" role="alert"></p></form></div>
</div>
</div></section>
'''
    scripts = '<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'
    write('account.html', h + body + foot(scripts))

# ---------------------------------------------------------------- monitor
def monitor():
    h = head('Monitor your websites — siteupdown.com', 'Build a personal watchlist and see at a glance which of your websites are up.', '/monitor').replace('{BODYATTR}', ' data-page="monitor"')
    body = f'''
<section class="page"><div class="wrap">
<span class="eyebrow"><i></i>Your watchlist</span>
<h1 style="margin:14px 0 10px">Monitor<span class="dot">.</span></h1>
<p class="lead" style="margin-bottom:26px">Keep an eye on the websites you care about. We re-check them every few minutes and show the latest result here.</p>
<div class="card" id="m-out" hidden><h3 style="margin-bottom:8px">Sign in to build your watchlist</h3><p class="note">A free account lets you save up to 25 sites and see their status at a glance. The checker on the home page stays free without one.</p>
<div class="row-actions" style="margin-top:14px"><a class="btn" href="/login?next=%2Fmonitor"><span>Sign in</span>{I_ARROW}</a><a class="btn ghost" href="/login?next=%2Fmonitor#create">Create account</a></div></div>
<div id="m-in" hidden>
<form class="stack" id="m-add" novalidate style="max-width:640px;margin-bottom:22px"><label class="lbl" for="m-input">Add a website</label>
<div class="row-actions" style="flex-wrap:nowrap"><div class="field" style="flex:1">{I_GLOBE}<input id="m-input" type="text" inputmode="url" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="example.com" maxlength="300"></div><button class="btn" type="submit"><span>Add</span></button></div><p class="err" id="m-err" role="alert"></p></form>
<div class="tools"><span class="fine" id="m-count"></span><span class="fine">Updates every minute while this page is open.</span></div>
<div class="list" id="m-list"><div class="skeleton">Loading your watchlist…</div></div></div>
</div></section>
'''
    scripts = '<script src="/assets/app.js"></script>\n<script src="/assets/pages.js"></script>'
    write('monitor.html', h + body + foot(scripts))

# ---------------------------------------------------------------- legal pages
def prose(name, title, desc, path, inner):
    h = head(title + ' — siteupdown.com', desc, path).replace('{BODYATTR}', '')
    body = f'<section class="page"><div class="wrap prose"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 20px">{title}<span class="dot">.</span></h1>{inner}<p style="margin-top:34px"><a href="/">&larr; Back to the website checker</a></p></div></section>'
    write(name, h + body + foot('<script src="/assets/app.js"></script>'))

def static_pages():
    prose('privacy.html', 'Privacy', 'How siteupdown.com handles checks, accounts, cookies and your data.', '/privacy', '''
<p>We keep this short and plain. siteupdown.com checks whether websites are reachable. We collect as little as we can to do that.</p>
<h2>Website checks</h2>
<p>When you check an address, our server fetches it. We store only the hostname, the result (status, HTTP code, response time) and the time in a public &ldquo;recently checked&rdquo; list. We do not publish who checked it. Regional checks send the hostname you entered to the Globalping probe network, which runs the request from machines around the world.</p>
<p>Share links keep a copy of the result so it can be shown to whoever you send it to. They expire after 30 days.</p>
<h2>Accounts</h2>
<p>Signing in is optional. If you create an account (with email and password, or with Google) we store your email address, display name and a hashed password (we never see or store your password itself). While you are signed in we also save your checks and your watchlist, and they are private to you. You can reset your data or delete your account at any time from the Account page; deleting removes everything saved with it.</p>
<p>If you sign in with Google, Google tells us your name and verified email address. We do not get access to anything else in your Google account.</p>
<h2>Cookies and storage</h2>
<p>We use essential storage to run the site: your theme, your cookie choice, your recent searches (kept on your device) and a sign-in cookie if you are signed in. Analytics and advertising cookies are optional and off until you allow them in &ldquo;Cookie settings&rdquo;. No advertising script is connected at the moment.</p>
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
<p>Regional probes run on the public <a href="https://globalping.io" rel="noopener">Globalping</a> network. Sign-in with Google uses Google&rsquo;s own sign-in service.</p>
<h2>Content</h2>
<p>Site names shown in lists are used only to identify the services being checked.</p>''')
    prose('contact.html', 'Contact', 'Get in touch with siteupdown.com.', '/contact', '''
<p>Found a bug, want a site added to the lists, or need your data removed? Send us an email and we will get back to you.</p>
<p><a href="mailto:hello@siteupdown.com">hello@siteupdown.com</a></p>
<p class="note">Please include the website address you checked if you are reporting a wrong result.</p>''')
    h = head('Page not found — siteupdown.com', 'That page could not be found.', '/404', noindex=True).replace('{BODYATTR}', '')
    write('404.html', h + '<section class="page"><div class="wrap narrow center"><span class="eyebrow"><i></i>Error 404</span><h1 style="margin:14px 0">Not found<span class="dot">.</span></h1><p class="lead">We checked everywhere. This page is down for everyone.</p><p style="margin-top:24px"><a class="btn" href="/"><span>Back to the checker</span></a></p></div></section>' + foot('<script src="/assets/app.js"></script>'))

if __name__ == '__main__':
    home(); login(); account(); monitor(); static_pages()
