/* "Is X down?" pages: live status, visitor problem reports and the site directory. */
(function () {
  'use strict';
  var root = document.querySelector('[data-sp]');
  if (!root) return;
  var S = window.SUD;
  function $(s, r) { return (r || document).querySelector(s); }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function ago(iso) {
    var s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 90) return 'just now';
    if (s < 3600) return Math.round(s / 60) + ' min ago';
    if (s < 86400) return Math.round(s / 3600) + ' h ago';
    return Math.round(s / 86400) + ' days ago';
  }
  function getJSON(u) { return fetch(u, { credentials: 'same-origin' }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, status: r.status, j: j }; }); }); }

  /* ---- browser notifications ---- */
  var pb = $('#sp-push'), pm = $('#sp-pushmsg'), pHost = (($('#lv-slot') || {}).getAttribute ? $('#lv-slot').getAttribute('data-host') : '') || '';
  if (pb && pHost && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window) {
    var pName = pb.textContent.replace(/^Notify me when /, '').replace(/ changes$/, '');
    var pKey = 'sud-push'; function pGet() { try { return JSON.parse(localStorage.getItem(pKey) || '[]'); } catch (x) { return []; } }
    function pSet(a) { try { localStorage.setItem(pKey, JSON.stringify(a)); } catch (x) {} }
    function pOn() { return pGet().indexOf(pHost) > -1 && Notification.permission === 'granted'; }
    function pDraw() { pb.firstElementChild.textContent = pOn() ? 'Notifications on \u00b7 turn off' : 'Notify me when ' + pName + ' changes'; pb.hidden = false; }
    function post(body) { return fetch('/api/push.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then(function (r) { return r.json(); }); }
    function u8(b) { var p = '='.repeat((4 - b.length % 4) % 4), s = atob((b + p).replace(/-/g, '+').replace(/_/g, '/')), o = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) o[i] = s.charCodeAt(i); return o; }
    pDraw();
    pb.addEventListener('click', function () {
      pb.disabled = true; pm.textContent = '';
      var done = function (m) { pb.disabled = false; pm.textContent = m || ''; pDraw(); };
      if (pOn()) {
        navigator.serviceWorker.getRegistration('/').then(function (reg) { return reg ? reg.pushManager.getSubscription() : null; }).then(function (sub) {
          var a = pGet().filter(function (h) { return h !== pHost; }); pSet(a);
          if (!sub) return;
          return post({ act: 'unsub', host: pHost, sub: sub.toJSON() }).then(function () { if (!a.length) return sub.unsubscribe(); });
        }).then(function () { done('Notifications are off for ' + pName + '.'); }, function () { done('Could not turn them off. Try again.'); });
        return;
      }
      Notification.requestPermission().then(function (perm) {
        if (perm !== 'granted') { done('Notifications are blocked. Allow them for this site in your browser settings, then try again.'); return; }
        return navigator.serviceWorker.register('/sw.js').then(function () { return navigator.serviceWorker.ready; }).then(function (reg) {
          return reg.pushManager.getSubscription().then(function (existing) {
            if (existing) return existing;
            return fetch('/api/push.php').then(function (r) { return r.json(); }).then(function (k) { return reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: u8(k.key) }); });
          });
        }).then(function (sub) { return post({ act: 'sub', host: pHost, sub: sub.toJSON() }); }).then(function (r) {
          if (r.error) { done(r.error); return; }
          var a = pGet(); if (a.indexOf(pHost) < 0) a.push(pHost); pSet(a);
          done('Done. We will alert you if ' + pName + ' goes down and when it comes back.');
        });
      }).catch(function (er) { done('Your browser would not allow notifications here.'); });
    });
  }

  [].forEach.call(document.querySelectorAll('.sp-embed-copy'), function (ec) {
    var label = ec.firstElementChild.textContent;
    ec.addEventListener('click', function () {
      var t = document.getElementById(ec.getAttribute('data-for')), s = ec.firstElementChild;
      t.focus(); t.select();
      try { navigator.clipboard.writeText(t.value).then(function () { s.textContent = 'Copied'; setTimeout(function () { s.textContent = label; }, 1800); }, function () {}); } catch (x) { s.textContent = 'Press and hold to copy'; }
    });
  });

  /* ----------------------------------------------------------------- directory */
  if (root.getAttribute('data-sp') === 'dir') {
    var VMAP = { up: 'up', down: 'down', timeout: 'slow', inconclusive: 'unsure' };
    getJSON('/api/sitelist.php').then(function (r) {
      if (!r.ok) return;
      document.querySelectorAll('.dgroup li').forEach(function (li) {
        var d = r.j.items[li.getAttribute('data-host')];
        if (!d) return;
        var i = li.querySelector('i');
        if (d.v) { i.className = 'dot-s ' + (VMAP[d.v] || 'unsure'); i.title = d.v === 'up' ? 'Up' : d.v === 'down' ? 'Down' : d.v === 'timeout' ? 'Slow or timing out' : 'Not sure'; }
        if (d.rep >= 3) li.querySelector('.rep').textContent = d.rep + ' reports in 3 h';
      });
    }).catch(function () {});
    getJSON('/api/reports.php?top=1').then(function (r) {
      if (!r.ok || !r.j.items || !r.j.items.length) return;
      $('#sp-toplist').innerHTML = r.j.items.map(function (x) { return '<li><a href="' + esc(x.page) + '">' + esc(x.name) + '</a> <span>' + x.count + ' reports in the last 3 hours</span></li>'; }).join('');
      $('#sp-top').hidden = false;
    }).catch(function () {});
    var f = $('#sp-find');
    if (f) f.addEventListener('input', function () {
      var q = f.value.trim().toLowerCase();
      document.querySelectorAll('.dgroup').forEach(function (g) {
        var any = false;
        g.querySelectorAll('li').forEach(function (li) { var m = !q || li.getAttribute('data-name').indexOf(q) > -1 || li.getAttribute('data-host').indexOf(q) > -1; li.hidden = !m; if (m) any = true; });
        g.hidden = !any;
      });
    });
    return;
  }

  /* ----------------------------------------------------------------- site page */
  var host = root.getAttribute('data-host'), name = root.getAttribute('data-name');
  var rep = { level: 'none' }, cur = null, wblk = null, isApp = root.getAttribute('data-app') === '1';

  function headline() {
    var pill = $('#sp-pill'), msg = $('#sp-msg');
    var busy = rep.level === 'high' || rep.level === 'raised';
    if (!cur) { pill.className = 'sp-pill unsure'; pill.textContent = 'No data yet'; msg.textContent = 'We have not run a scheduled check of ' + host + ' yet. Use the button below to test it now.'; return; }
    var v = cur.verdict;
    $('#sp-status').setAttribute('data-v', v);
    var cs = $('#sp-cs'); if (!cs) { cs = document.createElement('div'); cs.id = 'sp-cs'; cs.className = 'cantsure'; $('#sp-status').appendChild(cs); }
    S.cantSure(cs, host, v === 'timeout' || v === 'inconclusive');
    if (v === 'up') {
      pill.className = 'sp-pill up'; pill.textContent = 'Up';
      msg.textContent = busy ? 'We can reach ' + host + ', but many visitors are reporting problems. It may affect the app, logging in or certain regions.'
        : (cur.code == null || cur.code >= 400 ? name + ' is up. Our own check was blocked or got no clear answer ' + ago(cur.at) + ', but it was reached from most of the places on the map below.'
          : name + ' is up. Our server reached ' + host + ' ' + ago(cur.at) + (cur.ms ? ' in ' + cur.ms + ' ms' : '') + '.') + (isApp ? ' This shows the servers are reachable. Problems inside the app can still happen, so check the reports below.' : '');
    } else if (v === 'down') {
      pill.className = 'sp-pill down'; pill.textContent = 'Down';
      msg.textContent = name + ' looks down. Our server got errors on two attempts ' + ago(cur.at) + '.';
    } else if (wblk && (v === 'timeout' || v === 'inconclusive')) {
      pill.className = 'sp-pill blocked'; pill.textContent = 'Blocked';
      msg.textContent = name + ' \u2014 blocking automated checks. ' + host + ' is answering, but it turns our checks away' + (wblk.code ? ' (error ' + wblk.code + ')' : '') + '. ' + wblk.n + ' of ' + wblk.total + ' places we tried got a reply and were refused, so the site itself is running. Try opening it yourself to be sure.';
    } else if (v === 'timeout') {
      pill.className = 'sp-pill unsure'; pill.textContent = 'No answer';
      msg.textContent = 'Our server did not get an answer from ' + host + ' ' + ago(cur.at) + '. It may be down, overloaded, or simply ignoring automated checks.';
    } else {
      pill.className = 'sp-pill unsure'; pill.textContent = 'Not sure';
      msg.textContent = 'We could not confirm the status of ' + host + ' ' + ago(cur.at) + '. It may be blocking automated checks, which does not mean it is down.';
    }
  }
  function stat(label, val) { return '<div class="sp-stat"><span>' + esc(label) + '</span><b>' + esc(val) + '</b></div>'; }

  getJSON('/api/uptime.php?host=' + encodeURIComponent(host) + '&range=24h').then(function (r) {
    if (r.ok) {
      cur = r.j.current;
      var u = r.j.uptime, h = '';
      h += stat('Response time', cur.ms ? cur.ms + ' ms' : 'n/a');
      h += stat('Uptime, 24 hours', u['24h'] != null ? u['24h'] + '%' : 'n/a');
      h += stat('Uptime, 7 days', u['7d'] != null ? u['7d'] + '%' : 'n/a');
      h += stat('Certificate', r.j.ssl && r.j.ssl.days != null ? (r.j.ssl.days < 0 ? 'Expired' : r.j.ssl.days + ' days left') : 'n/a');
      $('#sp-stats').innerHTML = h;
    }
    headline();
  }).catch(function () { headline(); });

  /* Plain-English explanation of each result code, shown on hover, keyboard focus or tap */
  var CODES = {
    200: 'OK. The page loaded normally.', 201: 'Created. The request worked and something new was made.', 204: 'No content. The server answered fine but sent nothing back.',
    301: 'Moved permanently. The site sent us to a new address and we followed it.', 302: 'Temporary redirect. The site sent us to another page for now and we followed it.',
    303: 'See other. The site sent us to a different page and we followed it.', 304: 'Not modified. Nothing has changed since we last looked.',
    307: 'Temporary redirect. The site sent us to another address for now and we followed it.', 308: 'Permanent redirect. The site has moved for good and sent us to its new address. This is normal and means the site answered.',
    400: 'Bad request. The server did not understand the request.', 401: 'Login needed. The page is private, but the site itself is answering.',
    403: 'Forbidden. The site answered but refused our check. This often happens when a site blocks automated visitors, so it is not necessarily down.',
    404: 'Not found. The server answered but could not find that page.', 405: 'Method not allowed. The server answered but did not accept this kind of request.',
    408: 'Request timeout. The server gave up waiting for the request.', 410: 'Gone. That page has been removed for good.', 418: 'The server answered with a joke code. It is up.',
    429: 'Too many requests. The site is up but asked us to slow down, so it may be limiting automated checks.', 451: 'Unavailable for legal reasons. The site is blocking access from here.',
    500: 'Server error. Something went wrong on the website\'s own server.', 501: 'Not implemented. The server does not support this request.',
    502: 'Bad gateway. A server in front of the site got a bad answer from the main server. Usually a sign of an outage.', 503: 'Service unavailable. The site is overloaded or down for maintenance.',
    504: 'Gateway timeout. A server in front of the site waited too long for the main server to answer.', 520: 'Unknown error from Cloudflare, the service in front of the site.',
    521: 'Web server is down. Cloudflare could not reach the site\'s own server.', 522: 'Connection timed out between Cloudflare and the site\'s own server.',
    523: 'Origin unreachable. Cloudflare could not find the route to the site\'s own server.', 524: 'Timeout. The site\'s own server took too long to answer Cloudflare.',
    525: 'Secure connection failed between Cloudflare and the site\'s own server.', 526: 'Invalid certificate on the site\'s own server.'
  };
  function codeTip(p) {
    var c = +p.code, t = CODES[c];
    if (!t && c >= 200 && c < 300) t = 'Success. The page answered normally.';
    if (!t && c >= 300 && c < 400) t = 'Redirect. The site sent us to another address and we followed it.';
    if (!t && c >= 400 && c < 500) t = 'Client error. The server answered but refused or could not find the request.';
    if (!t && c >= 500) t = 'Server error. Something went wrong on the website\'s own server.';
    if (!t) t = p.state === 'none' ? 'No answer. This place could not reach the site before our check timed out.' : p.state === 'blocked' ? 'The site answered but turned our check away.' : 'Our probe reached the site.';
    return (p.code ? 'Code ' + p.code + ': ' : '') + t;
  }
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

  /* Deeper insight: grade, where the time goes, typical day, outage timeline, who runs it. All from our own checks. */
  getJSON('/api/sitestats.php?host=' + encodeURIComponent(host)).then(function (r) {
    var d = r.ok && r.j; if (!d || d.error || !d.u30) return;
    var box = $('#sp-deepc'); if (!box) return;
    function dur(sec) { var m = Math.round(sec / 60); if (m < 2) return 'under 2 min'; if (m < 90) return m + ' min'; var h = Math.floor(m / 60); return h < 48 ? h + ' h' + (m % 60 ? ' ' + (m % 60) + ' min' : '') : Math.floor(h / 24) + ' days'; }
    function pct(v) { return v == null ? '–' : (v >= 99.995 ? '100' : v.toFixed(2).replace(/0$/, '').replace(/\.0$/, '')) + '%'; }
    var h = '', G = { A: 'Excellent', B: 'Very good', C: 'Good', D: 'Patchy', F: 'Poor' };
    var capName = d.cat ? d.cat.charAt(0).toUpperCase() + d.cat.slice(1) : '';
    if (d.grade) {
      h += '<div class="dp-top"><div class="dp-grade g' + d.grade + '" aria-label="Reliability grade ' + d.grade + '">' + d.grade + '</div><div><b>' + G[d.grade] + ' reliability</b><p class="note" style="margin:2px 0 0">' + pct(d.u30.pct) + ' uptime over 30 days, ' + pct(d.u7.pct) + ' over 7 days. ' + d.u30.outages + (d.u30.outages === 1 ? ' outage' : ' outages') + (d.u30.down ? ', about ' + dur(d.u30.down) + ' down in total' : '') + '.' + (d.rank ? ' Ranked ' + d.rank.n + ' of ' + d.rank.of + ' in ' + esc(capName.toLowerCase()) + '.' : '') + '</p></div></div>';
      h += '<p class="note">Grade from our own checks over 30 days: A is 99.9% or better, B 99.5%, C 99%, D 97%, F below that. A site that blocks automated checks is never marked down for it.</p>';
    } else {
      h += '<p class="note" style="margin-top:0">We need a little more history before we can grade ' + esc(d.name) + '. So far: ' + (d.u30.checks || 0) + ' checks recorded.</p>';
    }
    var t = d.timing;
    if (t) {
      var tot = t.dns + t.conn + t.tls + t.ttfb || 1, seg = [['dns', 'DNS lookup', t.dns], ['conn', 'Connecting', t.conn], ['tls', 'Secure handshake', t.tls], ['ttfb', 'Waiting for the site', t.ttfb]];
      h += '<h3 class="dp-h">Where the time goes</h3><div class="dp-bar" role="img" aria-label="Time breakdown">' + seg.map(function (x) { return x[2] > 0 ? '<i class="s-' + x[0] + '" style="flex:' + x[2] + '" title="' + x[1] + ': ' + x[2] + ' ms"></i>' : ''; }).join('') + '</div><ul class="dp-leg">' + seg.map(function (x) { return '<li><i class="s-' + x[0] + '"></i>' + x[1] + ' <b>' + x[2] + ' ms</b></li>'; }).join('') + '</ul><p class="note">Average of our last 24 hours of checks (' + t.n + ' readings), measured from our server. If \"Waiting for the site\" is the biggest part, the site itself is the slow bit.</p>';
    }
    var hs = d.hours || [], have = hs.filter(function (x) { return x != null; });
    if (have.length >= 12) {
      var off = Math.round(-new Date().getTimezoneOffset() / 60), loc = new Array(24).fill(null);
      hs.forEach(function (v, u) { loc[((u + off) % 24 + 24) % 24] = v; });
      var mx = Math.max.apply(null, have), mn = Math.min.apply(null, have), hi = loc.indexOf(mx), lo = loc.indexOf(mn);
      function hh(x) { return ('0' + x).slice(-2) + ':00'; }
      h += '<h3 class="dp-h">Typical day</h3><div class="dp-day" role="img" aria-label="Average response time by hour of day">' + loc.map(function (v, i) { return '<i style="height:' + (v == null ? 2 : Math.max(6, Math.round(100 * v / mx))) + '%" class="' + (i === hi ? 'hi' : i === lo ? 'lo' : '') + '" title="' + hh(i) + ': ' + (v == null ? 'no data' : v + ' ms') + '"></i>'; }).join('') + '</div><div class="dp-axis"><span>00:00</span><span>12:00</span><span>23:00</span></div><p class="note">Usually slowest around ' + hh(hi) + ' (about ' + mx + ' ms) and quickest around ' + hh(lo) + ' (about ' + mn + ' ms), in your time zone, over the last 5 weeks.</p>';
    }
    h += '<h3 class="dp-h">Outage timeline</h3>';
    if (d.outages && d.outages.length) {
      h += '<ul class="dp-out">' + d.outages.map(function (o) { var dt = new Date(o.started); return '<li><span>' + dt.toLocaleDateString([], { day: 'numeric', month: 'short' }) + ', ' + dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + '</span><b>' + (o.ended ? dur(o.seconds) : 'Ongoing, ' + dur(o.seconds) + ' so far') + '</b></li>'; }).join('') + '</ul>' + (d.mtbf_h ? '<p class="note">' + d.outages_90 + ' outages in the last 90 days. On average one every ' + (d.mtbf_h >= 48 ? Math.round(d.mtbf_h / 24) + ' days' : d.mtbf_h + ' hours') + '.</p>' : '');
    } else h += '<p class="note" style="margin-top:0">No outages recorded in the last 90 days.</p>';
    if (d.provider) h += '<h3 class="dp-h">What is behind it</h3><p class="note" style="margin-top:0">Its responses carry the marks of <b>' + esc(d.provider) + '</b>. When that provider has trouble, many sites can be affected at once. This is a guess from the response headers, not a confirmed fact.</p>';
    h += '<div class="dp-act"><a class="btn small ghost" href="/compare?a=' + encodeURIComponent(host) + '"><span>Compare with another site</span></a> <a class="btn small ghost" href="/site-report?host=' + encodeURIComponent(host) + '"><span>Printable report</span></a> <a class="btn small ghost" href="/api/export.php?host=' + encodeURIComponent(host) + '&days=30" download><span>Download CSV</span></a></div>';
    box.innerHTML = h; $('#sp-deep').hidden = false;
  }).catch(function () {});

  /* Latest worldwide snapshot from the background sweep, if there is one */
  getJSON('/api/world.php?host=' + encodeURIComponent(host)).then(function (r) {
    var w = r.ok && r.j.world; if (!w || !w.probes || !w.probes.length) return;
    var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (z) {}
    var LBL = { ok: ['up', 'Reached'], error: ['down', 'Server error'], blocked: ['unsure', 'Blocked our check'], none: ['slow', 'No answer'] };
    var rows = w.probes.slice().sort(function (a, b) { return (a.country || '').localeCompare(b.country || ''); }).map(function (p) {
      var l = LBL[p.state] || LBL.none, nm = p.country ? (dn ? (dn.of(p.country) || p.country) : p.country) : (p.continent || '');
      return '<tr><td data-l="Place">' + esc(nm) + (p.city ? ' <span class="sp-ms">' + esc(p.city) + '</span>' : '') + '</td><td data-l="Result"><span class="sp-pill ' + l[0] + ' has-tip" tabindex="0" role="button" data-tip="' + esc(codeTip(p)) + '">' + l[1] + (p.code ? ' ' + p.code : '') + '</span></td><td data-l="Time">' + (p.ms != null && p.state !== 'none' ? p.ms + ' ms' : '') + '</td></tr>';
    });
    $('#sp-wtab tbody').innerHTML = rows.join('');
    /* small dotted world map with one marker per place */
    (function () {
      var svg = $('#sp-wsvg'), M = window.SUD_MAP; if (!svg || !M) return;
      var Wd = 1000, Hd = Math.round(Wd * 142 / 360 * 10) / 10, cell = Wd * M.cell / 360, sz = cell * 0.72, o = (cell - sz) / 2, d = '';
      M.runs.forEach(function (runs, r) { runs.forEach(function (run) { for (var c = run[0]; c < run[0] + run[1]; c++) d += 'M' + (c * cell + o).toFixed(1) + ' ' + (r * cell + o).toFixed(1) + 'h' + sz.toFixed(1) + 'v' + sz.toFixed(1) + 'h-' + sz.toFixed(1) + 'z'; });
      });
      var mk = '', TXT = { ok: 'Reached', error: 'Server error', blocked: 'Blocked our check', none: 'No answer' };
      w.probes.forEach(function (p) {
        if (p.lat == null || p.lon == null) return;
        var x = (p.lon + 180) / 360 * Wd, y = (84 - p.lat) / 142 * (Wd * 142 / 360), st = LBL[p.state] ? p.state : 'none';
        var nm = (p.city ? p.city + ', ' : '') + (p.country ? (dn ? (dn.of(p.country) || p.country) : p.country) : '') + ': ' + TXT[st] + (p.ms != null && st !== 'none' ? ', ' + p.ms + ' ms' : '');
        mk += '<g class="pr" role="img" aria-label="' + esc(nm) + '"><title>' + esc(nm) + '</title><circle class="mk-hit" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="20"/><circle class="mk ' + st + '" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="8"/></g>';
      });
      svg.setAttribute('viewBox', '0 0 ' + Wd + ' ' + Hd);
      svg.innerHTML = '<path class="map-land" d="' + d + '"/>' + mk;
    })();
    var nb = 0, cc = {}; w.probes.forEach(function (p) { if (p.state === 'blocked') { nb++; if (p.code) cc[p.code] = (cc[p.code] || 0) + 1; } });
    $('#sp-wsum').textContent = w.reachable + ' of ' + w.total + ' places reached ' + host + (w.median_ms ? ', typical time ' + w.median_ms + ' ms' : '') + '.' + (nb ? ' ' + nb + (nb === 1 ? ' place' : ' places') + ' got an answer but turned our check away.' : '');
    if (w.total >= 10 && nb / w.total >= 0.8 && (!w.measured_at || Date.now() - Date.parse(w.measured_at) < 14400000)) {
      var top = null; Object.keys(cc).forEach(function (k) { if (top == null || cc[k] > cc[top]) top = k; });
      wblk = { n: nb, total: w.total, code: top }; headline();
    }
    if (w.measured_at) $('#sp-wwhen').textContent = ago(w.measured_at);
    $('#sp-world').hidden = false;
  }).catch(function () {});

  var kindName = { site: 'website not loading', login: 'cannot log in', app: 'app not working', slow: 'very slow' };
  var range = '24h', getRange = S.repRanges($('#sp-ranges'), function (r) { range = r; loadReports(); });
  function renderReports() {
    S.repChart($('#sp-chart'), $('#sp-detail'), $('#sp-kinds'), rep, { date: $('#sp-date'), axis: document.querySelector('#sp-reports .sp-axis') });
    var total = rep.total || 0, rt = S.repRangeText(rep.range);
    $('#sp-chart').classList.toggle('empty', !total);
    $('#sp-rtotal').textContent = total ? total + (total === 1 ? ' problem report' : ' problem reports') + ' in ' + rt : 'No problem reports in ' + rt;
    var L = $('#sp-rlevel');
    L.className = 'sp-level ' + rep.level;
    L.textContent = rep.level === 'high' ? 'Many more than usual' : rep.level === 'raised' ? 'More than usual' : rep.level === 'low' ? 'Normal levels' : '';
    headline();
  }
  function loadReports() {
    getJSON('/api/reports.php?host=' + encodeURIComponent(host) + '&range=' + range).then(function (r) { if (r.ok) { rep = r.j; renderReports(); } }).catch(function () {});
  }
  loadReports();
  var feedUl = $('#sp-feed'); function loadFeed() { S.repFeed(feedUl, host, false); } loadFeed();

  var btn = $('#sp-rbtn'), pick = $('#sp-rpick'), rmsg = $('#sp-rmsg');
  S.repFix($('#sp-fix'), function () { return host; }, rmsg, function () { loadFeed(); });
  var key = 'sud-rep-' + host, last = 0;
  try { last = parseInt(localStorage.getItem(key) || '0', 10) || 0; } catch (e) {}
  btn.addEventListener('click', function () { pick.hidden = !pick.hidden; });
  var picker = S.repPicker(pick, function (kinds) {
    rmsg.textContent = 'Sending…';
    S.repLoc(pick).then(function (loc) { return fetch('/api/report.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.assign({ host: host, kinds: kinds, tz: S.tz() }, loc || {})), credentials: 'same-origin' }); })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        rmsg.textContent = r.ok ? r.j.message : (r.j.error || 'Sorry, that did not work. Please try again later.');
        if (r.ok) { pick.hidden = true; picker.reset(); try { localStorage.setItem(key, String(Date.now())); } catch (e) {} loadReports(); loadFeed(); }
      }).catch(function () { rmsg.textContent = 'Sorry, that did not work. Please try again later.'; });
  });
})();

/* App servers card (only on pages for apps) */
(function () {
  var root = document.querySelector('[data-sp="site"][data-app]');
  if (!root) return;
  var host = root.getAttribute('data-host');
  var LBL = { up: ['up', 'Up'], down: ['down', 'Down'], timeout: ['slow', 'Slow'], inconclusive: ['unsure', 'Not sure'] };
  function e(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  fetch('/api/appsvc.php?host=' + encodeURIComponent(host)).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
    if (!j || !j.items || !j.items.length) return;
    document.getElementById('sp-svc').innerHTML = j.items.map(function (x) {
      var l = x.v ? LBL[x.v] || LBL.inconclusive : ['unsure', 'Not checked yet'];
      return '<li><span class="sp-pill ' + l[0] + '">' + l[1] + '</span> <b>' + e(x.label) + '</b> <code>' + e(x.host) + '</code>' + (x.ms && x.v === 'up' ? ' <span class="sp-ms">' + x.ms + ' ms</span>' : '') + '</li>';
    }).join('');
    var rank = { down: 3, timeout: 2, inconclusive: 1, up: 0 }, worst = null;
    j.items.forEach(function (x) { if (x.v && (worst === null || rank[x.v] > rank[worst])) worst = x.v; });
    if (worst) document.getElementById('sp-app').setAttribute('data-v', worst);
    document.getElementById('sp-app').hidden = false;
  }).catch(function () {});
})();
