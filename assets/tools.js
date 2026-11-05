/* Tools pages: sends the address to /api/tool.php and draws the result. */
(function () {
  'use strict';
  var root = document.querySelector('[data-tool]');
  if (!root) return;
  var tool = root.getAttribute('data-tool');
  var form = document.getElementById('tf'), input = document.getElementById('ti'), btn = document.getElementById('tb');
  var err = document.getElementById('te'), out = document.getElementById('tout');
  function e(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function pill(cls, text) { return '<span class="sp-pill ' + cls + '">' + e(text) + '</span>'; }
  function table(head, rows) {
    return '<div class="rt-wrap"><table class="rt"><thead><tr>' + head.map(function (h) { return '<th>' + e(h) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) { return '<tr>' + r.map(function (c, i) { return '<td data-l="' + e(head[i]) + '">' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  function facts(rows) {
    return '<dl class="facts">' + rows.filter(function (r) { return r[1] !== null && r[1] !== undefined && r[1] !== ''; }).map(function (r) { return '<div><dt>' + e(r[0]) + '</dt><dd>' + r[1] + '</dd></div>'; }).join('') + '</dl>';
  }
  function dur(s) { s = +s || 0; if (s >= 86400) return Math.round(s / 86400) + ' d'; if (s >= 3600) return Math.round(s / 3600) + ' h'; if (s >= 60) return Math.round(s / 60) + ' min'; return s + ' s'; }
  function codeCls(c) { return c >= 200 && c < 300 ? 'up' : c >= 300 && c < 400 ? 'unsure' : c >= 400 && c < 500 ? 'slow' : 'down'; }

  var R = {
    ports: function (d) {
      var st = { open: ['up', 'Open'], closed: ['down', 'Closed'], filtered: ['slow', 'No answer'] }[d.state] || ['slow', 'No answer'];
      var why = { open: 'Our server connected to port ' + d.port + '. Something is listening there and nothing blocked us.',
        closed: 'The server answered but refused the connection, so nothing is listening on port ' + d.port + '.',
        filtered: 'We got no reply. A firewall may be dropping the connection, or the server is off or unreachable.' }[d.state];
      return '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.host) + ' &middot; port ' + d.port + ' (' + e(d.service) + ')</b>' + pill(st[0], st[1]) + '</div><p>' + e(why) + '</p>' +
        facts([['Address tested', '<code>' + e(d.ip) + '</code>'], ['Port', d.port + ' · ' + e(d.service)], ['Connection time', d.state === 'open' ? d.ms + ' ms' : '']]) +
        '<p class="note">TCP only, tested from our server at one moment. Games often use UDP, which this does not test.</p></div>';
    },
    dns: function (d) {
      if (!d.records.length) return '<div class="sp-card"><b>No records found for ' + e(d.host) + '.</b><p class="note">The name may not exist, or it may have no records of these types.</p></div>';
      var types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'CAA'], h = '<div class="sp-card"><b>DNS records for ' + e(d.host) + '</b></div>';
      types.forEach(function (t) {
        var rows = d.records.filter(function (r) { return r.type === t; });
        if (rows.length) h += '<h3>' + t + ' records</h3>' + table(['Value', 'TTL'], rows.map(function (r) { return ['<code>' + e(r.value) + '</code>', r.ttl != null ? dur(r.ttl) : '']; }));
      });
      return h;
    },
    headers: function (d) {
      return '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.url) + '</b>' + pill(codeCls(d.code), 'HTTP ' + d.code) + '</div>' +
        facts([['Protocol', e(d.version)], ['Response time', d.ms + ' ms'], ['Server address', d.ip ? '<code>' + e(d.ip) + '</code>' : ''], ['Redirects followed', d.redirects]]) +
        (d.note ? '<p class="note">' + e(d.note) + '</p>' : '') + '</div>' +
        '<h3>Response headers</h3>' + table(['Header', 'Value'], d.headers.map(function (h) { return ['<b>' + e(h[0]) + '</b>', '<code>' + e(h[1]) + '</code>']; }));
    },
    ssl: function (d) {
      var c = d.cert, cls = c.status === 'valid' ? 'up' : (c.status === 'expiring' ? 'slow' : (c.status === 'none' ? 'unsure' : 'down'));
      var label = { valid: 'Valid', expiring: 'Expiring soon', expired: 'Expired', notyet: 'Not valid yet', mismatch: 'Wrong name', untrusted: 'Not trusted', none: 'No certificate' }[c.status] || c.status;
      var h = '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.host) + '</b>' + pill(cls, label) + '</div><p>' + e(c.note) + '</p>';
      if (c.status !== 'none') {
        h += facts([['Issued to', e(c.subject)], ['Issued by', e(c.issuer_org || c.issuer)], ['Valid from', e(c.from)], ['Expires', e(c.to) + ' (' + c.days_left + ' days)'], ['Protocol', e(c.protocol)], ['Cipher', e(c.cipher)],
          ['Key', c.key_type ? e(c.key_type + ' ' + (c.key_bits || '')) : ''], ['Serial number', c.serial ? '<code>' + e(c.serial) + '</code>' : ''], ['Fingerprint (SHA-256)', c.fingerprint ? '<code>' + e(c.fingerprint) + '</code>' : '']]) + '</div>';
        if (c.sans && c.sans.length) h += '<h3>Names covered' + (c.sans_total > c.sans.length ? ' (showing ' + c.sans.length + ' of ' + c.sans_total + ')' : '') + '</h3><p class="chips2">' + c.sans.map(function (s) { return '<code>' + e(s) + '</code>'; }).join(' ') + '</p>';
        if (c.chain && c.chain.length) h += '<h3>Certificate chain</h3>' + table(['Role', 'Name', 'Issued by'], c.chain.map(function (x) { return [e(x.role), e(x.subject), e(x.issuer)]; }));
      } else h += '</div>';
      return h;
    },
    redirects: function (d) {
      var h = '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.start) + '</b>' + pill(d.error ? 'down' : (d.hops.length > 3 ? 'slow' : 'up'), d.error ? 'Problem' : (d.hops.length - 1) + (d.hops.length === 2 ? ' redirect' : ' redirects')) + '</div>';
      if (d.error) h += '<p>' + e(d.error) + '</p>';
      h += '<p class="note">Total time ' + d.total_ms + ' ms.</p></div><ol class="hops">';
      d.hops.forEach(function (x) {
        h += '<li><div class="hop-top">' + (x.code ? pill(codeCls(x.code), x.code) : pill('down', x.err || 'error')) + ' <code>' + e(x.url) + '</code>' + (x.ms != null ? ' <span class="sp-ms">' + x.ms + ' ms</span>' : '') + '</div>' +
          (x.location ? '<div class="hop-next">&darr; redirects to <code>' + e(x.location) + '</code></div>' : '') + '</li>';
      });
      h += '</ol>';
      var first = d.hops[0];
      if (first && first.code === 302) h += '<p class="note">The first redirect is a 302 (temporary). If the move is permanent, a 301 is usually better for search engines.</p>';
      if (d.hops.length > 3 && !d.error) h += '<p class="note">That is a long chain. Each hop adds delay, so consider redirecting straight to the final address.</p>';
      return h;
    },
    whois: function (d) {
      var w = d.whois;
      if (!w) return '<div class="sp-card"><b>' + e(d.domain) + '</b><p>The registry did not give us any public registration details for this domain. Some country domains do not publish them.</p>' + (d.ns.length ? facts([['Name servers', d.ns.map(function (n) { return '<code>' + e(n) + '</code>'; }).join('<br>')]]) : '') + '</div>';
      var cls = w.days_left == null ? 'unsure' : (w.days_left < 0 ? 'down' : (w.days_left < 30 ? 'slow' : 'up'));
      return '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.domain) + '</b>' + (w.days_left != null ? pill(cls, w.days_left < 0 ? 'Expired' : w.days_left + ' days left') : '') + '</div>' +
        facts([['Registered', e(w.created)], ['Expires', e(w.expires)], ['Registrar', e(w.registrar)], ['Name servers', d.ns.map(function (n) { return '<code>' + e(n) + '</code>'; }).join('<br>')]]) + '</div>' +
        '<p class="note">Registration details come from the public registry (RDAP). Personal contact details are normally hidden.</p>';
    },
    mx: function (d) {
      var h = '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.domain) + '</b>' + pill(d.mx.length ? 'up' : 'down', d.mx.length ? d.mx.length + ' mail server' + (d.mx.length > 1 ? 's' : '') : 'No MX records') + '</div>';
      if (!d.mx.length) h += '<p>This domain has no MX records, so it cannot receive email.</p>';
      h += '</div>';
      if (d.mx.length) h += '<h3>Mail servers</h3>' + table(['Priority', 'Mail server', 'Address', 'TTL'], d.mx.map(function (m) { return [m.pri, '<code>' + e(m.host) + '</code>', m.ips.map(function (i) { return '<code>' + e(i) + '</code>'; }).join('<br>'), dur(m.ttl)]; }));
      h += '<h3>SPF record ' + pill(d.spf.length ? 'up' : 'slow', d.spf.length ? 'Found' : 'Not found') + '</h3>' + (d.spf.length ? d.spf.map(function (s) { return '<pre class="raw">' + e(s) + '</pre>'; }).join('') : '<p class="note">Without SPF, anyone can more easily send email that claims to be from this domain.</p>');
      h += '<h3>DMARC record ' + pill(d.dmarc.length ? 'up' : 'slow', d.dmarc.length ? 'Found' : 'Not found') + '</h3>' + (d.dmarc.length ? d.dmarc.map(function (s) { return '<pre class="raw">' + e(s) + '</pre>'; }).join('') : '<p class="note">A DMARC record tells receiving servers what to do with email that fails the SPF check.</p>');
      return h;
    },
    robots: function (d) {
      var h = '<div class="sp-card"><div class="sp-rhead"><b>' + e(d.url) + '</b>' + pill(d.found ? 'up' : 'unsure', d.found ? 'Found' : 'HTTP ' + d.code) + '</div>';
      (d.issues || []).forEach(function (i) { h += '<p class="issue ' + e(i.level) + '">' + e(i.text) + '</p>'; });
      h += '</div>';
      if (d.groups && d.groups.length) {
        h += '<h3>Rules by crawler</h3>';
        d.groups.forEach(function (g) {
          h += '<div class="sp-card"><b>' + g.agents.map(e).join(', ') + '</b>' +
            (g.disallow.length ? '<p class="note">Not allowed</p><p class="chips2">' + g.disallow.map(function (x) { return '<code>' + e(x) + '</code>'; }).join(' ') + '</p>' : '<p class="note">Nothing is blocked.</p>') +
            (g.allow.length ? '<p class="note">Allowed</p><p class="chips2">' + g.allow.map(function (x) { return '<code>' + e(x) + '</code>'; }).join(' ') + '</p>' : '') + '</div>';
        });
      }
      if (d.sitemaps && d.sitemaps.length) h += '<h3>Sitemaps</h3><ul>' + d.sitemaps.map(function (s) { return '<li><code>' + e(s) + '</code></li>'; }).join('') + '</ul>';
      if (d.text) h += '<h3>File contents</h3><pre class="raw">' + e(d.text) + '</pre>';
      return h;
    },
    secheaders: function (d) {
      var cls = d.grade === 'A' || d.grade === 'B' ? 'up' : (d.grade === 'C' ? 'slow' : 'down');
      var h = '<div class="sp-card grade-card"><div class="grade ' + cls + '">' + e(d.grade) + '</div><div><b>' + e(d.url) + '</b><p>Score ' + d.score + ' out of 100.</p>' +
        (d.leaks && d.leaks.length ? '<p class="note">Software details shown: ' + d.leaks.map(function (x) { return '<code>' + e(x) + '</code>'; }).join(', ') + '. Hiding version numbers makes life harder for attackers.</p>' : '') + '</div></div><ul class="sec-list">';
      d.items.forEach(function (i) {
        h += '<li>' + pill(i.status === 'ok' ? 'up' : (i.status === 'warn' ? 'slow' : 'down'), i.status === 'ok' ? 'Good' : (i.status === 'warn' ? 'Weak' : 'Missing')) + ' <b>' + e(i.name) + '</b><p>' + e(i.text) + '</p>' + (i.value ? '<code>' + e(i.value) + '</code>' : '') + '</li>';
      });
      return h + '</ul>';
    }
  };

  /* ------------ worldwide tools (Globalping): start, then poll and fill in as probes answer ------------ */
  var GP = { ping: 'ping', dnsworld: 'dns', trace: 'trace' };
  var dn = null; try { dn = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (z) {}
  function place(p) { var n = p.country ? (dn ? (dn.of(p.country) || p.country) : p.country) : ''; return e(n) + (p.city ? ' <span class="sp-ms">' + e(p.city) + '</span>' : ''); }
  var W = {
    ping: function (rs, done) {
      var ok = rs.filter(function (r) { return r.ok; }), av = ok.map(function (r) { return r.avg; }).sort(function (a, b) { return a - b; });
      var h = '<div class="sp-card"><b>' + (done ? ok.length + ' of ' + rs.length + ' places answered' : 'Waiting for probes…') + '</b>' + (av.length ? '<p class="note">Fastest ' + av[0] + ' ms, slowest ' + av[av.length - 1] + ' ms, middle ' + av[Math.floor(av.length / 2)] + ' ms.</p>' : '') + '</div>';
      return h + table(['Place', 'Average', 'Min / max', 'Loss'], rs.map(function (r) {
        return [place(r), r.ok ? '<b>' + r.avg + ' ms</b>' : pill('slow', done ? 'No answer' : 'Waiting'), r.ok ? r.min + ' / ' + r.max + ' ms' : '', r.loss != null && r.ok ? (r.loss > 0 ? pill('down', r.loss + '%') : '0%') : ''];
      }));
    },
    dnsworld: function (rs, done) {
      var groups = {}, order = [];
      rs.forEach(function (r) { if (!r.ok || !r.answers.length) return; var k = r.answers.map(function (a) { return a.value; }).sort().join('|'); if (!groups[k]) { groups[k] = 0; order.push(k); } groups[k]++; });
      var same = order.length === 1;
      var h = '<div class="sp-card"><div class="sp-rhead"><b>' + (done ? (order.length === 0 ? 'No answers' : same ? 'Same answer everywhere' : order.length + ' different answers') : 'Waiting for probes…') + '</b>' + (done && order.length ? pill(same ? 'up' : 'slow', same ? 'Fully spread' : 'Still spreading') : '') + '</div>' +
        (done && !same && order.length ? '<p class="note">Some networks may still hold an older record. Check again after the TTL has passed.</p>' : '') + '</div>';
      return h + table(['Place', 'Answer', 'TTL'], rs.map(function (r) {
        return [place(r), r.ok && r.answers.length ? r.answers.map(function (a) { return '<code>' + e(a.value) + '</code>'; }).join('<br>') : pill('slow', done ? 'No answer' : 'Waiting'), r.ok && r.answers.length && r.answers[0].ttl != null ? dur(r.answers[0].ttl) : ''];
      }));
    },
    trace: function (rs, done) {
      var h = '<div class="sp-card"><b>' + (done ? 'Trace finished' : 'Tracing…') + '</b></div>';
      rs.forEach(function (r) {
        h += '<h3>From ' + place(r) + '</h3>';
        if (!r.ok || !r.hops || !r.hops.length) { h += '<p class="note">' + (done ? 'No path returned from this place.' : 'Waiting…') + '</p>'; return; }
        h += table(['Hop', 'Host', 'Time'], r.hops.map(function (x, i) { return [i + 1, x.host ? '<code>' + e(x.host) + '</code>' : '<span class="note">no reply</span>', x.ms != null ? x.ms + ' ms' : '']; }));
      });
      return h;
    }
  };
  function runGP(addr) {
    show(''); addr = (addr || '').trim();
    if (!addr) { show('Please enter a website address like example.com.'); input.focus(); return; }
    btn.disabled = true; out.innerHTML = '<p class="note">Starting the worldwide check&hellip;</p>';
    var qt = document.getElementById('tq');
    fetch('/api/gptool.php', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-SUD': '1' }, body: JSON.stringify({ tool: GP[tool], address: addr, qtype: qt ? qt.value : undefined }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        if (!x.ok) { btn.disabled = false; out.innerHTML = ''; show(x.j.error || 'Something went wrong. Please try again.'); return; }
        if (x.j.error) { btn.disabled = false; out.innerHTML = '<div class="sp-card"><b>' + e(x.j.host) + '</b><p>' + e(x.j.error) + '</p></div>'; return; }
        try { history.replaceState(null, '', location.pathname + '?q=' + encodeURIComponent(addr)); } catch (z) {}
        var n = 0;
        (function poll() {
          fetch('/api/gptool.php?tool=' + GP[tool] + '&id=' + encodeURIComponent(x.j.id)).then(function (r) { return r.json(); }).then(function (j) {
            n++;
            if (j.results && j.results.length) out.innerHTML = W[tool](j.results, !!j.done);
            if (j.done || n > 30) { btn.disabled = false; if (!j.results || !j.results.length) out.innerHTML = '<div class="sp-card"><p>No results came back. Please try again in a minute.</p></div>'; }
            else setTimeout(poll, 1500);
          }).catch(function () { btn.disabled = false; show('Could not reach the server. Please try again.'); });
        })();
      }).catch(function () { btn.disabled = false; out.innerHTML = ''; show('Could not reach the server. Please try again.'); });
  }

  function show(m) { err.textContent = m; err.hidden = !m; }
  function run(addr) {
    show(''); addr = (addr || '').trim();
    if (!addr) { show('Please enter a website address like example.com.'); input.focus(); return; }
    btn.disabled = true; out.innerHTML = '<p class="note">Checking&hellip;</p>';
    fetch('/api/tool.php', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-SUD': '1' }, body: JSON.stringify({ tool: tool, address: addr, port: (document.getElementById('tq') || {}).value }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        btn.disabled = false;
        if (!x.ok) { out.innerHTML = ''; show(x.j.error || 'Something went wrong. Please try again.'); return; }
        if (x.j.error) { out.innerHTML = '<div class="sp-card"><b>' + e(x.j.host) + '</b><p>' + e(x.j.error) + '</p></div>'; return; }
        out.innerHTML = R[tool](x.j);
        try { history.replaceState(null, '', location.pathname + '?q=' + encodeURIComponent(addr)); } catch (z) {}
      })
      .catch(function () { btn.disabled = false; out.innerHTML = ''; show('Could not reach the server. Please try again.'); });
  }
  var go = GP[tool] ? runGP : run;
  form.addEventListener('submit', function (ev) { ev.preventDefault(); go(input.value); });
  try { var q = new URLSearchParams(location.search).get('q'); if (q) { input.value = q.slice(0, 300); go(q); } } catch (z) {}
})();
