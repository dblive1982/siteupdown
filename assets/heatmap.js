/* Global heat map on the crayon paper map: how the sites we watch look from each of our worldwide probe places. */
(function () {
  'use strict';
  var box = document.getElementById('hm-map');
  if (!box) return;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
  var data = null, layer = 'reach', sel = null, sorted = [], dots = [];
  /* where the land sits on the paper picture (pixels of the 960x830 image) */
  var G = { x0: 52, y0: 110, w: 856, h: 560, W: 960, H: 830, rows: 136, top: 77 };

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
  function place(p) {
    var x = G.x0 + (p.lon + 180) / 360 * G.w, y = G.y0 + (G.top - p.lat) / G.rows * G.h;
    return 'left:' + (x / G.W * 100).toFixed(2) + '%;top:' + (y / G.H * 100).toFixed(2) + '%';
  }
  function paint() {
    if (!data) return;
    var html = '';
    dots = data.places.filter(function (p) { return p.lat != null && p.lon != null; });
    dots.forEach(function (p, i) {
      html += '<button type="button" class="d ' + heat(p).cls + (p === sel ? ' on' : '') + '" data-d="' + i + '" style="' + place(p) + '" aria-label="' + esc(name(p) + ': ' + heat(p).label) + '"><em>' + esc(p.city || name(p)) + '</em></button>';
    });
    box.querySelectorAll('.d').forEach(function (n) { n.remove(); });
    box.insertAdjacentHTML('beforeend', html);
  }
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
    if (b) { var p = dots[+b.getAttribute('data-d')]; select(p === sel ? null : p, false); } else if (sel) select(null, false);
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
