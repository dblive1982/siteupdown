/* siteupdown.com — shared behaviour: theme, header sign-in state, cookie consent, small helpers. No dependencies. */
(function () {
  'use strict';
  var d = document;
  var S = window.SUD = window.SUD || {};
  /* HTTP status codes in plain English. Every place that shows a code (check results, probe tables, redirect chains) uses this
     so a visitor never sees a bare number. S.codeInfo(code) gives {n: short name, t: one-sentence meaning};
     S.codeTag(code) gives ready-to-insert HTML with the name beside the number and the full meaning in a hover/tap popup. */
  var CODE_TEXT = {
    200: ['OK', 'The site answered normally. This is the result you want.'],
    201: ['Created', 'The request worked and something new was created.'],
    204: ['No content', 'The request worked and there is nothing to show. Normal for some background calls.'],
    301: ['Moved permanently', 'The page has a new permanent address and the browser was sent there.'],
    302: ['Moved temporarily', 'The page is temporarily at another address and the browser was sent there.'],
    304: ['Not modified', 'Your stored copy of the page is still current, so nothing new was sent.'],
    307: ['Temporary redirect', 'The page is temporarily somewhere else and the browser was sent there.'],
    308: ['Permanent redirect', 'The page has moved for good and the browser was sent to the new address.'],
    400: ['Bad request', 'The server could not understand the request. The site is up, but this request was malformed.'],
    401: ['Login required', 'The page needs you to sign in first. The site itself is working.'],
    403: ['Forbidden', 'The server is working but refused to let this request in. Many big sites do this to automated checks even when they work fine for people.'],
    404: ['Not found', 'The server is working but there is nothing at this address. The page is missing, the site is not necessarily down.'],
    405: ['Method not allowed', 'The page exists but does not accept this kind of request.'],
    408: ['Request timeout', 'The server gave up waiting for the request to finish arriving.'],
    410: ['Gone', 'The page was removed on purpose and will not come back.'],
    429: ['Too many requests', 'The site is asking us to slow down. It is a deliberate limit, not a breakage.'],
    451: ['Unavailable for legal reasons', 'The page is blocked for legal reasons in this place.'],
    500: ['Server error', 'Something went wrong on the website\'s own server. The problem is on their side.'],
    501: ['Not implemented', 'The server does not support the thing that was asked for. The problem is on their side.'],
    502: ['Bad gateway', 'A server in front of the site got a bad answer from the server behind it. Often a short fault on their side.'],
    503: ['Unavailable', 'The server is up but cannot take requests right now, usually because it is overloaded or in maintenance.'],
    504: ['Gateway timeout', 'A server in front of the site gave up waiting for the server behind it. Often overload on their side.'],
    520: ['Unknown error', 'The service in front of the site got an empty or unexpected answer from the site\'s own server.'],
    521: ['Web server is down', 'The service in front of the site could not reach the site\'s own server.'],
    522: ['Connection timed out', 'The service in front of the site could not connect to the site\'s own server in time.'],
    523: ['Origin unreachable', 'The service in front of the site could not find a route to the site\'s own server.'],
    524: ['Timeout', 'The site\'s own server took too long to answer the service in front of it.'],
    525: ['Secure connection failed', 'The secure handshake with the site\'s own server failed.'],
    526: ['Invalid certificate', 'The site\'s own server has a certificate that does not check out.']
  };
  S.codeInfo = function (code) {
    var c = +code; if (!c) return null;
    var h = CODE_TEXT[c]; if (h) return { n: h[0], t: h[1] };
    if (c >= 200 && c < 300) return { n: 'Success', t: 'The site answered and the request worked.' };
    if (c >= 300 && c < 400) return { n: 'Redirect', t: 'The site sent the browser to another address.' };
    if (c >= 400 && c < 500) return { n: 'Request refused', t: 'The server answered but refused the request or could not find what was asked for. The site itself is working.' };
    if (c >= 500) return { n: 'Server error', t: 'Something went wrong on the website\'s own server. The problem is on their side.' };
    return null;
  };
  S.codeTag = function (code, opts) {
    var i = S.codeInfo(code), e = function (x) { return String(x).replace(/[&<>"]/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]; }); };
    if (!i) return e(code);
    return '<span class="code-x has-tip" tabindex="0" data-tip="' + e(code + ' ' + i.n + ': ' + i.t) + '">' + e(code) + ' <small>' + e(i.n) + '</small></span>';
  };
  S.user = null; S.google = ''; S.ready = []; S.me = null;

  /* ---- helpers ---- */
  S.$ = function (s, r) { return (r || d).querySelector(s); };
  S.$$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  S.esc = function (t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  S.store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  };
  S.api = function (path, data) {
    var opt = { credentials: 'same-origin' };
    if (data !== undefined) { opt.method = 'POST'; opt.headers = { 'Content-Type': 'application/json', 'X-SUD': '1' }; opt.body = JSON.stringify(data); }
    return fetch('/api/' + path, opt).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) { var e = new Error(j.error || 'Something went wrong. Please try again.'); e.status = r.status; throw e; } return j; });
    });
  };
  S.ago = function (iso) {
    if (!iso) return '—';
    var s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 45) return 'just now'; if (s < 3600) return Math.round(s / 60) + ' min ago';
    if (s < 86400) return Math.round(s / 3600) + ' h ago'; return Math.round(s / 86400) + ' d ago';
  };
  S.when = function (iso) { if (!iso) return '—'; var t = new Date(iso); return t.toLocaleString([], { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); };
  S.ms = function (n) { return n == null ? '—' : (n >= 1000 ? (n / 1000).toFixed(1) + ' s' : n + ' ms'); };
  S.LABEL = { up: 'Up', down: 'Confirmed down', timeout: 'Timeout', inconclusive: 'Inconclusive', pending: 'Checking…', none: 'No data', partial: 'Partly reachable', blocked: 'Blocked', 'down-everywhere': 'Looks down', silent: 'No answer' };
  S.pill = function (v) { v = v || 'pending'; return '<span class="pill ' + S.esc(v) + '">' + S.esc(S.LABEL[v] || v) + '</span>'; };

  /* Problem-report helpers shared by the home page and the "Is X down?" pages. */
  S.REPKIND = { site: 'website not loading', login: 'cannot log in', app: 'app not working', slow: 'very slow' };
  var RANGES = { '24h': 'the last 24 hours', '7d': 'the last 7 days', '30d': 'the last 30 days', '1y': 'the last year' };
  S.repRangeText = function (r) { return RANGES[r] || RANGES['24h']; };
  function fmtDay(d, o) { return d.toLocaleDateString([], Object.assign({ timeZone: 'UTC' }, o)); }
  /* Shown when our automated check could not get a clear answer: be honest, and let the visitor try the site themselves. */
  S.cantSure = function (el, host, show) {
    if (!el) return;
    if (!show) { el.hidden = true; el.innerHTML = ''; return; }
    var safe = /^[a-z0-9.-]+$/i.test(host) ? host : '';
    if (!safe) { el.hidden = true; return; }
    el.hidden = false;
    el.innerHTML = '<p><b>We can\u2019t be sure it is down.</b> Our automated check did not get a clear answer, and some sites ignore or block automated checks. Try opening it yourself: if it loads, the site is fine and just blocking us.</p><a class="btn small" href="https://' + S.esc(safe) + '/" target="_blank" rel="noopener noreferrer">Open ' + S.esc(safe) + ' \u2197</a>';
  };
  S.tz = function () { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { return ''; } };
  S.repChart = function (chart, detail, kindsEl, rep, extra) {
    var bk = rep.buckets || [], max = Math.max.apply(null, bk.map(function (b) { return b.n; }).concat([3])), K = Object.keys(S.REPKIND), unit = rep.unit || 'hour';
    function when(b) {
      var d = new Date(b.t);
      if (unit === 'hour') return d.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' }) + ', ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      if (unit === 'week') return 'Week of ' + fmtDay(d, { day: 'numeric', month: 'short', year: 'numeric' });
      return fmtDay(d, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
    }
    function sentence(i) {
      var b = bk[i], n = b.n;
      if (!n) return when(b) + ': no reports.';
      var parts = K.filter(function (k) { return b.k[k]; }).map(function (k) { return b.k[k] + ' ' + S.REPKIND[k]; });
      return when(b) + ': ' + n + (n === 1 ? ' report' : ' reports') + ' (' + parts.join(', ') + ').';
    }
    chart.innerHTML = bk.map(function (b, i) {
      var segs = K.map(function (k) { var c = b.k[k] || 0; return c ? '<i class="rseg s-' + k + '" style="height:' + (100 * c / b.n) + '%"></i>' : ''; }).join('');
      var h = b.n ? Math.max(16, Math.round(100 * b.n / max)) : 0;
      return '<div tabindex="0" role="img" class="bar' + (b.n ? ' has' : '') + '" data-i="' + i + '" aria-label="' + S.esc(sentence(i)) + '"' + (b.n ? ' style="height:' + h + '%"' : '') + '>' + segs + '</div>';
    }).join('');
    var peak = bk.reduce(function (m, b, i) { return b.n > (bk[m] ? bk[m].n : 0) ? i : m; }, -1);
    var dflt = peak >= 0 && bk[peak].n ? 'Busiest ' + unit + ': ' + sentence(peak) : 'Tap or hover a bar to see what was reported.';
    if (detail) {
      detail.hidden = false; detail.textContent = dflt;
      var show = function (e) { var b = e.target.closest('.bar'); if (!b) return; detail.textContent = sentence(+b.getAttribute('data-i')); };
      chart.onmouseover = show; chart.onclick = show; chart.onfocusin = show; chart.onmouseleave = function () { detail.textContent = dflt; };
    }
    if (extra) {
      var first = new Date(bk[0].t), last = new Date(bk[bk.length - 1].t), today = new Date();
      var td = today.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' });
      if (extra.date) extra.date.textContent = rep.range === '24h' ? 'Today, ' + td : fmtDay(first, { day: 'numeric', month: 'short', year: rep.range === '1y' ? 'numeric' : undefined }) + ' to ' + fmtDay(last, { day: 'numeric', month: 'short', year: rep.range === '1y' ? 'numeric' : undefined });
      if (extra.axis) { var sp = extra.axis.children; sp[0].textContent = rep.range === '24h' ? '24 hours ago' : fmtDay(first, { day: 'numeric', month: 'short' }); sp[1].textContent = rep.range === '24h' ? 'Now' : 'Today'; }
    }
    if (kindsEl) {     // what people are reporting: a ring with a percentage for each problem type
      var k = rep.kinds || {}, used = K.filter(function (x) { return k[x]; }), tot = used.reduce(function (a, x) { return a + k[x]; }, 0);
      if (!tot) { kindsEl.innerHTML = ''; }
      else {
        var C = 2 * Math.PI * 40, off = 0, arcs = used.map(function (x) {
          var len = C * k[x] / tot, el = '<circle class="dn-seg s-' + x + '" cx="50" cy="50" r="40" stroke-dasharray="' + len.toFixed(2) + ' ' + (C - len).toFixed(2) + '" stroke-dashoffset="' + (-off).toFixed(2) + '"/>';
          off += len; return el;
        }).join('');
        var top = used.reduce(function (m, x) { return k[x] > k[m] ? x : m; }, used[0]);
        kindsEl.innerHTML = '<div class="dn"><svg viewBox="0 0 100 100" role="img" aria-label="Share of each type of problem reported"><g transform="rotate(-90 50 50)">' + arcs + '</g><text x="50" y="48" text-anchor="middle" class="dn-n">' + tot + '</text><text x="50" y="62" text-anchor="middle" class="dn-l">' + (tot === 1 ? 'report' : 'reports') + '</text></svg><ul class="dn-leg">' +
          used.map(function (x) { return '<li><i class="kdot s-' + x + '"></i><span>' + S.REPKIND[x] + '</span><b>' + Math.round(100 * k[x] / tot) + '%</b></li>'; }).join('') + '</ul></div>' +
          '<p class="dn-top">Most reported: <b>' + S.REPKIND[top] + '</b> (' + Math.round(100 * k[top] / tot) + '% of reports).</p>';
      }
      var cs = rep.countries || [], ctot = cs.reduce(function (a, c) { return a + c.n; }, 0);
      if (ctot >= 3) {
        var nm = function (cc) { try { return new Intl.DisplayNames([], { type: 'region' }).of(cc) || cc; } catch (e) { return cc; } };
        var share = cs[0].n / ctot, verdict = cs.length === 1 || share >= 0.8 ? 'Almost all reports come from ' + nm(cs[0].cc) + ', so this may be a local problem rather than a worldwide one.' : cs.length >= 3 ? 'Reports are coming from several countries, so this looks more widespread.' : 'Reports are coming from ' + cs.length + ' countries.';
        kindsEl.innerHTML += '<div class="cn"><b>Where reports come from</b><ul class="dn-leg cn-l">' + cs.map(function (c) { var pc = Math.round(100 * c.n / ctot); return '<li><span>' + S.esc(nm(c.cc)) + '</span><i class="cn-bar"><u style="width:' + pc + '%"></u></i><b>' + pc + '%</b></li>'; }).join('') + '</ul><p class="dn-top">' + verdict + '</p></div>';
      }
    }
  };
  /* Range tabs (24 hours / 7 days / 30 days / 1 year). */
  S.repRanges = function (el, onChange) {
    var cur = '24h';
    el.addEventListener('click', function (e) {
      var b = e.target.closest('[data-range]'); if (!b || b.getAttribute('data-range') === cur) return;
      cur = b.getAttribute('data-range');
      Array.prototype.forEach.call(el.querySelectorAll('[data-range]'), function (x) { var on = x === b; x.classList.toggle('on', on); x.setAttribute('aria-pressed', on); });
      onChange(cur);
    });
    return function () { return cur; };
  };
  /* Multi-select picker: toggle problems, then Send. onSend(kinds[]) is called. */
  S.repPicker = function (pick, onSend) {
    var send = pick.querySelector('.rsend');
    function sel() { return Array.prototype.map.call(pick.querySelectorAll('.rk.on'), function (b) { return b.getAttribute('data-kind'); }); }
    function sync() { var n = sel().length; send.disabled = !n; send.firstChild.textContent = n > 1 ? 'Send ' + n + ' reports' : 'Send report'; }
    pick.addEventListener('click', function (e) {
      var b = e.target.closest('.rk');
      if (b) { b.classList.toggle('on'); b.setAttribute('aria-pressed', b.classList.contains('on')); sync(); return; }
      if (e.target.closest('.rsend') && !send.disabled) onSend(sel());
    });
    return { reset: function () { Array.prototype.forEach.call(pick.querySelectorAll('.rk'), function (b) { b.classList.remove('on'); b.setAttribute('aria-pressed', 'false'); }); sync(); } };
  };
  // Optional coarse location for a problem report: only when the visitor ticks the box AND the browser grants it. Rounded to 0.1 degree (about 10 km) before it leaves the page.
  S.repLoc = function (pick) {
    var cb = pick.querySelector('.rloc input');
    if (!cb || !cb.checked || !navigator.geolocation) return Promise.resolve(null);
    return new Promise(function (res) {
      navigator.geolocation.getCurrentPosition(function (p) {
        res({ lat: Math.round(p.coords.latitude * 10) / 10, lon: Math.round(p.coords.longitude * 10) / 10 });
      }, function () { res(null); }, { timeout: 9000, maximumAge: 600000 });
    });
  };
  // Latest visitor reports as a plain list (type, time, and country only when several people reported from it). host = '' for all sites.
  S.repFeed = function (ul, host, withName) {
    if (!ul) return;
    var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
    function ago(iso) { var m = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000)); return m < 1 ? 'just now' : m < 60 ? m + ' min ago' : m < 1440 ? Math.round(m / 60) + ' h ago' : 'yesterday'; }
    fetch('/api/reports.php?recent=1' + (host ? '&host=' + encodeURIComponent(host) : ''), { credentials: 'same-origin' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      ul.textContent = '';
      var it = (j && j.items) || [];
      if (!it.length) { var e = d.createElement('li'); e.className = 'rf-none'; e.textContent = 'No reports in the last 24 hours.'; ul.appendChild(e); return; }
      it.forEach(function (r) {
        var li = d.createElement('li'), dot = d.createElement('i'), tx = d.createElement('span'), sm = d.createElement('small');
        dot.className = 'kdot s-' + r.kind;
        if (withName) { var nm = r.page ? d.createElement('a') : d.createElement('b'); nm.textContent = r.name; if (r.page) nm.href = r.page; tx.appendChild(nm); tx.appendChild(d.createTextNode(': ' + (r.kind === 'fixed' ? 'working again' : (S.REPKIND[r.kind] || r.kind)))); }
        else tx.textContent = (r.kind === 'fixed' ? 'working again' : (S.REPKIND[r.kind] || r.kind)).replace(/^./, function (c) { return c.toUpperCase(); });
        var place = r.country && dn ? (function () { try { return dn.of(r.country); } catch (e) { return ''; } })() : '';
        sm.textContent = (place ? place + ' · ' : '') + ago(r.ts);
        li.appendChild(dot); li.appendChild(tx); li.appendChild(sm); ul.appendChild(li);
      });
    }).catch(function () { ul.textContent = ''; });
  };
  // "It is working for me now": one-tap report that a problem has cleared. Helps the map fade a recovered site sooner.
  S.repFix = function (btn, getHost, msgEl, done) {
    if (!btn) return;
    btn.addEventListener('click', function () {
      var h = getHost(); if (!h) return;
      msgEl.textContent = 'Sending…';
      fetch('/api/report.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ host: h, kinds: ['fixed'], tz: S.tz() }), credentials: 'same-origin' })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (r) { msgEl.textContent = r.ok ? r.j.message : (r.j.error || 'Sorry, that did not work. Please try again later.'); if (r.ok && done) done(); })
        .catch(function () { msgEl.textContent = 'Sorry, that did not work. Please try again later.'; });
    });
  };
  S.toast = function (msg, bad) {
    var t = d.createElement('div'); t.className = 'toast' + (bad ? ' bad' : ''); t.setAttribute('role', 'status'); t.textContent = msg; d.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 3200);
  };
  S.onReady = function (fn) { if (S.me) fn(S.user); else S.ready.push(fn); };
  S.next = function () { var n = new URLSearchParams(location.search).get('next'); return n && /^\/[a-z0-9\-_/?=&#.]*$/i.test(n) && n.indexOf('//') < 0 ? n : '/'; };

  /* ---- theme ---- */
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  function applyTheme(t) { d.documentElement.setAttribute('data-theme', t); var b = S.$('#theme'); if (b) { b.innerHTML = t === 'dark' ? SUN : MOON; b.setAttribute('aria-label', t === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'); } }
  // Preview: add ?navy=1 to the address to try the deep-blue colours from the new logo (?navy=0 turns it off).
  try { var nq = new URLSearchParams(location.search).get('navy'); if (nq === '1') S.store.set('sud-navy', '1'); else if (nq === '0') S.store.set('sud-navy', ''); } catch (e) { /* ignore */ }
  if (S.store.get('sud-navy') === '1') d.documentElement.classList.add('navy');
  var theme = 'light'; /* new look is light only */
  applyTheme(theme);
  d.addEventListener('DOMContentLoaded', function () {
    applyTheme(theme);
    var b = S.$('#theme'); if (b) b.addEventListener('click', function () { theme = theme === 'dark' ? 'light' : 'dark'; S.store.set('sud-theme', theme); applyTheme(theme); });
    initAuth(); initCookies(); initEyes(); loadAds();
    try { var fl = sessionStorage.getItem('sud-flash'); if (fl) { sessionStorage.removeItem('sud-flash'); S.toast(fl); } } catch (e) { /* ignore */ }
    S.$$('[data-year]').forEach(function (e) { e.textContent = new Date().getFullYear(); });
  });

  /* ---- header sign-in state ---- */
  var I = {
    hist: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/></svg>',
    star: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/></svg>',
    user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
    out: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>'
  };
  function renderAuth() {
    var box = S.$('#auth'); if (!box) return;
    if (!S.user) {
      var here = location.pathname + location.search;
      box.innerHTML = '<a class="signin-btn" href="/login' + (here !== '/' && here.indexOf('/login') !== 0 ? '?next=' + encodeURIComponent(here) : '') + '">Login</a>';
      return;
    }
    var ini = S.esc((S.user.name || '?').trim().charAt(0).toUpperCase());
    box.innerHTML = '<div class="acct"><button class="avatar" id="avbtn" aria-haspopup="true" aria-expanded="false" aria-label="Account menu">' + ini + '</button>'
      + '<div class="menu" id="menu" role="menu"><div class="who">' + S.esc(S.user.email) + '</div>'
      + '<a href="/account#checks" role="menuitem">' + I.hist + 'My checks</a><a href="/monitor" role="menuitem">' + I.star + 'My watchlist</a>'
      + '<a href="/account#settings" role="menuitem">' + I.user + 'Account</a><button id="signout" role="menuitem">' + I.out + 'Sign out</button></div></div>';
    var btn = S.$('#avbtn'), menu = S.$('#menu');
    btn.addEventListener('click', function (e) { e.stopPropagation(); var o = menu.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    d.addEventListener('click', function (e) { if (!menu.contains(e.target)) { menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); } });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') menu.classList.remove('open'); });
    S.$('#signout').addEventListener('click', function () { S.api('logout.php', {}).then(function () { S.user = null; S.store.del('sud-in'); location.href = '/'; }); });
  }
  function initAuth() {
    S.api('me.php').then(function (j) {
      S.user = j.user || null; S.google = (j.google && j.google_id) || ''; S.enabled = j.enabled !== false; S.me = j;
      if (S.user) S.store.set('sud-in', '1'); else S.store.del('sud-in');
      renderAuth(); S.ready.splice(0).forEach(function (f) { f(S.user); });
    }).catch(function () { S.me = { user: null }; renderAuth(); S.ready.splice(0).forEach(function (f) { f(null); }); });
    // Paint the right button straight away from the last known state so the header does not jump.
    if (S.store.get('sud-in') === '1') { var box = S.$('#auth'); if (box && !box.firstChild) box.innerHTML = '<span class="avatar" aria-hidden="true">·</span>'; }
  }

  /* ---- cookie consent ---- */
  var SHIELD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/></svg>';
  S.consent = function () { try { return JSON.parse(S.store.get('sud-consent') || 'null'); } catch (e) { return null; } };
  function saveConsent(a, m) { S.store.set('sud-consent', JSON.stringify({ analytics: !!a, marketing: !!m, at: Date.now() })); var c = S.$('#cookie'); if (c) c.remove(); d.dispatchEvent(new CustomEvent('sud:consent')); }
  function showCookies(custom) {
    var old = S.$('#cookie'); if (old) old.remove();
    var cur = S.consent() || {};
    var c = d.createElement('div'); c.id = 'cookie'; c.className = 'cookie'; c.setAttribute('role', 'dialog'); c.setAttribute('aria-label', 'Cookie settings');
    c.innerHTML = '<h3>' + SHIELD + 'Your privacy. Your choice.</h3><p>We use essential storage to run this site. Optional cookies help measure visits and ads, only with your permission.</p>'
      + (custom ? '<div class="opts"><label class="check"><input type="checkbox" checked disabled><span><b>Essential</b><small>Theme, sign-in and your consent choice. Always on.</small></span></label>'
        + '<label class="check"><input type="checkbox" id="c-an"' + (cur.analytics ? ' checked' : '') + '><span><b>Analytics</b><small>Anonymous visit measurement.</small></span></label>'
        + '<label class="check"><input type="checkbox" id="c-mk"' + (cur.marketing ? ' checked' : '') + '><span><b>Advertising</b><small>Lets us show ads that keep the site free.</small></span></label></div>'
        + '<div class="btns"><button class="btn ghost" id="c-rej">Reject optional</button><button class="btn" id="c-save">Save choices</button></div>'
        : '<div class="btns"><button class="btn ghost" id="c-rej">Reject optional</button><button class="btn ghost" id="c-cus">Customize</button><button class="btn wide" id="c-all">Accept all</button></div>');
    d.body.appendChild(c);
    var q = function (id) { return S.$(id, c); };
    q('#c-rej').onclick = function () { saveConsent(false, false); };
    if (q('#c-cus')) q('#c-cus').onclick = function () { showCookies(true); };
    if (q('#c-all')) q('#c-all').onclick = function () { saveConsent(true, true); };
    if (q('#c-save')) q('#c-save').onclick = function () { saveConsent(q('#c-an').checked, q('#c-mk').checked); };
  }
  /* Google ads: the script is only added once the visitor has accepted advertising cookies. */
  function loadAds() {
    return; /* test site: ads never load */
    var c = S.consent(); if (!c || !c.marketing || S.$('#sud-ads')) return;
    var s = d.createElement('script'); s.id = 'sud-ads'; s.async = true; s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6517978259411056';
    d.head.appendChild(s);
  }
  /* Anonymous page-view count: no cookie, no storage, no address kept. Skipped if the visitor declined analytics or sends Do Not Track. */
  function countView() {
    try {
      var c = S.consent(); if (c && c.analytics === false) return;
      if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl) return;
      if (/^\/(admin|account|login)/.test(location.pathname)) return;
      var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
      var body = JSON.stringify({ p: location.pathname, r: d.referrer || '', tz: tz, w: window.innerWidth || 0 });
      if (navigator.sendBeacon) navigator.sendBeacon('/api/pv.php', new Blob([body], { type: 'application/json' }));
      else fetch('/api/pv.php', { method: 'POST', body: body, headers: { 'Content-Type': 'application/json' }, keepalive: true });
    } catch (e) {}
  }
  if (d.readyState === 'complete') setTimeout(countView, 600); else window.addEventListener('load', function () { setTimeout(countView, 600); });
  d.addEventListener('sud:consent', loadAds);
  function initEyes() {
        S.$$('.field input[type=password]').forEach(function (inp) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'eye'; b.setAttribute('aria-label', 'Show password'); b.setAttribute('aria-pressed', 'false'); b.textContent = 'Show';
      b.addEventListener('click', function () {
        var show = inp.type === 'password'; inp.type = show ? 'text' : 'password';
        b.textContent = show ? 'Hide' : 'Show'; b.setAttribute('aria-label', show ? 'Hide password' : 'Show password'); b.setAttribute('aria-pressed', show ? 'true' : 'false'); inp.focus();
      });
      inp.parentNode.appendChild(b);
    });
  }
  function initCookies() {
    if (!S.consent()) showCookies(false);
    S.$$('[data-cookie-settings]').forEach(function (b) { b.addEventListener('click', function () { showCookies(true); }); });
  }
  /* Shared hover / tap popup for anything marked .has-tip with a data-tip text. */
  (function () {
    var tip = document.createElement('div'); tip.className = 'sp-tip'; tip.setAttribute('role', 'tooltip'); tip.hidden = true; document.body.appendChild(tip);
    var cur = null;
    function show(el) {
      cur = el; tip.textContent = el.getAttribute('data-tip'); tip.hidden = false;
      var r = el.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
      var x = Math.max(8, Math.min(window.innerWidth - w - 8, r.left + r.width / 2 - w / 2));
      var y = r.top - h - 8; if (y < 8) y = r.bottom + 8;
      tip.style.left = (x + window.pageXOffset) + 'px'; tip.style.top = (y + window.pageYOffset) + 'px';
    }
    function hide() { tip.hidden = true; cur = null; }
    document.addEventListener('mouseover', function (e) { var t = e.target.closest && e.target.closest('.has-tip'); if (t) show(t); else if (cur && !tip.contains(e.target)) hide(); });
    document.addEventListener('focusin', function (e) { var t = e.target.closest && e.target.closest('.has-tip'); if (t) show(t); });
    document.addEventListener('focusout', hide);
    document.addEventListener('click', function (e) { var t = e.target.closest && e.target.closest('.has-tip'); if (t) show(t); else hide(); });
    window.addEventListener('scroll', function () { if (cur) hide(); }, { passive: true });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
  })();
})();
