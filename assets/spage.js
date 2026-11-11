/* Public customer status page at /p/<slug>. Shows the sites the owner chose, with 90 days of history. */
(function () {
  'use strict';
  var S = window.SUD, root = document.getElementById('spg'); if (!S || !root) return;
  var esc = S.esc, m = location.pathname.match(/\/p\/([a-z0-9-]+)/i), slug = m ? m[1].toLowerCase() : '';
  var LABEL = { up: 'Operational', down: 'Down', unclear: 'Unclear', unknown: 'Waiting for first check' };
  function bar(v) { return '<i class="' + (v == null ? '' : v >= 99.9 ? 'g' : v >= 99 ? 'a' : 'o') + '" title="' + (v == null ? 'No data' : v + '% up') + '"></i>'; }
  function draw(j) {
    document.title = j.title + ' status';
    var head = j.overall === 'up' ? 'All systems operational' : j.overall === 'down' ? (j.down === 1 ? 'One service is down' : j.down + ' services are down') : 'Some services could not be checked';
    var h = '<div class="spg-hero ' + esc(j.overall) + '"><h1>' + esc(j.title) + '</h1><p style="margin:0;font-size:18px;font-weight:700">' + esc(head) + '</p><p class="fine" style="margin:6px 0 0" id="spg-age">Updated just now</p></div>';
    h += j.sites.map(function (s) {
      return '<div class="spg-row"><div class="spg-top"><b>' + esc(s.host) + '</b><span class="spg-st ' + esc(s.state) + '">' + esc(LABEL[s.state] || s.state) + '</span></div>'
        + '<div class="spg-bars" role="img" aria-label="Daily uptime, last 90 days">' + s.bars.map(bar).join('') + '</div><div class="spg-scale"><span>90 days ago</span><span>' + (s.uptime90 != null ? esc(s.uptime90) + '% uptime' : 'No history yet') + '</span><span>Today</span></div></div>';
    }).join('');
    h += '<h2 style="margin-top:28px">Recent incidents</h2>' + (j.incidents.length ? '<ul class="ro-list" style="margin:8px 0">' + j.incidents.map(function (i) {
      return '<li class="' + (i.ended ? 'ro-end' : 'ro-on') + '"><b>' + esc(i.host) + '</b> <span class="ro-st">' + (i.ended ? 'Resolved' : 'Ongoing') + '</span><small>Started ' + esc(S.when(i.started)) + (i.ended ? ', resolved ' + esc(S.when(i.ended)) : '') + '</small></li>';
    }).join('') + '</ul>' : '<p class="note">No incidents in the last 30 days.</p>');
    h += '<p class="fine" style="margin-top:28px">Checked automatically by <a href="https://siteupdown.com/">siteupdown.com</a>. Times in your time zone. This page refreshes by itself.</p>';
    root.innerHTML = h; root.setAttribute('data-at', Date.now());
  }
  function load() {
    fetch('/api/statuspage.php?slug=' + encodeURIComponent(slug)).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'Not found'); return j; }); }).then(draw)
      .catch(function (e) { if (!root.getAttribute('data-at')) root.innerHTML = '<div class="spg-hero unclear"><h1>Status page not found</h1><p style="margin:0">' + esc(e.message) + '</p></div>'; });
  }
  load(); setInterval(function () { if (!document.hidden) load(); }, 30000);
  setInterval(function () { var a = +root.getAttribute('data-at'), el = document.getElementById('spg-age'); if (a && el) { var s = Math.round((Date.now() - a) / 1000); el.textContent = s < 5 ? 'Updated just now' : 'Updated ' + s + ' s ago'; } }, 1000);
})();
