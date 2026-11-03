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
  var rep = { level: 'none' }, cur = null, isApp = root.getAttribute('data-app') === '1';

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
        : name + ' is up. Our server reached ' + host + ' ' + ago(cur.at) + (cur.ms ? ' in ' + cur.ms + ' ms' : '') + '.' + (isApp ? ' This shows the servers are reachable. Problems inside the app can still happen, so check the reports below.' : '');
    } else if (v === 'down') {
      pill.className = 'sp-pill down'; pill.textContent = 'Down';
      msg.textContent = name + ' looks down. Our server got errors on two attempts ' + ago(cur.at) + '.';
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

  var btn = $('#sp-rbtn'), pick = $('#sp-rpick'), rmsg = $('#sp-rmsg');
  var key = 'sud-rep-' + host, last = 0;
  try { last = parseInt(localStorage.getItem(key) || '0', 10) || 0; } catch (e) {}
  btn.addEventListener('click', function () { pick.hidden = !pick.hidden; });
  var picker = S.repPicker(pick, function (kinds) {
    rmsg.textContent = 'Sending…';
    fetch('/api/report.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ host: host, kinds: kinds, tz: S.tz() }), credentials: 'same-origin' })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        rmsg.textContent = r.ok ? r.j.message : (r.j.error || 'Sorry, that did not work. Please try again later.');
        if (r.ok) { pick.hidden = true; picker.reset(); try { localStorage.setItem(key, String(Date.now())); } catch (e) {} loadReports(); }
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
