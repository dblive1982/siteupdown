/* Global heat map: how the sites we watch look from each of our worldwide probe places. */
(function () {
  'use strict';
  var cv = document.getElementById('hm-globe'), LAND = window.SUD_LAND;
  if (!cv || !LAND || !cv.getContext) return;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
  var data = null, layer = 'reach';
  var D2R = Math.PI / 180, ctx = cv.getContext('2d'), tip = $('hm-tip');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Land: evenly spaced points over the sphere, kept where the 1 degree land mask says there is land. */
  var AL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_', MR = 180, MC = 360;
  var mask = [], landTmp = [], r0, N = 30000, GA = Math.PI * (3 - Math.sqrt(5));
  LAND.split(';').forEach(function (row) {
    var m = new Uint8Array(MC), x = 0, cur = 0;
    for (var i = 0; i + 1 < row.length; i += 2) { var run = (AL.indexOf(row.charAt(i)) << 6) | AL.indexOf(row.charAt(i + 1)); if (cur) m.fill(1, x, Math.min(MC, x + run)); x += run; cur ^= 1; }
    mask.push(m);
  });
  function isLand(latD, lonD) {
    var fr = (90 - latD) - 0.5, fc = (lonD + 180) - 0.5, r = Math.floor(fr), c = Math.floor(fc), tr = fr - r, tc = fc - c, v = 0;
    for (var i = 0; i < 2; i++) for (var j = 0; j < 2; j++) {
      var rr = r + i, cc = ((c + j) % MC + MC) % MC;
      v += (rr >= 0 && rr < MR ? mask[rr][cc] : 0) * (i ? tr : 1 - tr) * (j ? tc : 1 - tc);
    }
    return v >= 0.5;
  }
  for (r0 = 0; r0 < N; r0++) {
    var la = Math.asin(1 - 2 * (r0 + 0.5) / N), lo = ((r0 * GA) % (2 * Math.PI)) - Math.PI;
    if (isLand(la / D2R, lo / D2R)) landTmp.push(Math.sin(la), Math.cos(la), Math.sin(lo), Math.cos(lo));
  }
  var NL = landTmp.length / 4, LS = new Float32Array(landTmp), PX = new Float32Array(NL), PY = new Float32Array(NL), PB = new Uint8Array(NL), PZ = new Float32Array(NL);

  function name(p) { return (p.city ? p.city + ', ' : '') + (p.country ? (dn ? (dn.of(p.country) || p.country) : p.country) : ''); }
  function heat(p) {
    if (layer === 'reach') {
      var r = p.n ? p.ok / p.n : 0;
      return { cls: r >= 0.9 ? 'g' : r >= 0.7 ? 'a' : 'r', val: Math.round(r * 100) + '%', label: Math.round(r * 100) + '% of sites reached' };
    }
    var m = p.median_ms;
    if (m == null) return { cls: 'n', val: '–', label: 'No timing' };
    return { cls: m < 400 ? 'g' : m < 900 ? 'a' : 'r', val: m + ' ms', label: 'Typical load time ' + m + ' ms' };
  }

  /* View state: lon0/lat0 is the point facing the viewer. Angles in radians, speeds in radians per second. */
  var lon0 = 10 * D2R, lat0 = 22 * D2R, wLon = 0, wLat = 0, TILT = -16 * D2R, ct = Math.cos(TILT), st = Math.sin(TILT);
  var AUTO = 3.5 * D2R, autoV = 0, idleAt = 0, MAXW = 1.6;
  var sel = null, fly = null, sorted = [];
  var drag = null, hover = null, W = 0, R = 0, dpr = 1, visible = true, raf = 0, lastT = 0, lastDraw = 0, markers = [], wcache = {};
  var COL = { g: '126,217,87', a: '255,176,32', r: '232,74,74', n: '170,170,180' };
  var NB = 8, fills = [], fillTheme = null;

  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = cv.clientWidth; if (!W) return;
    cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr);
    R = W / 2 - 6; wcache = {}; need();
  }
  function projP(latD, lonD) {
    var la = latD * D2R, dl = lonD * D2R - lon0, sl = Math.sin(la), cl = Math.cos(la), cd = Math.cos(dl), sc = Math.sin(lat0), cc = Math.cos(lat0);
    var x = cl * Math.sin(dl), y = cc * sl - sc * cl * cd;
    return [x * ct - y * st, x * st + y * ct, sc * sl + cc * cl * cd];
  }
  function render() {
    if (!W) return;
    var light = document.documentElement.getAttribute('data-theme') === 'light';
    var c = W / 2, i, p;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, W);
    /* cartoon globe: blue sea, hard shadow, thick sketchy black outline, solid green land with an ink edge */
    var INK = '#111';
    ctx.beginPath(); ctx.arc(c + 4, c + 5, R, 0, 7); ctx.fillStyle = INK; ctx.fill();
    var g = ctx.createRadialGradient(c - R * 0.35, c - R * 0.4, R * 0.1, c, c, R * 1.05);
    g.addColorStop(0, '#6cc4ff'); g.addColorStop(0.65, '#3aa4ff'); g.addColorStop(1, '#1b8cf0');
    ctx.beginPath(); ctx.arc(c, c, R, 0, 7); ctx.fillStyle = g; ctx.fill();
    ctx.save(); ctx.beginPath(); ctx.arc(c, c, R, 0, 7); ctx.clip();
    var sl0 = Math.sin(lat0), cl0 = Math.cos(lat0), sL = Math.sin(lon0), cL = Math.cos(lon0), i2, k;
    for (i = 0; i < NL; i++) {
      var o = i * 4, a = LS[o], b = LS[o + 1], sn = LS[o + 2], cs = LS[o + 3];
      var cd = cs * cL + sn * sL, sd = sn * cL - cs * sL, x = b * sd, y = cl0 * a - sl0 * b * cd, z = sl0 * a + cl0 * b * cd;
      PX[i] = c + (x * ct - y * st) * R; PY[i] = c - (x * st + y * ct) * R; PB[i] = z > 0.02 ? 1 : 0; PZ[i] = z;
    }
    var rr = R * 0.026, ink = Math.max(1.5, R * 0.009);
    for (k = 0; k < 2; k++) {
      ctx.beginPath();
      for (i = 0; i < NL; i++) if (PB[i]) { var q = rr * (0.45 + 0.55 * Math.min(1, PZ[i] * 1.6)) + (k ? 0 : ink); ctx.moveTo(PX[i] + q, PY[i]); ctx.arc(PX[i], PY[i], q, 0, 7); }
      ctx.fillStyle = k ? '#a5c24a' : INK; ctx.fill();
    }
    ctx.restore();
    var shade = ctx.createRadialGradient(c - R * 0.3, c - R * 0.35, R * 0.6, c, c, R);
    shade.addColorStop(0, 'rgba(0,0,40,0)'); shade.addColorStop(1, 'rgba(0,0,60,.18)');
    ctx.beginPath(); ctx.arc(c, c, R, 0, 7); ctx.fillStyle = shade; ctx.fill();
    ctx.lineWidth = Math.max(3.5, R * 0.026); ctx.strokeStyle = INK; ctx.stroke();
    ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(c + 1.5, c - 1, R + 2.5, 0.2, 5.6); ctx.stroke();

    /* heat glows and place markers */
    markers = [];
    if (data) {
      var list = [];
      data.places.forEach(function (pl) {
        if (pl.lat == null || pl.lon == null) return;
        p = projP(pl.lat, pl.lon);
        if (p[2] <= 0.04) return;
        list.push({ pl: pl, x: c + p[0] * R, y: c - p[1] * R, z: p[2], h: heat(pl) });
      });
      var bg = '#ffffff';
      list.forEach(function (m) {
        var col = COL[m.h.cls], rad = 5 + 2.5 * m.z, on = hover === m.pl || sel === m.pl;
        if (on) rad += 2;
        ctx.beginPath(); ctx.arc(m.x, m.y + 1.5, rad + 2, 0, 7); ctx.fillStyle = INK; ctx.fill();
        ctx.beginPath(); ctx.arc(m.x, m.y, rad + 1.5, 0, 7); ctx.fillStyle = INK; ctx.fill();
        ctx.beginPath(); ctx.arc(m.x, m.y, rad - 0.5, 0, 7); ctx.fillStyle = 'rgb(' + col + ')'; ctx.fill();
        ctx.beginPath(); ctx.arc(m.x - rad * 0.3, m.y - rad * 0.3, rad * 0.25, 0, 7); ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.fill();
        markers.push(m);
      });
    }
    /* place name labels, nudged apart so they do not overlap */
    ctx.font = '600 ' + Math.max(10, Math.round(R * 0.032)) + 'px "Space Grotesk",system-ui,sans-serif'; ctx.textBaseline = 'middle';
    var placed = [];
    markers.slice().sort(function (a, b) { return b.z - a.z; }).forEach(function (m) {
      if (m.z < 0.25 || !m.pl.city) return;
      var t = m.pl.city.toUpperCase(), w = wcache[t] || (wcache[t] = ctx.measureText(t).width + 12), h = Math.max(16, R * 0.05), x = m.x + 9, y = m.y, tries = 0;
      if (x + w > W - 2) x = m.x - 9 - w;
      function hit() { return placed.some(function (b) { return x < b.x + b.w && x + w > b.x && y - h / 2 < b.y + b.h / 2 && y + h / 2 > b.y - b.h / 2; }); }
      while (hit() && tries < 8) { y += (tries % 2 ? -1 : 1) * (tries + 1) * (h + 2) / 2; tries++; }
      if (hit()) return;
      placed.push({ x: x, y: y, w: w, h: h });
      var col = COL[m.h.cls];
      ctx.fillStyle = '#fffbe8'; ctx.strokeStyle = INK; ctx.lineWidth = 2;
      ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y - h / 2, w, h, 4); else ctx.rect(x, y - h / 2, w, h); ctx.fill(); ctx.stroke();
      ctx.fillStyle = INK; ctx.fillText(t, x + 6, y + 0.5);
    });
    if (hover && tip) {
      var hm = markers.filter(function (m) { return m.pl === hover; })[0];
      if (hm) { tip.hidden = false; tip.textContent = name(hover) + ': ' + hm.h.label; tip.style.left = Math.min(Math.max(hm.x, 70), W - 70) + 'px'; tip.style.top = (hm.y - 18) + 'px'; }
      else tip.hidden = true;
    } else if (tip) tip.hidden = true;
  }
  function clampLat(v) { return Math.max(-80 * D2R, Math.min(80 * D2R, v)); }
  function need() { if (!raf) raf = requestAnimationFrame(frame); }

  /* One frame: physics are time-based so the speed is the same on any screen. */
  function frame(t) {
    raf = 0;
    var dt = lastT ? Math.min(0.05, (t - lastT) / 1000) : 0.016; lastT = t;
    var live = false;
    if (fly) {
      var pf = Math.min(1, (t - fly.t0) / fly.dur), ef = pf < 0.5 ? 2 * pf * pf : 1 - Math.pow(-2 * pf + 2, 2) / 2;
      lon0 = fly.a + fly.da * ef; lat0 = fly.b + fly.db * ef; wLon = wLat = 0; autoV = 0; idleAt = performance.now(); live = true;
      if (pf >= 1) fly = null;
    } else if (!drag) {
      var sp = Math.abs(wLon) + Math.abs(wLat);
      if (sp > 0.02) {
        lon0 += wLon * dt; lat0 = clampLat(lat0 + wLat * dt);
        var f = Math.exp(-dt * 3.2); wLon *= f; wLat *= f; live = true;
      } else {
        wLon = wLat = 0;
        if (!reduce && visible && !document.hidden && t - idleAt > 2500) {
          autoV += (AUTO - autoV) * (1 - Math.exp(-dt * 0.9));
          lon0 += autoV * dt; live = true;
        } else if (autoV > 0.001) { autoV *= Math.exp(-dt * 4); lon0 += autoV * dt; live = true; }
      }
    }
    /* idle spinning only needs ~30 frames a second; dragging gets every frame */
    if (drag || fly || sp > 0.02 || t - lastDraw >= 30) { render(); lastDraw = t; }
    if (live || drag) raf = requestAnimationFrame(frame); else lastT = 0;
  }

  function pick(x, y) {
    var best = null, bd = 22 * 22;
    markers.forEach(function (m) { var d = (m.x - x) * (m.x - x) + (m.y - y) * (m.y - y); if (d < bd) { bd = d; best = m.pl; } });
    return best;
  }
  function pos(e) { var b = cv.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; }
  cv.addEventListener('pointerdown', function (e) {
    var q = pos(e); drag = { x: q[0], y: q[1], moved: 0, t: e.timeStamp, last: e.timeStamp };
    wLon = wLat = 0; autoV = 0; idleAt = Infinity; fly = null;
    try { cv.setPointerCapture(e.pointerId); } catch (x) {}
    cv.classList.add('grab'); need();
  });
  cv.addEventListener('pointermove', function (e) {
    var q = pos(e);
    if (drag) {
      var dx = q[0] - drag.x, dy = q[1] - drag.y, dts = Math.max(0.008, (e.timeStamp - drag.t) / 1000);
      drag.x = q[0]; drag.y = q[1]; drag.t = e.timeStamp; drag.last = e.timeStamp; drag.moved += Math.abs(dx) + Math.abs(dy);
      var ux = dx * ct + dy * st, uy = -dx * st + dy * ct, dLon = -ux / R, dLat = uy / R;
      lon0 += dLon; lat0 = clampLat(lat0 + dLat);
      /* smoothed finger speed, used only when you let go */
      wLon = wLon * 0.6 + (dLon / dts) * 0.4; wLat = wLat * 0.6 + (dLat / dts) * 0.4;
      hover = null; need();
    } else {
      var h = pick(q[0], q[1]); if (h !== hover) { hover = h; cv.style.cursor = h ? 'pointer' : 'grab'; need(); }
    }
  });
  function end(e) {
    if (!drag) return;
    var tap = drag.moved < 6, stale = e && e.timeStamp - drag.last > 80;
    drag = null; cv.classList.remove('grab'); idleAt = performance.now();
    if (stale || tap) wLon = wLat = 0;
    wLon = Math.max(-MAXW, Math.min(MAXW, wLon)); wLat = Math.max(-MAXW, Math.min(MAXW, wLat));
    if (tap && e && e.type === 'pointerup') { var q = pos(e), h = pick(q[0], q[1]); hover = h; if (h) select(h === sel ? null : h, false); }
    need();
  }
  cv.addEventListener('pointerup', end); cv.addEventListener('pointercancel', end);
  cv.addEventListener('pointerleave', function () { if (!drag && hover) { hover = null; need(); } });
  cv.addEventListener('keydown', function (e) {
    var step = 8 * D2R, key = e.key;
    if (key === 'ArrowLeft') lon0 -= step; else if (key === 'ArrowRight') lon0 += step; else if (key === 'ArrowUp') lat0 = clampLat(lat0 + step); else if (key === 'ArrowDown') lat0 = clampLat(lat0 - step); else return;
    autoV = 0; idleAt = performance.now(); e.preventDefault(); need();
  });
  if (window.ResizeObserver) new ResizeObserver(size).observe(cv); else window.addEventListener('resize', size);
  if (window.IntersectionObserver) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; lastT = 0; if (visible) need(); }).observe(cv);
  document.addEventListener('visibilitychange', function () { lastT = 0; need(); });
  var th = $('theme'); if (th) th.addEventListener('click', function () { fillTheme = null; setTimeout(need, 30); });
  size();

  function flyTo(p) {
    if (p.lat == null || p.lon == null) return;
    var lo = p.lon * D2R, da = (((lo - lon0 + Math.PI) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI) - Math.PI, la = Math.max(-55 * D2R, Math.min(55 * D2R, p.lat * D2R));
    fly = { t0: performance.now(), dur: 900, a: lon0, da: da, b: lat0, db: la - lat0 }; wLon = wLat = 0; need();
  }
  function select(p, fromList) {
    sel = p; if (fromList) hover = null;
    if (p && fromList) { flyTo(p); try { cv.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (x) {} }
    var rows = document.querySelectorAll('#hm-tab tr');
    for (var i = 0; i < rows.length; i++) rows[i].classList.toggle('on', !!p && sorted[i] === p);
    card(); need();
  }
  function pct(p) { return Math.round(p.ok / Math.max(p.n, 1) * 100); }
  function card() {
    var el = $('hm-card'); if (!el || !data) return;
    var ps = data.places, i;
    if (!sel) {
      var withT = ps.filter(function (p) { return p.median_ms != null; }).sort(function (a, b) { return a.median_ms - b.median_ms; });
      var avg = Math.round(ps.reduce(function (t, p) { return t + pct(p); }, 0) / ps.length);
      el.innerHTML = '<div class="hm-card-h"><b>Worldwide summary</b></div><div class="hm-stats"><div><i>Places checked</i><b>' + ps.length + '</b></div><div><i>Average reached</i><b>' + avg + '%</b></div>' +
        (withT.length ? '<div><i>Fastest</i><b>' + withT[0].median_ms + ' ms</b><em>' + esc(name(withT[0])) + '</em></div><div><i>Slowest</i><b>' + withT[withT.length - 1].median_ms + ' ms</b><em>' + esc(name(withT[withT.length - 1])) + '</em></div>' : '') +
        '</div><p class="note">Tap a dot on the globe, or a country in the list below, to see its details.</p>';
      return;
    }
    var p = sel, r = p.n ? p.ok / p.n : 0, cls = r >= 0.9 ? 'g' : r >= 0.7 ? 'a' : 'r';
    var verdict = r >= 0.9 ? 'Almost every site we watch answered from here.' : r >= 0.7 ? 'Most sites answered from here, but some did not.' : 'Many sites did not answer from here. This can point to a problem with a network or country, or to sites blocking automated checks.';
    el.innerHTML = '<div class="hm-card-h"><b>' + esc(name(p)) + '</b><span class="hm-chip ' + cls + '">' + pct(p) + '%</span><button type="button" class="hm-x" data-close aria-label="Close details">&times;</button></div>' +
      '<p class="hm-verdict">' + verdict + '</p><div class="hm-stats"><div><i>Sites reached</i><b>' + p.ok + ' of ' + p.n + '</b></div><div><i>Typical time</i><b>' + (p.median_ms != null ? p.median_ms + ' ms' : '–') + '</b></div>' +
      '<div><i>Failed to load</i><b>' + (p.error || 0) + '</b></div><div><i>Blocked our check</i><b>' + (p.blocked || 0) + '</b></div><div><i>No answer</i><b>' + (p.none || 0) + '</b></div></div>' +
      '<p class="note">A site that cannot be reached from one place is not always down. Some sites block automated checks from certain countries.</p>';
  }
  $('hm-card') && $('hm-card').addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-close]')) select(null, false); });
  var tb = $('hm-tab');
  if (tb) {
    tb.addEventListener('click', function (e) { var tr = e.target.closest && e.target.closest('tr[data-i]'); if (tr) { var p = sorted[+tr.getAttribute('data-i')]; select(p === sel ? null : p, true); } });
    tb.addEventListener('keydown', function (e) { if (e.key !== 'Enter' && e.key !== ' ') return; var tr = e.target.closest && e.target.closest('tr[data-i]'); if (tr) { e.preventDefault(); var p = sorted[+tr.getAttribute('data-i')]; select(p === sel ? null : p, true); } });
  }

  function draw() {
    if (!data) return;
    need();
    sorted = data.places.slice().sort(function (a, b) { return name(a).localeCompare(name(b)); });
    var rows = sorted.map(function (p, i) {
      var h = heat(p);
      return '<tr class="hm-row' + (p === sel ? ' on' : '') + '" tabindex="0" role="button" data-i="' + i + '" aria-label="Show details for ' + esc(name(p)) + '"><td data-l="Place">' + esc(name(p)) + '</td><td data-l="Sites reached"><span class="hm-chip ' + h.cls + '">' + Math.round(p.ok / Math.max(p.n, 1) * 100) + '%</span> <span class="sp-ms">' + p.ok + ' of ' + p.n + '</span></td><td data-l="Typical time">' + (p.median_ms != null ? p.median_ms + ' ms' : '–') + '</td></tr>';
    });
    $('hm-tab').innerHTML = rows.join('');
    card();
    $('hm-leg').innerHTML = layer === 'reach' ? '<span><i class="g"></i>90% or more reached</span><span><i class="a"></i>70 to 90%</span><span><i class="r"></i>Under 70%</span>' : '<span><i class="g"></i>Under 400 ms</span><span><i class="a"></i>400 to 900 ms</span><span><i class="r"></i>Over 900 ms</span>';
  }
  function ago(ts) {
    var s = Math.max(0, Date.now() / 1000 - ts), m = Math.round(s / 60);
    return m < 90 ? m + ' minutes ago' : Math.round(m / 60) + ' hours ago';
  }
  function load() { return fetch('/api/heatmap.php').then(function (r) { return r.json(); }).then(function (j) {
    if (!j.places || !j.places.length) { $('hm-sum').textContent = 'The first worldwide results are still being collected. Please check back soon.'; return; }
    var sk = sel ? name(sel) : null; data = j; sel = null; hover = null;
    if (sk) j.places.forEach(function (p) { if (name(p) === sk) sel = p; });
    draw();
    $('hm-sum').textContent = 'Based on the latest worldwide check of ' + j.sites_count + ' websites and apps from ' + j.places.length + ' places. Results from ' + ago(j.newest) + ' back to ' + ago(j.oldest) + '.';
    if (j.unreachable && j.unreachable.length) {
      $('hm-sites').innerHTML = '<h2>Sites not reached everywhere right now</h2><div class="hm-list">' + j.unreachable.map(function (s) {
        return '<a href="' + esc(s.page) + '"><span>' + esc(s.name) + '</span><b>' + s.ok + ' of ' + s.total + ' places</b></a>';
      }).join('') + '</div><p class="note">A site that some places cannot reach is not always down. It may block automated checks from those countries.</p>';
    } else $('hm-sites').innerHTML = '<p class="note"><b>Every site we watch was reached from every place in the latest check.</b></p>';
  }).catch(function () { if (!data) $('hm-sum').textContent = 'Could not load the map just now.'; }); }
  load();
  setInterval(function () { if (!document.hidden) load(); }, 180000);
  document.querySelectorAll('[data-hm]').forEach(function (b) {
    b.addEventListener('click', function () {
      layer = b.getAttribute('data-hm');
      document.querySelectorAll('[data-hm]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      draw();
    });
  });
})();
