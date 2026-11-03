/* Live response-time graph on the "Is X down?" pages: samples every few seconds while the page is open, plus 24h / 7d / 30d history. */
(function () {
  'use strict';
  var root = document.querySelector('[data-sp="site"]'); if (!root) return;
  var host = root.getAttribute('data-host');
  var card = document.getElementById('sp-live'), svg = document.getElementById('lv-svg'), strip = document.getElementById('lv-strip');
  var $ = function (i) { return document.getElementById(i); };
  var mode = 'live', samples = [], every = 5, timer = 0, started = Date.now(), data = null, stopped = false, W = 600, H = 170, PAD = 14;
  var COL = { up: '#39b54a', down: '#ff5a5f', slow: '#f5b83d', none: '#6b7c73' };

  function cls(v) { return v === 'up' ? 'up' : (v === 'down' ? 'down' : (v === 'none' ? 'none' : 'slow')); }
  function clock(t) { return new Date(t * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
  function draw(pts, unit) {      // pts: [{ms, c ('up'|'slow'|'down'|'none'), label}]
    data = pts;
    var vals = pts.map(function (p) { return p.ms; }).filter(function (x) { return x != null; });
    var max = Math.max.apply(null, vals.concat([100])) * 1.15, n = pts.length, h = H - PAD * 2;
    var x = function (i) { return n < 2 ? W / 2 : PAD + (W - PAD * 2) * i / (n - 1); }, y = function (v) { return H - PAD - h * v / max; };
    var out = '';
    [0.25, 0.5, 0.75].forEach(function (g) { out += '<line x1="0" x2="' + W + '" y1="' + (H - PAD - h * g).toFixed(1) + '" y2="' + (H - PAD - h * g).toFixed(1) + '" stroke="currentColor" stroke-opacity=".12" stroke-dasharray="3 5" vector-effect="non-scaling-stroke"/>'; });
    var seg = [], line = '';
    pts.forEach(function (p, i) { if (p.ms != null) seg.push(x(i).toFixed(1) + ',' + y(p.ms).toFixed(1)); else if (seg.length) { line += '<polyline points="' + seg.join(' ') + '" fill="none" stroke="#39b54a" stroke-width="2.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'; seg = []; } });
    if (seg.length) {
      var area = 'M' + seg[0] + ' L' + seg.join(' L') + ' L' + seg[seg.length - 1].split(',')[0] + ',' + (H - PAD) + ' L' + seg[0].split(',')[0] + ',' + (H - PAD) + ' Z';
      out += '<defs><linearGradient id="lvg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#39b54a" stop-opacity=".35"/><stop offset="1" stop-color="#39b54a" stop-opacity="0"/></linearGradient></defs><path d="' + area + '" fill="url(#lvg)"/>';
      line += '<polyline points="' + seg.join(' ') + '" fill="none" stroke="#39b54a" stroke-width="2.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>';
    }
    out += line;
    svg.innerHTML = out;
    // markers drawn as HTML-free circles would stretch with preserveAspectRatio none, so the status strip carries the colours instead
    strip.innerHTML = pts.map(function (p) { return '<i class="' + p.c + '"></i>'; }).join('');
    var top = Math.round(max / 1.15); $('lv-a1').dataset.top = top;
  }
  function setNow(p, sub) { $('lv-ms').textContent = p && p.ms != null ? p.ms + ' ms' : '—'; $('lv-sub').textContent = sub; }
  function pill(v) {
    var el = $('lv-pill'), c = cls(v);
    el.className = 'sp-pill ' + (c === 'none' ? 'unsure' : c);
    el.textContent = mode === 'live' ? (c === 'up' ? 'Live · up' : c === 'down' ? 'Live · down' : 'Live · slow') : (c === 'up' ? 'Up' : c === 'down' ? 'Down' : 'Mixed');
  }

  /* ---- live mode ---- */
  function renderLive() {
    var win = samples.slice(-60);
    if (!win.length) return;
    draw(win.map(function (s) { return { ms: s.ms, c: s.v === 'up' ? 'up' : (s.v === 'down' ? 'down' : 'slow'), label: clock(s.t) + ': ' + (s.ms != null ? s.ms + ' ms' : 'no answer') + (s.c ? ' (HTTP ' + s.c + ')' : '') }; }), 'sample');
    var last = win[win.length - 1], vals = win.map(function (s) { return s.ms; }).filter(function (x) { return x != null; });
    var avg = vals.length ? Math.round(vals.reduce(function (a, b) { return a + b; }, 0) / vals.length) : null;
    setNow(last, 'Updated ' + clock(last.t) + (avg != null ? ' · average ' + avg + ' ms · fastest ' + Math.min.apply(null, vals) + ' · slowest ' + Math.max.apply(null, vals) : ''));
    pill(last.v);
    $('lv-a1').textContent = Math.max(1, Math.round((win[win.length - 1].t - win[0].t) / 60)) + ' min ago'; $('lv-a2').textContent = 'Now';
  }
  function poll() {
    clearTimeout(timer);
    if (mode !== 'live') return;
    if (document.hidden) { timer = setTimeout(poll, 2000); return; }
    if (Date.now() - started > 15 * 60 * 1000) { stopped = true; $('lv-sub').textContent = 'Paused to save resources. Tap Live to resume.'; return; }
    fetch('/api/live.php?host=' + encodeURIComponent(host), { credentials: 'same-origin' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j) { card.hidden = true; return; }
      card.hidden = false; every = j.every || 5; samples = j.samples || [];
      if (mode === 'live') renderLive();
      var age = samples.length ? j.now - samples[samples.length - 1].t : every;
      timer = setTimeout(poll, Math.max(1000, (every - age) * 1000 + 300));
    }).catch(function () { timer = setTimeout(poll, 8000); });
  }

  /* ---- history ---- */
  function history(range) {
    fetch('/api/uptime.php?host=' + encodeURIComponent(host) + '&range=' + range).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j || mode !== range) { if (!j) { $('lv-sub').textContent = 'No history for this site yet.'; svg.innerHTML = ''; strip.innerHTML = ''; } return; }
      var pts = j.series.map(function (s) {
        var d = new Date(s.t), lab = d.toLocaleString([], range === '24h' ? { weekday: 'short', hour: '2-digit', minute: '2-digit' } : { weekday: 'short', day: 'numeric', month: 'short' });
        return { ms: s.ms, c: s.state === 'up' ? 'up' : (s.state === 'down' ? 'down' : (s.state === 'partial' ? 'slow' : 'none')), label: lab + ': ' + (s.state === 'none' ? 'no data' : (s.ms != null ? s.ms + ' ms' : s.state)) };
      });
      draw(pts, 'bucket');
      var u = j.uptime[range];
      setNow({ ms: j.avg_ms }, 'average' + (j.min_ms != null ? ' · fastest ' + j.min_ms + ' ms · slowest ' + j.max_ms + ' ms' : '') + (u != null ? ' · uptime ' + u + '%' : ''));
      pill(j.current.verdict === 'up' ? 'up' : (j.current.verdict === 'down' ? 'down' : 'slow'));
      $('lv-a1').textContent = { '24h': '24 hours ago', '7d': '7 days ago', '30d': '30 days ago' }[range]; $('lv-a2').textContent = 'Now';
    }).catch(function () {});
  }

  /* ---- tabs and tooltip ---- */
  $('lv-ranges').addEventListener('click', function (e) {
    var b = e.target.closest('[data-range]'); if (!b) return; var r = b.getAttribute('data-range');
    if (r === mode && !stopped) return;
    Array.prototype.forEach.call(this.querySelectorAll('[data-range]'), function (x) { var on = x === b; x.classList.toggle('on', on); x.setAttribute('aria-pressed', on); });
    mode = r; clearTimeout(timer);
    if (r === 'live') { stopped = false; started = Date.now(); renderLive(); poll(); } else history(r);
  });
  function tipAt(e) {
    if (!data || !data.length) return;
    var wrap = $('lv-svg').getBoundingClientRect(), cx = (e.touches ? e.touches[0].clientX : e.clientX), f = Math.min(1, Math.max(0, (cx - wrap.left) / wrap.width));
    var i = Math.round(f * (data.length - 1)), p = data[i]; if (!p) return;
    $('lv-detail').textContent = p.label;
  }
  var wrap = document.querySelector('.lv-wrap'); wrap.addEventListener('mousemove', tipAt); wrap.addEventListener('click', tipAt); wrap.addEventListener('touchmove', tipAt, { passive: true });
  document.addEventListener('visibilitychange', function () { if (!document.hidden && mode === 'live' && !stopped) poll(); });
  poll();
})();
