/* Game ping test: times your connection to cloud regions that many online games and game services run in. Runs in your browser. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var REGIONS = [
    ['eu-west-2', 'London', 'Europe'], ['eu-west-1', 'Dublin', 'Europe'], ['eu-west-3', 'Paris', 'Europe'], ['eu-central-1', 'Frankfurt', 'Europe'], ['eu-north-1', 'Stockholm', 'Europe'],
    ['us-east-1', 'N. Virginia', 'US East'], ['us-east-2', 'Ohio', 'US East'], ['us-west-1', 'California', 'US West'], ['us-west-2', 'Oregon', 'US West'], ['ca-central-1', 'Montreal', 'Canada'],
    ['sa-east-1', 'São Paulo', 'South America'], ['ap-south-1', 'Mumbai', 'India'], ['ap-southeast-1', 'Singapore', 'Southeast Asia'], ['ap-northeast-1', 'Tokyo', 'Japan'],
    ['ap-northeast-2', 'Seoul', 'South Korea'], ['ap-southeast-2', 'Sydney', 'Australia'], ['af-south-1', 'Cape Town', 'Africa']
  ];
  var res = {}, running = false;
  function rate(ms) { return ms < 75 ? ['up', 'Great'] : ms < 130 ? ['slow', 'Works'] : ['down', 'Laggy']; }
  function url(r) { return 'https://dynamodb.' + r + '.amazonaws.com/ping?t=' + Date.now() + Math.random().toString(36).slice(2, 6); }
  function one(r) {
    var t0 = performance.now();
    return fetch(url(r), { mode: 'no-cors', cache: 'no-store' }).then(function () { return performance.now() - t0; });
  }
  function measure(reg) {
    var s = [];
    return one(reg).then(function () {            /* first request pays for the secure connection, so it is thrown away */
      var chain = Promise.resolve();
      for (var i = 0; i < 5; i++) chain = chain.then(function () { return one(reg).then(function (ms) { s.push(ms); }); });
      return chain;
    }).then(function () {
      s.sort(function (a, b) { return a - b; });
      return { ms: Math.round(s[0]), mid: Math.round(s[Math.floor(s.length / 2)]), jit: Math.round(s[s.length - 1] - s[0]) };
    }).catch(function () { return null; });
  }
  function draw() {
    var done = REGIONS.filter(function (r) { return res[r[0]] !== undefined; }), ok = done.filter(function (r) { return res[r[0]]; });
    var rows = REGIONS.slice().sort(function (a, b) {
      var x = res[a[0]], y = res[b[0]]; if (x && y) return x.ms - y.ms; if (x) return -1; if (y) return 1; return 0;
    });
    $('gp-rows').innerHTML = rows.map(function (r) {
      var v = res[r[0]], c = '';
      if (v === undefined) c = '<td data-l="Ping"><span class="note">' + (running ? 'Testing…' : '') + '</span></td><td data-l="Rating"></td>';
      else if (v === null) c = '<td data-l="Ping"><span class="note">No answer</span></td><td data-l="Rating"></td>';
      else { var q = rate(v.ms); c = '<td data-l="Ping"><b>' + v.ms + ' ms</b><small class="gp-st">' + (v.jit < 15 ? 'Steady' : v.jit < 40 ? 'A little uneven' : 'Uneven') + '</small></td><td data-l="Rating"><span class="sp-pill ' + q[0] + '">' + q[1] + '</span></td>'; }
      return '<tr><td data-l="Region">' + esc(r[1]) + '<small class="gp-st">' + esc(r[2]) + '</small></td>' + c + '</tr>';
    }).join('');
    $('gp-table').hidden = false;
    if (ok.length) {
      var best = rows[0], b = res[best[0]];
      $('gp-best').innerHTML = '<b>Closest region: ' + esc(best[1]) + ' &middot; ' + b.ms + ' ms</b><span>' + (rate(b.ms)[1] === 'Great' ? 'That is a good result for most online games.' : rate(b.ms)[1] === 'Works' ? 'Fine for most games, but fast competitive games will feel a little behind.' : 'This is high. Try a cable, close other downloads and turn off any VPN, then test again.') + '</span>';
      $('gp-best').hidden = false;
    }
  }
  function run() {
    if (running) return; running = true; res = {};
    $('gp-go').disabled = true; $('gp-go').firstElementChild.textContent = 'Testing…'; $('gp-best').hidden = true; $('gp-err').hidden = true;
    draw();
    var queue = REGIONS.slice(), active = 0, total = queue.length;
    (function next() {
      while (active < 4 && queue.length) {
        (function (reg) {
          active++;
          measure(reg[0]).then(function (m) { res[reg[0]] = m; draw(); }).then(function () { active--; if (!queue.length && active === 0) finish(); else next(); });
        })(queue.shift());
      }
    })();
    function finish() {
      running = false; $('gp-go').disabled = false; $('gp-go').firstElementChild.textContent = 'Test again'; draw();
      if (!REGIONS.some(function (r) { return res[r[0]]; })) { $('gp-err').textContent = 'No region answered. Check your connection, and make sure an ad blocker or VPN is not stopping the test.'; $('gp-err').hidden = false; }
    }
  }
  $('gp-go').addEventListener('click', run);
})();
