/* Global heat map: how the sites we watch look from each of our worldwide probe places. */
(function () {
  'use strict';
  var svg = document.getElementById('hm-svg'), M = window.SUD_MAP;
  if (!svg || !M) return;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
  var data = null, layer = 'reach';
  var Wd = 1000, Hd = Math.round(Wd * 142 / 360 * 10) / 10, cell = Wd * M.cell / 360, sz = cell * 0.72, o = (cell - sz) / 2, land = '';
  M.runs.forEach(function (runs, r) { runs.forEach(function (run) { for (var c = run[0]; c < run[0] + run[1]; c++) land += 'M' + (c * cell + o).toFixed(1) + ' ' + (r * cell + o).toFixed(1) + 'h' + sz.toFixed(1) + 'v' + sz.toFixed(1) + 'h-' + sz.toFixed(1) + 'z'; });
  });
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
  function draw() {
    if (!data) return;
    var glow = '', dots = '';
    data.places.forEach(function (p) {
      if (p.lat == null || p.lon == null) return;
      var x = ((p.lon + 180) / 360 * Wd).toFixed(1), y = ((84 - p.lat) / 142 * Hd).toFixed(1), h = heat(p);
      glow += '<circle class="hm-glow ' + h.cls + '" cx="' + x + '" cy="' + y + '" r="62"/>';
      dots += '<g role="img" aria-label="' + esc(name(p) + ': ' + h.label) + '"><title>' + esc(name(p) + ': ' + h.label) + '</title><circle class="mk-hit" cx="' + x + '" cy="' + y + '" r="22"/><circle class="hm-dot ' + h.cls + '" cx="' + x + '" cy="' + y + '" r="6"/></g>';
    });
    svg.setAttribute('viewBox', '0 0 ' + Wd + ' ' + Hd);
    svg.innerHTML = '<defs><filter id="hm-blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter></defs><path class="map-land" d="' + land + '"/><g filter="url(#hm-blur)">' + glow + '</g>' + dots;
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
  fetch('/api/heatmap.php').then(function (r) { return r.json(); }).then(function (j) {
    if (!j.places || !j.places.length) { $('hm-sum').textContent = 'The first worldwide results are still being collected. Please check back soon.'; return; }
    data = j; draw();
    $('hm-sum').textContent = 'Based on the latest worldwide check of ' + j.sites_count + ' websites and apps from ' + j.places.length + ' places. Results from ' + ago(j.newest) + ' back to ' + ago(j.oldest) + '.';
    if (j.unreachable && j.unreachable.length) {
      $('hm-sites').innerHTML = '<h2>Sites not reached everywhere right now</h2><div class="hm-list">' + j.unreachable.map(function (s) {
        return '<a href="' + esc(s.page) + '"><span>' + esc(s.name) + '</span><b>' + s.ok + ' of ' + s.total + ' places</b></a>';
      }).join('') + '</div><p class="note">A site that some places cannot reach is not always down. It may block automated checks from those countries.</p>';
    } else $('hm-sites').innerHTML = '<p class="note"><b>Every site we watch was reached from every place in the latest check.</b></p>';
  }).catch(function () { $('hm-sum').textContent = 'Could not load the map just now.'; });
  document.querySelectorAll('[data-hm]').forEach(function (b) {
    b.addEventListener('click', function () {
      layer = b.getAttribute('data-hm');
      document.querySelectorAll('[data-hm]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      draw();
    });
  });
})();
