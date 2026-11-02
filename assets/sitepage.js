/* "Is X down?" pages: live status, visitor problem reports and the site directory. */
(function () {
  'use strict';
  var root = document.querySelector('[data-sp]');
  if (!root) return;
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
  var rep = { level: 'none' }, cur = null;

  function headline() {
    var pill = $('#sp-pill'), msg = $('#sp-msg');
    var busy = rep.level === 'high' || rep.level === 'raised';
    if (!cur) { pill.className = 'sp-pill unsure'; pill.textContent = 'No data yet'; msg.textContent = 'We have not run a scheduled check of ' + host + ' yet. Use the button below to test it now.'; return; }
    var v = cur.verdict;
    if (v === 'up') {
      pill.className = 'sp-pill up'; pill.textContent = 'Up';
      msg.textContent = busy ? 'We can reach ' + host + ', but many visitors are reporting problems. It may affect the app, logging in or certain regions.'
        : name + ' is up. Our server reached ' + host + ' ' + ago(cur.at) + (cur.ms ? ' in ' + cur.ms + ' ms' : '') + '.';
    } else if (v === 'down') {
      pill.className = 'sp-pill down'; pill.textContent = 'Down';
      msg.textContent = name + ' looks down. Our server got errors on two attempts ' + ago(cur.at) + '.';
    } else if (v === 'timeout') {
      pill.className = 'sp-pill slow'; pill.textContent = 'Slow or timing out';
      msg.textContent = 'Our server could not get a timely answer from ' + host + ' ' + ago(cur.at) + '. That can mean it is overloaded or down.';
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

  var kindName = { site: 'website not loading', login: 'cannot log in', app: 'app not working', slow: 'very slow' };
  function renderReports() {
    var hours = rep.hours || new Array(24).fill(0), max = Math.max.apply(null, hours.concat([3]));
    $('#sp-chart').innerHTML = hours.map(function (n, i) {
      var t = new Date(new Date(rep.start).getTime() + i * 3600000);
      var lab = n + (n === 1 ? ' report' : ' reports') + ' around ' + t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      return '<span class="bar' + (n ? ' has' : '') + '" style="height:' + Math.max(4, Math.round(100 * n / max)) + '%" title="' + esc(lab) + '"></span>';
    }).join('');
    var total = rep.total || 0;
    $('#sp-rtotal').textContent = total ? total + (total === 1 ? ' problem report' : ' problem reports') + ' in the last 24 hours' : 'No problem reports in the last 24 hours';
    var L = $('#sp-rlevel');
    L.className = 'sp-level ' + rep.level;
    L.textContent = rep.level === 'high' ? 'Many more than usual' : rep.level === 'raised' ? 'More than usual' : rep.level === 'low' ? 'Normal levels' : '';
    var k = rep.kinds || {}, parts = [];
    Object.keys(kindName).forEach(function (key) { if (k[key]) parts.push('<span>' + k[key] + ' ' + kindName[key] + '</span>'); });
    $('#sp-kinds').innerHTML = parts.join('');
    headline();
  }
  function loadReports() {
    getJSON('/api/reports.php?host=' + encodeURIComponent(host)).then(function (r) { if (r.ok) { rep = r.j; renderReports(); } }).catch(function () {});
  }
  loadReports();

  var btn = $('#sp-rbtn'), pick = $('#sp-rpick'), rmsg = $('#sp-rmsg');
  var key = 'sud-rep-' + host, last = 0;
  try { last = parseInt(localStorage.getItem(key) || '0', 10) || 0; } catch (e) {}
  btn.addEventListener('click', function () { pick.hidden = !pick.hidden; });
  pick.addEventListener('click', function (e) {
    var b = e.target.closest('.rk'); if (!b) return;
    rmsg.textContent = 'Sending…';
    fetch('/api/report.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ host: host, kind: b.getAttribute('data-kind') }), credentials: 'same-origin' })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        rmsg.textContent = r.ok ? r.j.message : (r.j.error || 'Sorry, that did not work. Please try again later.');
        if (r.ok) { pick.hidden = true; try { localStorage.setItem(key, String(Date.now())); } catch (e) {} loadReports(); }
      }).catch(function () { rmsg.textContent = 'Sorry, that did not work. Please try again later.'; });
  });
})();
