(function () {
  'use strict';
  var A = document.getElementById('cmp-a'), B = document.getElementById('cmp-b'), out = document.getElementById('cmp-out');
  if (!A || !B || !out) return;
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function pct(v) { return v == null ? '–' : (v >= 99.995 ? '100' : v.toFixed(2).replace(/0$/, '').replace(/\.0$/, '')) + '%'; }
  function dur(sec) { var m = Math.round(sec / 60); if (!sec) return 'none'; if (m < 2) return 'under 2 min'; if (m < 90) return m + ' min'; var h = Math.floor(m / 60); return h < 48 ? h + ' h' : Math.floor(h / 24) + ' days'; }
  function get(h) { return fetch('/api/sitestats.php?host=' + encodeURIComponent(h)).then(function (r) { return r.json(); }); }
  var qs = new URLSearchParams(location.search);
  if (qs.get('a')) A.value = qs.get('a'); if (qs.get('b')) B.value = qs.get('b');
  var GR = { A: 5, B: 4, C: 3, D: 2, F: 1 };
  function row(label, a, b, fa, fb, lowBetter) {
    var w = '';
    if (a != null && b != null && a !== b) w = (lowBetter ? a < b : a > b) ? 'a' : 'b';
    return '<tr><th scope="row">' + label + '</th><td class="' + (w === 'a' ? 'win' : '') + '">' + fa + '</td><td class="' + (w === 'b' ? 'win' : '') + '">' + fb + '</td></tr>';
  }
  function draw() {
    var a = A.value, b = B.value;
    try { history.replaceState(null, '', '/compare' + (a || b ? '?' + (a ? 'a=' + encodeURIComponent(a) : '') + (a && b ? '&' : '') + (b ? 'b=' + encodeURIComponent(b) : '') : '')); } catch (e) {}
    if (!a || !b) { out.innerHTML = '<p class="note">Choose two sites above.</p>'; return; }
    if (a === b) { out.innerHTML = '<p class="note">Pick two different sites to compare.</p>'; return; }
    out.innerHTML = '<p class="note">Loading&hellip;</p>';
    Promise.all([get(a), get(b)]).then(function (r) {
      var x = r[0], y = r[1];
      if (!x || x.error || !y || y.error) { out.innerHTML = '<p class="note">We could not load one of those just now.</p>'; return; }
      var g = function (d) { return d.grade ? '<span class="dp-grade sm g' + d.grade + '">' + d.grade + '</span>' : '<span class="note">Not enough history yet</span>'; };
      var t = '<div class="card"><div class="rt-wrap"><table class="rt cmp-t"><thead><tr><th></th><th><a href="' + esc(x.page) + '">' + esc(x.name) + '</a></th><th><a href="' + esc(y.page) + '">' + esc(y.name) + '</a></th></tr></thead><tbody>';
      t += row('Reliability grade', x.grade ? GR[x.grade] : null, y.grade ? GR[y.grade] : null, g(x), g(y), false);
      t += row('Uptime, 30 days', x.u30.pct, y.u30.pct, pct(x.u30.pct), pct(y.u30.pct), false);
      t += row('Uptime, 7 days', x.u7.pct, y.u7.pct, pct(x.u7.pct), pct(y.u7.pct), false);
      t += row('Outages, 30 days', x.u30.outages, y.u30.outages, String(x.u30.outages), String(y.u30.outages), true);
      t += row('Time down, 30 days', x.u30.down, y.u30.down, dur(x.u30.down), dur(y.u30.down), true);
      t += row('Average response', x.u30.avg, y.u30.avg, x.u30.avg ? x.u30.avg + ' ms' : '–', y.u30.avg ? y.u30.avg + ' ms' : '–', true);
      t += '<tr><th scope="row">Runs on</th><td>' + esc(x.provider || 'Not detected') + '</td><td>' + esc(y.provider || 'Not detected') + '</td></tr>';
      t += '</tbody></table></div></div>';
      var v = '';
      if (x.u30.pct != null && y.u30.pct != null && x.u30.checks >= 150 && y.u30.checks >= 150) {
        if (Math.abs(x.u30.pct - y.u30.pct) < 0.01) v = '<p class="lead">' + esc(x.name) + ' and ' + esc(y.name) + ' have been about equally reliable over the last 30 days.</p>';
        else { var w = x.u30.pct > y.u30.pct ? x : y, l = w === x ? y : x; v = '<p class="lead">' + esc(w.name) + ' has been more reliable over the last 30 days (' + pct(w.u30.pct) + ' uptime against ' + pct(l.u30.pct) + ').' + (w.u30.avg && l.u30.avg ? ' On speed, ' + esc((x.u30.avg <= y.u30.avg ? x : y).name) + ' answers faster on average.' : '') + '</p>'; }
      }
      out.innerHTML = v + t;
    }).catch(function () { out.innerHTML = '<p class="note">We could not load that just now.</p>'; });
  }
  A.addEventListener('change', draw); B.addEventListener('change', draw);
  draw();
})();
