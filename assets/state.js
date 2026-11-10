(function () {
  'use strict';
  var out = document.getElementById('st-out'); if (!out) return;
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function dur(sec) { var m = Math.round(sec / 60); if (m < 2) return 'under 2 min'; if (m < 90) return m + ' min'; var h = Math.floor(m / 60); return h < 48 ? h + ' h' + (m % 60 ? ' ' + (m % 60) + ' min' : '') : Math.floor(h / 24) + ' days'; }
  function pct(v) { return (v >= 99.995 ? '100' : v.toFixed(2).replace(/0$/, '').replace(/\.0$/, '')) + '%'; }
  function cap(c) { return c.charAt(0).toUpperCase() + c.slice(1); }
  function name(o) { return o.page ? '<a href="' + esc(o.page) + '">' + esc(o.name) + '</a>' : esc(o.name); }
  function fd(d) { return new Date(d + 'T12:00:00Z').toLocaleDateString([], { day: 'numeric', month: 'long' }); }
  function bars(rows) { var mx = Math.max.apply(null, rows.map(function (r) { return r.n; })) || 1; return '<ul class="ins-bars">' + rows.map(function (r) { return '<li><span class="ib-l">' + esc(r.l) + '</span><span class="ib-b"><i style="width:' + Math.max(4, Math.round(100 * r.n / mx)) + '%"></i></span><span class="ib-n">' + esc(r.t) + '</span></li>'; }).join('') + '</ul>'; }
  Promise.all([fetch('/api/weekly.php').then(function (r) { return r.json(); }), fetch('/api/insights.php').then(function (r) { return r.json(); }).catch(function () { return {}; })]).then(function (r) {
    var d = r[0], ins = r[1] || {}; if (!d || d.error) throw 0;
    var h = '', delta = d.outages - d.outages_prev;
    var lead = d.outages + (d.outages === 1 ? ' outage' : ' outages') + ' across the sites we watch in the last 7 days' + (d.outages_prev ? (delta === 0 ? ', the same as the week before' : ', ' + Math.abs(delta) + (delta > 0 ? ' more' : ' fewer') + ' than the week before') : '') + '.';
    document.getElementById('st-lead').textContent = 'Week to ' + fd(d.to) + '. ' + lead;
    var dl = function (cur, prev, unit) { if (!prev && !cur) return ''; var x = cur - prev; return '<em class="' + (x > 0 ? 'dn' : x < 0 ? 'upv' : '') + '">' + (x === 0 ? 'Same as last week' : (x > 0 ? '\u25B2 ' : '\u25BC ') + Math.abs(x) + ' ' + (x > 0 ? 'more' : 'fewer') + ' than last week') + '</em>'; };
    var pf = d.tracked ? Math.round(100 * (d.perfect || 0) / d.tracked) : 0;
    h += '<div class="ins-stats"><div><b>' + d.outages + '</b><span>outages detected</span>' + dl(d.outages, d.outages_prev) + '</div><div><b>' + (d.perfect || 0) + '</b><span>of ' + (d.tracked || 0) + ' sites had none</span><em>' + pf + '% had a perfect week</em></div><div><b>' + (d.down_s ? dur(d.down_s) : '0') + '</b><span>combined time down</span>' + (d.outages ? '<em>About ' + dur(Math.round(d.down_s / d.outages)) + ' per outage</em>' : '') + '</div><div><b>' + (d.reports || 0) + '</b><span>problem reports from visitors</span></div></div>';
    if (d.longest) h += '<h2>Longest outage</h2><p>' + name(d.longest) + ' was down for about <b>' + dur(d.longest.seconds) + '</b>, starting ' + new Date(d.longest.started).toLocaleString([], { weekday: 'long', hour: '2-digit', minute: '2-digit' }) + '.</p>';
    if (d.worst_day) h += '<p>The roughest day was <b>' + fd(d.worst_day.day) + '</b>, with ' + d.worst_day.n + ' outages.</p>';
    function list(arr, fn) { return '<ul class="ro-list">' + arr.map(function (o) { return '<li class="' + fn(o)[1] + '"><span class="ro-name">' + name(o) + '</span><span class="ro-st">' + fn(o)[0] + '</span></li>'; }).join('') + '</ul>'; }
    if (d.best && d.best.length) h += '<h2>Most reliable this week</h2>' + list(d.best, function (o) { return [pct(o.pct) + ' uptime', 'ro-up']; });
    if (d.worst && d.worst.length) h += '<h2>Least reliable this week</h2>' + list(d.worst, function (o) { return [pct(o.pct) + ' uptime, ' + o.outages + (o.outages === 1 ? ' outage' : ' outages'), 'ro-end']; });
    if (d.cats && d.cats.length) h += '<h2>How each category did</h2>' + window.SUD.catChart(d.cats);
    if (ins.cascade && ins.cascade.length) h += '<h2>Shared provider trouble right now</h2>' + ins.cascade.map(function (c) { return '<p><b>' + esc(c.provider) + '</b>: ' + c.count + ' sites behind it look down or slow at the moment (' + c.sites.map(function (s) { return esc(s.name); }).join(', ') + '). When one provider has trouble, many unrelated sites can be affected together.</p>'; }).join('');
    if (ins.cal) h += '<h2>Outage calendar, last 13 weeks</h2>' + window.SUD.calendar(ins.cal);
    h += '<p class="note">Figures refresh about every 10 minutes. An outage is counted only after it is confirmed from more than one location, so short blips and blocked checks are not counted. <a href="/how-we-check">How we check</a> &middot; <a href="/editorial-policy">Editorial policy</a></p>';
    out.innerHTML = h;
  }).catch(function () { out.innerHTML = '<p class="note">We could not load the summary just now.</p>'; });
})();
