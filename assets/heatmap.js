/* Global heat map: how the sites we watch look from each of our worldwide probe places. */
(function () {
  'use strict';
  var cv = document.getElementById('hm-globe'), M = window.SUD_MAP;
  if (!cv || !M || !cv.getContext) return;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
  var data = null, layer = 'reach';
  var D2R = Math.PI / 180, ctx = cv.getContext('2d'), tip = $('hm-tip');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Land: evenly spaced points over the sphere, kept where the land grid says there is land. */
  var mask = [], landTmp = [], r0, c0, N = 24000, GA = Math.PI * (3 - Math.sqrt(5));
  for (r0 = 0; r0 < M.rows; r0++) mask.push(new Uint8Array(M.cols));
  M.runs.forEach(function (runs, r) { runs.forEach(function (run) { for (var c = run[0]; c < run[0] + run[1] && c < M.cols; c++) mask[r][c] = 1; }); });
  function isLand(latD, lonD) {
    var fr = (M.top - latD) / M.cell - 0.5, fc = (lonD + 180) / M.cell - 0.5, r = Math.floor(fr), c = Math.floor(fc), tr = fr - r, tc = fc - c, v = 0;
    for (var i = 0; i < 2; i++) for (var j = 0; j < 2; j++) {
      var rr = r + i, cc = ((c + j) % M.cols + M.cols) % M.cols;
      v += (rr >= 0 && rr < M.rows ? mask[rr][cc] : 0) * (i ? tr : 1 - tr) * (j ? tc : 1 - tc);
    }
    return v >= 0.5;
  }
  for (r0 = 0; r0 < N; r0++) {
    var la = Math.asin(1 - 2 * (r0 + 0.5) / N), lo = ((r0 * GA) % (2 * Math.PI)) - Math.PI;
    if (isLand(la / D2R, lo / D2R)) landTmp.push(Math.sin(la), Math.cos(la), Math.sin(lo), Math.cos(lo));
  }
  var NL = landTmp.length / 4, LS = new Float32Array(landTmp), PX = new Float32Array(NL), PY = new Float32Array(NL), PB = new Uint8Array(NL);

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
  var drag = null, hover = null, W = 0, R = 0, dpr = 1, visible = true, raf = 0, lastT = 0, lastDraw = 0, markers = [], wcache = {};
  var COL = { g: '13,192,78', a: '245,184,61', r: '255,90,95', n: '107,124,115' };
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
    var g = ctx.createRadialGradient(c - R * 0.3, c - R * 0.35, R * 0.1, c, c, R);
    g.addColorStop(0, light ? 'rgba(47,158,65,.10)' : 'rgba(13,192,78,.10)');
    g.addColorStop(1, light ? 'rgba(47,158,65,.02)' : 'rgba(13,192,78,.015)');
    ctx.beginPath(); ctx.arc(c, c, R, 0, 7); ctx.fillStyle = g; ctx.fill();
    ctx.lineWidth = 1.5; ctx.strokeStyle = light ? 'rgba(47,158,65,.45)' : 'rgba(13,192,78,.35)'; ctx.stroke();

    /* land dots: project all of them with plain numbers (no allocation), then draw one batch per brightness level */
    var rgb = light ? '47,158,65' : '13,192,78', base = light ? 0.9 : 0.85, d = Math.max(1.2, R * 0.0072), k;
    if (fillTheme !== light) {
      fillTheme = light; fills = [];
      for (k = 0; k < NB - 1; k++) { var zm = (k + 0.5) / (NB - 1); fills.push('rgba(' + rgb + ',' + (base * Math.min(1, 0.3 + zm * 0.95)).toFixed(2) + ')'); }
      fills.push('rgba(' + rgb + ',' + (light ? 0.07 : 0.09) + ')');
    }
    var sl0 = Math.sin(lat0), cl0 = Math.cos(lat0), sL = Math.sin(lon0), cL = Math.cos(lon0);
    for (i = 0; i < NL; i++) {
      var o = i * 4, a = LS[o], b = LS[o + 1], sn = LS[o + 2], cs = LS[o + 3];
      var cd = cs * cL + sn * sL, sd = sn * cL - cs * sL, x = b * sd, y = cl0 * a - sl0 * b * cd, z = sl0 * a + cl0 * b * cd;
      PX[i] = c + (x * ct - y * st) * R; PY[i] = c - (x * st + y * ct) * R;
      PB[i] = z > 0 ? Math.min(NB - 2, (z * (NB - 1)) | 0) : NB - 1;
    }
    for (k = 0; k < NB; k++) {
      var sz = k === NB - 1 ? d * 0.55 : d * (0.6 + 0.4 * (k + 0.5) / (NB - 1)), h2 = sz / 2;
      ctx.beginPath();
      for (i = 0; i < NL; i++) if (PB[i] === k) ctx.rect(PX[i] - h2, PY[i] - h2, sz, sz);
      ctx.fillStyle = fills[k]; ctx.fill();
    }

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
      ctx.globalCompositeOperation = light ? 'source-over' : 'lighter';
      list.forEach(function (m) {
        var gr = R * 0.2 * (0.6 + 0.4 * m.z), rg = ctx.createRadialGradient(m.x, m.y, 0, m.x, m.y, gr), col = COL[m.h.cls];
        rg.addColorStop(0, 'rgba(' + col + ',' + (light ? 0.55 : 0.75) + ')'); rg.addColorStop(1, 'rgba(' + col + ',0)');
        ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(m.x, m.y, gr, 0, 7); ctx.fill();
      });
      ctx.globalCompositeOperation = 'source-over';
      list.forEach(function (m) {
        var col = COL[m.h.cls], rad = 4.2 + 2.2 * m.z, on = hover === m.pl;
        ctx.beginPath(); ctx.arc(m.x, m.y, on ? rad + 2 : rad, 0, 7);
        ctx.fillStyle = 'rgb(' + col + ')'; ctx.fill();
        ctx.lineWidth = on ? 2.5 : 1.5; ctx.strokeStyle = '#fff'; ctx.stroke();
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
      ctx.fillStyle = light ? 'rgba(255,255,255,.88)' : 'rgba(19,2,40,.78)'; ctx.strokeStyle = 'rgba(' + col + ',.75)'; ctx.lineWidth = 1;
      ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y - h / 2, w, h, 4); else ctx.rect(x, y - h / 2, w, h); ctx.fill(); ctx.stroke();
      ctx.fillStyle = light ? '#14301d' : '#f3f1fa'; ctx.fillText(t, x + 6, y + 0.5);
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
    if (!drag) {
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
    if (drag || sp > 0.02 || t - lastDraw >= 30) { render(); lastDraw = t; }
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
    wLon = wLat = 0; autoV = 0; idleAt = Infinity;
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
    if (tap && e && e.type === 'pointerup') { var q = pos(e), h = pick(q[0], q[1]); hover = h === hover ? null : h; }
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

  function draw() {
    if (!data) return;
    need();
    var rows = data.places.slice().sort(function (a, b) { return (a.country || '').localeCompare(b.country || ''); }).map(function (p) {
      var h = heat(p);
      return '<tr><td data-l="Place">' + esc(name(p)) + '</td><td data-l="Sites reached"><span class="hm-chip ' + h.cls + '">' + Math.round(p.ok / Math.max(p.n, 1) * 100) + '%</span> <span class="sp-ms">' + p.ok + ' of ' + p.n + '</span></td><td data-l="Typical time">' + (p.median_ms != null ? p.median_ms + ' ms' : '–') + '</td></tr>';
    });
    $('hm-tab').innerHTML = rows.join('');
    $('hm-leg').innerHTML = layer === 'reach' ? '<span><i class="g"></i>90% or more reached</span><span><i class="a"></i>70 to 90%</span><span><i class="r"></i>Under 70%</span>' : '<span><i class="g"></i>Under 400 ms</span><span><i class="a"></i>400 to 900 ms</span><span><i class="r"></i>Over 900 ms</span>';
  }
  function ago(ts) {
    var s = Math.max(0, Date.now() / 1000 - ts), m = Math.round(s / 60);
    return m < 90 ? m + ' minutes ago' : Math.round(m / 60) + ' hours ago';
  }
  function load() { return fetch('/api/heatmap.php').then(function (r) { return r.json(); }).then(function (j) {
    if (!j.places || !j.places.length) { $('hm-sum').textContent = 'The first worldwide results are still being collected. Please check back soon.'; return; }
    data = j; draw();
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
