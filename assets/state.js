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
    h += '<div class="ins-stats"><div><b>' + d.outages + '</b><span>outages detected</span></div><div><b>' + (d.perfect || 0) + '</b><span>of ' + (d.tracked || 0) + ' sites had none</span></div><div><b>' + (d.down_s ? dur(d.down_s) : '0') + '</b><span>combined time down</span></div><div><b>' + (d.reports || 0) + '</b><span>problem reports from visitors</span></div></div>';
    if (d.longest) h += '<h2>Longest outage</h2><p>' + name(d.longest) + ' was down for about <b>' + dur(d.longest.seconds) + '</b>, starting ' + new Date(d.longest.started).toLocaleString([], { weekday: 'long', hour: '2-digit', minute: '2-digit' }) + '.</p>';
    if (d.worst_day) h += '<p>The roughest day was <b>' + fd(d.worst_day.day) + '</b>, with ' + d.worst_day.n + ' outages.</p>';
    function list(arr, fn) { return '<ul class="ro-list">' + arr.map(function (o) { return '<li class="' + fn(o)[1] + '"><span class="ro-name">' + name(o) + '</span><span class="ro-st">' + fn(o)[0] + '</span></li>'; }).join('') + '</ul>'; }
    if (d.best && d.best.length) h += '<h2>Most reliable this week</h2>' + list(d.best, function (o) { return [pct(o.pct) + ' uptime', 'ro-up']; });
    if (d.worst && d.worst.length) h += '<h2>Least reliable this week</h2>' + list(d.worst, function (o) { return [pct(o.pct) + ' uptime, ' + o.outages + (o.outages === 1 ? ' outage' : ' outages'), 'ro-end']; });
    if (d.cats && d.cats.length) h += '<h2>How each category did</h2><p class="note">Average uptime across the sites in each category.</p>' + bars(d.cats.map(function (c) { return { l: cap(c.cat), n: Math.max(0, c.pct - 95), t: pct(c.pct) }; }));
    if (ins.cascade && ins.cascade.length) h += '<h2>Shared provider trouble right now</h2>' + ins.cascade.map(function (c) { return '<p><b>' + esc(c.provider) + '</b>: ' + c.count + ' sites behind it look down or slow at the moment (' + c.sites.map(function (s) { return esc(s.name); }).join(', ') + '). When one provider has trouble, many unrelated sites can be affected together.</p>'; }).join('');
    if (ins.cal) {
      var cl = ins.cal, mx = Math.max.apply(null, cl.map(function (x) { return x.n; })) || 1, tot = cl.reduce(function (a, x) { return a + x.n; }, 0), act = cl.filter(function (x) { return x.n; }).length, avg = tot / (cl.length || 1);
      var top = cl.filter(function (x) { return x.n === mx && x.n; })[0];
      var long = function (d) { return new Date(d + 'T12:00:00Z').toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }); };
      h += '<h2>Outage calendar, last 13 weeks</h2><p class="note">Each square is one day, oldest on the left and newest on the right, with each column a week. Darker means more outages started that day. Tap or hover a square for the date and the number.</p>';
      h += '<p>' + (tot ? '<b>' + tot + '</b> outage' + (tot === 1 ? '' : 's') + ' in the last 13 weeks, on <b>' + act + '</b> different day' + (act === 1 ? '' : 's') + '. Busiest day: <b>' + long(top.day) + '</b> with ' + mx + '.' : 'No outages in the last 13 weeks.') + '</p>';
      var wd = function (d) { return new Date(d + 'T12:00:00Z').getUTCDay(); }, mo = function (d) { return new Date(d + 'T12:00:00Z').toLocaleDateString([], { month: 'short', timeZone: 'UTC' }); };
      var dn = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], nw = Math.ceil(cl.length / 7), g = '<span></span>', pm = '';
      for (var ri = 0; ri < 7; ri++) g += '<span class="cal-d">' + (ri < cl.length ? dn[wd(cl[ri].day)] : '') + '</span>';
      for (var ci = 0; ci < cl.length; ci += 7) {
        var m = mo(cl[ci].day);
        g += '<span class="cal-m">' + (m !== pm || ci === 0 ? new Date(cl[ci].day + 'T12:00:00Z').getUTCDate() + ' ' + m : '') + '</span>'; pm = m;
        for (var k = ci; k < ci + 7; k++) {
          var x = cl[k];
          if (!x) { g += '<b></b>'; continue; }
          var l = x.n ? Math.min(4, 1 + Math.floor(3 * x.n / mx)) : 0;
          var tip = long(x.day) + ': ' + (x.n ? x.n + ' outage' + (x.n === 1 ? '' : 's') + ' started' + (x.n > avg * 1.5 ? ', busier than usual' : '') + '.' : 'no outages started.');
          g += '<i class="c' + l + ' has-tip" tabindex="0" data-tip="' + esc(tip) + '"></i>';
        }
      }
      h += '<p class="note"><b>' + fd(cl[0].day) + '</b> to <b>' + fd(cl[cl.length - 1].day) + '</b>. Dates run along the top and weekdays down the side.</p>';
      h += '<div class="cal cal-full" style="--w:' + nw + '" role="img" aria-label="Outages per day over 13 weeks">' + g + '</div>';
      h += '<p class="cal-key" aria-hidden="true"><span>Fewer</span><i></i><i class="c1"></i><i class="c2"></i><i class="c3"></i><i class="c4"></i><span>More</span></p>';
    }
    out.innerHTML = h;
  }).catch(function () { out.innerHTML = '<p class="note">We could not load the summary just now.</p>'; });
})();
