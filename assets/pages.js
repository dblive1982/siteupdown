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
        window.google.accounts.id.renderButton($('#gbtn'), { type: 'standard', theme: document.documentElement.getAttribute('data-theme') === 'light' ? 'outline' : 'filled_black', size: 'large', text: 'continue_with', shape: 'pill', width: w });
      };
      s.onerror = function () { $('#g-err').textContent = 'Google sign-in could not be loaded. Try email instead.'; };
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
      $('#m-in').hidden = false; load(); timer = setInterval(function () { if (!document.hidden) load(); }, 60000);
    });
    function draw(j) {
      var L = $('#m-list');
      $('#m-count').textContent = j.items.length + ' of ' + j.max + ' sites';
      if (!j.items.length) { L.innerHTML = '<div class="empty">Your watchlist is empty.<br>Add a site above to see whether it is up.</div>'; return; }
      L.innerHTML = j.items.map(function (x) {
        return '<div class="item"><div class="t"><b>' + esc(x.host) + '</b><small>' + (x.at ? 'Last checked ' + esc(S.ago(x.at)) : 'Not checked yet') + (x.ms != null ? ' · ' + esc(S.ms(x.ms)) : '') + (x.code ? ' · HTTP ' + x.code : '') + '</small></div>'
          + '<div class="acts">' + S.pill(x.verdict || 'pending') + '<button class="btn small ghost" data-chk="' + esc(x.host) + '">Check now</button><a class="btn small ghost" href="/?q=' + encodeURIComponent(x.host) + '">Worldwide</a><button class="btn small ghost" data-rm="' + esc(x.host) + '" aria-label="Remove ' + esc(x.host) + '">Remove</button></div></div>';
      }).join('');
    }
    function load() { S.api('watch.php').then(draw).catch(function (e) { $('#m-list').innerHTML = '<div class="empty">' + esc(e.message) + '</div>'; }); }
    $('#m-add').addEventListener('submit', function (e) {
      e.preventDefault(); var er = $('#m-err'), i = $('#m-input'), b = $('button', e.target); er.textContent = ''; b.disabled = true;
      S.api('watch.php', { action: 'add', address: i.value }).then(function (j) { i.value = ''; draw(j); }).catch(function (x) { er.textContent = x.message; }).then(function () { b.disabled = false; });
    });
    $('#m-list').addEventListener('click', function (e) {
      var c = e.target.closest('[data-chk]'), r = e.target.closest('[data-rm]');
      if (c) { c.disabled = true; c.textContent = 'Checking…'; S.api('watch.php', { action: 'check', host: c.getAttribute('data-chk') }).then(draw).catch(function (x) { S.toast(x.message, true); load(); }); }
      if (r) S.api('watch.php', { action: 'remove', host: r.getAttribute('data-rm') }).then(draw).catch(function (x) { S.toast(x.message, true); });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (page === 'login') initLogin(); else if (page === 'account') initAccount(); else if (page === 'monitor') initMonitor();
  });
})();
