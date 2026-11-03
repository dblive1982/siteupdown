/* Internet speed test. Runs in the browser against Cloudflare's public speed-test servers.
   Nothing about the result leaves the browser except the test traffic itself. */
(function () {
  'use strict';
  var go = document.getElementById('st-go');
  if (!go) return;
  var B = 'https://speed.cloudflare.com';
  var $ = function (id) { return document.getElementById(id); };
  var arc = $('st-arc'), num = $('st-num'), phase = $('st-phase'), err = $('st-err');
  var running = false, cancelled = false, ctrl = null, xhrs = [], bytesUsed = 0;
  var L = 0;
  try { L = arc.getTotalLength(); } catch (e) { L = 424.1; }
  var STOPS = [0, 5, 10, 50, 100, 250, 500, 750, 1000];

  function frac(v) {
    if (v <= 0) return 0;
    if (v >= 1000) return 1;
    for (var i = 1; i < STOPS.length; i++) if (v <= STOPS[i]) return (i - 1 + (v - STOPS[i - 1]) / (STOPS[i] - STOPS[i - 1])) / (STOPS.length - 1);
    return 1;
  }
  function fmt(v) { return v >= 100 ? String(Math.round(v)) : v >= 10 ? v.toFixed(1) : v.toFixed(2); }
  function gauge(v, unit, label) {
    arc.style.strokeDasharray = (frac(v) * L).toFixed(1) + ' ' + L.toFixed(1);
    num.textContent = fmt(v);
    if (unit) $('st-unit').textContent = unit;
    if (label) phase.textContent = label;
  }
  function tile(id, text, on) { var t = $(id); t.textContent = text; t.parentNode.classList.toggle('on', !!on); }
  function showErr(m) { err.textContent = m; err.hidden = !m; }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  // ---- ping and jitter: time many tiny requests, ignore the first (it pays for the connection set-up)
  function ping(n) {
    var times = [], i = 0;
    function one() {
      if (cancelled) return Promise.resolve();
      var s = performance.now();
      return fetch(B + '/__down?bytes=0&r=' + Math.random(), { cache: 'no-store', signal: ctrl.signal }).then(function (r) {
        return r.arrayBuffer();
      }).then(function () {
        var d = performance.now() - s;
        if (i++ > 0) { times.push(d); tile('st-ping', Math.round(median(times)) + ' ms', true); gauge(median(times), 'ms', 'Measuring latency'); }
        if (i <= n) return one();
      });
    }
    return one().then(function () {
      if (times.length < 3) throw new Error('ping');
      var sorted = times.slice().sort(function (a, b) { return a - b; }), jit = 0;
      for (var k = 1; k < times.length; k++) jit += Math.abs(times[k] - times[k - 1]);
      return { ping: median(times), jitter: jit / (times.length - 1), min: sorted[0] };
    });
  }
  function median(a) { var s = a.slice().sort(function (x, y) { return x - y; }), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }

  // ---- download: several parallel streams of big files, measured after a short warm-up
  function download(ms, live) {
    return new Promise(function (resolve, reject) {
      var t0 = performance.now(), total = 0, mark = 0, base = 0, fails = 0, done = false, WARM = 1200;
      function speed(now) { var from = mark || t0, b = mark ? total - base : total; return b * 8 / 1e6 / Math.max((now - from) / 1000, 0.2); }
      function finish() {
        if (done) return; done = true;
        try { ctrl.abort(); } catch (e) {}
        bytesUsed += total;
        if (!total) return reject(new Error('download'));
        resolve(speed(performance.now()));
      }
      function stream() {
        if (done || cancelled) return;
        fetch(B + '/__down?bytes=25000000&r=' + Math.random(), { cache: 'no-store', signal: ctrl.signal }).then(function (r) {
          if (!r.ok || !r.body) throw new Error('bad');
          var rd = r.body.getReader();
          function pump() {
            return rd.read().then(function (x) {
              if (done) return;
              if (x.done) return stream();
              total += x.value.length;
              var now = performance.now();
              if (!mark && now - t0 > WARM) { mark = now; base = total; }
              if (mark && now - mark > 250) live(speed(now));
              if (now - t0 > ms) return finish();
              return pump();
            });
          }
          return pump();
        }).catch(function () {
          if (cancelled) return finish();
          if (done) return;
          if (++fails > 6) return finish();
          setTimeout(stream, 300);
        });
      }
      for (var i = 0; i < 4; i++) stream();
      setTimeout(finish, ms + 4000);
    });
  }

  // ---- upload: random data posted in parallel, progress read from the browser
  function payload() {
    var size = 4 * 1024 * 1024, buf = new Uint8Array(size);
    try { for (var o = 0; o < size; o += 65536) crypto.getRandomValues(buf.subarray(o, Math.min(o + 65536, size))); } catch (e) { for (var j = 0; j < size; j += 4) buf[j] = (j * 31) & 255; }
    return new Blob([buf]);
  }
  function upload(ms, live) {
    return new Promise(function (resolve, reject) {
      var blob = payload(), t0 = performance.now(), cur = [0, 0, 0], doneBytes = 0, mark = 0, base = 0, fails = 0, done = false, WARM = 1200;
      function sum() { return doneBytes + cur[0] + cur[1] + cur[2]; }
      function speed(now) { var from = mark || t0, b = mark ? sum() - base : sum(); return b * 8 / 1e6 / Math.max((now - from) / 1000, 0.2); }
      function finish() {
        if (done) return; done = true;
        xhrs.forEach(function (x) { try { x.abort(); } catch (e) {} });
        xhrs = [];
        var t = sum(); bytesUsed += t;
        if (!t) return reject(new Error('upload'));
        resolve(speed(performance.now()));
      }
      function start(i) {
        if (done || cancelled) return;
        var x = new XMLHttpRequest(); xhrs.push(x);
        x.open('POST', B + '/__up?r=' + Math.random(), true);
        x.upload.onprogress = function (e) {
          cur[i] = e.loaded;
          var now = performance.now();
          if (!mark && now - t0 > WARM) { mark = now; base = sum(); }
          if (mark && now - mark > 250) live(speed(now));
          if (now - t0 > ms) finish();
        };
        x.onload = function () { doneBytes += blob.size; cur[i] = 0; start(i); };
        x.onerror = x.ontimeout = function () { cur[i] = 0; if (done || cancelled) return; if (++fails > 6) return finish(); setTimeout(function () { start(i); }, 300); };
        x.onabort = function () { if (cancelled) finish(); };
        x.timeout = 20000;
        x.send(blob);
      }
      for (var i = 0; i < 3; i++) start(i);
      setTimeout(finish, ms + 4000);
    });
  }

  // ---- what the numbers are good for
  var ROWS = [
    ['Video calls', function (r) { return r.down >= 5 && r.up >= 2 && r.ping < 150 ? 2 : r.down >= 2 && r.up >= 1 ? 1 : 0; }],
    ['HD streaming', function (r) { return r.down >= 10 ? 2 : r.down >= 5 ? 1 : 0; }],
    ['4K streaming', function (r) { return r.down >= 25 ? 2 : r.down >= 15 ? 1 : 0; }],
    ['Online gaming', function (r) { return r.ping < 50 && r.jitter < 20 ? 2 : r.ping < 100 && r.jitter < 40 ? 1 : 0; }],
    ['Large downloads', function (r) { return r.down >= 100 ? 2 : r.down >= 30 ? 1 : 0; }]
  ];
  var WORDS = ['Struggles', 'Works', 'Great'];
  function good(r) {
    $('st-good').innerHTML = '<h2>What your connection is good for</h2><div class="st-use">' + ROWS.map(function (x) {
      var s = x[1](r); return '<div class="st-u s' + s + '"><span>' + x[0] + '</span><b>' + WORDS[s] + '</b></div>';
    }).join('') + '</div>';
    $('st-good').hidden = false;
  }

  function meta() {
    fetch(B + '/meta', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (m) {
      var bits = [];
      if (m.asOrganization) bits.push(String(m.asOrganization));
      var place = [m.city, m.country].filter(Boolean).join(', ');
      if (place) bits.push(place);
      var s = bits.join(' · ');
      if (s) $('st-conn').textContent = 'Your connection: ' + s + (m.colo ? ' · tested against the ' + m.colo + ' server' : '');
    }).catch(function () {});
  }

  function reset() {
    ['st-dl', 'st-ul', 'st-ping', 'st-jit'].forEach(function (id) { tile(id, '–', false); });
    $('st-good').hidden = true; $('st-used').textContent = ''; showErr('');
    gauge(0, 'Mbps', 'Getting ready');
  }
  function end(label) {
    running = false; ctrl = null;
    go.disabled = false; go.querySelector('span').textContent = label || 'Test again';
    go.classList.remove('stop');
  }

  function run() {
    if (running) { cancelled = true; phase.textContent = 'Stopping…'; try { ctrl.abort(); } catch (e) {} xhrs.forEach(function (x) { try { x.abort(); } catch (e) {} }); return; }
    running = true; cancelled = false; bytesUsed = 0; ctrl = new AbortController(); xhrs = [];
    go.querySelector('span').textContent = 'Stop test'; go.classList.add('stop');
    reset(); meta();
    var R = { down: 0, up: 0, ping: 0, jitter: 0 };
    ping(12).then(function (p) {
      R.ping = p.ping; R.jitter = p.jitter;
      tile('st-ping', Math.round(p.ping) + ' ms', true); tile('st-jit', Math.round(p.jitter * 10) / 10 + ' ms', true);
      if (cancelled) throw new Error('stop');
      ctrl = new AbortController();
      gauge(0, 'Mbps', 'Testing download');
      return download(8000, function (v) { gauge(v, 'Mbps', 'Testing download'); tile('st-dl', fmt(v) + ' Mbps', true); });
    }).then(function (d) {
      R.down = d; gauge(d, 'Mbps', 'Download'); tile('st-dl', fmt(d) + ' Mbps', true);
      if (cancelled) throw new Error('stop');
      ctrl = new AbortController();
      return sleep(500).then(function () {
        gauge(0, 'Mbps', 'Testing upload');
        return upload(8000, function (v) { gauge(v, 'Mbps', 'Testing upload'); tile('st-ul', fmt(v) + ' Mbps', true); });
      });
    }).then(function (u) {
      R.up = u; gauge(u, 'Mbps', 'Upload'); tile('st-ul', fmt(u) + ' Mbps', true);
      gauge(R.down, 'Mbps', 'Done: download speed');
      good(R);
      $('st-used').textContent = 'This test used about ' + Math.max(1, Math.round(bytesUsed / 1048576)) + ' MB of data.';
      try { localStorage.setItem('sud-speed', JSON.stringify({ d: R.down, u: R.up, p: R.ping, t: Date.now() })); } catch (e) {}
      end('Test again');
    }).catch(function (e) {
      if (cancelled || (e && e.message === 'stop')) { gauge(0, 'Mbps', 'Stopped'); return end('Start again'); }
      gauge(0, 'Mbps', 'Could not finish');
      showErr('The test could not reach the speed servers. A VPN, ad blocker or strict network may be blocking them. Try again, or turn those off for this page.');
      end('Try again');
    });
  }
  go.addEventListener('click', run);
  gauge(0, 'Mbps', 'Ready');
  try {
    var last = JSON.parse(localStorage.getItem('sud-speed') || 'null');
    if (last && last.d) $('st-last').textContent = 'Your last test on this device: ' + fmt(last.d) + ' Mbps down, ' + fmt(last.u) + ' Mbps up, ' + Math.round(last.p) + ' ms ping.';
  } catch (e) {}
})();
