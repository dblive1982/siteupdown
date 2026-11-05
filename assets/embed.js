// The live status card that people put on their own pages (iframe from /widget/<host>).
(function () {
  'use strict';
  var host = document.body.getAttribute('data-host'), $ = function (i) { return document.getElementById(i); };
  var vid = ''; for (var i = 0; i < 24; i++) vid += Math.floor(Math.random() * 16).toString(16);
  var data = null, samples = [], stop = Date.now() + 20 * 60 * 1000, timer = null;
  function ago(t) { var s = Math.max(0, Math.round(Date.now() / 1000 - t)); return s < 5 ? 'just now' : s < 90 ? s + ' s ago' : Math.round(s / 60) + ' min ago'; }
  function state() {
    var last = samples.length ? samples[samples.length - 1] : null, v = data ? data.v : 'unknown';
    if (last && Date.now() / 1000 - last.t < 60) v = last.v;
    return v;
  }
  function draw() {
    var v = state(), p = $('p'), cls = v === 'up' ? 'up' : v === 'down' ? 'down' : v === 'unknown' ? '' : 'maybe';
    p.className = 'p ' + cls; $('pt').textContent = v === 'up' ? 'Up' : v === 'down' ? 'Down' : v === 'unknown' ? 'Checking' : 'Not sure';
    var last = samples.length ? samples[samples.length - 1] : null, ms = last && last.ms != null ? last.ms : (data ? data.ms : null);
    $('u').textContent = data && data.up24 != null ? data.up24 + '%' : '–';
    $('m').textContent = ms != null ? ms + ' ms' + (data && data.avg24 ? ' (avg ' + data.avg24 + ')' : '') : '–';
    var t = last ? last.t : (data && data.at ? Date.parse(data.at) / 1000 : 0);
    $('ra').textContent = t ? 'Checked ' + ago(t) : 'siteupdown.com';
    var g = $('g'), pts = samples.filter(function (s) { return s.ms != null; }), W = 200, H = 30;
    if (pts.length < 2) { g.innerHTML = ''; return; }
    var mx = 0, mn = 1e9; pts.forEach(function (s) { if (s.ms > mx) mx = s.ms; if (s.ms < mn) mn = s.ms; });
    var span = Math.max(mx - mn, 20), d = '';
    pts.forEach(function (s, k) { d += (k ? 'L' : 'M') + (k * W / (pts.length - 1)).toFixed(1) + ' ' + (H - 3 - (s.ms - mn) / span * (H - 8)).toFixed(1); });
    g.innerHTML = '<path d="' + d + '" fill="none" stroke="#2e9d46" stroke-width="1.6" vector-effect="non-scaling-stroke"/><line id="cur" y1="0" y2="' + H + '" stroke="#5b5870" stroke-width="1" vector-effect="non-scaling-stroke" opacity="0"/>';
    g._pts = pts;
  }
  var g = $('g');
  function hover(ev) {
    var pts = g._pts; if (!pts || pts.length < 2) return;
    var r = g.getBoundingClientRect(), x = (ev.touches ? ev.touches[0].clientX : ev.clientX) - r.left;
    var k = Math.max(0, Math.min(pts.length - 1, Math.round(x / r.width * (pts.length - 1)))), s = pts[k], c = $('cur');
    if (c) { var cx = k * 200 / (pts.length - 1); c.setAttribute('x1', cx); c.setAttribute('x2', cx); c.setAttribute('opacity', '1'); }
    $('rd').textContent = s.ms + ' ms · ' + ago(s.t); ev.preventDefault();
  }
  function leave() { var c = $('cur'); if (c) c.setAttribute('opacity', '0'); $('rd').textContent = 'Live, updates every few seconds'; }
  g.addEventListener('mousemove', hover); g.addEventListener('touchmove', hover, { passive: false }); g.addEventListener('mouseleave', leave); g.addEventListener('touchend', leave);
  function get(u, cb) { var x = new XMLHttpRequest(); x.open('GET', u); x.onload = function () { try { cb(JSON.parse(x.responseText)); } catch (e) {} }; x.send(); }
  function loadData() { get('/api/widget.php?host=' + encodeURIComponent(host) + '&data=1', function (j) { data = j; draw(); }); }
  function loadLive() { get('/api/live.php?host=' + encodeURIComponent(host) + '&take=1&vid=' + vid, function (j) { if (j && j.samples) { samples = j.samples.slice(-40); draw(); } }); }
  var n = 0;
  function tick() {
    if (document.hidden) return;
    if (Date.now() > stop) { clearInterval(timer); $('rd').textContent = 'Paused to save bandwidth – reload to resume'; return; }
    loadLive(); if (++n % 4 === 0) loadData();
  }
  loadData(); loadLive(); timer = setInterval(tick, 15000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) tick(); });
})();
