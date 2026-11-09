(function () {
  'use strict';
  var out = document.getElementById('rp-out'); if (!out) return;
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function dur(sec) { var m = Math.round(sec / 60); if (!sec) return 'none'; if (m < 2) return 'under 2 min'; if (m < 90) return m + ' min'; var h = Math.floor(m / 60); return h < 48 ? h + ' h ' + (m % 60) + ' min' : Math.floor(h / 24) + ' days'; }
  function pct(v) { return v == null ? '–' : (v >= 99.995 ? '100' : v.toFixed(2).replace(/0$/, '').replace(/\.0$/, '')) + '%'; }
  var host = (new URLSearchParams(location.search).get('host') || '').toLowerCase();
  if (!host) { out.innerHTML = '<h1>Site report</h1><p>Open this page from a site\'s status page, using “Printable report”.</p>'; return; }
  fetch('/api/sitestats.php?host=' + encodeURIComponent(host)).then(function (r) { return r.json(); }).then(function (d) {
    if (!d || d.error) { out.innerHTML = '<h1>Site report</h1><p>' + esc(d && d.error || 'We could not load that report.') + '</p>'; return; }
    document.title = 'Reliability report: ' + d.name + ' | siteupdown.com';
    var G = { A: 'Excellent', B: 'Very good', C: 'Good', D: 'Patchy', F: 'Poor' }, t = d.timing;
    var h = '<h1 style="margin:14px 0 4px">Reliability report: ' + esc(d.name) + '</h1><p class="note" style="margin-top:0">' + esc(d.host) + ' &middot; generated ' + new Date().toLocaleString([], { dateStyle: 'long', timeStyle: 'short' }) + ' &middot; from siteupdown.com checks</p>';
    h += '<div class="card rp-sum"><div class="dp-top">' + (d.grade ? '<div class="dp-grade g' + d.grade + '">' + d.grade + '</div><div><b>' + G[d.grade] + ' reliability</b></div>' : '<div><b>Not enough history to grade yet</b></div>') + '</div>';
    h += '<table class="rt"><tbody><tr><th>Uptime, 30 days</th><td>' + pct(d.u30.pct) + '</td></tr><tr><th>Uptime, 7 days</th><td>' + pct(d.u7.pct) + '</td></tr><tr><th>Outages, 30 days</th><td>' + d.u30.outages + '</td></tr><tr><th>Time down, 30 days</th><td>' + dur(d.u30.down) + '</td></tr><tr><th>Average response</th><td>' + (d.u30.avg ? d.u30.avg + ' ms' : '–') + '</td></tr>' + (t ? '<tr><th>Response breakdown (24 h average)</th><td>DNS ' + t.dns + ' ms, connect ' + t.conn + ' ms, secure handshake ' + t.tls + ' ms, waiting ' + t.ttfb + ' ms</td></tr>' : '') + (d.provider ? '<tr><th>Appears to run on</th><td>' + esc(d.provider) + '</td></tr>' : '') + '</tbody></table></div>';
    h += '<h2>Outages, last 90 days</h2>' + (d.outages && d.outages.length ? '<table class="rt"><thead><tr><th>Started</th><th>Length</th></tr></thead><tbody>' + d.outages.map(function (o) { return '<tr><td>' + new Date(o.started).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) + '</td><td>' + (o.ended ? dur(o.seconds) : 'Ongoing') + '</td></tr>'; }).join('') + '</tbody></table>' : '<p>No outages recorded.</p>');
    h += '<p class="note">Measured from siteupdown.com\'s own server. Uptime counts our own checks only, a site that blocks automated checks is not marked down for it, and these figures are a guide, not a service guarantee or an official record.</p>';
    h += '<p class="no-print"><button type="button" class="btn" id="rp-print"><span>Print or save as PDF</span></button> <a class="btn ghost" href="/api/export.php?host=' + encodeURIComponent(d.host) + '&days=30" download><span>Download CSV</span></a> <a class="btn ghost" href="' + esc(d.page) + '"><span>Back to ' + esc(d.name) + '</span></a></p>';
    out.innerHTML = h; document.getElementById('rp-print').onclick = function () { window.print(); };
  }).catch(function () { out.innerHTML = '<h1>Site report</h1><p>We could not load that report just now.</p>'; });
})();
