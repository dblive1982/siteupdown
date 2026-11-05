/* Live response-time graph plus 24h / 7d / 12-month history and a written 7-day outage summary.
   Used on the "Is X down?" pages and under any site checked on the home page: SUD_LIVE.mount(element, host). */
(function () {
  'use strict';
  var W = 600, H = 170, PAD = 14, uid = 0, current = null;
  function vid() { try { var v = localStorage.getItem('sud-vid'); if (!v) { v = ''; for (var i = 0; i < 24; i++) v += Math.floor(Math.random() * 16).toString(16); localStorage.setItem('sud-vid', v); } return v; } catch (e) { return ''; } }
  function dur(sec) {
    sec = Math.max(0, Math.round(sec)); if (sec < 90) return sec + ' sec';
    var m = Math.round(sec / 60); if (m < 90) return m + ' min';
    var h = Math.floor(m / 60), r = m % 60; if (h < 48) return h + ' h' + (r ? ' ' + r + ' min' : '');
    return Math.floor(h / 24) + ' days ' + (h % 24) + ' h';
  }
  function plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  function when(iso) { return new Date(iso).toLocaleString([], { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); }
  function clock(t) { return new Date(t * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
  function cls(v) { return v === 'up' ? 'up' : (v === 'down' ? 'down' : (v === 'none' ? 'none' : 'slow')); }

  var HTML = '<div class="sp-card live-card"><div class="sp-rhead"><b>Response time</b><span class="sp-pill up" data-lv="pill">&hellip;</span></div>' +
    '<div class="sp-ranges" data-lv="ranges" role="group" aria-label="Graph range"><button type="button" class="rg" data-range="live" aria-pressed="false">Live</button><button type="button" class="rg on" data-range="24h" aria-pressed="true">24 hours</button><button type="button" class="rg" data-range="7d" aria-pressed="false">7 days</button><button type="button" class="rg" data-range="1y" aria-pressed="false">12 months</button></div>' +
    '<div class="lv-now"><b data-lv="ms">&mdash;</b><span data-lv="sub">Waiting for the first sample&hellip;</span></div>' +
    '<div class="lv-wrap"><svg data-lv="svg" viewBox="0 0 600 170" preserveAspectRatio="none" role="img" aria-label="Response time graph"></svg></div>' +
    '<div class="lv-strip" data-lv="strip" aria-hidden="true"></div>' +
    '<div class="sp-axis"><span data-lv="a1">24 hours ago</span><span data-lv="a2">Now</span></div>' +
    '<p class="sp-rdetail" data-lv="detail">Tap or hover the graph for a time.</p></div>' +
    '<div class="sp-card" data-lv="outcard"><div class="sp-rhead"><b>Outages in the last 7 days</b><span class="sp-level" data-lv="osum"></span></div><div data-lv="obody"><p class="so-clear">Checking the record&hellip;</p></div>' +
    '<p class="note" data-lv="oyear"></p><p class="note">Times are shown in your own time zone. A site counts as down after two failed checks in a row, so start times can be a few minutes late and lengths are approximate.</p></div>';

  function mount(box, host) {
    if (current) current.destroy();
    box.innerHTML = HTML; box.hidden = false;
    var q = function (n) { return box.querySelector('[data-lv="' + n + '"]'); };
    var svg = q('svg'), strip = q('strip');
    var mode = '24h', samples = [], every = 10, timer = 0, started = Date.now(), data = null, stopped = false, dead = false, first = true, take = true, gid = 'lvg' + (++uid);

    function draw(pts) {
      data = pts;
      var vals = pts.map(function (p) { return p.ms; }).filter(function (x) { return x != null; });
      var max = Math.max.apply(null, vals.concat([100])) * 1.15, n = pts.length, h = H - PAD * 2;
      var x = function (i) { return n < 2 ? W / 2 : PAD + (W - PAD * 2) * i / (n - 1); }, y = function (v) { return H - PAD - h * v / max; };
      var out = '';
      [0.25, 0.5, 0.75].forEach(function (g) { var yy = (H - PAD - h * g).toFixed(1); out += '<line x1="0" x2="' + W + '" y1="' + yy + '" y2="' + yy + '" stroke="currentColor" stroke-opacity=".12" stroke-dasharray="3 5" vector-effect="non-scaling-stroke"/>'; });
      var seg = [];
      pts.forEach(function (p, i) { if (p.ms != null) seg.push(x(i).toFixed(1) + ',' + y(p.ms).toFixed(1)); });
      if (seg.length) {
        var area = 'M' + seg[0] + ' L' + seg.join(' L') + ' L' + seg[seg.length - 1].split(',')[0] + ',' + (H - PAD) + ' L' + seg[0].split(',')[0] + ',' + (H - PAD) + ' Z';
        out += '<defs><linearGradient id="' + gid + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#39b54a" stop-opacity=".35"/><stop offset="1" stop-color="#39b54a" stop-opacity="0"/></linearGradient></defs><path d="' + area + '" fill="url(#' + gid + ')"/>';
        out += '<polyline points="' + seg.join(' ') + '" fill="none" stroke="#39b54a" stroke-width="2.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>';
      }
      svg.innerHTML = out;
      strip.innerHTML = pts.map(function (p) { return '<i class="' + p.c + '"></i>'; }).join('');
    }
    function emit(d) { d.host = host; try { document.dispatchEvent(new CustomEvent('sud-live', { detail: d })); } catch (e) {} }
    function clear() { svg.innerHTML = ''; strip.innerHTML = ''; data = null; }
    function setNow(big, sub) { q('ms').textContent = big; q('sub').textContent = sub; }
    function pill(v) {
      var el = q('pill'), c = cls(v);
      if (v === 'timeout' || v === 'inconclusive') { el.className = 'sp-pill unsure'; el.textContent = mode === 'live' ? 'Live · no answer' : 'No answer'; return; }
      if (v === 'collecting') { el.className = 'sp-pill unsure'; el.textContent = 'Collecting data'; return; }
      el.className = 'sp-pill ' + (c === 'none' ? 'unsure' : c);
      el.textContent = mode === 'live' ? (c === 'up' ? 'Live · up' : c === 'down' ? 'Live · down' : 'Live · slow') : (c === 'up' ? 'Up' : c === 'down' ? 'Down' : 'Mixed');
    }

    /* ---- live ---- */
    function renderLive() {
      var win = samples.slice(-30);
      if (!win.length) return;
      draw(win.map(function (s) { return { ms: s.ms, c: s.v === 'up' ? 'up' : (s.v === 'down' ? 'down' : 'slow'), label: clock(s.t) + ': ' + (s.ms != null ? s.ms + ' ms' : 'no answer') + (s.c ? ' (HTTP ' + s.c + ')' : '') }; }));
      var last = win[win.length - 1], vals = win.map(function (s) { return s.ms; }).filter(function (x) { return x != null; });
      var avg = vals.length ? Math.round(vals.reduce(function (a, b) { return a + b; }, 0) / vals.length) : null;
      setNow(last.ms != null ? last.ms + ' ms' : '—', 'Updated ' + clock(last.t) + (avg != null ? ' · average ' + avg + ' ms · fastest ' + Math.min.apply(null, vals) + ' · slowest ' + Math.max.apply(null, vals) : ''));
      pill(last.v);
      emit({ kind: 'sample', ms: last.ms, v: last.v, avg: avg, t: last.t, series: win.map(function (x) { return x.ms; }) });
      q('a1').textContent = Math.max(1, Math.round((win[win.length - 1].t - win[0].t) / 60)) + ' min ago'; q('a2').textContent = 'Now';
    }
    function poll() {
      clearTimeout(timer);
      if (dead || mode !== 'live') return;
      if (document.hidden) { timer = setTimeout(poll, 2000); return; }
      if (Date.now() - started > 15 * 60 * 1000) { stopped = true; q('sub').textContent = 'Paused to save resources. Tap Live to resume.'; return; }
      var url = '/api/live.php?host=' + encodeURIComponent(host) + '&vid=' + vid() + (take ? '&take=1' : ''); take = false;
      fetch(url, { credentials: 'same-origin' }).then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); }).then(function (r) {
        if (dead || mode !== 'live') return;
        if (r.s === 409) { stopped = true; q('sub').textContent = 'Paused — you are watching ' + (r.j.other || 'another site') + ' live in another tab. Tap Live to watch this one here instead.'; return; }
        if (r.s === 429) { q('sub').textContent = 'You have started a lot of live graphs. Please wait a few minutes.'; stopped = true; return; }
        if (r.s !== 200) { q('sub').textContent = 'A live graph is not available for this site.'; return; }
        var j = r.j; every = j.every || 10; samples = j.samples || [];
        renderLive();
        var age = samples.length ? j.now - samples[samples.length - 1].t : every;
        timer = setTimeout(poll, age >= every ? 3000 : Math.max(1000, (every - age) * 1000 + 300));
      }).catch(function () { timer = setTimeout(poll, 8000); });
    }

    /* ---- history ---- */
    function history(range) {
      fetch('/api/uptime.php?host=' + encodeURIComponent(host) + '&range=' + range).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
        if (dead || mode !== range) return;
        if (!j) { clear(); setNow('—', 'We have only just started recording this site. Its history fills in over the next hours — the Live tab works right away.'); return; }
        var pts = j.series.map(function (s) {
          var d = new Date(s.t), lab;
          if (range === '1y') lab = d.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }) + ': ' + (s.pct != null ? s.pct + '% up' : 'no data') + (s.outages ? ' · ' + plural(s.outages, 'outage') : '') + (s.down_s ? ' · down about ' + dur(s.down_s) : '') + (s.ms != null ? ' · ' + s.ms + ' ms average' : '');
          else lab = d.toLocaleString([], range === '24h' ? { weekday: 'short', hour: '2-digit', minute: '2-digit' } : { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit' }) + ': ' + (s.state === 'none' ? 'no data' : (s.ms != null ? s.ms + ' ms' : s.state));
          return { ms: s.ms, c: s.state === 'up' ? 'up' : (s.state === 'down' ? 'down' : (s.state === 'partial' ? 'slow' : 'none')), label: lab };
        });
        if (!pts.length) { clear(); setNow('—', 'The 12-month record starts building today. Check back tomorrow.'); return; }
        draw(pts);
        if (range === '1y') {
          setNow(j.year.uptime != null ? j.year.uptime + '% up' : '—', 'over ' + plural(j.year.days, 'day') + ' recorded · ' + plural(j.year.outages, 'outage') + (j.year.down_s ? ' · about ' + dur(j.year.down_s) + ' down in total' : '') + ' · graph shows average speed per day');
          q('a1').textContent = j.year.days >= 360 ? '12 months ago' : j.year.days + ' days ago';
        } else {
          var u = j.uptime[range];
          setNow(j.avg_ms != null ? j.avg_ms + ' ms' : '—', 'average' + (j.min_ms != null ? ' · fastest ' + j.min_ms + ' ms · slowest ' + j.max_ms + ' ms' : '') + (u != null ? ' · uptime ' + u + '%' : ''));
          q('a1').textContent = { '24h': '24 hours ago', '7d': '7 days ago' }[range] || '';
        }
        var got = pts.filter(function (x) { return x.c !== 'none'; }).length, cv = j.current.verdict;
        if (got < 4) pill('collecting'); else pill(cv === 'timeout' || cv === 'inconclusive' ? cv : (cv === 'up' ? 'up' : (cv === 'down' ? 'down' : 'slow')));
        q('a2').textContent = 'Now';
        if (range === '24h') {
          var ms = pts.map(function (x) { return x.ms; }), lastMs = null;
          for (var k = ms.length - 1; k >= 0; k--) if (ms[k] != null) { lastMs = ms[k]; break; }
          emit({ kind: 'sample', ms: lastMs, v: cv, avg: j.avg_ms, t: Math.round(Date.now() / 1000), series: ms.filter(function (x) { return x != null; }).slice(-30) });
        }
      }).catch(function () {});
    }

    /* ---- written outage summary ---- */
    function outages() {
      fetch('/api/uptime.php?host=' + encodeURIComponent(host) + '&range=7d').then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
        if (dead) return;
        var body = q('obody'); body.textContent = '';
        var p;
        if (!j) { q('osum').textContent = 'Just started'; p = document.createElement('p'); p.className = 'so-clear'; p.textContent = 'We have only just started watching ' + host + ', so there is no outage record yet. Anything we see from now on will be listed here.'; body.appendChild(p); q('oyear').textContent = ''; return; }
        emit({ kind: 'hist', uptime24: j.uptime && j.uptime['24h'], uptime7: j.uptime && j.uptime['7d'], outages7: (j.recent || []).length, down7: j.recent_down_s || 0 });
        var rec = j.recent || [];
        q('osum').textContent = rec.length ? plural(rec.length, 'outage') + ' · ' + dur(j.recent_down_s) + ' down' : 'All clear';
        if (!rec.length) { p = document.createElement('p'); p.className = 'so-clear'; p.textContent = 'No outages recorded in the last 7 days. We have not seen ' + host + ' go down.'; body.appendChild(p); }
        else {
          var ul = document.createElement('ul'); ul.className = 'so-list';
          rec.forEach(function (o) {
            var li = document.createElement('li'); li.className = o.ended ? '' : 'on';
            var t = document.createElement('b'); t.textContent = o.ended ? when(o.started) + ' → ' + new Date(o.ended).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Since ' + when(o.started);
            var d = document.createElement('span'); d.textContent = o.ended ? 'Down for about ' + dur(o.seconds) : 'Still down — ' + dur(o.seconds) + ' so far';
            li.appendChild(t); li.appendChild(d); ul.appendChild(li);
          });
          body.appendChild(ul);
        }
        var y = j.year;
        q('oyear').textContent = y && y.days ? 'Last 12 months (recorded since ' + new Date(y.since + 'T12:00:00Z').toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' }) + '): ' + (y.uptime != null ? y.uptime + '% up, ' : '') + plural(y.outages, 'outage') + (y.down_s ? ', about ' + dur(y.down_s) + ' down in total.' : '.') : '';
      }).catch(function () {});
    }

    /* ---- tabs and tooltip ---- */
    q('ranges').addEventListener('click', function (e) {
      var b = e.target.closest('[data-range]'); if (!b) return; var r = b.getAttribute('data-range');
      if (r === mode && !stopped) return;
      Array.prototype.forEach.call(this.querySelectorAll('[data-range]'), function (x) { var on = x === b; x.classList.toggle('on', on); x.setAttribute('aria-pressed', on); });
      mode = r; clearTimeout(timer);
      if (r === 'live') { stopped = false; take = true; started = Date.now(); renderLive(); poll(); } else history(r);
    });
    function tipAt(e) {
      if (!data || !data.length) return;
      var wrap = svg.getBoundingClientRect(), cx = (e.touches ? e.touches[0].clientX : e.clientX), f = Math.min(1, Math.max(0, (cx - wrap.left) / wrap.width));
      var n = data.length, i = Math.round(f * (n - 1)), p = data[i]; if (p) q('detail').textContent = p.label;
      /* thin white bar that snaps to the sample under the pointer (wrap here is the graph's own rectangle) */
      var lw = box.querySelector('.lv-wrap').getBoundingClientRect(), xf = n < 2 ? 0.5 : (PAD + (W - PAD * 2) * i / (n - 1)) / W;
      var px = wrap.left - lw.left + xf * wrap.width;
      cursor.style.left = px.toFixed(1) + 'px'; cursor.style.display = 'block';
      /* floating card with the reading under the bar */
      if (p) {
        var k = p.label.lastIndexOf(': '), when = k > 0 ? p.label.slice(0, k) : p.label, val = k > 0 ? p.label.slice(k + 2) : '';
        var vs = data.map(function (d) { return d.ms; }).filter(function (v) { return v != null; }), avg = vs.length ? vs.reduce(function (a, b) { return a + b; }, 0) / vs.length : null, rel = '';
        if (p.ms != null && avg) { var dv = Math.round((p.ms - avg) / avg * 100); rel = Math.abs(dv) < 8 ? 'about average' : (dv > 0 ? dv + '% slower than average' : Math.abs(dv) + '% faster than average'); }
        var stx = { up: 'Up', down: 'Down', slow: 'Slow', none: 'No data' }[p.c] || '';
        tip.innerHTML = '<span class="lt-when">' + when.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span><b>' + val.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</b>' + (stx ? '<span class="lt-st ' + p.c + '">' + stx + '</span>' : '') + (rel ? '<span class="lt-rel">' + rel + '</span>' : '');
        tip.className = 'lv-tip' + (xf > 0.6 ? ' l' : ''); tip.style.left = px.toFixed(1) + 'px'; tip.style.display = 'block';
      }
    }
    var wrap = box.querySelector('.lv-wrap'), cursor = document.createElement('div'); cursor.className = 'lv-cursor'; cursor.setAttribute('aria-hidden', 'true'); wrap.appendChild(cursor);
    var tip = document.createElement('div'); tip.className = 'lv-tip'; tip.setAttribute('aria-hidden', 'true'); wrap.appendChild(tip);
    function hideCursor() { cursor.style.display = 'none'; tip.style.display = 'none'; }
    wrap.addEventListener('mousemove', tipAt); wrap.addEventListener('click', tipAt); wrap.addEventListener('touchmove', tipAt, { passive: true }); wrap.addEventListener('touchstart', tipAt, { passive: true });
    wrap.addEventListener('mouseleave', hideCursor); wrap.addEventListener('touchend', function () { setTimeout(hideCursor, 1500); });
    function vis() { if (!document.hidden && mode === 'live' && !stopped) poll(); }
    document.addEventListener('visibilitychange', vis);
    history('24h'); outages();
    current = { destroy: function () { dead = true; clearTimeout(timer); document.removeEventListener('visibilitychange', vis); box.innerHTML = ''; } };
    return current;
  }
  window.SUD_LIVE = { mount: mount, clear: function () { if (current) { current.destroy(); current = null; } } };
  var slot = document.getElementById('lv-slot');
  if (slot) mount(slot, slot.getAttribute('data-host'));
})();
