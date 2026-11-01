/* siteupdown.com — shared behaviour: theme, header sign-in state, cookie consent, small helpers. No dependencies. */
(function () {
  'use strict';
  var d = document;
  var S = window.SUD = window.SUD || {};
  S.user = null; S.google = ''; S.ready = []; S.me = null;

  /* ---- helpers ---- */
  S.$ = function (s, r) { return (r || d).querySelector(s); };
  S.$$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  S.esc = function (t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  S.store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  };
  S.api = function (path, data) {
    var opt = { credentials: 'same-origin' };
    if (data !== undefined) { opt.method = 'POST'; opt.headers = { 'Content-Type': 'application/json', 'X-SUD': '1' }; opt.body = JSON.stringify(data); }
    return fetch('/api/' + path, opt).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) { var e = new Error(j.error || 'Something went wrong. Please try again.'); e.status = r.status; throw e; } return j; });
    });
  };
  S.ago = function (iso) {
    if (!iso) return '—';
    var s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 45) return 'just now'; if (s < 3600) return Math.round(s / 60) + ' min ago';
    if (s < 86400) return Math.round(s / 3600) + ' h ago'; return Math.round(s / 86400) + ' d ago';
  };
  S.when = function (iso) { if (!iso) return '—'; var t = new Date(iso); return t.toLocaleString([], { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); };
  S.ms = function (n) { return n == null ? '—' : (n >= 1000 ? (n / 1000).toFixed(1) + ' s' : n + ' ms'); };
  S.LABEL = { up: 'Up', down: 'Confirmed down', timeout: 'Timeout', inconclusive: 'Inconclusive', pending: 'Checking…', none: 'No data', partial: 'Partly reachable', blocked: 'Blocked', 'down-everywhere': 'Looks down' };
  S.pill = function (v) { v = v || 'pending'; return '<span class="pill ' + S.esc(v) + '">' + S.esc(S.LABEL[v] || v) + '</span>'; };
  S.toast = function (msg, bad) {
    var t = d.createElement('div'); t.className = 'toast' + (bad ? ' bad' : ''); t.setAttribute('role', 'status'); t.textContent = msg; d.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 3200);
  };
  S.onReady = function (fn) { if (S.me) fn(S.user); else S.ready.push(fn); };
  S.next = function () { var n = new URLSearchParams(location.search).get('next'); return n && /^\/[a-z0-9\-_/?=&#.]*$/i.test(n) && n.indexOf('//') < 0 ? n : '/'; };

  /* ---- theme ---- */
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  function applyTheme(t) { d.documentElement.setAttribute('data-theme', t); var b = S.$('#theme'); if (b) { b.innerHTML = t === 'dark' ? SUN : MOON; b.setAttribute('aria-label', t === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'); } }
  var theme = S.store.get('sud-theme') || 'dark';
  applyTheme(theme);
  d.addEventListener('DOMContentLoaded', function () {
    applyTheme(theme);
    var b = S.$('#theme'); if (b) b.addEventListener('click', function () { theme = theme === 'dark' ? 'light' : 'dark'; S.store.set('sud-theme', theme); applyTheme(theme); });
    initAuth(); initCookies();
    try { var fl = sessionStorage.getItem('sud-flash'); if (fl) { sessionStorage.removeItem('sud-flash'); S.toast(fl); } } catch (e) { /* ignore */ }
    S.$$('[data-year]').forEach(function (e) { e.textContent = new Date().getFullYear(); });
  });

  /* ---- header sign-in state ---- */
  var I = {
    hist: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/></svg>',
    star: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/></svg>',
    user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
    out: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>'
  };
  function renderAuth() {
    var box = S.$('#auth'); if (!box) return;
    if (!S.user) {
      var here = location.pathname + location.search;
      box.innerHTML = '<a class="signin-btn" href="/login' + (here !== '/' && here.indexOf('/login') !== 0 ? '?next=' + encodeURIComponent(here) : '') + '">Sign in</a>';
      return;
    }
    var ini = S.esc((S.user.name || '?').trim().charAt(0).toUpperCase());
    box.innerHTML = '<div class="acct"><button class="avatar" id="avbtn" aria-haspopup="true" aria-expanded="false" aria-label="Account menu">' + ini + '</button>'
      + '<div class="menu" id="menu" role="menu"><div class="who">' + S.esc(S.user.email) + '</div>'
      + '<a href="/account#checks" role="menuitem">' + I.hist + 'My checks</a><a href="/monitor" role="menuitem">' + I.star + 'My watchlist</a>'
      + '<a href="/account#settings" role="menuitem">' + I.user + 'Account</a><button id="signout" role="menuitem">' + I.out + 'Sign out</button></div></div>';
    var btn = S.$('#avbtn'), menu = S.$('#menu');
    btn.addEventListener('click', function (e) { e.stopPropagation(); var o = menu.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    d.addEventListener('click', function (e) { if (!menu.contains(e.target)) { menu.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); } });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') menu.classList.remove('open'); });
    S.$('#signout').addEventListener('click', function () { S.api('logout.php', {}).then(function () { S.user = null; S.store.del('sud-in'); location.href = '/'; }); });
  }
  function initAuth() {
    S.api('me.php').then(function (j) {
      S.user = j.user || null; S.google = (j.google && j.google_id) || ''; S.enabled = j.enabled !== false; S.me = j;
      if (S.user) S.store.set('sud-in', '1'); else S.store.del('sud-in');
      renderAuth(); S.ready.splice(0).forEach(function (f) { f(S.user); });
    }).catch(function () { S.me = { user: null }; renderAuth(); S.ready.splice(0).forEach(function (f) { f(null); }); });
    // Paint the right button straight away from the last known state so the header does not jump.
    if (S.store.get('sud-in') === '1') { var box = S.$('#auth'); if (box && !box.firstChild) box.innerHTML = '<span class="avatar" aria-hidden="true">·</span>'; }
  }

  /* ---- cookie consent ---- */
  var SHIELD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/></svg>';
  S.consent = function () { try { return JSON.parse(S.store.get('sud-consent') || 'null'); } catch (e) { return null; } };
  function saveConsent(a, m) { S.store.set('sud-consent', JSON.stringify({ analytics: !!a, marketing: !!m, at: Date.now() })); var c = S.$('#cookie'); if (c) c.remove(); d.dispatchEvent(new CustomEvent('sud:consent')); }
  function showCookies(custom) {
    var old = S.$('#cookie'); if (old) old.remove();
    var cur = S.consent() || {};
    var c = d.createElement('div'); c.id = 'cookie'; c.className = 'cookie'; c.setAttribute('role', 'dialog'); c.setAttribute('aria-label', 'Cookie settings');
    c.innerHTML = '<h3>' + SHIELD + 'Your privacy. Your choice.</h3><p>We use essential storage to run this site. Optional cookies help measure visits and ads, only with your permission.</p>'
      + (custom ? '<div class="opts"><label class="check"><input type="checkbox" checked disabled><span><b>Essential</b><small>Theme, sign-in and your consent choice. Always on.</small></span></label>'
        + '<label class="check"><input type="checkbox" id="c-an"' + (cur.analytics ? ' checked' : '') + '><span><b>Analytics</b><small>Anonymous visit measurement.</small></span></label>'
        + '<label class="check"><input type="checkbox" id="c-mk"' + (cur.marketing ? ' checked' : '') + '><span><b>Advertising</b><small>Lets us show ads that keep the site free.</small></span></label></div>'
        + '<div class="btns"><button class="btn ghost" id="c-rej">Reject optional</button><button class="btn" id="c-save">Save choices</button></div>'
        : '<div class="btns"><button class="btn ghost" id="c-rej">Reject optional</button><button class="btn ghost" id="c-cus">Customize</button><button class="btn wide" id="c-all">Accept all</button></div>');
    d.body.appendChild(c);
    var q = function (id) { return S.$(id, c); };
    q('#c-rej').onclick = function () { saveConsent(false, false); };
    if (q('#c-cus')) q('#c-cus').onclick = function () { showCookies(true); };
    if (q('#c-all')) q('#c-all').onclick = function () { saveConsent(true, true); };
    if (q('#c-save')) q('#c-save').onclick = function () { saveConsent(q('#c-an').checked, q('#c-mk').checked); };
  }
  function initCookies() {
    if (!S.consent()) showCookies(false);
    S.$$('[data-cookie-settings]').forEach(function (b) { b.addEventListener('click', function () { showCookies(true); }); });
  }
})();
