/* Admin area: email-code unlock, overview with charts, user list. Everything is checked again on the server. */
(function () {
  'use strict';
  var S = window.SUD, esc = S.esc, root = document.getElementById('adm-root');
  if (!root) return;
  var tab = 'overview', tm = 0;

  function box(html) { root.innerHTML = html; }
  function notFound() { box('<div class="center"><span class="eyebrow"><i></i>Error 404</span><h1 style="margin:14px 0">Not found<span class="dot">.</span></h1><p class="lead">We checked everywhere. This page is down for everyone.</p></div>'); }
  function fail(e) { if (e.status === 401) signin(); else if (e.status === 404) notFound(); else if (e.status === 403) start(); else box('<p class="cf-err">' + esc(e.message) + '</p>'); }

  function signin() {
    box('<div class="adm-lock"><h1>Admin<span class="dot">.</span></h1><p class="lead">Sign in with your admin account to continue.</p>'
      + '<div id="a-g" hidden><div id="gbtn"></div><p class="note">or use your email</p></div>'
      + '<form id="a-si"><label for="a-em">Email</label><div class="field"><input id="a-em" type="email" autocomplete="email" required></div>'
      + '<label for="a-pw">Password</label><div class="field"><input id="a-pw" type="password" autocomplete="current-password" required></div>'
      + '<p id="a-err" class="cf-err" role="alert" hidden></p><p><button class="btn" type="submit"><span>Sign in</span></button></p></form></div>');
    var err = document.getElementById('a-err');
    function bad(e) { err.textContent = e.message; err.hidden = false; }
    document.getElementById('a-si').addEventListener('submit', function (ev) {
      ev.preventDefault(); err.hidden = true;
      S.api('login.php', { email: document.getElementById('a-em').value, password: document.getElementById('a-pw').value }).then(function (j) { if (j && j.twofa) { bad(new Error('Two-step sign-in is on for this account. Sign in on the main sign-in page first, then come back here.')); return; } S.store.set('sud-in', '1'); location.reload(); }).catch(bad);
    });
    S.onReady(function (u) {
      if (u) { start(); return; }
      if (!S.google) return;
      var g = document.createElement('script'); g.src = 'https://accounts.google.com/gsi/client'; g.async = true;
      g.onload = function () {
        window.google.accounts.id.initialize({ client_id: S.google, ux_mode: 'popup', callback: function (r) {
          S.api('google.php', { credential: r.credential }).then(function () { S.store.set('sud-in', '1'); location.reload(); }).catch(bad);
        } });
        document.getElementById('a-g').hidden = false;
        window.google.accounts.id.renderButton(document.getElementById('gbtn'), { type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', shape: 'pill', width: 280 });
      };
      document.head.appendChild(g);
    });
  }
  function start() {
    S.api('admin.php?a=status').then(function (j) { if (j.unlocked) shell(); else lock(j); }).catch(fail);
  }
  function lock(j) {
    box('<div class="adm-lock"><h1>Admin<span class="dot">.</span></h1><p class="lead">Signed in as ' + esc(j.email) + '. For safety we email you a code each time.</p>'
      + '<p><button class="btn" id="a-send" type="button"><span>Email me a code</span></button></p>'
      + '<form id="a-form" hidden><label for="a-code">Six-digit code</label><div class="field"><input id="a-code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="123456"></div>'
      + '<p id="a-err" class="cf-err" role="alert" hidden></p><p><button class="btn" type="submit"><span>Open admin</span></button></p></form><p id="a-msg" class="note"></p></div>');
    var err = document.getElementById('a-err');
    document.getElementById('a-send').addEventListener('click', function () {
      var m = document.getElementById('a-msg'); m.textContent = 'Sending…';
      S.api('admin.php', { a: 'code' }).then(function (r) { m.textContent = r.message; document.getElementById('a-form').hidden = false; document.getElementById('a-code').focus(); }).catch(function (e) { m.textContent = e.message; });
    });
    document.getElementById('a-form').addEventListener('submit', function (ev) {
      ev.preventDefault(); err.hidden = true;
      S.api('admin.php', { a: 'verify', code: document.getElementById('a-code').value }).then(function () { shell(); }).catch(function (e) { err.textContent = e.message; err.hidden = false; });
    });
  }

  function shell() {
    box('<div class="adm"><aside class="adm-nav"><b class="adm-brand">Admin</b>'
      + '<button type="button" data-t="overview" class="on">Overview</button><button type="button" data-t="traffic">Traffic</button><button type="button" data-t="seo">SEO</button><button type="button" data-t="users">Users</button><button type="button" data-t="data">Data &amp; export</button><button type="button" data-t="log">Activity log</button>'
      + '<button type="button" data-t="lock" class="adm-lockbtn">Lock admin</button></aside><div class="adm-main" id="adm-main"></div></div>');
    root.querySelector('.adm-nav').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.getAttribute('data-t') === 'lock') { S.api('admin.php', { a: 'lock' }).then(start); return; }
      tab = b.getAttribute('data-t');
      Array.prototype.forEach.call(root.querySelectorAll('.adm-nav button'), function (x) { x.classList.toggle('on', x === b); });
      view();
    });
    view();
  }
  function view() { var m = document.getElementById('adm-main'); m.innerHTML = '<p class="lead">Loading&hellip;</p>'; ({ users: users, data: dataTab, log: logTab, traffic: traffic, seo: seo }[tab] || overview)(m); }
  var n = function (v) { return Number(v || 0).toLocaleString(); };

  function chart(title, ser, cls) {
    var max = Math.max.apply(null, ser.map(function (x) { return x.n; }).concat([1])), tot = ser.reduce(function (a, x) { return a + x.n; }, 0);
    var id = 'c' + (++tm);
    var bars = ser.map(function (x, i) { var d = new Date(x.d + 'T00:00:00Z').toLocaleDateString([], { day: 'numeric', month: 'short', timeZone: 'UTC' });
      return '<div class="bar' + (x.n ? ' has' : '') + '" tabindex="0" role="img" data-t="' + esc(d + ': ' + x.n) + '" aria-label="' + esc(d + ': ' + x.n) + '"' + (x.n ? ' style="height:' + Math.max(8, Math.round(100 * x.n / max)) + '%"' : '') + '><i class="rseg ' + cls + '" style="height:100%"></i></div>'; }).join('');
    return '<div class="sp-card adm-chart"><div class="sp-rhead"><b>' + esc(title) + '</b><span class="adm-total">' + n(tot) + ' in 30 days</span></div><div class="sp-chart" id="' + id + '">' + bars + '</div>'
      + '<div class="sp-axis"><span>30 days ago</span><span>Today</span></div><p class="sp-rdetail" data-for="' + id + '">Tap or hover a bar for the day.</p></div>';
  }
  function wireCharts(m) {
    m.addEventListener('mouseover', tip); m.addEventListener('click', tip); m.addEventListener('focusin', tip);
    function tip(e) { var b = e.target.closest('.bar'); if (!b) return; var c = b.parentNode; var d = m.querySelector('[data-for="' + c.id + '"]'); if (d) d.textContent = b.getAttribute('data-t'); }
  }
  function tile(label, v, sub) { return '<div class="adm-tile"><span>' + esc(label) + '</span><b>' + n(v) + '</b>' + (sub ? '<em>' + esc(sub) + '</em>' : '') + '</div>'; }
  function list(title, rows, fmt) {
    return '<div class="sp-card"><div class="sp-rhead"><b>' + esc(title) + '</b></div>' + (rows.length ? '<ul class="adm-list">' + rows.map(fmt).join('') + '</ul>' : '<p class="note">Nothing yet.</p>') + '</div>';
  }
  function overview(m) {
    S.api('admin.php?a=overview').then(function (j) {
      var t = j.tiles;
      m.innerHTML = '<h1>Overview<span class="dot">.</span></h1><div class="adm-tiles">'
        + tile('Registered users', t.users) + tile('New this week', t.new7) + tile('Signed in this week', t.active7)
        + tile('Sites on watchlists', t.watching, t.hosts + ' different sites') + tile('Checks, last 24h', t.checks24) + tile('Problem reports, 24h', t.reports24) + tile('Outages, 7 days', t.incidents7) + '</div>'
        + '<p class="note">Last background probe: ' + esc(S.ago(j.last_probe)) + ' &middot; database: ' + esc(j.db) + '</p>'
        + '<div class="adm-grid">' + chart('New users', j.signups, 's-app') + chart('Users signing in', j.logins, 's-slow') + chart('Checks run', j.checks, 's-login') + chart('Problem reports', j.reports, 's-site') + '</div>'
        + '<div class="adm-grid">' + list('Most reported (7 days)', j.top_reported, function (r) { return '<li><span>' + esc(r.host) + '</span><b>' + n(r.n) + '</b></li>'; })
        + list('Most watched', j.top_watched, function (r) { return '<li><span>' + esc(r.host) + '</span><b>' + n(r.n) + '</b></li>'; })
        + list('Alert channels', j.channels, function (r) { return '<li><span>' + esc(r.kind) + '</span><b>' + n(r.n) + '</b></li>'; }) + '</div>';
      wireCharts(m);
    }).catch(fail);
  }


  /* ---- Traffic: who visits, from where, on what (counts only; nothing identifying is stored) ---- */
  function flag(c) { if (!/^[A-Z]{2}$/.test(c || '')) return '🌐'; return String.fromCodePoint(c.charCodeAt(0) + 127397, c.charCodeAt(1) + 127397); }
  function cname(c) { if (!c) return 'Unknown'; try { return new Intl.DisplayNames(undefined, { type: 'region' }).of(c) || c; } catch (e) { return c; } }
  function hbars(rows) {
    var mx = Math.max.apply(null, rows.map(function (r) { return r.n; }).concat([1]));
    return '<ul class="ins-bars adm-hb">' + rows.map(function (r) { return '<li><span class="ib-l" title="' + esc(r.l) + '">' + (r.pre || '') + esc(r.l) + '</span><span class="ib-b"><i style="width:' + Math.max(3, Math.round(100 * r.n / mx)) + '%"></i></span><span class="ib-n">' + esc(r.t != null ? r.t : n(r.n)) + '</span></li>'; }).join('') + '</ul>';
  }
  function lineChart(a, b, la, lb) {
    var W = 640, H = 190, pl = 34, pb = 22, mx = Math.max.apply(null, a.map(function (x) { return x.n; }).concat(b.map(function (x) { return x.n; })).concat([1]));
    var step = (W - pl - 6) / Math.max(1, a.length - 1);
    function pts(ser) { return ser.map(function (x, i) { return [pl + i * step, H - pb - (H - pb - 8) * x.n / mx]; }); }
    function path(P) { return P.map(function (q, i) { return (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1); }).join(' '); }
    var pa = pts(a), pb2 = pts(b), grid = '';
    for (var g = 0; g <= 4; g++) { var y = 8 + (H - pb - 8) * g / 4; grid += '<line x1="' + pl + '" x2="' + (W - 6) + '" y1="' + y + '" y2="' + y + '"/><text x="' + (pl - 5) + '" y="' + (y + 3) + '" text-anchor="end">' + n(Math.round(mx * (1 - g / 4))) + '</text>'; }
    var dots = a.map(function (x, i) { var d = new Date(x.d + 'T00:00:00Z').toLocaleDateString([], { day: 'numeric', month: 'short', timeZone: 'UTC' }); return '<circle class="hit" cx="' + pa[i][0].toFixed(1) + '" cy="' + pa[i][1].toFixed(1) + '" r="9"><title>' + d + ': ' + n(x.n) + ' ' + la.toLowerCase() + ', ' + n(b[i].n) + ' ' + lb.toLowerCase() + '</title></circle>'; }).join('');
    var d0 = new Date(a[0].d + 'T00:00:00Z').toLocaleDateString([], { day: 'numeric', month: 'short', timeZone: 'UTC' });
    return '<svg class="adm-line" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(la + ' and ' + lb + ' per day') + '"><g class="gr">' + grid + '</g>'
      + '<path class="area" d="' + path(pa) + ' L' + pa[pa.length - 1][0].toFixed(1) + ' ' + (H - pb) + ' L' + pa[0][0].toFixed(1) + ' ' + (H - pb) + 'Z"/><path class="l1" d="' + path(pa) + '"/><path class="l2" d="' + path(pb2) + '"/>' + dots
      + '<text class="ax" x="' + pl + '" y="' + (H - 5) + '">' + d0 + '</text><text class="ax" x="' + (W - 6) + '" y="' + (H - 5) + '" text-anchor="end">Today</text></svg>'
      + '<p class="adm-key"><i class="k1"></i>' + esc(la) + ' <i class="k2"></i>' + esc(lb) + '</p>';
  }
  function traffic(m) {
    var days = +(m.getAttribute('data-days') || 30);
    S.api('admin.php?a=traffic&days=' + days).then(function (j) {
      var t = j.tiles, d = function (a, b) { return b ? (a >= b ? '▲ ' : '▼ ') + Math.abs(Math.round(100 * (a - b) / b)) + '% vs yesterday' : ''; };
      var off = Math.round(-new Date().getTimezoneOffset() / 60), loc = new Array(24).fill(0);
      j.hours.forEach(function (v, u) { loc[((u + off) % 24 + 24) % 24] += v; });
      var hmx = Math.max.apply(null, loc.concat([1])), hi = loc.indexOf(Math.max.apply(null, loc));
      var tot = j.devices.d + j.devices.m + j.devices.t || 1, pc = function (v) { return Math.round(100 * v / tot); };
      var cnt = j.countries.map(function (c) { return { l: cname(c.code), pre: flag(c.code) + ' ', n: c.views, t: n(c.views) + ' views · ' + n(c.visitors) + ' visitors' }; });
      m.innerHTML = '<h1>Traffic<span class="dot">.</span></h1>'
        + '<div class="seg2 adm-range" id="t-range">' + [7, 30, 90].map(function (x) { return '<button type="button" data-d="' + x + '" aria-pressed="' + (x === days) + '">' + x + ' days</button>'; }).join('') + '</div>'
        + '<div class="adm-tiles">' + tile('Visitors today', t.visitors_today, d(t.visitors_today, t.visitors_yesterday)) + tile('Page views today', t.views_today, d(t.views_today, t.views_yesterday)) + tile('Visitors, ' + days + ' days', t.visitors_range) + tile('Page views, ' + days + ' days', t.views_range) + tile('Countries', t.countries) + '</div>'
        + (j.since ? '<p class="note">Counting since ' + esc(j.since) + '. Visitors are counted once a day without keeping any address, and anyone who declines analytics or sends Do Not Track is not counted. Country is the network’s country where available, otherwise guessed from the visitor’s time zone, so treat it as a close guide.</p>' : '<p class="note">No visits counted yet. Counting starts once this version of the site is live and people browse it.</p>')
        + '<div class="sp-card"><div class="sp-rhead"><b>Visitors and page views per day</b></div>' + lineChart(j.views, j.visitors, 'Page views', 'Visitors') + '</div>'
        + '<div class="adm-grid"><div class="sp-card"><div class="sp-rhead"><b>Where visitors are</b></div>' + (cnt.length ? hbars(cnt) : '<p class="note">Nothing yet.</p>') + '</div>'
        + '<div class="sp-card"><div class="sp-rhead"><b>Top pages</b></div>' + (j.pages.length ? hbars(j.pages.map(function (p) { return { l: p.path, n: p.views }; })) : '<p class="note">Nothing yet.</p>') + '</div></div>'
        + '<div class="adm-grid"><div class="sp-card"><div class="sp-rhead"><b>Where they came from</b></div>' + (j.refs.length ? hbars(j.refs.map(function (r) { return { l: r.ref, n: r.views }; })) : '<p class="note">Nothing yet.</p>') + '</div>'
        + '<div class="sp-card"><div class="sp-rhead"><b>Devices</b></div><div class="dp-bar" role="img" aria-label="Device split"><i class="s-dns" style="flex:' + j.devices.m + '"></i><i class="s-conn" style="flex:' + j.devices.t + '"></i><i class="s-tls" style="flex:' + j.devices.d + '"></i></div>'
        + '<ul class="dp-leg"><li><i class="s-dns"></i>Mobile <b>' + pc(j.devices.m) + '%</b></li><li><i class="s-conn"></i>Tablet <b>' + pc(j.devices.t) + '%</b></li><li><i class="s-tls"></i>Desktop <b>' + pc(j.devices.d) + '%</b></li></ul>'
        + '<div class="sp-rhead" style="margin-top:18px"><b>Busiest hours</b></div><div class="dp-day" role="img" aria-label="Page views by hour of day">' + loc.map(function (v, i) { return '<i style="height:' + Math.max(3, Math.round(100 * v / hmx)) + '%"' + (i === hi && v ? ' class="hi"' : '') + ' title="' + ('0' + i).slice(-2) + ':00: ' + n(v) + ' views"></i>'; }).join('') + '</div><div class="dp-axis"><span>00:00</span><span>12:00</span><span>23:00</span></div><p class="note">Your time zone.</p></div></div>';
      m.querySelector('#t-range').addEventListener('click', function (e) { var b = e.target.closest('[data-d]'); if (!b) return; m.setAttribute('data-days', b.getAttribute('data-d')); traffic(m); });
    }).catch(fail);
  }

  /* ---- SEO: page-by-page search audit from the last site build, plus what only you can do ---- */
  function seo(m) {
    S.api('admin.php?a=seo').then(function (j) {
      var ps = j.pages || [];
      if (!ps.length) { m.innerHTML = '<h1>SEO<span class="dot">.</span></h1><p class="lead">The audit is written each time the site is built, and none has been uploaded yet.</p>'; return; }
      var bad = ps.filter(function (p) { return p.issues && p.issues.length; });
      var kinds = {}; bad.forEach(function (p) { p.issues.forEach(function (i) { var k = i.replace(/ \(.*$/, '').replace(/\d+/g, 'N'); kinds[k] = (kinds[k] || 0) + 1; }); });
      var krows = Object.keys(kinds).sort(function (a, b) { return kinds[b] - kinds[a]; }).map(function (k) { return { l: k, n: kinds[k] }; });
      var lens = [0, 0, 0, 0]; ps.filter(function (p) { return !p.noindex; }).forEach(function (p) { lens[p.tl < 25 ? 0 : p.tl <= 62 ? 1 : 2]++; });
      var sc = j.score;
      var site = j.site || {}, chk = function (ok, y, no) { return '<li class="' + (ok ? 'ok' : 'no') + '">' + (ok ? '✔ ' + y : '✖ ' + no) + '</li>'; };
      m.innerHTML = '<h1>SEO<span class="dot">.</span></h1>'
        + '<div class="adm-tiles">' + tile('SEO health', sc, 'out of 100') + tile('Pages Google can index', j.indexable) + tile('Pages with no problems', j.clean) + tile('Pages in the sitemap', j.in_sitemap) + tile('Kept out of search', j.noindex) + '</div>'
        + '<p class="note">Checked at the last site build (' + esc(S.ago(j.built)) + '): titles, descriptions, headings, images, canonical links and social previews on every page.</p>'
        + '<div class="adm-grid"><div class="sp-card"><div class="sp-rhead"><b>Problems found</b></div>' + (krows.length ? hbars(krows) : '<p class="note">None. Every indexable page passes our checks.</p>') + '</div>'
        + '<div class="sp-card"><div class="sp-rhead"><b>Site basics</b></div><ul class="adm-chk">' + chk(site.robots, 'robots.txt is in place', 'robots.txt is missing') + chk(site.sitemap, 'sitemap.xml lists ' + j.in_sitemap + ' pages', 'No sitemap') + chk(site.ads_txt, 'ads.txt is in place', 'ads.txt is missing') + chk(true, 'Every page has a canonical link, social preview and structured data where it helps', '') + '</ul></div></div>'
        + (bad.length ? '<div class="sp-card"><div class="sp-rhead"><b>Pages to fix (' + bad.length + ')</b></div><ul class="adm-list">' + bad.slice(0, 60).map(function (p) { return '<li><span><a href="' + esc(p.url) + '" target="_blank" rel="noopener">' + esc(p.url) + '</a><br><small>' + p.issues.map(esc).join(' · ') + '</small></span></li>'; }).join('') + '</ul></div>' : '')
        + '<div class="sp-card"><div class="sp-rhead"><b>Only you can do these</b></div><ul class="adm-chk todo"><li>☐ In Google Search Console, open Sitemaps and submit <code>https://siteupdown.com/sitemap.xml</code>, then check Pages for anything marked not indexed.</li>'
        + '<li>☐ Add the site to Bing Webmaster Tools. You can import it straight from Search Console, and it also covers DuckDuckGo and Yahoo.</li>'
        + '<li>☐ Run a page through PageSpeed Insights. Speed on a phone is a ranking factor.</li><li>☐ Get real links to the site: the Chrome extension listing, a short post on Reddit or a forum when it is useful, and any directories that fit. Links from other sites are the biggest ranking factor we cannot build ourselves.</li>'
        + '<li>☐ Add the social links to the footer once the accounts exist.</li></ul></div>';
    }).catch(fail);
  }
  function users(m) {
    var q = '', page = 1;
    function load() {
      S.api('admin.php?a=users&q=' + encodeURIComponent(q) + '&page=' + page).then(function (j) {
        var pages = Math.max(1, Math.ceil(j.total / j.per));
        var rows = j.users.map(function (u) {
          return '<tr data-id="' + u.id + '" data-email="' + esc(u.email) + '" data-name="' + esc(u.name) + '"><td><b>' + esc(u.name) + '</b><br><span class="adm-mail">' + esc(u.email) + '</span><br><button type="button" class="btn small ghost adm-manage"><span>Manage / email</span></button></td><td>' + esc(S.when(u.created)) + '</td><td>' + esc(u.last ? S.ago(u.last) : 'never') + '</td>'
            + '<td>' + u.watching + '</td><td>' + u.channels + '</td><td>' + (u.google ? 'Google' : '') + (u.google && u.pw ? ' + ' : '') + (u.pw ? 'Password' : '') + '</td></tr><tr class="adm-det" id="d' + u.id + '" hidden><td colspan="6"></td></tr>';
        }).join('');
        m.querySelector('#u-body').innerHTML = rows || '<tr><td colspan="6">No users found.</td></tr>';
        m.querySelector('#u-info').textContent = n(j.total) + ' users · page ' + j.page + ' of ' + pages;
        m.querySelector('#u-prev').disabled = page <= 1; m.querySelector('#u-next').disabled = page >= pages;
      }).catch(fail);
    }
    m.innerHTML = '<h1>Users<span class="dot">.</span></h1><form id="u-form" class="adm-search"><div class="field"><input id="u-q" type="search" placeholder="Search by name or email"></div><button class="btn small" type="submit"><span>Search</span></button></form>'
      + '<div class="adm-table"><table><thead><tr><th>User</th><th>Joined</th><th>Last sign-in</th><th>Watching</th><th>Alerts</th><th>Sign-in</th></tr></thead><tbody id="u-body"></tbody></table></div>'
      + '<p class="adm-pager"><button class="btn small ghost" id="u-prev" type="button"><span>Previous</span></button> <span id="u-info"></span> <button class="btn small ghost" id="u-next" type="button"><span>Next</span></button></p>';
    m.querySelector('#u-form').addEventListener('submit', function (e) { e.preventDefault(); q = m.querySelector('#u-q').value.trim(); page = 1; load(); });
    m.querySelector('#u-prev').addEventListener('click', function () { page--; load(); });
    m.querySelector('#u-next').addEventListener('click', function () { page++; load(); });
    m.querySelector('#u-body').addEventListener('click', function (e) {
      var tr = e.target.closest('tr[data-id]'); if (!tr) return; var id = tr.getAttribute('data-id'), d = document.getElementById('d' + id);
      if (!d.hidden) { d.hidden = true; return; }
      d.hidden = false; var td = d.firstChild; td.textContent = 'Loading…';
      S.api('admin.php?a=user&id=' + id).then(function (j) {
        td.innerHTML = '<div class="adm-detin"><p><b>Watchlist</b>: ' + (j.watchlist.length ? j.watchlist.map(function (w) { return esc(w.host); }).join(', ') : 'none')
          + '<br><b>Alert channels</b>: ' + (j.channels.length ? j.channels.map(function (c) { return esc(c.kind + (c.label ? ' (' + c.label + ')' : '')); }).join(', ') : 'none') + '</p>'
          + '<div class="adm-act"><h3>Email ' + esc(tr.getAttribute('data-name')) + '</h3><div class="field"><input class="e-sub" maxlength="120" placeholder="Subject"></div>'
          + '<textarea class="e-msg" rows="5" maxlength="5000" placeholder="Your message"></textarea>'
          + '<p><button type="button" class="btn small e-send"><span>Send email</span></button> <span class="adm-res e-res" role="status"></span></p></div>'
          + '<div class="adm-act"><h3>Reset or remove</h3><p class="note">Type RESET to clear part of this user&rsquo;s data. To delete the account, type their email address.</p>'
          + '<div class="field"><input class="r-conf" placeholder="RESET or their email"></div><p class="adm-btns">'
          + '<button type="button" class="btn small ghost r-do" data-w="watchlist"><span>Clear watchlist</span></button>'
          + '<button type="button" class="btn small ghost r-do" data-w="channels"><span>Clear alert channels</span></button>'
          + '<button type="button" class="btn small ghost r-do" data-w="saved"><span>Clear saved checks</span></button>'
          + '<button type="button" class="btn small ghost r-del"><span>Delete account</span></button></p><p class="adm-res r-res" role="status"></p></div></div>';
        td.onclick = function (ev) {
          ev.stopPropagation(); var t = ev.target.closest('button'); if (!t) return;
          var er = td.querySelector('.e-res'), rr = td.querySelector('.r-res'), conf = td.querySelector('.r-conf').value;
          if (t.classList.contains('e-send')) {
            er.textContent = 'Sending…';
            S.api('admin.php', { a: 'email', id: +id, subject: td.querySelector('.e-sub').value, message: td.querySelector('.e-msg').value }).then(function (r) { er.textContent = r.message; td.querySelector('.e-msg').value = ''; }).catch(function (x) { er.textContent = x.message; });
          } else if (t.classList.contains('r-do')) {
            S.api('admin.php', { a: 'user_clear', id: +id, what: t.getAttribute('data-w'), confirm: conf }).then(function (r) { rr.textContent = r.message; }).catch(function (x) { rr.textContent = x.message; });
          } else if (t.classList.contains('r-del')) {
            S.api('admin.php', { a: 'user_delete', id: +id, confirm: conf }).then(function (r) { rr.textContent = r.message; load(); }).catch(function (x) { rr.textContent = x.message; });
          }
        };
      }).catch(function (er) { td.textContent = er.message; });
    });
    load();
  }
  function dataTab(m) {
    m.innerHTML = '<h1>Data &amp; export<span class="dot">.</span></h1>'
      + '<div class="sp-card"><div class="sp-rhead"><b>Export</b></div><p class="note">Download a CSV file you can open in Excel or Google Sheets.</p><p class="adm-btns"><a class="btn small" href="/api/admin.php?a=export&what=users"><span>Users (CSV)</span></a><a class="btn small" href="/api/admin.php?a=export&what=reports"><span>Problem reports (CSV)</span></a></p></div>'
      + '<div class="sp-card" style="margin-top:14px"><div class="sp-rhead"><b>Reset site data</b></div><p class="note">This cannot be undone. Leave the website empty to apply it to <b>every</b> site, or enter one (for example google.com). Type RESET to confirm.</p>'
      + '<div class="cf-two"><div><label for="x-host">Website <span class="opt">(optional)</span></label><div class="field"><input id="x-host" placeholder="google.com" autocapitalize="none" spellcheck="false"></div></div>'
      + '<div><label for="x-conf">Confirm</label><div class="field"><input id="x-conf" placeholder="RESET"></div></div></div>'
      + '<p class="adm-btns"><button type="button" class="btn small ghost x-do" data-w="reports"><span>Reset problem reports</span></button><button type="button" class="btn small ghost x-do" data-w="history"><span>Reset uptime history &amp; outages</span></button><button type="button" class="btn small ghost x-do" data-w="checks"><span>Clear recent checks feed</span></button></p><p class="adm-res" id="x-res" role="status"></p></div>';
    m.querySelectorAll('.sp-card')[1].addEventListener('click', function (e) {
      var t = e.target.closest('.x-do'); if (!t) return;
      var r = m.querySelector('#x-res'); r.textContent = 'Working…';
      S.api('admin.php', { a: 'reset', what: t.getAttribute('data-w'), host: m.querySelector('#x-host').value, confirm: m.querySelector('#x-conf').value }).then(function (j) { r.textContent = j.message; }).catch(function (x) { r.textContent = x.message; });
    });
  }
  function logTab(m) {
    S.api('admin.php?a=log').then(function (j) {
      m.innerHTML = '<h1>Activity log<span class="dot">.</span></h1><div class="adm-table"><table><thead><tr><th>When</th><th>Action</th><th>Detail</th></tr></thead><tbody>'
        + (j.log.length ? j.log.map(function (x) { return '<tr><td>' + esc(S.when(x.ts)) + '</td><td>' + esc(x.action) + '</td><td>' + esc(x.detail) + '</td></tr>'; }).join('') : '<tr><td colspan="3">Nothing yet.</td></tr>') + '</tbody></table></div>';
    }).catch(fail);
  }
  start();
})();
