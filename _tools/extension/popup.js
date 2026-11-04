/* siteupdown.com browser extension. Reads the address of the active tab only when the toolbar button is clicked
   (activeTab permission), sends just the website name to siteupdown.com to be checked, and never stores browsing history. */
(function () {
  'use strict';
  var SITE = 'https://siteupdown.com';
  var $ = function (id) { return document.getElementById(id); };
  var host = '', user = null, onList = false, seq = 0;

  function api(path, data) {
    var opt = { credentials: 'include' };
    if (data !== undefined) { opt.method = 'POST'; opt.headers = { 'Content-Type': 'application/json', 'X-SUD': '1' }; opt.body = JSON.stringify(data); }
    return fetch(SITE + '/api/' + path, opt).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) { var e = new Error(j.error || 'Something went wrong. Please try again.'); e.status = r.status; throw e; }
        return j;
      });
    });
  }
  function say(t, err) { var m = $('msg'); m.textContent = t || ''; m.className = 'msg' + (err ? ' err' : ''); }
  function show(v, title, detail) { var r = $('result'); r.setAttribute('data-v', v); $('title').textContent = title; $('detail').textContent = detail || ''; }

  function describe(j) {
    var ms = j.ms != null ? j.ms + ' ms' : '', code = j.http_code ? 'HTTP ' + j.http_code : '';
    if (j.verdict === 'up') return ['up', 'It is up', ['Answered' + (ms ? ' in ' + ms : ''), code && '(' + code + ').'].filter(Boolean).join(' ') + ' If it will not load for you, the problem is probably on your side.'];
    if (j.verdict === 'down') return ['down', j.err === 'dns' ? 'Address not found' : 'It looks down', j.err === 'dns' ? 'We could not find that website address. Check the spelling.' : 'It is not answering properly for us either, so it is down for everyone, not just you.'];
    if (j.verdict === 'timeout') return ['timeout', 'Not responding', 'It took too long to answer. It may be very slow, or down.'];
    return ['inconclusive', 'Cannot tell', 'This site blocks automatic checks, so we cannot confirm. Open the full report for more detail.'];
  }

  function check(h) {
    var mine = ++seq; host = h;
    $('host').textContent = h; show('pending', 'Checking…', ''); say('');
    $('again').disabled = true; $('report').hidden = true;
    $('report').href = SITE + '/?q=' + encodeURIComponent(h);
    return api('quick.php', { address: h }).then(function (j) {
      if (mine !== seq) return;
      var d = describe(j); host = j.host || h; $('host').textContent = host; show(d[0], d[1], d[2]);
      $('report').hidden = false; $('report').href = SITE + '/?q=' + encodeURIComponent(host);
      drawWatch();
    }).catch(function (e) {
      if (mine !== seq) return;
      show('inconclusive', 'Could not check', e.message); say(e.status === 429 ? 'You have checked a lot just now. Please wait a few minutes.' : '', true);
    }).then(function () { if (mine === seq) $('again').disabled = false; });
  }

  function drawWatch() {
    var b = $('watch'); b.hidden = false;
    b.disabled = onList; b.textContent = onList ? 'On your watchlist' : 'Add to watchlist';
  }

  function loadUser() {
    return api('me.php').then(function (j) {
      user = j.user || null;
      var w = $('who');
      if (user) w.textContent = 'Signed in as ' + user.name; else { w.textContent = ''; var a = document.createElement('a'); a.href = SITE + '/login'; a.target = '_blank'; a.rel = 'noopener'; a.textContent = 'Sign in'; w.appendChild(a); }
      if (!user) return;
      return api('watch.php').then(function (r) { onList = (r.items || []).some(function (x) { return x.host === host; }); drawWatch(); }).catch(function () {});
    }).catch(function () {});
  }

  $('again').addEventListener('click', function () { if (host) check(host); });
  $('form').addEventListener('submit', function (e) {
    e.preventDefault();
    var v = $('addr').value.trim(); if (!v) return;
    onList = false; check(v).then(loadUser); $('addr').value = '';
  });
  $('watch').addEventListener('click', function () {
    if (!host || onList) return;
    if (!user) { chrome.tabs.create({ url: SITE + '/login?next=' + encodeURIComponent('/monitor?add=' + host) }); return; }
    var b = this; b.disabled = true; say('');
    api('watch.php', { action: 'add', address: host }).then(function () { onList = true; drawWatch(); say('Added. We will email you if it goes down.'); })
      .catch(function (e) { b.disabled = false; say(e.message, true); });
  });
  $('monitor').href = SITE + '/monitor';
  $('speed').href = SITE + '/internet-speed-test';

  function start() {
    var q = (window.chrome && chrome.tabs && chrome.tabs.query) ? chrome.tabs.query({ active: true, currentWindow: true }) : Promise.resolve([]);
    Promise.resolve(q).then(function (tabs) {
      var h = '';
      try { var u = new URL((tabs[0] || {}).url || ''); if (u.protocol === 'http:' || u.protocol === 'https:') h = u.hostname; } catch (e) {}
      if (h && h !== 'siteupdown.com' && h !== 'localhost' && !/^[\d.]+$/.test(h) && h.indexOf(':') < 0) { return check(h).then(loadUser); }
      $('host').textContent = 'No website open here'; show('pending', 'Type a website below', 'Open a site and click the icon, or check any address.'); $('again').hidden = true;
      return loadUser();
    });
  }
  start();
})();
