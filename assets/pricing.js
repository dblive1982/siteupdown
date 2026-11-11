/* Pricing page: the Upgrade button. Takes signed-in users to Stripe, sends others to sign in first. */
(function () {
  'use strict';
  var S = window.SUD, go = document.getElementById('pr-go'); if (!S || !go) return;
  var err = document.getElementById('pr-err'), yr = document.getElementById('pr-year'), note = document.getElementById('pr-note'), on = false, price = null;
  S.api('billing.php').then(function (b) {
    on = !!b.on; price = b;
    if (b.price_year) { yr.hidden = false; yr.innerHTML = 'or &pound;' + S.esc(b.price_year) + ' a year, which is two months free.'; }
    if (b.plan && b.plan.pro) { go.textContent = 'You have Pro'; go.disabled = true; note.innerHTML = 'Manage it from <a href="/account#plan">your account</a>.'; return; }
    if (!on) { go.textContent = 'Opening soon'; go.disabled = true; note.textContent = 'Pro is opening soon. Everything else on siteupdown.com is free in the meantime.'; }
  }).catch(function () { go.textContent = 'Opening soon'; go.disabled = true; });
  go.addEventListener('click', function () {
    err.textContent = '';
    S.onReady(function (u) {
      if (!u) { location.href = '/login?next=' + encodeURIComponent('/pricing'); return; }
      go.disabled = true;
      S.api('billing.php', { action: 'checkout', interval: 'month' }).then(function (j) { location.href = j.url; }).catch(function (e) { go.disabled = false; err.textContent = e.message; });
    });
  });
})();
