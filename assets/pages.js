/* siteupdown.com — login, account and monitor pages. */
(function () {
  'use strict';
  var S = window.SUD, $ = S.$, esc = S.esc;
  var page = document.body.getAttribute('data-page');

  function busy(btn, on, label) { btn.disabled = on; if (label) btn.firstElementChild ? (btn.firstElementChild.textContent = on ? 'Please wait…' : label) : (btn.textContent = on ? 'Please wait…' : label); }
  function arrow() { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'; }

  /* ================= LOGIN ================= */
  function initLogin() {
    var view = 'signin', token = new URLSearchParams(location.search).get('reset') || '';
    var T = { signin: ['Sign in.', 'Save your checks, build a watchlist and keep your history across devices. The checker itself stays free and works without signing in.'],
      create: ['Create account.', 'Free, takes a few seconds. Your checks and watchlist are saved and private to you.'],
      forgot: ['Reset password.', 'Enter your email and we will send you a link to choose a new password.'],
      reset: ['New password.', 'Choose a new password for your account.'],
      sent: ['Check your email.', 'If that address has an account, a reset link is on its way. It works for one hour.'] };
    function show(v) {
      view = v;
      $('#t-h').innerHTML = esc(T[v][0]).replace(/\.$/, '<span class="dot">.</span>'); $('#t-p').textContent = T[v][1];
      ['signin', 'create', 'forgot', 'reset', 'sent'].forEach(function (x) { var f = $('#v-' + x); if (f) f.hidden = x !== v; });
      $('#gwrap').hidden = !(S.google && (v === 'signin' || v === 'create'));
      S.$$('#seg button').forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-v') === v); });
      S.$$('.err').forEach(function (e) { e.textContent = ''; });
    }
    S.$$('#seg button').forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-v')); }); });
    S.$$('[data-go]').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); show(b.getAttribute('data-go')); }); });
    function done(u, msg) { S.store.set('sud-in', '1'); try { sessionStorage.setItem('sud-flash', msg); } catch (e) { /* ignore */ } location.href = S.next(); }
    function wire(id, path, body, ok) {
      $(id).addEventListener('submit', function (e) {
        e.preventDefault(); var f = e.target, btn = $('button[type=submit]', f), er = $('.err', f), lbl = btn.textContent;
        er.textContent = ''; btn.disabled = true; btn.firstElementChild ? btn.firstElementChild.textContent = 'Please wait…' : null;
        S.api(path, body(f)).then(ok).catch(function (x) { er.textContent = x.message; }).then(function () { btn.disabled = false; if (btn.firstElementChild) btn.firstElementChild.textContent = lbl.trim(); });
      });
    }
    var v = function (f, n) { return f.elements[n].value; };
    wire('#v-signin', 'login.php', function (f) { return { email: v(f, 'email'), password: v(f, 'password') }; }, function (j) { done(j.user, 'Signed in as ' + j.user.email); });
    wire('#v-create', 'register.php', function (f) { return { name: v(f, 'name'), email: v(f, 'email'), password: v(f, 'password') }; }, function (j) { done(j.user, 'Welcome, ' + j.user.name + '! Your account is ready.'); });
    wire('#v-forgot', 'forgot.php', function (f) { return { email: v(f, 'email') }; }, function () { show('sent'); });
    wire('#v-reset', 'reset.php', function (f) { return { token: token, password: v(f, 'password') }; }, function () { history.replaceState(null, '', '/login'); show('signin'); S.toast('Password changed. You can sign in now.'); });

    S.onReady(function (u) {
      if (u) { location.replace(S.next()); return; }
      if (S.enabled === false) { $('#off').hidden = false; $('#card').hidden = true; return; }
      show(token ? 'reset' : (location.hash === '#create' ? 'create' : 'signin'));
      if (S.google) loadGoogle();
    });
    function loadGoogle() {
      var s = document.createElement('script'); s.src = 'https://accounts.google.com/gsi/client'; s.async = true;
      s.onload = function () {
        window.google.accounts.id.initialize({ client_id: S.google, ux_mode: 'popup', callback: function (r) {
          S.api('google.php', { credential: r.credential }).then(function (j) { done(j.user, 'Signed in with Google as ' + j.user.email); }).catch(function (e) { $('#g-err').textContent = e.message; });
        } });
        var w = Math.min(400, Math.max(200, $('#gbtn').clientWidth || 320));
        window.google.accounts.id.renderButton($('#gbtn'), { type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', shape: 'pill', width: w });
      };
      s.onerror = function () { var g = $('#gbtn'); g.className = 'gfail'; g.textContent = 'Google sign-in is unavailable. Use email below.'; };
      document.head.appendChild(s);
    }
  }

  /* ================= ACCOUNT ================= */
  function initAccount() {
    S.onReady(function (u) {
      if (!u) { location.replace('/login?next=' + encodeURIComponent('/account')); return; }
      $('#acct').hidden = false;
      $('#a-name').value = u.name; $('#a-email').textContent = u.email; $('#a-since').textContent = u.since ? 'Member since ' + u.since.split('-').reverse().join('/') : '';
      $('#pw-card').hidden = !S.me.user.pw; $('#del-pw-wrap').hidden = !S.me.user.pw;
      tab(location.hash === '#settings' ? 'settings' : 'checks');
      loadChecks();
    });
    function tab(t) {
      S.$$('#tabs button').forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-t') === t); });
      $('#p-checks').hidden = t !== 'checks'; $('#p-settings').hidden = t !== 'settings';
      history.replaceState(null, '', '#' + t);
    }
    S.$$('#tabs button').forEach(function (b) { b.addEventListener('click', function () { tab(b.getAttribute('data-t')); }); });
    window.addEventListener('hashchange', function () { tab(location.hash === '#settings' ? 'settings' : 'checks'); });

    function loadChecks() {
      S.api('history.php').then(function (j) {
        var L = $('#checks-list');
        $('#clear-checks').hidden = !j.items.length;
        if (!j.items.length) { L.innerHTML = '<div class="empty">No saved checks yet.<br>Run a check while signed in and it will appear here.<br><br><a class="btn small" href="/">Check a website</a></div>'; return; }
        L.innerHTML = j.items.map(function (x) {
          var reach = x.probes ? '<span class="note"> · reachable from ' + x.reachable + '/' + x.probes + ' places' + (x.median_ms != null ? ' · median ' + esc(S.ms(x.median_ms)) : '') + '</span>' : '';
          return '<div class="item"><div class="t"><b>' + esc(x.host) + '</b><small>' + esc(S.when(x.at)) + '</small>' + reach + '</div><div class="acts">' + S.pill(x.verdict)
            + '<a class="btn small ghost" href="/?q=' + encodeURIComponent(x.host) + '">Run again</a><button class="btn small ghost" data-del="' + x.id + '" aria-label="Delete this check">Delete</button></div></div>';
        }).join('');
      }).catch(function (e) { $('#checks-list').innerHTML = '<div class="empty">' + esc(e.message) + '</div>'; });
    }
    $('#checks-list').addEventListener('click', function (e) {
      var b = e.target.closest('[data-del]'); if (!b) return;
      S.api('history.php', { action: 'delete', id: +b.getAttribute('data-del') }).then(loadChecks).catch(function (x) { S.toast(x.message, true); });
    });
    $('#clear-checks').addEventListener('click', function () {
      if (!confirm('Delete all your saved checks?')) return;
      S.api('history.php', { action: 'clear' }).then(function () { loadChecks(); S.toast('History cleared'); });
    });

    $('#f-name').addEventListener('submit', function (e) {
      e.preventDefault(); var er = $('.err', e.target); er.textContent = '';
      S.api('account.php', { action: 'name', name: $('#a-name').value }).then(function (j) { S.user.name = j.user.name; S.toast('Name saved'); var a = $('#avbtn'); if (a) a.textContent = j.user.name.charAt(0).toUpperCase(); }).catch(function (x) { er.textContent = x.message; });
    });
    $('#f-pw').addEventListener('submit', function (e) {
      e.preventDefault(); var f = e.target, er = $('.err', f); er.textContent = '';
      S.api('account.php', { action: 'password', password: f.elements.cur.value, new: f.elements.nw.value }).then(function () { f.reset(); S.toast('Password changed'); }).catch(function (x) { er.textContent = x.message; });
    });
    $('#reset-data').addEventListener('click', function () {
      if (!confirm('This clears your saved checks and your watchlist. Your account stays. Continue?')) return;
      S.api('account.php', { action: 'clear' }).then(function () { S.toast('Your data was reset'); loadChecks(); }).catch(function (x) { S.toast(x.message, true); });
    });
    $('#del-open').addEventListener('click', function () { $('#del-form').hidden = false; this.hidden = true; });
    $('#del-form').addEventListener('submit', function (e) {
      e.preventDefault(); var f = e.target, er = $('.err', f); er.textContent = '';
      S.api('account.php', { action: 'delete', confirm: f.elements.confirm.value, password: f.elements.password ? f.elements.password.value : '' })
        .then(function () { S.store.del('sud-in'); try { sessionStorage.setItem('sud-flash', 'Your account and data were deleted.'); } catch (x) { /* ignore */ } location.href = '/'; })
        .catch(function (x) { er.textContent = x.message; });
    });
  }

  /* ================= MONITOR ================= */
  function initMonitor() {
    var timer;
    S.onReady(function (u) {
      if (!u) { $('#m-out').hidden = false; return; }
      $('#m-in').hidden = false; load(); loadCh(); loadXc(); try { var ad = new URLSearchParams(location.search).get('add'); if (ad) { $('#m-input').value = ad.slice(0, 253); $('#m-input').focus(); } } catch (e) {} timer = setInterval(function () { if (!document.hidden) load(); }, 60000);
    });
    function draw(j) {
      var L = $('#m-list');
      $('#m-count').textContent = j.items.length + ' of ' + j.max + ' sites';
      if (!j.items.length) { L.innerHTML = '<div class="empty">Your watchlist is empty.<br>Add a site above to see whether it is up.</div>'; return; }
      L.innerHTML = j.items.map(function (x) {
        return '<div class="item"><div class="t"><b>' + esc(x.host) + '</b><small>' + (x.at ? 'Last checked ' + esc(S.ago(x.at)) : 'Not checked yet') + (x.ms != null ? ' · ' + esc(S.ms(x.ms)) : '') + (x.code ? ' · HTTP ' + x.code : '') + (x.uptime != null ? ' · ' + x.uptime + '% up (24h)' : '') + '</small></div>'
          + '<div class="acts">' + S.pill(x.verdict || 'pending') + '<button class="btn small ghost bell' + (x.alerts ? ' on' : '') + '" data-al="' + esc(x.host) + '" data-on="' + (x.alerts ? 1 : 0) + '" aria-pressed="' + !!x.alerts + '" title="Email me when this site goes down or comes back">' + (x.alerts ? 'Alerts on' : 'Alerts off') + '</button>'
          + '<a class="btn small ghost" href="/status/' + encodeURIComponent(x.host) + '">History</a><button class="btn small ghost" data-chk="' + esc(x.host) + '">Check now</button><a class="btn small ghost" href="/?q=' + encodeURIComponent(x.host) + '">Worldwide</a><button class="btn small ghost" data-rm="' + esc(x.host) + '" aria-label="Remove ' + esc(x.host) + '">Remove</button></div></div>';
      }).join('');
    }
    /* alert channels */
    var chPoll, chBefore = 0;
    function drawCh(j) {
      $('#ch-card').hidden = false;
      $('#ch-tg-box').hidden = !j.can.telegram;
      var L = $('#ch-list');
      L.innerHTML = j.items.length ? j.items.map(function (x) {
        return '<div class="item"><div class="t"><b>' + esc(x.label) + '</b><small>' + (x.kind === 'telegram' ? 'Telegram chat' : x.kind === 'slack' ? 'Slack webhook' : 'Discord webhook') + '</small></div><div class="acts"><button class="btn small ghost" data-cht="' + x.id + '">Send test</button><button class="btn small ghost" data-chr="' + x.id + '">Remove</button></div></div>';
      }).join('') : '<div class="empty" style="padding:14px">No extra channels yet. Email alerts are always on.</div>';
      return j;
    }
    function loadCh() { return S.api('channels.php').then(drawCh).catch(function () {}); }
    function stopPoll() { clearInterval(chPoll); chPoll = null; }
    $('#ch-tg').addEventListener('click', function () {
      var b = this, msg = $('#ch-tg-msg'), open = $('#ch-tg-open'); msg.textContent = ''; b.disabled = true;
      S.api('channels.php', { action: 'tg_link' }).then(function (j) {
        drawCh(j); chBefore = j.items.length; open.href = j.link; open.hidden = false;
        msg.textContent = 'Tap Open Telegram, then press Start. This page updates by itself.';
        stopPoll(); var n = 0;
        chPoll = setInterval(function () {
          if (++n > 40) { stopPoll(); msg.textContent = 'The link expired. Tap Connect Telegram to try again.'; open.hidden = true; return; }
          S.api('channels.php').then(function (r) { if (r.items.length > chBefore) { stopPoll(); drawCh(r); open.hidden = true; msg.textContent = ''; S.toast('Telegram connected'); } }).catch(function () {});
        }, 3000);
      }).catch(function (x) { msg.textContent = x.message; }).then(function () { b.disabled = false; });
    });
    $('#ch-wh').addEventListener('submit', function (e) {
      e.preventDefault(); var er = $('#ch-err'), i = $('#ch-url'), b = $('button', e.target); er.textContent = ''; b.disabled = true;
      S.api('channels.php', { action: 'add_webhook', url: i.value }).then(function (j) { i.value = ''; drawCh(j); S.toast('Connected. A test message was sent.'); }).catch(function (x) { er.textContent = x.message; }).then(function () { b.disabled = false; });
    });
    $('#ch-list').addEventListener('click', function (e) {
      var t = e.target.closest('[data-cht]'), r = e.target.closest('[data-chr]');
      if (t) { t.disabled = true; S.api('channels.php', { action: 'test', id: +t.getAttribute('data-cht') }).then(function (j) { drawCh(j); S.toast('Test message sent'); }).catch(function (x) { S.toast(x.message, true); loadCh(); }); }
      if (r) S.api('channels.php', { action: 'remove', id: +r.getAttribute('data-chr') }).then(drawCh).catch(function (x) { S.toast(x.message, true); });
    });
    /* extra checks: word on page, open port */
    function drawXc(j) {
      $('#xc-card').hidden = false;
      $('#xc-count').textContent = j.items.length + ' of ' + j.max;
      $('#xc-list').innerHTML = j.items.length ? j.items.map(function (x) {
        var v = x.verdict === 'up' ? 'up' : x.verdict === 'down' ? (x.state === 'down' ? 'down' : 'timeout') : 'pending';
        return '<div class="item"><div class="t"><b>' + esc(x.host) + '</b><small>' + (x.kind === 'port' ? 'Port ' + esc(x.param) + ' must be open' : 'Page must contain &ldquo;' + esc(x.param) + '&rdquo;') + (x.detail ? ' &middot; ' + esc(x.detail) : '') + (x.at ? ' &middot; checked ' + esc(S.ago(x.at)) : ' &middot; not checked yet') + '</small></div>'
          + '<div class="acts">' + S.pill(v) + '<button class="btn small ghost" data-xr="' + x.id + '">Check now</button><button class="btn small ghost" data-xd="' + x.id + '" aria-label="Remove this check">Remove</button></div></div>';
      }).join('') : '<div class="empty" style="padding:14px">No extra checks yet.</div>';
    }
    function loadXc() { return S.api('xcheck.php').then(drawXc).catch(function () {}); }
    $('#xc-kind').addEventListener('change', function () { var p = this.value === 'port'; $('#xc-portf').hidden = !p; $('#xc-wordf').hidden = p; });
    $('#xc-form').addEventListener('submit', function (e) {
      e.preventDefault(); var er = $('#xc-err'), b = $('button', e.target), port = $('#xc-kind').value === 'port'; er.textContent = ''; b.disabled = true;
      S.api('xcheck.php', { action: 'add', kind: $('#xc-kind').value, address: $('#xc-host').value, param: port ? $('#xc-port').value : $('#xc-word').value })
        .then(function (j) { drawXc(j); $('#xc-word').value = ''; S.toast('Check added'); }).catch(function (x) { er.textContent = x.message; }).then(function () { b.disabled = false; });
    });
    $('#xc-list').addEventListener('click', function (e) {
      var r = e.target.closest('[data-xr]'), d = e.target.closest('[data-xd]');
      if (r) { r.disabled = true; S.api('xcheck.php', { action: 'run', id: +r.getAttribute('data-xr') }).then(drawXc).catch(function (x) { S.toast(x.message, true); loadXc(); }); }
      if (d) S.api('xcheck.php', { action: 'remove', id: +d.getAttribute('data-xd') }).then(drawXc).catch(function (x) { S.toast(x.message, true); });
    });
    function load() { S.api('watch.php').then(draw).catch(function (e) { $('#m-list').innerHTML = '<div class="empty">' + esc(e.message) + '</div>'; }); }
    $('#m-add').addEventListener('submit', function (e) {
      e.preventDefault(); var er = $('#m-err'), i = $('#m-input'), b = $('button', e.target); er.textContent = ''; b.disabled = true;
      S.api('watch.php', { action: 'add', address: i.value }).then(function (j) { i.value = ''; draw(j); }).catch(function (x) { er.textContent = x.message; }).then(function () { b.disabled = false; });
    });
    $('#m-list').addEventListener('click', function (e) {
      var c = e.target.closest('[data-chk]'), r = e.target.closest('[data-rm]'), al = e.target.closest('[data-al]');
      if (al) { S.api('watch.php', { action: 'alerts', host: al.getAttribute('data-al'), on: al.getAttribute('data-on') !== '1' }).then(draw).catch(function (x) { S.toast(x.message, true); }); }
      if (c) { c.disabled = true; c.textContent = 'Checking…'; S.api('watch.php', { action: 'check', host: c.getAttribute('data-chk') }).then(draw).catch(function (x) { S.toast(x.message, true); load(); }); }
      if (r) S.api('watch.php', { action: 'remove', host: r.getAttribute('data-rm') }).then(draw).catch(function (x) { S.toast(x.message, true); });
    });
  }

  /* ================= STATUS PAGE ================= */
  function initStatus() {
    var m = location.pathname.match(/\/status\/([^\/]+)/), host = m ? decodeURIComponent(m[1]).toLowerCase() : '', range = '24h';
    if (!host) { $('#st-p').textContent = 'Add a website address to the end of this link, like /status/example.com.'; $('#st-body').innerHTML = ''; return; }
    document.title = host + ' status — siteupdown.com';
    (function () { var c = document.querySelector('link[rel=canonical]'), u = location.origin + '/status/' + host; if (c) c.href = u; var set = function (sel, v) { var m = document.querySelector(sel); if (m) m.setAttribute('content', v); };
      var d = 'Live status, uptime and recent outages for ' + host + ', checked every few minutes by siteupdown.com.'; set('meta[name=description]', d); set('meta[property="og:title"]', host + ' status — siteupdown.com'); set('meta[property="og:description"]', d); set('meta[property="og:url"]', u); set('meta[name="twitter:title"]', host + ' status — siteupdown.com'); })();
    $('#st-h').innerHTML = esc(host) + '<span class="dot">.</span>';
    function dur(sec) { if (sec < 90) return 'about a minute'; if (sec < 5400) return Math.round(sec / 60) + ' min'; if (sec < 172800) return (sec / 3600).toFixed(1) + ' hours'; return (sec / 86400).toFixed(1) + ' days'; }
    function fmtPct(v) { return v == null ? '—' : (v >= 99.995 ? '100' : v.toFixed(2).replace(/0$/, '')) + '%'; }
    function load() {
      fetch('/api/uptime.php?host=' + encodeURIComponent(host) + '&range=' + range).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'Could not load.'); return j; }); }).then(draw).catch(function (e) {
        var rb = document.querySelector('meta[name=robots]'); if (rb) rb.setAttribute('content', 'noindex,follow');
        $('#st-p').textContent = ''; $('#st-pill').innerHTML = '';
        $('#st-body').innerHTML = '<div class="empty">' + esc(e.message) + '<br><br><a class="btn small" href="/monitor"><span>Open Monitor</span></a> <a class="btn small ghost" href="/?q=' + encodeURIComponent(host) + '">Check it now</a></div>';
      });
    }
    function draw(j) {
      var c = j.current, v = c.verdict;
      var say = { up: 'is up and answering.', down: 'looks down right now.', timeout: 'is slow to answer right now.', inconclusive: 'could not be verified on the last check.' }[v] || 'status unknown.';
      $('#st-p').textContent = host + ' ' + say + ' Last checked ' + S.ago(c.at) + '.';
      $('#st-pill').innerHTML = S.pill(v);
      var u = j.uptime, h = '<div class="stat-row">'
        + '<div class="stat"><span class="k">Uptime 24h</span><b>' + fmtPct(u['24h']) + '</b></div><div class="stat"><span class="k">Uptime 7 days</span><b>' + fmtPct(u['7d']) + '</b></div><div class="stat"><span class="k">Uptime 30 days</span><b>' + fmtPct(u['30d']) + '</b></div>'
        + '<div class="stat"><span class="k">Avg response</span><b>' + (j.avg_ms != null ? esc(S.ms(j.avg_ms)) : '—') + '</b></div></div>';
      h += '<div class="seg2" role="tablist">' + ['24h', '7d', '30d'].map(function (r) { return '<button type="button" data-r="' + r + '" aria-selected="' + (r === range) + '">' + (r === '24h' ? 'Last 24 hours' : r === '7d' ? 'Last 7 days' : 'Last 30 days') + '</button>'; }).join('') + '</div>';
      h += '<div class="upbar" role="img" aria-label="Uptime over the selected period">' + j.series.map(function (b) { return '<i class="' + b.state + '" title="' + esc(S.when(b.t)) + ' · ' + (b.state === 'none' ? 'no data' : b.state === 'up' ? 'up' : b.state === 'down' ? 'down' : 'some failures') + (b.ms != null ? ' · ' + esc(S.ms(b.ms)) : '') + '"></i>'; }).join('') + '</div>';
      h += '<div class="upleg"><span>' + (range === '24h' ? '24 hours ago' : range === '7d' ? '7 days ago' : '30 days ago') + '</span><span>Now</span></div>';
      h += '<h3 class="sh3">Response time</h3>' + lineChart(j.series);
      h += '<h3 class="sh3">Recent outages</h3>';
      h += j.incidents.length ? '<div class="inc">' + j.incidents.map(function (i) { return '<div><b>' + (i.ended ? 'Down for ' + esc(dur(i.seconds)) : 'Down now · ' + esc(dur(i.seconds)) + ' so far') + '</b><small>' + esc(S.when(i.started)) + (i.ended ? ' → ' + esc(S.when(i.ended)) : '') + '</small></div>'; }).join('') + '</div>' : '<p class="note">No outages recorded. ✔</p>';
      if (j.ssl && j.ssl.days != null) h += '<p class="note" style="margin-top:14px">SSL certificate: <b>' + esc(j.ssl.status === 'valid' || j.ssl.status === 'expiring' ? 'valid, expires in ' + j.ssl.days + ' days' : j.ssl.status) + '</b></p>';
      h += '<div class="row-actions" style="margin-top:18px"><a class="btn small" href="/?q=' + encodeURIComponent(host) + '"><span>Check from 12 places</span></a><button class="btn small ghost" id="st-copy" type="button">Copy this link</button></div>';
      $('#st-body').innerHTML = h;
    }
    function lineChart(series) {
      var pts = series.map(function (b, i) { return b.ms != null ? [i, b.ms] : null; }).filter(Boolean);
      if (pts.length < 2) return '<p class="note">Not enough data yet. Results appear after a few checks.</p>';
      var W = 600, H = 150, max = Math.max.apply(null, pts.map(function (p) { return p[1]; })) * 1.15 || 1, n = series.length - 1;
      var xy = function (p) { return (p[0] / n * W).toFixed(1) + ',' + (H - 10 - (p[1] / max) * (H - 24)).toFixed(1); };
      var d = pts.map(xy).join(' ');
      return '<svg class="lc" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img" aria-label="Response time over the selected period"><line x1="0" x2="' + W + '" y1="' + (H - 10) + '" y2="' + (H - 10) + '" class="ax"/><polyline points="' + d + '" class="ln"/><polyline points="0,' + (H - 10) + ' ' + d + ' ' + W + ',' + (H - 10) + '" class="ar"/></svg><div class="upleg"><span>Peak ' + esc(S.ms(Math.round(max / 1.15))) + '</span><span>Lower is faster</span></div>';
    }
    $('#st-body').addEventListener('click', function (e) {
      var b = e.target.closest('[data-r]'); if (b) { range = b.getAttribute('data-r'); load(); }
      if (e.target.closest('#st-copy')) { try { navigator.clipboard.writeText(location.href); S.toast('Link copied'); } catch (x) { S.toast('Copy the address from your browser bar'); } }
    });
    load(); setInterval(function () { if (!document.hidden) load(); }, 60000);
  }


  /* ================= SPEED TEST ================= */
  function initSpeed() {
    var q = new URLSearchParams(location.search).get('q');
    function kb(n) { return n >= 1048576 ? (n / 1048576).toFixed(2) + ' MB' : n >= 1024 ? (n / 1024).toFixed(1) + ' KB' : n + ' B'; }
    $('#sp-form').addEventListener('submit', function (e) { e.preventDefault(); run($('#sp-input').value); });
    function run(addr) {
      var er = $('#sp-err'), b = $('#sp-btn'); er.textContent = '';
      if (!addr.trim()) { er.textContent = 'Please enter a website address.'; return; }
      b.disabled = true; b.firstElementChild.textContent = 'Testing…';
      var o = $('#sp-out'); o.hidden = false; o.innerHTML = '<div class="skeleton">Loading the page three times… this takes a few seconds.</div>';
      S.api('speed.php', { address: addr }).then(draw).catch(function (x) { o.hidden = true; er.textContent = x.message; }).then(function () { b.disabled = false; b.firstElementChild.textContent = 'Test speed'; });
    }
    function draw(j) {
      var o = $('#sp-out');
      if (!j.ok) { o.innerHTML = '<div class="empty">' + esc(j.error) + '</div>'; return; }
      var m = j.median, parts = [['Find server (DNS)', m.dns, 'dns'], ['Connect', m.connect, 'con'], ['Secure (TLS)', m.tls, 'tls'], ['Wait for server', m.wait, 'wait'], ['Download', m.download, 'dl']].filter(function (p) { return p[1] > 0 || p[2] === 'wait'; });
      var sum = parts.reduce(function (a, p) { return a + p[1]; }, 0) || 1;
      var h = '<div class="sp-top"><div class="grade g' + j.grade + '"><b>' + j.grade + '</b><span>' + j.score + '/100</span></div><div><h2 class="sp-h">' + esc(j.host) + '<span class="dot">.</span></h2><p class="note">Loaded in <b>' + esc(S.ms(m.total)) + '</b> (median of ' + j.runs.length + ' loads: ' + j.runs.map(function (x) { return esc(S.ms(x)); }).join(', ') + '). First byte after <b>' + esc(S.ms(m.ttfb)) + '</b>.</p></div></div>';
      h += '<h3 class="sh3">Where the time goes</h3><div class="wf">' + parts.map(function (p) { return '<div class="wr"><span class="wl">' + p[0] + '</span><span class="wt"><i class="' + p[2] + '" style="width:' + Math.max(2, p[1] / sum * 100).toFixed(1) + '%"></i></span><b>' + esc(S.ms(p[1])) + '</b></div>'; }).join('') + '</div>';
      h += '<div class="stat-row" style="margin-top:20px"><div class="stat"><span class="k">Page size</span><b>' + kb(j.size) + '</b></div><div class="stat"><span class="k">Sent compressed</span><b>' + (j.encoding ? esc(j.encoding) + (j.wire ? ' · ' + kb(j.wire) : '') : 'No') + '</b></div><div class="stat"><span class="k">Protocol</span><b>' + esc(j.version || '—') + (j.https ? '' : ' · no HTTPS') + '</b></div><div class="stat"><span class="k">Redirects</span><b>' + j.redirects + '</b></div></div>';
      h += '<p class="note">The page links <b>' + j.resources.scripts + '</b> scripts, <b>' + j.resources.styles + '</b> stylesheets and <b>' + j.resources.images + '</b> images (counted in the HTML). ' + (j.cache.cache_control ? 'Cache-Control: <b>' + esc(j.cache.cache_control) + '</b>.' : 'No Cache-Control header.') + '</p>';
      h += '<h3 class="sh3">What to improve</h3><ul class="tips">' + j.tips.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>';
      h += '<p class="fine" style="margin-top:14px">This tests the page document from our server, not every file it loads, and one location only. For a view from 12 places, run a <a href="/?q=' + encodeURIComponent(j.host) + '">worldwide check</a>.</p>';
      o.innerHTML = h;
    }
    if (q) { $('#sp-input').value = q; run(q); }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (page === 'login') initLogin(); else if (page === 'account') initAccount(); else if (page === 'monitor') initMonitor(); else if (page === 'status') initStatus(); else if (page === 'speed') initSpeed();
  });
})();
