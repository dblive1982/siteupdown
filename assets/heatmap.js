/* Global heat map on the flat continents map: how the sites we watch look from each of our worldwide probe places. */
(function () {
  'use strict';
  var box = document.getElementById('hm-map'), lay = document.getElementById('hm-lay'), tip = document.getElementById('hm-bub');
  if (!box || !lay) return;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
  var centred = false, data = null, layer = 'reach', sel = null, sorted = [], dots = [];
  /* flat continents picture (2400x1221): fitted projection from lon/lat to picture pixels */
  var A = { ax: 3.41904622, bx: -24.79309414, ay: -213.39670053, by: 670.34834736, mix: 0.5, S: 2.5, y0: 690, k: 2400 / 3125 };
  function mil(d) { return 1.25 * Math.log(Math.tan(Math.PI / 4 + 0.4 * d * Math.PI / 180)); }
  function PR(lon, lat) { var f = A.mix * mil(lat) + (1 - A.mix) * lat * Math.PI / 180; return [(A.ax * (lon + 180) + A.bx) * A.S * A.k, ((A.ay * f + A.by) * A.S - A.y0) * A.k]; }
  var COL = { g: '#2fbf4a', a: '#ffb020', r: '#e84a4a', n: '#bbbbbb' };
  var CN = [['NORTH AMERICA', -106, 58, 40], ['SOUTH AMERICA', -68, -8, 34], ['AFRICA', 19, 11, 46], ['EUROPE', 17, 63, 26, 'eu'], ['ASIA', 96, 54, 52], ['MIDDLE EAST', 43, 21, 20, 'me'], ['AUSTRALIA', 128, -26, 28]];
  var OC = [['ATLANTIC', -35, 30, 30], ['OCEAN', -35, 24, 30], ['PACIFIC', -150, 10, 30], ['OCEAN', -150, 4, 30], ['INDIAN', 78, -20, 30], ['OCEAN', 78, -26, 30], ['ARCTIC OCEAN', -60, 80, 26], ['PACIFIC', 148, -44, 26], ['OCEAN', 148, -50, 26]];
  var labels = '';
  CN.forEach(function (c) { var q = PR(c[1], c[2]); labels += '<text class="cn' + (c[4] ? ' ' + c[4] : '') + '" x="' + q[0].toFixed(0) + '" y="' + q[1].toFixed(0) + '" style="font-size:' + c[3] + 'px">' + c[0] + '</text>'; });
  OC.forEach(function (c) { var q = PR(c[1], c[2]); labels += '<text class="oc" x="' + q[0].toFixed(0) + '" y="' + q[1].toFixed(0) + '" style="font-size:' + c[3] + 'px">' + c[0] + '</text>'; });
  var WORD = { g: 'Reachable', a: 'Slow or patchy', r: 'Problems', n: 'No timing' };

  function name(p) { return (p.city ? p.city + ', ' : '') + (p.country ? (dn ? (dn.of(p.country) || p.country) : p.country) : ''); }
  function heat(p) {
    if (layer === 'reach') {
      var r = p.n ? p.ok / p.n : 0;
      return { cls: r >= 0.9 ? 'g' : r >= 0.7 ? 'a' : 'r', val: Math.round(r * 100) + '%', label: Math.round(r * 100) + '% of sites reached' };
    }
    var m = p.median_ms;
    if (m == null) return { cls: 'n', val: '\u2013', label: 'No timing' };
    return { cls: m < 400 ? 'g' : m < 900 ? 'a' : 'r', val: m + ' ms', label: 'Typical load time ' + m + ' ms' };
  }
  function paint() {
    if (!data) return;
    dots = data.places.filter(function (p) { return p.lat != null && p.lon != null; });
    var pos = [], html = labels;
    dots.forEach(function (p, i) {
      var q = PR(p.lon, p.lat), h = heat(p), L = 1;
      for (var k = 0; k < pos.length; k++) if (Math.abs(pos[k][0] - q[0]) < 90 && Math.abs(pos[k][1] - q[1]) < 70 && pos[k][2] === 1) L = -1;
      pos.push([q[0], q[1], L]);
      html += '<g class="pole ' + h.cls + (p === sel ? ' on' : '') + '" data-d="' + i + '" tabindex="0" role="button" aria-label="' + esc(name(p) + ': ' + h.label) + '" transform="translate(' + q[0].toFixed(1) + ' ' + q[1].toFixed(1) + ')">' +
        (h.cls === 'r' || h.cls === 'a' ? '<circle class="ring" r="14" fill="none" stroke="' + COL[h.cls] + '" stroke-width="5"/>' : '') +
        '<ellipse cx="0" cy="2" rx="20" ry="7" fill="rgba(0,0,0,.28)"/><line x1="0" y1="0" x2="0" y2="-100" stroke="#3a2412" stroke-width="7" stroke-linecap="round"/>' +
        '<path class="flag" d="M' + (3 * L) + ' -100 L' + (66 * L) + ' -84 L' + (3 * L) + ' -64 Z" fill="' + COL[h.cls] + '" stroke="#111" stroke-width="5.5" stroke-linejoin="round"/><circle cx="0" cy="-104" r="9" fill="#111"/></g>';
    });
    lay.innerHTML = html;
    if (!centred) { centred = true; var sc = box.querySelector('.hm-scroll'); if (sc) sc.scrollLeft = (sc.scrollWidth - sc.clientWidth) * 0.52; }
  }
  function showTip(g) {
    var p = dots[+g.getAttribute('data-d')]; if (!p) return;
    var h = heat(p);
    tip.innerHTML = '<b>' + esc(name(p)) + '</b><span class="tp" style="background:' + COL[h.cls] + '">' + h.val + '</span><small>' + WORD[h.cls] + ' &middot; ' + (p.median_ms != null ? p.median_ms + ' ms' : 'no timing') + '</small>';
    tip.style.display = 'block';
    var r = g.querySelector('line').getBoundingClientRect(), b = tip.parentNode.getBoundingClientRect();
    var x = r.left + r.width / 2 - b.left, y = r.top - b.top, w = tip.offsetWidth, hh = tip.offsetHeight;
    var left = Math.max(6, Math.min(b.width - w - 6, x - w / 2)), top = y - hh - 8; if (top < 6) top = r.bottom - b.top + 14;
    tip.style.left = left + 'px'; tip.style.top = top + 'px';
  }
  function hideTip() { tip.style.display = 'none'; }
  lay.addEventListener('mouseover', function (e) { var g = e.target.closest && e.target.closest('.pole'); if (g) showTip(g); });
  lay.addEventListener('mouseout', function (e) { if (e.target.closest && e.target.closest('.pole')) hideTip(); });
  lay.addEventListener('focusin', function (e) { var g = e.target.closest && e.target.closest('.pole'); if (g) showTip(g); });
  lay.addEventListener('focusout', hideTip);
  lay.addEventListener('keydown', function (e) { if (e.key !== 'Enter' && e.key !== ' ') return; var g = e.target.closest && e.target.closest('.pole'); if (g) { e.preventDefault(); var p = dots[+g.getAttribute('data-d')]; select(p === sel ? null : p, false); } });
  function need() { paint(); }
  function pct(p) { return Math.round(p.ok / Math.max(p.n, 1) * 100); }
  function card() {
    var el = $('hm-card'); if (!el || !data) return;
    var ps = data.places, i;
    if (!sel) {
      var withT = ps.filter(function (p) { return p.median_ms != null; }).sort(function (a, b) { return a.median_ms - b.median_ms; });
      var avg = Math.round(ps.reduce(function (t, p) { return t + pct(p); }, 0) / ps.length);
      el.innerHTML = '<div class="hm-card-h"><b>Worldwide summary</b></div><div class="hm-stats"><div><i>Places checked</i><b>' + ps.length + '</b></div><div><i>Average reached</i><b>' + avg + '%</b></div>' +
        (withT.length ? '<div><i>Fastest</i><b>' + withT[0].median_ms + ' ms</b><em>' + esc(name(withT[0])) + '</em></div><div><i>Slowest</i><b>' + withT[withT.length - 1].median_ms + ' ms</b><em>' + esc(name(withT[withT.length - 1])) + '</em></div>' : '') +
        '</div><p class="note">Tap a dot on the map, or a country in the list below, to see its details.</p>';
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
  function select(p, fromList) {
    sel = p;
    var rows = document.querySelectorAll('#hm-tab tr');
    for (var i = 0; i < rows.length; i++) rows[i].classList.toggle('on', !!p && sorted[i] === p);
    card(); paint();
    if (p && fromList) { try { box.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (x) {} }
  }
  box.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-d]');
    if (b) { var p = dots[+b.getAttribute('data-d')]; select(p === sel ? null : p, false); var g2 = lay.querySelector('.pole.on'); if (g2) showTip(g2); else hideTip(); } else { hideTip(); if (sel) select(null, false); }
  });
  $('hm-card') && $('hm-card').addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-close]')) select(null, false); });
  var tb = $('hm-tab');
  if (tb) {
    tb.addEventListener('click', function (e) { var tr = e.target.closest && e.target.closest('tr[data-i]'); if (tr) { var p = sorted[+tr.getAttribute('data-i')]; select(p === sel ? null : p, true); } });
    tb.addEventListener('keydown', function (e) { if (e.key !== 'Enter' && e.key !== ' ') return; var tr = e.target.closest && e.target.closest('tr[data-i]'); if (tr) { e.preventDefault(); var p = sorted[+tr.getAttribute('data-i')]; select(p === sel ? null : p, true); } });
  }
  function ago(ts) {
    var s = Math.max(0, Date.now() / 1000 - ts), m = Math.round(s / 60);
    return m < 90 ? m + ' minutes ago' : Math.round(m / 60) + ' hours ago';
  }
  function load() { return fetch('/api/heatmap.php').then(function (r) { return r.json(); }).then(function (j) {
    if (!j.places || !j.places.length) { $('hm-sum').textContent = 'The first worldwide results are still being collected. Please check back soon.'; return; }
    var sk = sel ? name(sel) : null; data = j; sel = null;
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
