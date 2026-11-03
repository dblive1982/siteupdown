/* Uptime and SLA calculator: all in the browser, nothing is sent anywhere. */
(function () {
  'use strict';
  var pct = document.getElementById('sla-pct'), out = document.getElementById('sla-out'), mins = document.getElementById('sla-min'), per = document.getElementById('sla-per'), out2 = document.getElementById('sla-out2'), tab = document.getElementById('sla-tab');
  if (!pct) return;
  function fmt(m) {
    if (m < 1 / 60 * 0.5) return 'under a second';
    if (m < 1) return Math.round(m * 60) + ' seconds';
    if (m < 90) return (Math.round(m * 10) / 10) + ' minutes';
    var h = Math.floor(m / 60), r = Math.round(m - h * 60);
    if (h < 48) return h + ' h ' + r + ' min';
    var d = Math.floor(h / 24); return d + ' days ' + (h - d * 24) + ' h';
  }
  function num(v) { v = parseFloat(String(v).replace(',', '.').replace('%', '')); return isFinite(v) ? v : null; }
  var P = [['day', 1440], ['week', 10080], ['month (30 days)', 43200], ['year', 525600]];
  function one() {
    var v = num(pct.value);
    if (v === null || v < 0 || v > 100) { out.innerHTML = '<p class="note">Enter a number between 0 and 100.</p>'; return; }
    out.innerHTML = '<dl class="facts">' + P.map(function (p) { return '<div><dt>Allowed downtime per ' + p[0] + '</dt><dd>' + fmt(p[1] * (100 - v) / 100) + '</dd></div>'; }).join('') + '</dl>';
  }
  function two() {
    var m = num(mins.value), t = parseFloat(per.value);
    if (m === null || m < 0) { out2.innerHTML = ''; return; }
    var u = Math.max(0, 100 - m / t * 100);
    out2.innerHTML = '<p><b>' + (Math.round(u * 1000) / 1000) + '% uptime</b> over that period.</p>';
  }
  [99, 99.5, 99.9, 99.95, 99.99, 99.999].forEach(function (v) {
    tab.insertAdjacentHTML('beforeend', '<tr><td data-l="Uptime"><b>' + v + '%</b></td>' + [1440, 43200, 525600].map(function (t, i) { return '<td data-l="' + ['Per day', 'Per month (30 days)', 'Per year'][i] + '">' + fmt(t * (100 - v) / 100) + '</td>'; }).join('') + '</tr>');
  });
  pct.addEventListener('input', one); mins.addEventListener('input', two); per.addEventListener('change', two);
  one();
})();
