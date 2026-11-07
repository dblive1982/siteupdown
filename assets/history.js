/* Outage history: a permanent day-by-day record. Dates are UTC. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var dateEl = $('hs-date'); if (!dateEl) return;
  var out = $('hs-out'), title = $('hs-title'), days = $('hs-days'), q = $('hs-q'), allBtn = $('hs-all');
  var LAB = { site: 'Website not loading', login: 'Cannot log in', app: 'App not working', slow: 'Very slow' };
  var host = '', today = new Date().toISOString().slice(0, 10), cur = today;
  var m = /[?&]host=([a-z0-9.-]+)/i.exec(location.search); if (m) { host = m[1].toLowerCase(); q.value = host; }
  var d1 = /[?&]date=(\d{4}-\d{2}-\d{2})/.exec(location.search); if (d1 && d1[1] <= today) cur = d1[1];
  dateEl.max = today;

  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function nice(d) { try { return new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }); } catch (e) { return d; } }
  function shift(d, n) { var t = new Date(d + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + n); return t.toISOString().slice(0, 10); }
  function mins(n) { return n < 60 ? n + ' min' : Math.floor(n / 60) + ' h ' + (n % 60 ? (n % 60) + ' min' : '').trim(); }

  function row(r) {
    var c = el('div', 'hs-row'), h = el('div', 'hs-name');
    var a = r.page ? el('a', null, r.name) : el('b', null, r.name); if (r.page) a.href = r.page; h.appendChild(a); c.appendChild(h);
    var tags = el('div', 'hs-tags');
    if (r.outages) tags.appendChild(el('span', 'hs-tag bad', 'Detected down ' + r.outages + (r.outages === 1 ? ' time' : ' times') + (r.down_min ? ', ' + mins(r.down_min) + ' in total' : '')));
    Object.keys(LAB).forEach(function (k) { if (r.kinds && r.kinds[k]) tags.appendChild(el('span', 'hs-tag s-' + k, LAB[k] + ': ' + r.kinds[k])); });
    if (r.fixed) tags.appendChild(el('span', 'hs-tag s-fixed', 'Said it worked again: ' + r.fixed));
    c.appendChild(tags); return c;
  }
  function loadDay() {
    dateEl.value = cur; title.textContent = nice(cur) + (host ? ' · ' + host : '');
    out.textContent = ''; out.appendChild(el('p', 'note', 'Loading…'));
    fetch('/api/history-day.php?date=' + cur + (host ? '&host=' + encodeURIComponent(host) : ''), { credentials: 'same-origin' }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); }).then(function (r) {
      out.textContent = '';
      if (!r.ok) { out.appendChild(el('p', 'note', r.j.error || 'Could not load that day.')); return; }
      var j = r.j;
      if (!j.rows.length) { out.appendChild(el('p', 'note', 'Nothing was reported or detected' + (host ? ' for ' + host : '') + ' on this day.' + (cur === today ? ' Today is still in progress.' : ''))); return; }
      out.appendChild(el('p', 'hs-sum', j.total_reports + (j.total_reports === 1 ? ' visitor report' : ' visitor reports') + ' and ' + j.total_outages + (j.total_outages === 1 ? ' outage' : ' outages') + ' detected by our checks.'));
      j.rows.forEach(function (r2) { out.appendChild(row(r2)); });
    }).catch(function () { out.textContent = ''; out.appendChild(el('p', 'note', 'Could not load that day just now.')); });
    try { history.replaceState(null, '', '/outage-history?' + (host ? 'host=' + encodeURIComponent(host) + '&' : '') + 'date=' + cur); } catch (e) {}
  }
  function loadDays() {
    allBtn.hidden = !host;
    fetch('/api/history-day.php?days=1' + (host ? '&host=' + encodeURIComponent(host) : ''), { credentials: 'same-origin' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      days.textContent = '';
      var list = (j && j.days) || [];
      if (!list.length) { days.appendChild(el('li', 'rf-none', 'No days recorded yet. The record builds up as visitors report problems and our checks run.')); return; }
      list.forEach(function (d) {
        var li = el('li', 'hs-day'), b = el('button', 'hs-daybtn', nice(d.day)); b.type = 'button';
        b.addEventListener('click', function () { cur = d.day; loadDay(); window.scrollTo({ top: 0, behavior: 'smooth' }); });
        var sm = el('small', null, d.reports + (d.reports === 1 ? ' report' : ' reports') + (d.outages ? ' · ' + d.outages + (d.outages === 1 ? ' outage' : ' outages') : ''));
        li.appendChild(el('i', 'kdot ' + (d.outages ? 's-site' : 's-login'))); li.appendChild(b); li.appendChild(sm); days.appendChild(li);
      });
    }).catch(function () { days.textContent = ''; });
  }
  dateEl.addEventListener('change', function () { if (dateEl.value && dateEl.value <= today) { cur = dateEl.value; loadDay(); } });
  $('hs-prev').addEventListener('click', function () { cur = shift(cur, -1); loadDay(); });
  $('hs-next').addEventListener('click', function () { if (cur < today) { cur = shift(cur, 1); loadDay(); } });
  $('hs-today').addEventListener('click', function () { cur = today; loadDay(); });
  $('hs-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var v = q.value.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split(/[\/?#]/)[0];
    host = /^[a-z0-9.-]{3,253}$/.test(v) ? v : ''; q.value = host; loadDay(); loadDays();
  });
  allBtn.addEventListener('click', function () { host = ''; q.value = ''; loadDay(); loadDays(); });
  loadDay(); loadDays();
})();
