/* What is my IP: reads your connection details from Cloudflare in your own browser. Nothing is sent to or stored by siteupdown.com. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var ip = '';
  function row(k, v) { return v ? '<div><dt>' + esc(k) + '</dt><dd>' + v + '</dd></div>' : ''; }
  function draw(m) {
    ip = String(m.clientIp || '');
    if (!ip) { fail(); return; }
    var v6 = ip.indexOf(':') > -1;
    $('ip-big').textContent = ip;
    $('ip-kind').textContent = v6 ? 'IPv6 address' : 'IPv4 address';
    $('ip-copy').hidden = false;
    var place = [m.city, m.region, m.country].filter(Boolean).join(', ');
    var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (z) {}
    $('ip-facts').innerHTML =
      row('Internet provider', esc(m.asOrganization || '')) + row('Network number (ASN)', m.asn ? 'AS' + esc(m.asn) : '') +
      row('Approximate location', esc(place)) + row('Provider time zone', esc(m.timezone || '')) +
      row('Connection', esc([m.httpProtocol, m.tlsVersion].filter(Boolean).join(' · '))) +
      row('Your browser language', esc(navigator.language || '')) + row('Your device time zone', esc(tz));
    $('ip-facts').hidden = false;
    $('ip-note').hidden = false;
  }
  function fail() { $('ip-big').textContent = 'Could not find it'; $('ip-kind').textContent = 'Check your connection, turn off any ad blocker for this page, and try again.'; }
  function load() {
    $('ip-big').textContent = 'Looking…'; $('ip-kind').textContent = '';
    fetch('https://speed.cloudflare.com/meta', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(draw).catch(fail);
  }
  $('ip-copy').addEventListener('click', function () {
    var b = this, t = b.firstElementChild;
    try { navigator.clipboard.writeText(ip).then(function () { t.textContent = 'Copied'; setTimeout(function () { t.textContent = 'Copy address'; }, 1800); }); } catch (x) { t.textContent = 'Press and hold to copy'; }
  });
  $('ip-again').addEventListener('click', load);
  load();
})();
