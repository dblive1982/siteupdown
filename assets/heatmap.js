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
  var mask = [], land = [], r0, c0, N = 24000, GA = Math.PI * (3 - Math.sqrt(5));
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
    if (isLand(la / D2R, lo / D2R)) land.push([Math.sin(la), Math.cos(la), lo]);
  }

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

  /* View state: lon0/lat0 is the point facing the viewer. */
  var lon0 = 10 * D2R, lat0 = 22 * D2R, vLon = 0, vLat = 0, TILT = -16 * D2R, ct = Math.cos(TILT), st = Math.sin(TILT);
  var drag = null, hover = null, W = 0, R = 0, dpr = 1, auto = !reduce, visible = true, raf = 0, lastT = 0, markers = [];
  var COL = { g: '13,192,78', a: '245,184,61', r: '255,90,95', n: '107,124,115' };

  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = cv.clientWidth; if (!W) return;
    cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr);
    R = W / 2 - 6; need();
  }
  function proj(sl, cl, lon) {
    var dl = lon - lon0, cd = Math.cos(dl), sc = Math.sin(lat0), cc = Math.cos(lat0);
    var x = cl * Math.sin(dl), y = cc * sl - sc * cl * cd;
    return [x * ct - y * st, x * st + y * ct, sc * sl + cc * cl * cd];
  }
  function render() {
    raf = 0;
    if (!W) return;
    var light = document.documentElement.getAttribute('data-theme') === 'light';
    var c = W / 2, i, p, q;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, W);
    var g = ctx.createRadialGradient(c - R * 0.3, c - R * 0.35, R * 0.1, c, c, R);
    g.addColorStop(0, light ? 'rgba(47,158,65,.10)' : 'rgba(13,192,78,.10)');
    g.addColorStop(1, light ? 'rgba(47,158,65,.02)' : 'rgba(13,192,78,.015)');
    ctx.beginPath(); ctx.arc(c, c, R, 0, 7); ctx.fillStyle = g; ctx.fill();
    ctx.lineWidth = 1.5; ctx.strokeStyle = light ? 'rgba(47,158,65,.45)' : 'rgba(13,192,78,.35)'; ctx.stroke();
    /* land dots: bright on the near side, faint through the globe on the far side */
    var rgb = light ? '47,158,65' : '13,192,78', base = light ? 0.9 : 0.85, d = Math.max(1.2, R * 0.0072);
    for (i = 0; i < land.length; i++) {
      q = land[i]; p = proj(q[0], q[1], q[2]);
      var near = p[2] > 0, al = near ? base * Math.min(1, 0.3 + p[2] * 0.95) : (light ? 0.07 : 0.09) * (1 + p[2]), s = d * (near ? 0.6 + 0.4 * p[2] : 0.55);
      ctx.fillStyle = 'rgba(' + rgb + ',' + al.toFixed(2) + ')';
      ctx.fillRect(c + p[0] * R - s / 2, c - p[1] * R - s / 2, s, s);
    }
    /* heat glows and place markers */
    markers = [];
    if (data) {
      var list = [];
      data.places.forEach(function (pl) {
        if (pl.lat == null || pl.lon == null) return;
        var a = pl.lat * D2R; p = proj(Math.sin(a), Math.cos(a), pl.lon * D2R);
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
      var t = m.pl.city.toUpperCase(), w = ctx.measureText(t).width + 12, h = Math.max(16, R * 0.05), x = m.x + 9, y = m.y, tries = 0;
      if (x + w > W - 2) x = m.x - 9 - w;
      function hit() { return placed.some(function (b) { return x < b.x + b.w && x + w > b.x && y - h / 2 < b.y + b.h / 2 && y + h / 2 > b.y - b.h / 2; }); }
      while (hit() && tries < 8) { y += (tries % 2 ? -1 : 1) * (tries + 1) * (h + 2) / 2 * 1.0; tries++; }
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
  function need() { if (!raf) raf = requestAnimationFrame(frame); }
  function frame(t) {
    raf = 0;
    var dt = Math.min(0.05, (t - (lastT || t)) / 1000); lastT = t;
    var moving = false;
    if (!drag) {
      if (Math.abs(vLon) > 0.00004 || Math.abs(vLat) > 0.00004) { lon0 += vLon * dt * 60; lat0 = clampLat(lat0 + vLat * dt * 60); vLon *= 0.94; vLat *= 0.94; moving = true; }
      else if (auto && visible && !document.hidden) { lon0 += 0.14 * D2R * dt * 6; moving = true; }
    }
    render();
    if (moving || drag) { raf = requestAnimationFrame(frame); } else lastT = 0;
  }
  function clampLat(v) { return Math.max(-80 * D2R, Math.min(80 * D2R, v)); }

  function pick(x, y) {
    var best = null, bd = 22 * 22;
    markers.forEach(function (m) { var d = (m.x - x) * (m.x - x) + (m.y - y) * (m.y - y); if (d < bd) { bd = d; best = m.pl; } });
    return best;
  }
  function pos(e) { var b = cv.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; }
  cv.addEventListener('pointerdown', function (e) {
    var q = pos(e); drag = { x: q[0], y: q[1], moved: 0 }; vLon = vLat = 0; auto = false;
    try { cv.setPointerCapture(e.pointerId); } catch (x) {}
    cv.classList.add('grab'); need();
  });
  cv.addEventListener('pointermove', function (e) {
    var q = pos(e);
    if (drag) {
      var dx = q[0] - drag.x, dy = q[1] - drag.y; drag.x = q[0]; drag.y = q[1]; drag.moved += Math.abs(dx) + Math.abs(dy);
      var k = 1 / R / Math.max(0.35, Math.cos(lat0) * 0.4 + 0.6);
      var ux = dx * ct + dy * st, uy = -dx * st + dy * ct;
      lon0 -= ux * k; lat0 = clampLat(lat0 + uy * k * 0.9); vLon = -ux * k * 0.5; vLat = uy * k * 0.45;
      hover = null; need();
    } else {
      var h = pick(q[0], q[1]); if (h !== hover) { hover = h; cv.style.cursor = h ? 'pointer' : 'grab'; need(); }
    }
  });
  function end(e) {
    if (!drag) return;
    var tap = drag.moved < 6; drag = null; cv.classList.remove('grab');
    if (tap && e && e.type === 'pointerup') { var q = pos(e), h = pick(q[0], q[1]); hover = h === hover ? null : h; vLon = vLat = 0; }
    need();
  }
  cv.addEventListener('pointerup', end); cv.addEventListener('pointercancel', end);
  cv.addEventListener('pointerleave', function () { if (!drag && hover) { hover = null; need(); } });
  cv.addEventListener('keydown', function (e) {
    var st = 8 * D2R, k = e.key;
    if (k === 'ArrowLeft') lon0 -= st; else if (k === 'ArrowRight') lon0 += st; else if (k === 'ArrowUp') lat0 = clampLat(lat0 + st); else if (k === 'ArrowDown') lat0 = clampLat(lat0 - st); else return;
    auto = false; e.preventDefault(); need();
  });
  if (window.ResizeObserver) new ResizeObserver(size).observe(cv); else window.addEventListener('resize', size);
  if (window.IntersectionObserver) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) need(); }).observe(cv);
  document.addEventListener('visibilitychange', need);
  var th = $('theme'); if (th) th.addEventListener('click', function () { setTimeout(need, 30); });
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
