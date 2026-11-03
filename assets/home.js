/* siteupdown.com — home page: checker, Global Pulse map, watchlist, gaming list, live feed. */
(function () {
  'use strict';
  var S = window.SUD, $ = S.$, esc = S.esc;
  function tile() { return ''; }
  var W = 1000, MAP = window.SUD_MAP, H = Math.round(W * 142 / 360 * 10) / 10;
  var state = { host: '', share: '', timer: null, runId: 0, last: '' };
  var BIG = { up: 'Up for everyone', partial: 'Reachable from some places', 'down-everywhere': 'Down for everyone', blocked: 'Blocking automated checks', silent: 'No answer from anywhere', down: 'Confirmed down', timeout: 'Timed out', inconclusive: 'Inconclusive' };

  /* ---------- map ---------- */
  var svg = $('#map-svg'), tip = $('#tip'), mwrap = $('#map');
  function px(lon, lat) { return [(lon + 180) / 360 * W, (84 - lat) / 142 * (W * 142 / 360)]; }
  function drawLand() {
    if (!MAP || !svg) return;
    var cell = W * MAP.cell / 360, s = cell * 0.72, o = (cell - s) / 2, p = '';
    MAP.runs.forEach(function (runs, r) {
      runs.forEach(function (run) { for (var c = run[0]; c < run[0] + run[1]; c++) p += 'M' + (c * cell + o).toFixed(1) + ' ' + (r * cell + o).toFixed(1) + 'h' + s.toFixed(1) + 'v' + s.toFixed(1) + 'h-' + s.toFixed(1) + 'z'; });
    });
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.innerHTML = '<path class="map-land" d="' + p + '"/><g id="markers"></g>';
  }

  var CN = { US: 'United States', CA: 'Canada', BR: 'Brazil', GB: 'United Kingdom', DE: 'Germany', FR: 'France', ZA: 'South Africa', AE: 'United Arab Emirates', IN: 'India', JP: 'Japan', SG: 'Singapore', AU: 'Australia',
    NL: 'Netherlands', IE: 'Ireland', ES: 'Spain', IT: 'Italy', SE: 'Sweden', NO: 'Norway', FI: 'Finland', DK: 'Denmark', PL: 'Poland', CH: 'Switzerland', AT: 'Austria', BE: 'Belgium', PT: 'Portugal', CZ: 'Czechia', RO: 'Romania', UA: 'Ukraine', RU: 'Russia',
    TR: 'Turkey', IL: 'Israel', SA: 'Saudi Arabia', EG: 'Egypt', NG: 'Nigeria', KE: 'Kenya', KR: 'South Korea', HK: 'Hong Kong', TW: 'Taiwan', CN: 'China', ID: 'Indonesia', TH: 'Thailand', VN: 'Vietnam', MY: 'Malaysia', PH: 'Philippines', NZ: 'New Zealand',
    MX: 'Mexico', AR: 'Argentina', CL: 'Chile', CO: 'Colombia', PE: 'Peru' };
  function cname(p) { var n = CN[p.country] || p.country || 'Unknown'; return (p.city ? p.city + ', ' : '') + n; }
  var LBL = { ok: 'Responded', blocked: 'Blocked', error: 'Server error', none: 'No connection' };
  var CONT = { EU: 'Europe', AS: 'Asia', NA: 'North America', SA: 'South America', AF: 'Africa', OC: 'Oceania', AN: 'Antarctica' };
  var EXPLAIN = { ok: 'This location reached the site normally.', blocked: 'The site refused this location\u2019s automated request. That is usually bot protection, not an outage.', error: 'The site answered here with a server error.', none: 'This location got no answer from the site.' };
  var HTTPN = { 200: 'OK', 201: 'Created', 204: 'No content', 301: 'Redirect', 302: 'Redirect', 304: 'Not modified', 307: 'Redirect', 308: 'Redirect', 400: 'Bad request', 401: 'Login required', 403: 'Forbidden', 404: 'Not found', 429: 'Too many requests', 500: 'Server error', 502: 'Bad gateway', 503: 'Unavailable', 504: 'Gateway timeout' };
  function tipHtml(p, st, i, med) {
    var rows = '<div class="tp-r"><span>Checking</span><b>' + esc(state.host || 'this site') + '</b></div>';
    rows += '<div class="tp-r"><span>HTTP</span><b>' + (p.code ? p.code + (HTTPN[p.code] ? ' ' + esc(HTTPN[p.code]) : '') : 'No reply') + '</b></div>';
    if (p.ms != null) {
      var cmp = '';
      if (med && st !== 'none') { var r = p.ms / med; cmp = r >= 1.5 ? ' <i>' + (Math.round(r * 10) / 10) + 'x slower than typical</i>' : r <= 0.67 ? ' <i>' + (Math.round(med / p.ms * 10) / 10) + 'x faster than typical</i>' : ' <i>about typical</i>'; }
      rows += '<div class="tp-r"><span>Response</span><b>' + p.ms + ' ms</b></div>' + (cmp ? '<div class="tp-c">' + cmp.replace(/<\/?i>/g, '').trim() + '</div>' : '');
    }
    return '<div class="tp-h ' + st + '"><i></i>' + LBL[st] + '</div><div class="tp-t">' + esc(cname(p)) + '</div><div class="tp-s">' + esc(CONT[p.continent] || p.continent || '') + '</div>'
      + '<div class="tp-e">' + EXPLAIN[st] + '</div>' + rows;
  }
  function drawProbes(probes) {
    var g = $('#markers'); if (!g) return;
    var out = '', ms = probes.filter(function (p) { return p.ms != null && p.state !== 'none'; }).map(function (p) { return p.ms; }).sort(function (a, b) { return a - b; });
    var med = ms.length ? ms[Math.floor(ms.length / 2)] : null;
    probes.forEach(function (p, i) {
      if (p.lat == null || p.lon == null) return;
      var xy = px(p.lon, p.lat), st = p.state || 'none';
      var tx = cname(p) + ', ' + LBL[st] + (p.code ? ' (HTTP ' + p.code + ')' : '') + (p.ms != null ? ', ' + p.ms + ' milliseconds' : '');
      out += '<g class="pr" tabindex="0" role="img" aria-label="' + esc(tx) + '" data-i="' + i + '" data-x="' + (xy[0] / W * 100).toFixed(2) + '" data-y="' + (xy[1] / H * 100).toFixed(2) + '">'
        + '<circle class="mk-ring ' + st + '" cx="' + xy[0].toFixed(1) + '" cy="' + xy[1].toFixed(1) + '" r="8"/>'
        + '<circle class="mk-hit" cx="' + xy[0].toFixed(1) + '" cy="' + xy[1].toFixed(1) + '" r="20"/>'
        + '<circle class="mk ' + st + '" cx="' + xy[0].toFixed(1) + '" cy="' + xy[1].toFixed(1) + '" r="8"/></g>';
    });
    g.innerHTML = out;
    S.$$('.pr', g).forEach(function (n) {
      var p = probes[+n.getAttribute('data-i')], st = p.state || 'none';
      var show = function () {
        var x = +n.getAttribute('data-x'), y = +n.getAttribute('data-y');
        tip.innerHTML = tipHtml(p, st, +n.getAttribute('data-i'), med);
        tip.className = 'tip' + (x > 62 ? ' l' : x < 38 ? ' r' : '') + (y < 42 ? ' b' : '');
        tip.style.left = x + '%'; tip.style.top = y + '%'; tip.hidden = false;
      };
      n.addEventListener('mouseenter', show); n.addEventListener('focus', show); n.addEventListener('click', function (e) { e.stopPropagation(); show(); });
      n.addEventListener('mouseleave', function () { tip.hidden = true; }); n.addEventListener('blur', function () { tip.hidden = true; });
    });
  }
  document.addEventListener('click', function () { if (tip) tip.hidden = true; });
  function mapMsg(t) { var m = $('#map-empty'); if (!m) return; m.hidden = !t; if (t) m.firstElementChild.textContent = t; }


  /* ---------- charts under the map ---------- */
  var COL = { ok: 'var(--green)', blocked: 'var(--amber)', error: 'var(--red)', none: 'var(--grey)' };
  function chartsClear() { ['ch-bars', 'ch-donut', 'ch-range'].forEach(function (id) { var e = $('#' + id); if (e) { e.className = 'ch-empty'; e.textContent = 'Run a check to see this chart.'; } }); }
  function drawCharts(probes, res) {
    if (!probes || !probes.length) { chartsClear(); return; }
    var n = probes.length, byState = { ok: 0, blocked: 0, error: 0, none: 0 };
    probes.forEach(function (p) { byState[p.state || 'none']++; });
    /* 1. response time by region */
    var withMs = probes.filter(function (p) { return p.ms != null; }), max = Math.max.apply(null, withMs.map(function (p) { return p.ms; }).concat([res && res.ms || 0, 100]));
    var sorted = probes.slice().sort(function (a, b) { return (a.ms == null ? 1e9 : a.ms) - (b.ms == null ? 1e9 : b.ms); });
    var bars = sorted.map(function (p) {
      var st = p.state || 'none', w = p.ms != null ? Math.max(3, p.ms / max * 100) : 0;
      return '<div class="br"><span class="bl"><abbr tabindex="0" data-n="' + esc(cname(p)) + '">' + esc(p.country || '?') + '</abbr></span><span class="bt"><i style="width:' + w.toFixed(1) + '%;background:' + COL[st] + '"></i></span><span class="bv">' + (p.ms != null ? esc(S.ms(p.ms)) : (st === 'none' ? 'no reply' : esc(LBL[st]))) + '</span></div>';
    }).join('');
    var b = $('#ch-bars'); b.className = 'bars'; b.innerHTML = bars;
    /* 2. outcomes donut */
    var R = 52, C = 2 * Math.PI * R, off = 0, segs = '', keys = ['ok', 'blocked', 'error', 'none'];
    keys.forEach(function (k) { if (!byState[k]) return; var len = byState[k] / n * C; segs += '<circle r="' + R + '" cx="70" cy="70" fill="none" stroke="' + COL[k] + '" stroke-width="18" stroke-dasharray="' + len.toFixed(2) + ' ' + (C - len).toFixed(2) + '" stroke-dashoffset="' + (-off).toFixed(2) + '" transform="rotate(-90 70 70)"/>'; off += len; });
    var leg = keys.map(function (k) { return '<li><i style="background:' + COL[k] + '"></i>' + LBL[k] + '<b>' + byState[k] + '</b></li>'; }).join('');
    var d = $('#ch-donut'); d.className = 'donut';
    d.innerHTML = '<svg viewBox="0 0 140 140" role="img" aria-label="' + byState.ok + ' of ' + n + ' probes responded"><circle r="' + R + '" cx="70" cy="70" fill="none" stroke="var(--line)" stroke-width="18"/>' + segs + '<text x="70" y="68" text-anchor="middle" class="dn">' + byState.ok + '/' + n + '</text><text x="70" y="86" text-anchor="middle" class="dl">responded</text></svg><ul>' + leg + '</ul>';
    /* 3. speed range */
    var r = $('#ch-range');
    if (!withMs.length) { r.className = 'ch-empty'; r.textContent = 'No regional response times to compare.'; return; }
    var ms = withMs.map(function (p) { return p.ms; }).sort(function (a, c) { return a - c; }), mid = ms[Math.floor(ms.length / 2)], lo = ms[0], hi = ms[ms.length - 1], top = Math.max(hi, res && res.ms || 0, 100);
    var pos = function (v) { return (v / top * 100).toFixed(1) + '%'; };
    var srv = res && res.ms != null ? '<span class="tick" title="Our server" style="left:' + pos(res.ms) + '"></span>' : '';
    r.className = 'range';
    r.innerHTML = '<div class="track"><i class="span" style="left:' + pos(lo) + ';width:' + (((hi - lo) / top) * 100).toFixed(1) + '%"></i><span class="pin" style="left:' + pos(mid) + '"><b>Median</b>' + esc(S.ms(mid)) + '</span>' + srv + '</div>'
      + '<dl><dt>Fastest</dt><dd>' + esc(S.ms(lo)) + '</dd><dt>Median</dt><dd>' + esc(S.ms(mid)) + '</dd><dt>Slowest</dt><dd>' + esc(S.ms(hi)) + '</dd>' + (res && res.ms != null ? '<dt class="srv">Our server</dt><dd>' + esc(S.ms(res.ms)) + '</dd>' : '') + '</dl>';
  }

  /* ---------- verdict panel ---------- */
  function setPanel(o) {
    $('#v-pill').innerHTML = S.pill(o.key || 'pending');
    $('#v-big').textContent = o.big || 'Waiting for probes';
    $('#v-sub').textContent = o.sub || 'No address checked yet';
    $('#s-reach').textContent = o.reach || '0/12';
    $('#s-med').textContent = o.med || '—';
    $('#s-at').textContent = o.at || '—'; if ($('#s-at').nextElementSibling) $('#s-at').nextElementSibling.textContent = o.at ? 'your local time' : 'Not run yet';
    $('#facts').innerHTML = o.facts || '';
    $('#facts').hidden = !o.facts;
    var ss = $('#ssl'); if (ss) { ss.innerHTML = o.ssl || ''; ss.hidden = !o.ssl; }
    var dd = $('#dns'); if (dd) { dd.innerHTML = o.dns || ''; dd.hidden = !o.dns; }
    S.cantSure($('#cs-home'), o.host || '', !!(o.again && o.host && /^(silent|blocked|inconclusive|timeout)$/.test(o.key || '')));
    var md = $('#more-det'); if (md) md.hidden = !(o.facts || o.ssl || o.dns);
    var sl = $('#speed-link'); if (sl) { sl.hidden = !(o.again && o.host); if (o.host) sl.href = '/speed?q=' + encodeURIComponent(o.host); }
    var os = $('#open-site'); if (os) { os.hidden = !(o.again && o.host); if (o.host) os.href = 'https://' + o.host + '/'; }
    $('#run-again').hidden = !o.again;
    var hh = o.again && o.host ? o.host : null;
    if (hh !== HS.host) HS = { host: hh, ms: null, v: null, series: [], up24: null, rep: null, reach: null, total: null };
    if (hh && o.reach) { var m = /^(\d+)\/(\d+)$/.exec(o.reach); if (m && +m[2] > 0 && o.status === 'Complete') { HS.reach = +m[1]; HS.total = +m[2]; } }
    hsRender();
    repBox(hh);
    $('#wl-add').hidden = !o.again;
    $('#share').hidden = !o.share;
    $('#pulse-status').textContent = o.status || 'Standby';
  }
  function factsFor(r) {
    var f = '';
    if (r.http_code) f += '<div>Server check: <b>HTTP ' + esc(r.http_code) + '</b> in <b>' + esc(S.ms(r.ms)) + '</b>' + (r.redirected ? ' (after a redirect)' : '') + '</div>';
    if (r.note) f += '<div>' + esc(r.note) + '</div>';
    if (r.title) f += '<div>Title: <b>' + esc(r.title) + '</b></div>';
    (r.headings || []).forEach(function (h) { f += '<div>' + esc(h) + '</div>'; });
    if (r.server) f += '<div>Server: <b>' + esc(r.server) + '</b></div>';
    if (r.chain && r.chain.length > 1) f += '<div>Redirects: ' + r.chain.map(function (c) { return '<b>' + esc(c.url.replace(/^https?:\/\//, '')) + '</b> <small>(' + esc(c.code) + ')</small>'; }).join(' → ') + '</div>';
    var x = r.extra;
    if (x && (x.ip || x.ctype || x.desc || x.tls_expires)) {
      f += '<div class="xt"><div><b>More details</b></div>';
      if (x.final) f += '<div>Final address: <b>' + esc(x.final) + '</b></div>';
      if (x.ip) f += '<div>Server IP: <b>' + esc(x.ip) + '</b></div>';
      if (x.ctype) f += '<div>Content type: <b>' + esc(x.ctype) + '</b>' + (x.lang ? ' (language ' + esc(x.lang) + ')' : '') + '</div>';
      if (x.desc) f += '<div>Description: ' + esc(x.desc) + '</div>';
      if (x.tls_expires) f += '<div>Certificate: <b>valid until ' + esc(x.tls_expires) + '</b>' + (x.tls_issuer ? ' (' + esc(x.tls_issuer) + ')' : '') + '</div>';
      f += '<div>Security headers: <b>' + (x.sec && x.sec.length ? esc(x.sec.join(', ')) : 'none seen') + '</b></div></div>';
    }
    var on = !!(r.dns || (x && (x.ip || x.ctype || x.desc || x.tls_expires)));
    return f ? '<details class="dl"><summary>What was checked<span>' + (on ? 'Full details' : 'Basic') + '</span></summary><div class="dlb">' + f + '</div></details>' : '';
  }


  /* ---------- DNS & domain card (thorough check) ---------- */
  function dnsFor(r) {
    var d = r && r.dns; if (!d) return '';
    var cell = function (k, v) { return '<div class="c"><span class="k">' + k + '</span><b>' + v + '</b></div>'; };
    var list = function (a) { return a && a.length ? a.map(esc).join('<br>') : '—'; };
    var w = d.whois, h = '<div class="ssl dnsc"><div class="sh"><span>DNS &amp; domain</span><span class="bd none">' + esc(d.domain) + '</span></div>';
    if (w && w.expires) {
      var warn = w.days_left != null && w.days_left <= 30;
      h += '<p class="note">Domain registration ' + (w.days_left < 0 ? '<b class="badt">expired ' + Math.abs(w.days_left) + ' days ago</b>' : 'expires <b' + (warn ? ' class="badt"' : '') + '>' + esc(w.expires) + '</b> (in ' + w.days_left + ' days)') + (w.registrar ? ' · registrar ' + esc(w.registrar) : '') + (w.created ? ' · registered ' + esc(w.created) : '') + '.</p>';
    } else h += '<p class="note">The registry did not share an expiry date for this domain.</p>';
    h += '<div class="grid2">' + cell('Address (A)', list(d.a)) + cell('IPv6 (AAAA)', list(d.aaaa)) + cell('Name servers', list(d.ns))
      + cell('Mail (MX)', d.mx && d.mx.length ? d.mx.map(function (m) { return esc(m.pri + ' ' + m.host); }).join('<br>') : 'No mail records')
      + (d.cname ? cell('Alias (CNAME)', esc(d.cname)) : '') + cell('Email protection', (d.spf ? '✓ SPF' : '✕ no SPF') + ' · ' + (d.dmarc ? '✓ DMARC' : '✕ no DMARC')) + '</div></div>';
    return h;
  }

  /* ---------- SSL certificate card ---------- */
  var SSL_BADGE = { valid: ['Trusted & valid', 'ok'], expiring: ['Expires soon', 'warn'], expired: ['Expired', 'bad'], notyet: ['Not valid yet', 'bad'], mismatch: ['Wrong name', 'bad'], untrusted: ['Not trusted', 'bad'], none: ['No certificate', 'none'] };
  function sslFor(r, host) {
    var t = r && r.tls;
    if (!t) return r && r.verdict && !r.https && r.http_code ? '<div class="ssl"><div class="sh"><span>SSL certificate</span><span class="bd bad">No HTTPS</span></div><p class="note">This site answered over plain HTTP only, so there is no secure connection to inspect.</p></div>' : '';
    var bd = SSL_BADGE[t.status] || SSL_BADGE.none;
    var h = '<div class="ssl"><div class="sh"><span>SSL certificate</span><span class="bd ' + bd[1] + '">' + esc(bd[0]) + '</span></div>';
    if (t.status === 'none') return h + '<p class="note">' + esc(t.note) + '</p></div>';
    var cell = function (k, v, cls) { return '<div class="c"><span class="k">' + k + '</span><b' + (cls ? ' class="' + cls + '"' : '') + '>' + v + '</b></div>'; };
    h += '<p class="note">' + esc(t.note) + '</p>';
    h += '<div class="g1"><span class="k">Secured domain</span><b>' + esc(t.subject || host) + '</b></div><div class="grid2">'
      + cell('Issued by', esc(t.issuer || '—'))
      + cell('Covers this host', t.covers ? '✓ Yes' : '✕ No', t.covers ? '' : 'badt')
      + cell('Issued', esc(t.from))
      + cell('Expires', esc(t.to) + ' <em>' + (t.days_left < 0 ? Math.abs(t.days_left) + ' days ago' : 'in ' + t.days_left + ' days') + '</em>', t.days_left <= 14 ? 'badt' : '')
      + cell('Protocol', esc(t.protocol || '—'))
      + cell('Cipher', esc(t.cipher || '—'))
      + cell('Public key', t.key_bits ? esc(t.key_bits + ' bit' + (t.key_type ? ' ' + t.key_type : '')) : '—')
      + cell('Serial', '<small>' + esc(t.serial || '—') + '</small>') + '</div>';
    if (t.fingerprint) h += '<div class="fpr"><span class="k">Fingerprint (SHA-256)</span><code>' + esc(t.fingerprint) + '</code></div>';
    if (t.elapsed != null) h += '<div class="vw"><div><span>Validity window</span><span>' + esc(t.from) + ' → ' + esc(t.to) + ' (' + t.elapsed + '% elapsed)</span></div><div class="bar"><i style="width:' + t.elapsed + '%"></i></div></div>';
    if (t.sans_total > 1) h += '<details class="sans"><summary>Also covers ' + (t.sans_total - 1) + ' domain' + (t.sans_total === 2 ? '' : 's') + '</summary><p>' + t.sans.map(esc).join(' · ') + (t.sans_total > t.sans.length ? ' …' : '') + '</p></details>';
    if (t.chain && t.chain.length) h += '<div class="chain"><span class="k">Certificate chain</span>' + t.chain.map(function (c) { return '<div class="ch"><i class="' + (c.role === 'leaf' ? 'lf' : '') + '"></i><div><b>' + esc(c.subject) + '</b><small>issued by ' + esc(c.issuer) + '</small></div><span>' + esc(c.role) + '</span></div>'; }).join('') + '</div>';
    return h + '</div>';
  }

  function renderResult(host, r, reg, verdict, at, share) {
    var key = (verdict && verdict.key) || r.verdict;
    var sub = (verdict && verdict.text) || r.note || '';
    var done = reg && reg.done;
    setPanel({
      key: key, big: host + ' — ' + (BIG[key] || BIG[r.verdict] || 'Checked'), sub: sub,
      reach: reg ? reg.reachable + '/' + (reg.total || 12) : '0/12', med: reg && reg.median_ms != null ? S.ms(reg.median_ms) : '—',
      at: S.when(at), facts: factsFor(r), ssl: sslFor(r, host), dns: dnsFor(r), host: host, again: true, share: !!(done && reg.total > 0 && share),
      status: done ? 'Complete' : 'Probing…'
    });
  }


  /* ---------- headline summary under the verdict: moves with the live graph ---------- */
  var HS = { host: null, ms: null, v: null, series: [], up24: null, rep: null, reach: null, total: null };
  function hsRender() {
    var box = $('#hsum'); if (!box) return;
    if (!HS.host) { box.hidden = true; return; }
    box.hidden = false;
    $('#hs-ms').textContent = HS.ms != null ? HS.ms + ' ms' : '\u2014';
    $('#hs-up').textContent = HS.up24 != null ? HS.up24 + '%' : 'new';
    $('#hs-rep').textContent = HS.rep != null ? String(HS.rep) : '\u2014';
    $('#hs-pr').textContent = HS.reach != null ? HS.reach + '/' + HS.total : '\u2014';
    var dot = box.querySelector('.hs-dot'); dot.className = 'hs-dot ' + (HS.v === 'down' ? 'down' : (HS.v && HS.v !== 'up' ? 'slow' : 'up'));
    var vals = HS.series.filter(function (x) { return x != null; });
    if (vals.length > 1) { var mx = Math.max.apply(null, vals.concat([50])), n = HS.series.length; $('#hs-spark').innerHTML = '<polyline fill="none" stroke="#39b54a" stroke-width="1.6" vector-effect="non-scaling-stroke" points="' + HS.series.map(function (x, i) { return x == null ? '' : (60 * i / Math.max(1, n - 1)).toFixed(1) + ',' + (16 - 14 * x / mx).toFixed(1); }).filter(Boolean).join(' ') + '"/>'; }
    var s = HS.host;
    if (HS.v === 'down') s += ' is not answering right now.';
    else if (HS.v === 'inconclusive' || HS.v === 'timeout') s += ' did not answer our quick check just now. It may be down, or it may ignore automated checks.';
    else if (HS.v && HS.v !== 'up') s += ' is answering, but slowly' + (HS.ms != null ? ' (' + HS.ms + ' ms)' : '') + '.';
    else s += ' is up' + (HS.ms != null ? ' and answering in ' + HS.ms + ' ms right now' : '') + '.';
    if (HS.reach != null && HS.total) s += ' ' + (HS.reach === HS.total ? 'All ' + HS.total + ' regions' : HS.reach + ' of ' + HS.total + ' regions') + ' reached it.';
    if (HS.rep != null) s += HS.rep === 0 ? ' Nobody has reported a problem in the last 3 hours.' : ' ' + HS.rep + (HS.rep === 1 ? ' person has' : ' people have') + ' reported a problem in the last 3 hours.';
    $('#hs-line').textContent = s;
  }
  document.addEventListener('sud-live', function (e) {
    var d = e.detail; if (!d || d.host !== HS.host) return;
    if (d.kind === 'sample') { HS.ms = d.ms; HS.v = d.v; HS.series = d.series || []; }
    else if (d.kind === 'hist') HS.up24 = d.uptime24;
    hsRender();
  });

  /* ---------- report a problem with the site just checked ---------- */
  var repHost = null, REPKIND = { site: 'website not loading', login: 'cannot log in', app: 'app not working', slow: 'very slow' };
  var getRange = null;
  function repLoad(host) {
    var range = getRange ? getRange() : '24h';
    fetch('/api/reports.php?host=' + encodeURIComponent(host) + '&range=' + range).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j || host !== repHost) return;
      var total = j.total || 0, rt = S.repRangeText(range);
      $('#rb-title').textContent = total ? total + (total === 1 ? ' problem report' : ' problem reports') + ' for ' + host + ' in ' + rt : 'No problem reports for ' + host + ' in ' + rt;
      HS.rep = j.last3h; hsRender();
      var L = $('#rb-level'); L.className = 'sp-level ' + j.level; L.textContent = j.level === 'high' ? 'Many more than usual' : j.level === 'raised' ? 'More than usual' : '';
      S.repChart($('#rb-chart'), $('#rb-detail'), $('#rb-kinds'), j, { date: $('#rb-date'), axis: $('#rb-axis') });
    }).catch(function () {});
  }
  function repBox(host) {
    var box = $('#rep-box'); if (!box) return;
    var lh = $('#lv-home');
    if (!host) { box.hidden = true; repHost = null; if (lh) { lh.hidden = true; if (window.SUD_LIVE) SUD_LIVE.clear(); } return; }
    if (lh && window.SUD_LIVE && host !== repHost) SUD_LIVE.mount(lh, host);
    if (host === repHost) return;
    repHost = host; box.hidden = false; $('#rb-pick').hidden = true; $('#rb-msg').textContent = '';
    $('#rb-title').textContent = 'Problems reported for ' + host; $('#rb-level').textContent = '';
    if (!getRange) getRange = S.repRanges($('#rb-ranges'), function () { if (repHost) repLoad(repHost); });
    repLoad(host);
  }
  (function () {
    var btn = $('#rb-btn'); if (!btn) return;
    var picker = S.repPicker($('#rb-pick'), function (kinds) {
      if (!repHost) return;
      var h = repHost, m = $('#rb-msg'); m.textContent = 'Sending…';
      fetch('/api/report.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ host: h, kinds: kinds, tz: S.tz() }), credentials: 'same-origin' })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (r) { m.textContent = r.ok ? r.j.message : (r.j.error || 'Sorry, that did not work. Please try again later.'); if (r.ok) { $('#rb-pick').hidden = true; picker.reset(); repHost = null; repBox(h); m.textContent = r.j.message; } })
        .catch(function () { m.textContent = 'Sorry, that did not work. Please try again later.'; });
    });
    btn.addEventListener('click', function () { $('#rb-pick').hidden = !$('#rb-pick').hidden; });
  })();

  /* ---------- run a check ---------- */
  function saveRecent(h) { var a = JSON.parse(S.store.get('sud-recent') || '[]').filter(function (x) { return x !== h; }); a.unshift(h); S.store.set('sud-recent', JSON.stringify(a.slice(0, 6))); drawRecent(); }
  function drawRecent() {
    var a; try { a = JSON.parse(S.store.get('sud-recent') || '[]'); } catch (e) { a = []; }
    var w = $('#recent-wrap'); if (!w) return; w.hidden = !a.length;
    $('#recent-chips').innerHTML = a.map(function (h) { return '<button class="chip" type="button" data-h="' + esc(h) + '">' + esc(h) + '</button>'; }).join('')
      + '<button class="chip dashed" type="button" id="recent-clear">✕ Clear</button>';
  }
  function setBusy(b) { var x = $('#chk-btn'); x.disabled = b; x.firstElementChild.textContent = b ? 'Checking…' : 'Check website'; }
  function run(addr) {
    addr = (addr || '').trim();
    var err = $('#chk-err'); err.textContent = '';
    if (!addr) { err.textContent = 'Please enter a website address.'; $('#chk-input').focus(); return; }
    clearTimeout(state.timer);
    var id = ++state.runId;
    setBusy(true); state.last = addr;
    setPanel({ key: 'pending', big: 'Checking ' + addr + '…', sub: 'Asking our server first, then probes around the world.', status: 'Running' });
    drawProbes([]); chartsClear(); mapMsg('Dispatching probes…'); tip.hidden = true;
    $('#global-pulse').scrollIntoView({ behavior: 'smooth', block: 'start' });
    S.api('check.php', { address: addr }).then(function (j) {
      if (id !== state.runId) return;
      state.host = j.result.host; state.share = j.share; state.result = j.result;
      saveRecent(j.result.host); refreshFeed();
      renderResult(j.result.host, j.result, null, null, j.checked_at, j.share);
      setBusy(false);
      return S.api('regional.php', { share: j.share }).then(function () { poll(id, 0); }).catch(function (e) {
        mapMsg('The worldwide probes are busy, so this result is from our server only.'); finish(id, e.message);
      });
    }).catch(function (e) {
      if (id !== state.runId) return;
      setBusy(false); err.textContent = e.message; mapMsg(''); setPanel({ status: 'Standby' });
    });
  }
  function poll(id, n) {
    if (id !== state.runId) return;
    fetch('/api/regional.php?share=' + state.share, { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (j) {
      if (id !== state.runId) return;
      var reg = j.regional;
      if (reg && reg.probes && reg.probes.length) { mapMsg(''); drawProbes(reg.probes); drawCharts(reg.probes, state.result); }
      if (reg && reg.done) { renderResult(state.host, state.result, reg, j.verdict, reg.measured_at, state.share); finish(id); return; }
      if (reg) renderResult(state.host, state.result, reg, j.verdict, reg.measured_at, state.share);
      if (n > 32) { mapMsg('The probes took too long. This is a partial picture.'); finish(id); return; }
      state.timer = setTimeout(function () { poll(id, n + 1); }, 1500);
    }).catch(function () { if (n > 4) finish(id); else state.timer = setTimeout(function () { poll(id, n + 1); }, 2000); });
  }
  function finish(id) {
    if (id !== state.runId) return;
    if (S.user && state.share) S.api('history.php', { action: 'add', share: state.share }).catch(function () { /* history is optional */ });
    refreshFeed();
  }

  /* ---------- saved / shared result ---------- */
  function loadShared(sid) {
    fetch('/api/share.php?id=' + encodeURIComponent(sid)).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error); return j; }); }).then(function (j) {
      state.host = j.host; state.share = sid; state.result = j.result; $('#chk-input').value = j.host;
      renderResult(j.host, j.result, j.regional, j.verdict, j.checked_at, sid);
      if (j.regional && j.regional.probes) { mapMsg(''); drawProbes(j.regional.probes); drawCharts(j.regional.probes, j.result); } else mapMsg('This shared check has no regional map.');
      $('#pulse-status').textContent = 'Saved result';
      $('#global-pulse').scrollIntoView({ block: 'start' });
    }).catch(function (e) { S.toast(e.message || 'That shared check could not be loaded.', true); });
  }

  /* ---------- share ---------- */
  function initShare() {
    var box = $('#share'); if (!box) return;
    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-share]'); if (!b || !state.share) return;
      var url = location.origin + '/s/' + state.share, text = state.host + ' — is it down or just me? Checked from 12 places worldwide.';
      var k = b.getAttribute('data-share');
      if (k === 'copy') { (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { S.toast('Link copied'); }, function () { window.prompt('Copy this link', url); }); }
      else if (k === 'native') { navigator.share({ title: 'siteupdown.com', text: text, url: url }).catch(function () { /* cancelled */ }); }
      else { var u = { x: 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(text) + '&url=' + encodeURIComponent(url), fb: 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), wa: 'https://wa.me/?text=' + encodeURIComponent(text + ' ' + url) }[k]; window.open(u, '_blank', 'noopener'); }
    });
    if (navigator.share) $('[data-share=native]').hidden = false;
  }

  /* ---------- watch / top / gaming / feed ---------- */
  function sslTag(x) {
    if (!x.ssl) return '';
    var st = x.ssl, d = x.ssl_days, cls = 'ok', txt;
    if (st === 'none') return '<span class="sslt none" title="No HTTPS certificate could be read">SSL: none</span>';
    if (st === 'expired') { cls = 'bad'; txt = 'SSL expired'; } else if (st === 'untrusted' || st === 'mismatch' || st === 'notyet') { cls = 'bad'; txt = 'SSL problem'; }
    else if (st === 'expiring') { cls = 'warn'; txt = 'SSL expires in ' + d + ' d'; } else txt = 'SSL ' + (d != null ? d + ' d' : 'valid');
    return '<span class="sslt ' + cls + '" title="' + esc(st === 'valid' ? 'Certificate valid for ' + d + ' more days' : txt) + '">🔒 ' + esc(txt) + '</span>';
  }
  function siteCard(x) {
    var v = x.verdict, cls = !v ? 'none' : (v === 'up' ? 'up' : (v === 'down' || v === 'timeout' || !x.code ? 'bad' : 'warn'));
    var say = !v ? 'has not been checked yet.' : v === 'up' ? 'is up.' : v === 'down' ? 'is down.' : v === 'timeout' ? 'timed out.' : x.code ? 'answered, but blocks automated checks.' : 'is not responding.';
    var right = x.code ? 'HTTP ' + esc(x.code) + (x.ms != null ? ' · ' + esc(S.ms(x.ms)) : '') : (v ? 'No status' : '');
    return '<div class="row ' + cls + '"><div class="rl"><b>' + tile(x.name, x.host) + (x.page ? '<a href="' + esc(x.page) + '">' + esc(x.name) + '</a>' : esc(x.name)) + '</b><span class="st"><i></i>' + esc(x.host) + ' ' + say + (x.at ? ' <em>Checked ' + esc(S.ago(x.at)) + '</em>' : '') + '</span></div>'
      + '<div class="rr"><span class="code">' + right + '</span>' + sslTag(x)
      + '<button class="go" type="button" data-h="' + esc(x.host) + '" aria-label="Check ' + esc(x.name) + '" title="Check ' + esc(x.name) + '">↗</button></div></div>';
  }
  var topItems = [], topFilter = 'all', topCat = '', topLimit = 12, topLabel = '';
  function drawTop() {
    var g = $('#top-grid');
    var items = topItems.filter(function (x) { return topFilter === 'all' || (x.verdict && x.verdict !== 'up'); });
    var bad = topItems.filter(function (x) { return x.verdict && x.verdict !== 'up'; }).length, got = topItems.filter(function (x) { return x.verdict; });
    $('#f-issues').textContent = 'Issues (' + bad + ')';
    $('#top-count').textContent = got.length ? (got.length - bad) + '/' + got.length + ' answering' : '';
    var shown = topCat && topFilter === 'all' ? items.slice(0, topLimit) : items;
    g.innerHTML = items.length ? shown.map(function (x) { return siteCard(x); }).join('') : '<div class="skeleton">' + (topFilter === 'all' ? 'Sweeping the watchlist…' : 'No issues right now. Every site we have checked is responding.') + '</div>';
    var mo = $('#top-more'); if (!mo) return;
    if (topCat && items.length > shown.length) { mo.hidden = false; mo.innerHTML = '<button class="btn small ghost" type="button" id="top-showall">Show all ' + items.length + ' ' + esc(topLabel) + ' sites</button> <a class="fine" href="/is-it-down/#' + esc(topCat) + '">or open the full list</a>'; }
    else if (topCat) { mo.hidden = false; mo.innerHTML = '<a class="fine" href="/is-it-down/#' + esc(topCat) + '">Open the full ' + esc(topLabel) + ' list</a>'; }
    else { mo.hidden = false; mo.innerHTML = '<a class="fine" href="/is-it-down/">Browse every site by category</a>'; }
  }
  function loadOutages() {
    var ul = $('#ro-list'); if (!ul) return;
    function dur(sec) { var m = Math.round(sec / 60); if (m < 2) return 'under 2 min'; if (m < 90) return m + ' min'; var h = Math.floor(m / 60); if (h < 48) return h + ' h' + (m % 60 ? ' ' + (m % 60) + ' min' : ''); return Math.floor(h / 24) + ' days'; }
    function ago(iso) { var m = Math.max(0, Math.round((Date.now() - new Date(iso)) / 60000)); if (m < 2) return 'just now'; if (m < 90) return m + ' min ago'; var h = Math.round(m / 60); return h < 48 ? h + ' h ago' : Math.round(h / 24) + ' days ago'; }
    fetch('/api/outages.php?n=5').then(function (r) { return r.json(); }).then(function (j) {
      ul.textContent = '';
      var live = (j.items || []).filter(function (o) { return !o.ended; }).length;
      $('#ro-lead').textContent = live ? live + (live === 1 ? ' popular site is' : ' popular sites are') + ' down right now. Sites that came back in the last 24 hours are listed underneath.' : 'Nothing we watch is down right now. Sites that had an outage and came back in the last 24 hours are listed underneath.';
      if (!j.items || !j.items.length) { var li = document.createElement('li'); li.className = 'ro-none'; li.textContent = 'No outages right now, and none in the last 24 hours. All quiet.'; ul.appendChild(li); return; }
      j.items.forEach(function (o) {
        var li = document.createElement('li'); li.className = o.ended ? 'ro-end' : 'ro-on';
        var a = document.createElement(o.page ? 'a' : 'span'); if (o.page) a.href = o.page; a.className = 'ro-name'; a.textContent = o.name;
        var st = document.createElement('span'); st.className = 'ro-st'; st.textContent = o.ended ? 'Back up \u00b7 was down about ' + dur(o.seconds) : 'Down now \u00b7 ' + dur(o.seconds) + ' so far';
        var t = document.createElement('small'); t.textContent = o.ended ? 'Started ' + ago(o.started) : 'Since ' + new Date(o.started).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        li.appendChild(a); li.appendChild(st); li.appendChild(t); ul.appendChild(li);
      });
    }).catch(function () { ul.innerHTML = '<li class="ro-none">Could not load recent outages.</li>'; });
  }
  setTimeout(loadOutages, 300); setInterval(loadOutages, 60000);
  function loadTop() {
    fetch('/api/top.php' + (topCat ? '?cat=' + encodeURIComponent(topCat) : '')).then(function (r) { return r.json(); }).then(function (j) {
      topItems = j.items || []; drawTop();
      $('#top-updated').textContent = j.updated ? 'A snapshot, not continuous uptime monitoring. Last sweep ' + S.ago(j.updated) + '.' : 'The first sweep is on its way.';
    }).catch(function () { $('#top-grid').innerHTML = '<div class="skeleton">Could not load the watchlist. Please refresh.</div>'; });
  }
  var gq = '', gcat = 'All', gpage = 1, gtimer;
  function loadGaming() {
    var u = '/api/gaming.php?page=' + gpage + '&cat=' + encodeURIComponent(gcat) + '&q=' + encodeURIComponent(gq);
    fetch(u).then(function (r) { return r.json(); }).then(function (j) {
      gpage = j.page;
      $('#g-cats').innerHTML = j.cats.map(function (c) { return '<button class="chip" type="button" data-c="' + esc(c) + '" aria-pressed="' + (c === gcat) + '">' + esc(c) + '</button>'; }).join('');
      $('#g-count').textContent = j.total + (j.total === j.all_total ? ' services' : ' of ' + j.all_total + ' services') + ' · page ' + j.page + ' of ' + j.pages;
      $('#g-grid').innerHTML = j.items.length ? j.items.map(function (x) { return siteCard(x); }).join('') : '<div class="skeleton">No services match that search.</div>';
      $('#g-prev').disabled = j.page <= 1; $('#g-next').disabled = j.page >= j.pages;
    }).catch(function () { $('#g-grid').innerHTML = '<div class="skeleton">Could not load gaming services. Please refresh.</div>'; });
  }
  function refreshFeed() {
    fetch('/api/recent.php').then(function (r) { return r.json(); }).then(function (j) {
      var rows = (j.items || []).map(function (x) {
        return '<tr><td><a href="/?q=' + encodeURIComponent(x.host) + '" data-h="' + esc(x.host) + '">' + esc(x.host) + '</a></td><td>' + S.pill(x.verdict) + '</td><td>' + esc(S.ago(x.at)) + '</td></tr>';
      }).join('');
      $('#feed-body').innerHTML = rows || '<tr><td colspan="3" class="skeleton">No checks yet. Be the first.</td></tr>';
    }).catch(function () { $('#feed-body').innerHTML = '<tr><td colspan="3" class="skeleton">Could not load recent checks.</td></tr>'; });
  }

  /* ---------- wiring ---------- */
  function go(h) { $('#chk-input').value = h; run(h); }
  document.addEventListener('DOMContentLoaded', function () {
    drawLand(); setPanel({}); drawRecent(); initShare();
    $('#chk-form').addEventListener('submit', function (e) { e.preventDefault(); run($('#chk-input').value); });
    document.addEventListener('click', function (e) {
      var h = e.target.closest('[data-h]');
      if (h && !h.closest('#recent-clear')) { e.preventDefault(); go(h.getAttribute('data-h')); return; }
      if (e.target.closest('#recent-clear')) { S.store.del('sud-recent'); drawRecent(); }
    });
    $('#run-again').addEventListener('click', function () { if (state.host) go(state.host); });
    $('#wl-add').addEventListener('click', function () {
      if (!S.user) { location.href = '/login?next=' + encodeURIComponent('/'); return; }
      S.api('watch.php', { action: 'add', address: state.host }).then(function () { S.toast(state.host + ' added to your watchlist'); }).catch(function (e) { S.toast(e.message, true); });
    });
    S.$$('[data-f]').forEach(function (b) { b.addEventListener('click', function () { topFilter = b.getAttribute('data-f'); S.$$('[data-f]').forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); drawTop(); }); });
    var tc = $('#top-cats'); if (tc) tc.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cat]'); if (!b) return;
      topCat = b.getAttribute('data-cat'); topLabel = b.textContent; topLimit = 12;
      S.$$('#top-cats [data-cat]').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
      $('#top-grid').innerHTML = '<div class="skeleton">Loading&hellip;</div>'; loadTop();
    });
    document.addEventListener('click', function (e) { if (e.target.closest('#top-showall')) { topLimit = 9999; drawTop(); } });
    var rf = $('#top-refresh'); if (rf) rf.addEventListener('click', function () { loadTop(); });
    $('#g-q').addEventListener('input', function (e) { clearTimeout(gtimer); gtimer = setTimeout(function () { gq = e.target.value.trim(); gpage = 1; loadGaming(); }, 250); });
    $('#g-cats').addEventListener('click', function (e) { var c = e.target.closest('[data-c]'); if (c) { gcat = c.getAttribute('data-c'); gpage = 1; loadGaming(); } });
    $('#g-prev').addEventListener('click', function () { gpage--; loadGaming(); $('#online-gaming').scrollIntoView({ behavior: 'smooth' }); });
    $('#g-next').addEventListener('click', function () { gpage++; loadGaming(); $('#online-gaming').scrollIntoView({ behavior: 'smooth' }); });
    loadTop(); loadGaming(); refreshFeed();
    setInterval(function () { if (!document.hidden) { loadTop(); loadGaming(); refreshFeed(); } }, 60000);
    var p = new URLSearchParams(location.search);
    var pm = location.pathname.match(/^\/s\/([a-f0-9]{10})\/?$/), rid = (pm && pm[1]) || p.get('r');
    if (rid && /^[a-f0-9]{10}$/.test(rid)) loadShared(rid);
    else if (p.get('q')) { $('#chk-input').value = p.get('q'); run(p.get('q')); }
  });
})();
