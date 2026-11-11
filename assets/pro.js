/* Account > Plan tab: upgrade and billing, phone alerts, status page and reports (Pro). */
(function () {
  'use strict';
  var S = window.SUD, root = document.getElementById('p-plan');
  if (!S || !root) return;
  var esc = S.esc, $ = function (s, r) { return (r || root).querySelector(s); };
  var B = null, P = null, SP = null;

  function fmtDate(iso) { return iso ? new Date(iso).toLocaleDateString([], { day: 'numeric', month: 'long', year: 'numeric' }) : ''; }
  function say(el, msg, bad) { if (el) { el.textContent = msg || ''; el.className = bad ? 'err' : 'note ok-note'; } }
  function lock(title, text) {
    return '<div class="card stack pro-card pro-locked"><h3>' + esc(title) + ' <span class="pro-badge">PRO</span></h3><p class="note" style="margin:0">' + esc(text) + '</p><button type="button" class="btn small" data-up="1" style="justify-self:start">See Pro</button></div>';
  }

  function planCard() {
    var pl = B.plan || {}, h = '';
    if (pl.pro) {
      var s = pl.state, msg = s === 'canceling' ? 'Your plan ends on ' + fmtDate(pl.until) + ' and will not renew.' : s === 'past_due' ? 'Your last payment did not go through. Please update your card in Manage billing so Pro is not interrupted.' : 'Active. Your plan renews around ' + fmtDate(pl.until) + '.';
      h = '<div class="card stack pro-card plan-hero pro-on"><h3>siteupdown Pro <span class="pro-badge">ACTIVE</span></h3><p class="note' + (s === 'past_due' ? ' warn-note' : '') + '" style="margin:0">' + esc(msg) + '</p>'
        + '<button type="button" class="btn small" id="pl-portal" style="justify-self:start">Manage billing</button><p class="err" role="alert" id="pl-err"></p>'
        + '<p class="note" style="margin:0">Change card, switch between monthly and yearly, download invoices or cancel, all on Stripe&rsquo;s secure page.</p></div>';
    } else {
      var yr = B.price_year ? '<label class="seg-int"><input type="radio" name="pl-int" value="month" checked> &pound;' + esc(B.price_month) + ' a month</label> <label class="seg-int"><input type="radio" name="pl-int" value="year"> &pound;' + esc(B.price_year) + ' a year <em>(2 months free)</em></label>' : '<p class="plan-price"><b>&pound;' + esc(B.price_month) + '</b> a month</p>';
      h = '<div class="card stack pro-card plan-hero"><h3>You are on the Free plan</h3>'
        + '<p class="note" style="margin:0">Pro adds text and phone-call alerts, a watchlist of up to ' + esc(B.limits.watch) + ' sites with checks about every 30 seconds, your own public status page, and monthly uptime reports with 12 months of history.</p>'
        + '<div class="int-row">' + yr + '</div>'
        + (B.on ? '<button type="button" class="btn" id="pl-up" style="justify-self:start">Upgrade to Pro</button>' : '<p class="note soon-note" style="margin:0"><b>Pro is opening soon.</b> You can already see everything it will include below.</p>')
        + '<p class="err" role="alert" id="pl-err"></p><p class="fine" style="margin:0">Cancel any time. See the <a href="/pricing">pricing page</a> for the full comparison.</p></div>';
    }
    return h;
  }

  function phoneCard() {
    if (!B.plan.pro) return lock('Text and phone alerts', 'Get a text message the moment a site goes down, and optionally a phone call so you cannot miss it.');
    var p = P && P.phone, h = '<div class="card stack pro-card" id="ph-card"><h3>Text and phone alerts <span class="pro-badge">PRO</span></h3>';
    if (!P.ready) return h + '<p class="note" style="margin:0">Text and phone alerts are being switched on. Check back soon.</p></div>';
    if (!p || !p.verified) {
      h += '<p class="note" style="margin:0">' + (p ? 'We texted a 6-digit code to ' + esc(p.number) + '. Enter it to finish.' : 'Add your mobile number with its country code, for example +44 7700 900123. We text you a code to check it is yours.') + '</p>';
      if (!p) h += '<form class="stack" id="ph-add" novalidate><div class="field"><input name="number" type="tel" autocomplete="tel" inputmode="tel" placeholder="+44 7700 900123" aria-label="Mobile number"></div><button class="btn small" type="submit" style="justify-self:start">Send code</button></form>';
      else h += '<form class="stack" id="ph-ver" novalidate><div class="field"><input name="code" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="6-digit code" aria-label="Six-digit code"></div><div class="btn-row"><button class="btn small" type="submit">Confirm</button><button class="btn small ghost" type="button" id="ph-rm">Use a different number</button></div></form>';
    } else {
      h += '<p class="note" style="margin:0">Alerts go to <b>' + esc(p.number) + '</b>.</p>'
        + '<label class="chk"><input type="checkbox" id="ph-sms"' + (p.sms ? ' checked' : '') + '> Text me when a watched site goes down or comes back</label>'
        + '<label class="chk"><input type="checkbox" id="ph-call"' + (p.call ? ' checked' : '') + '> Also phone me when a site goes down</label>'
        + '<p class="fine" style="margin:0">This month: ' + esc(P.used.sms) + ' of ' + esc(P.caps.sms) + ' texts and ' + esc(P.used.calls) + ' of ' + esc(P.caps.calls) + ' calls used. The limits stop a flapping site from running up a bill.</p>'
        + '<div class="btn-row"><button class="btn small ghost" type="button" id="ph-test">Send a test text</button><button class="btn small ghost" type="button" id="ph-rm">Remove number</button></div>';
    }
    return h + '<p class="note" id="ph-msg" role="status" style="margin:0"></p></div>';
  }

  function statusCard() {
    if (!B.plan.pro) return lock('Your own status page', 'Show customers whether your sites are up on a page with your name on it, with 90 days of history.');
    var pg = SP && SP.page, h = '<div class="card stack pro-card" id="sp-card"><h3>Your status page <span class="pro-badge">PRO</span></h3>';
    if (!SP || !SP.watch.length) return h + '<p class="note" style="margin:0">Add a few sites to your <a href="/monitor">watchlist</a> first, then choose which ones to show here.</p></div>';
    var sel = pg ? pg.hosts : [];
    h += '<p class="note" style="margin:0">A public page, with no sign-in needed, showing the sites you choose, their current status and 90 days of history.</p>'
      + '<form class="stack" id="sp-form" novalidate><div><label class="lbl" for="sp-title">Page name</label><div class="field"><input id="sp-title" name="title" maxlength="80" placeholder="Acme Ltd status" value="' + esc(pg ? pg.title : '') + '"></div></div>'
      + '<div><label class="lbl" for="sp-slug">Web address</label><div class="field slug-field"><span>siteupdown.com/p/</span><input id="sp-slug" name="slug" maxlength="40" placeholder="acme" value="' + esc(pg ? pg.slug : '') + '" autocapitalize="none"></div></div>'
      + '<fieldset class="chk-grid"><legend class="lbl">Sites to show</legend>' + SP.watch.map(function (w) { return '<label class="chk"><input type="checkbox" name="hosts" value="' + esc(w) + '"' + (sel.indexOf(w) > -1 ? ' checked' : '') + '> ' + esc(w) + '</label>'; }).join('') + '</fieldset>'
      + '<div class="btn-row"><button class="btn small" type="submit">' + (pg ? 'Save changes' : 'Create page') + '</button>' + (pg ? '<a class="btn small ghost" target="_blank" rel="noopener" href="/p/' + esc(pg.slug) + '">Open page</a><button class="btn small ghost" type="button" id="sp-del">Delete page</button>' : '') + '</div><p class="err" role="alert" id="sp-err"></p></form></div>';
    return h;
  }

  function reportCard() {
    var pro = B.plan.pro;
    return '<div class="card stack pro-card" id="rp-card"><h3>Uptime reports ' + (pro ? '<span class="pro-badge">PRO</span>' : '') + '</h3>'
      + '<p class="note" style="margin:0">' + (pro ? 'Uptime, outages and response time for the sites you watch, from our own checks. Pick a period or a past month. Pro members also get this report by email on the 1st of each month.' : 'The last 30 days for the sites you watch. Pro adds 12 months of history, any past month, CSV download and a monthly email.') + '</p>'
      + '<div class="btn-row"><select id="rp-range" aria-label="Report period"><option value="30">Last 30 days</option>' + (pro ? '<option value="90">Last 90 days</option><option value="180">Last 6 months</option><option value="365">Last 12 months</option>' : '<option value="" disabled>Last 90 days (Pro)</option><option value="" disabled>Last 12 months (Pro)</option>') + '</select>'
      + '<select id="rp-month" aria-label="Choose a month"' + (pro ? '' : ' disabled') + '><option value="">' + (pro ? 'Or choose a month' : 'Past months (Pro)') + '</option></select></div>'
      + '<div id="rp-out" class="rp-out" aria-live="polite"><div class="skeleton">Loading&hellip;</div></div>'
      + '<div class="btn-row"><a class="btn small ghost" id="rp-csv"' + (pro ? '' : ' hidden') + ' href="#">Download CSV</a><button type="button" class="btn small ghost" id="rp-print">Print</button></div></div>';
  }

  function paint() {
    root.innerHTML = '<div class="stack plan-stack">' + planCard() + phoneCard() + statusCard() + reportCard() + '</div>';
    wire(); loadReport();
  }

  function loadReport() {
    var rng = $('#rp-range'), mon = $('#rp-month'), out = $('#rp-out'), csv = $('#rp-csv');
    var q = mon.value ? 'month=' + encodeURIComponent(mon.value) : 'days=' + encodeURIComponent(rng.value || 30);
    csv.href = '/api/proreport.php?csv=1&' + q;
    S.api('proreport.php?' + q).then(function (j) {
      if (j.months && mon.options.length < 2) j.months.forEach(function (m) { var o = document.createElement('option'); o.value = m; o.textContent = new Date(m + '-01T12:00:00Z').toLocaleDateString([], { month: 'long', year: 'numeric' }); mon.appendChild(o); });
      if (!j.rows.length) { out.innerHTML = '<div class="empty-note note">You are not watching any sites yet. <a href="/monitor">Add a site to your watchlist</a> and its report appears here.</div>'; return; }
      out.innerHTML = '<p class="fine" style="margin:0 0 8px">' + esc(j.from) + ' to ' + esc(j.to) + ' (UTC)</p><div class="rp-list">'
        + j.rows.map(function (r) {
          var cls = r.uptime == null ? '' : r.uptime >= 99.9 ? 'g' : r.uptime >= 99 ? 'a' : 'o';
          var dn = r.down_min < 1 ? 'no downtime' : (r.down_min < 90 ? r.down_min + ' min' : Math.floor(r.down_min / 60) + ' h ' + (r.down_min % 60) + ' min') + ' down';
          var meta = r.checks ? esc(r.outages) + (r.outages === 1 ? ' outage' : ' outages') + ' &middot; ' + esc(dn) + (r.avg_ms != null ? ' &middot; ' + esc(r.avg_ms) + ' ms average' : '') : 'No checks recorded in this period yet';
          return '<div class="rp-row"><div class="rp-main"><b>' + esc(r.host) + '</b><small>' + meta + '</small></div><div class="rp-up ' + cls + '">' + (r.uptime == null ? '&ndash;' : esc(r.uptime) + '%') + '<small>uptime</small></div></div>';
        }).join('') + '</div><p class="fine" style="margin:8px 0 0">Measured by siteupdown.com from our own server. A guide from our own checks, not a service-level guarantee.</p>';
    }).catch(function (e) { out.innerHTML = '<div class="empty-note note">' + esc(e.message) + '</div>'; });
  }

  function wire() {
    S.$$('[data-up]', root).forEach(function (b) { b.addEventListener('click', function () { location.href = '/pricing'; }); });
    var up = $('#pl-up');
    if (up) up.addEventListener('click', function () {
      var iv = (root.querySelector('input[name=pl-int]:checked') || {}).value || 'month'; up.disabled = true; say($('#pl-err'), '');
      S.api('billing.php', { action: 'checkout', interval: iv }).then(function (j) { location.href = j.url; }).catch(function (e) { up.disabled = false; say($('#pl-err'), e.message, true); });
    });
    var po = $('#pl-portal');
    if (po) po.addEventListener('click', function () { po.disabled = true; S.api('billing.php', { action: 'portal' }).then(function (j) { location.href = j.url; }).catch(function (e) { po.disabled = false; say($('#pl-err'), e.message, true); }); });
    // phone
    var add = $('#ph-add'), ver = $('#ph-ver'), msg = $('#ph-msg');
    function ph(data, okMsg) { return S.api('phone.php', data).then(function (j) { P = j; paint(); var m = $('#ph-msg'); if (okMsg) say(m, okMsg); }).catch(function (e) { say($('#ph-msg'), e.message, true); }); }
    if (add) add.addEventListener('submit', function (e) { e.preventDefault(); say(msg, 'Sending…'); ph({ action: 'add', number: add.elements.number.value }, 'Code sent. It can take a minute to arrive.'); });
    if (ver) ver.addEventListener('submit', function (e) { e.preventDefault(); ph({ action: 'verify', code: ver.elements.code.value }, 'Number confirmed. Alerts are on.'); });
    var rm = $('#ph-rm'); if (rm) rm.addEventListener('click', function () { ph({ action: 'remove' }); });
    var pt = $('#ph-test'); if (pt) pt.addEventListener('click', function () { pt.disabled = true; say(msg, 'Sending…'); ph({ action: 'test' }, 'Test text sent.'); });
    ['#ph-sms', '#ph-call'].forEach(function (id) { var c = $(id); if (c) c.addEventListener('change', function () { ph({ action: 'prefs', sms: $('#ph-sms').checked, call: $('#ph-call').checked }, 'Saved.'); }); });
    // status page
    var sf = $('#sp-form');
    if (sf) sf.addEventListener('submit', function (e) {
      e.preventDefault(); var hosts = S.$$('input[name=hosts]:checked', sf).map(function (i) { return i.value; });
      S.api('statuspage.php', { action: 'save', slug: sf.elements.slug.value, title: sf.elements.title.value, hosts: hosts }).then(function (j) { SP = j; paint(); S.toast('Status page saved.'); }).catch(function (x) { say($('#sp-err'), x.message, true); });
    });
    var sd = $('#sp-del'); if (sd) sd.addEventListener('click', function () { if (confirm('Delete your status page? The address will stop working.')) S.api('statuspage.php', { action: 'delete' }).then(function (j) { SP = j; paint(); }); });
    // report
    ['#rp-range', '#rp-month'].forEach(function (id) { $(id).addEventListener('change', function () { if (id === '#rp-range') $('#rp-month').value = ''; else if ($('#rp-month').value) $('#rp-range').selectedIndex = -1; loadReport(); }); });
    $('#rp-print').addEventListener('click', function () { window.print(); });
  }

  function start() {
    S.api('billing.php').then(function (b) {
      B = b; var all = [Promise.resolve()];
      if (b.plan.pro) { all.push(S.api('phone.php').then(function (j) { P = j; }).catch(function () {})); all.push(S.api('statuspage.php').then(function (j) { SP = j; }).catch(function () {})); }
      return Promise.all(all);
    }).then(function () {
      paint();
      // Coming back from Stripe: the plan switches on when Stripe's message reaches us, a few seconds later. Check a few times.
      if (/[?&]plan=ok/.test(location.search) && !B.plan.pro) { var n = 0, t = setInterval(function () { n++; S.api('billing.php').then(function (b) { if (b.plan.pro || n > 12) { clearInterval(t); if (b.plan.pro) start(); } }); }, 3000); }
    }).catch(function () { root.innerHTML = '<div class="empty-note note">We could not load your plan just now. Please refresh the page.</div>'; });
  }
  var started = false;
  window.SUD_planTab = function () { if (!started) { started = true; start(); } };
  if (/[?&]plan=ok/.test(location.search)) S.toast('Thank you! Your Pro plan is being set up. It can take a few seconds to appear.');
})();
