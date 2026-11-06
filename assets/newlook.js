/* siteupdown.com — new look behaviour: slide-out menu, collapsed sections that open from links, results panel. No dependencies. */
(function () {
  var d = document;
  var btn = d.getElementById('nl-menu-btn'), drawer = d.getElementById('nl-drawer'), scrim = d.getElementById('nl-scrim'), closeB = d.getElementById('nl-close');
  function setOpen(o) {
    if (!btn || !drawer) return;
    drawer.classList.toggle('open', o); btn.setAttribute('aria-expanded', o ? 'true' : 'false'); btn.setAttribute('aria-label', o ? 'Close menu' : 'Open menu');
    if (scrim) scrim.hidden = !o; d.body.style.overflow = o ? 'hidden' : '';
    if (o && closeB) closeB.focus(); else if (!o) btn.focus && btn.focus({ preventScroll: true });
  }
  if (scrim) scrim.hidden = true;
  if (btn) btn.addEventListener('click', function () { setOpen(!drawer.classList.contains('open')); });
  if (closeB) closeB.addEventListener('click', function () { setOpen(false); });
  if (scrim) scrim.addEventListener('click', function () { setOpen(false); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && drawer && drawer.classList.contains('open')) setOpen(false); });
  if (drawer) drawer.addEventListener('click', function (e) { var a = e.target.closest && e.target.closest('a'); if (a) setOpen(false); });
  var here = location.pathname.replace(/\/$/, '') || '/';
  if (drawer) Array.prototype.forEach.call(drawer.querySelectorAll('a'), function (a) { var p = a.getAttribute('href').replace(/\/$/, '') || '/'; if (p === here) a.setAttribute('aria-current', 'page'); });

  /* open the collapsed section that holds a link target (#top-sites, #faq ...) */
  function openFor(id) {
    if (!id) return;
    var el = d.getElementById(id); if (!el) return;
    var det = el.closest ? el.closest('details') : null;
    while (det) { det.open = true; det = det.parentElement ? det.parentElement.closest('details') : null; }
    setTimeout(function () { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 30);
  }
  function fromHash() { var h = location.hash; if (h.length > 1) openFor(decodeURIComponent(h.slice(1))); }
  window.addEventListener('hashchange', fromHash); fromHash();
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a) return;
    var id = a.getAttribute('href').slice(1); if (id && d.getElementById(id) && d.getElementById(id).closest('details')) { e.preventDefault(); openFor(id); }
  });

  /* the results panel stays hidden until a check has run */
  var pulse = d.getElementById('global-pulse'), st = d.getElementById('pulse-status');
  if (pulse && st) {
    var check = function () { var t = (st.textContent || '').trim(); if (t && t !== 'Standby') pulse.classList.add('on'); };
    check(); new MutationObserver(check).observe(st, { childList: true, characterData: true, subtree: true });
    var f = d.getElementById('chk-form'); if (f) f.addEventListener('submit', function () { setTimeout(function () { pulse.classList.add('on'); }, 50); });
  }
})();
