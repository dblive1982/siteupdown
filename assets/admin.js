/* Admin area: email-code unlock, overview with charts, user list. Everything is checked again on the server. */
(function () {
  'use strict';
  var S = window.SUD, esc = S.esc, root = document.getElementById('adm-root');
  if (!root) return;
  var tab = 'overview', tm = 0;

  function box(html) { root.innerHTML = html; }
  function notFound() { box('<div class="center"><span class="eyebrow"><i></i>Error 404</span><h1 style="margin:14px 0">Not found<span class="dot">.</span></h1><p class="lead">We checked everywhere. This page is down for everyone.</p></div>'); }
  function fail(e) { if (e.status === 401) location.replace('/login?next=' + encodeURIComponent('/admin')); else if (e.status === 404) notFound(); else if (e.status === 403) start(); else box('<p class="cf-err">' + esc(e.message) + '</p>'); }

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
      + '<button type="button" data-t="overview" class="on">Overview</button><button type="button" data-t="users">Users</button>'
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
  function view() { var m = document.getElementById('adm-main'); m.innerHTML = '<p class="lead">Loading&hellip;</p>'; (tab === 'users' ? users : overview)(m); }
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

  function users(m) {
    var q = '', page = 1;
    function load() {
      S.api('admin.php?a=users&q=' + encodeURIComponent(q) + '&page=' + page).then(function (j) {
        var pages = Math.max(1, Math.ceil(j.total / j.per));
        var rows = j.users.map(function (u) {
          return '<tr data-id="' + u.id + '"><td><b>' + esc(u.name) + '</b><br><span class="adm-mail">' + esc(u.email) + '</span></td><td>' + esc(S.when(u.created)) + '</td><td>' + esc(u.last ? S.ago(u.last) : 'never') + '</td>'
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
      var tr = e.target.closest('tr[data-id]'); if (!tr) return; var d = document.getElementById('d' + tr.getAttribute('data-id'));
      if (!d.hidden) { d.hidden = true; return; }
      d.hidden = false; var td = d.firstChild; td.textContent = 'Loading…';
      S.api('admin.php?a=user&id=' + tr.getAttribute('data-id')).then(function (j) {
        td.innerHTML = '<b>Watchlist</b>: ' + (j.watchlist.length ? j.watchlist.map(function (w) { return esc(w.host); }).join(', ') : 'none')
          + '<br><b>Alert channels</b>: ' + (j.channels.length ? j.channels.map(function (c) { return esc(c.kind + (c.label ? ' (' + c.label + ')' : '')); }).join(', ') : 'none');
      }).catch(function (er) { td.textContent = er.message; });
    });
    load();
  }
  start();
})();
