(function () {
  var f = document.getElementById('cf'); if (!f) return;
  var $ = function (i) { return document.getElementById(i); };
  var topic = $('cf-topic'), err = $('cf-err'), btn = $('cf-btn');
  var siteTopics = { wrong: 1, issue: 1, addsite: 1, complaint: 1 };
  topic.addEventListener('change', function () { $('cf-siterow').hidden = !siteTopics[topic.value]; });
  // Pre-select a topic from ?topic= and the website from ?site= (used by links elsewhere).
  try {
    var q = new URLSearchParams(location.search);
    if (q.get('topic') && topic.querySelector('option[value="' + q.get('topic').replace(/[^a-z]/g, '') + '"]')) { topic.value = q.get('topic'); topic.dispatchEvent(new Event('change')); }
    if (q.get('site')) { $('cf-site').value = q.get('site').slice(0, 253); }
  } catch (e) {}
  function show(m) { err.textContent = m; err.hidden = !m; }
  f.addEventListener('submit', function (ev) {
    ev.preventDefault(); show('');
    if (!topic.value) { show('Please choose what your message is about.'); topic.focus(); return; }
    var em = $('cf-email').value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)) { show('Please enter a valid email address so we can reply.'); $('cf-email').focus(); return; }
    if ($('cf-msg').value.trim().length < 10) { show('Please write a little more so we can help.'); $('cf-msg').focus(); return; }
    btn.disabled = true; btn.firstChild.textContent = 'Sending…';
    fetch('/api/contact.php', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic.value, name: $('cf-name').value, email: em, site: $('cf-site').value, message: $('cf-msg').value, website: $('cf-hp').value })
    }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (x) {
        if (x.ok && x.d.ok) { f.hidden = true; $('cf-ok').hidden = false; $('cf-ok').scrollIntoView({ block: 'center' }); return; }
        show(x.d.error || 'Something went wrong. Please try again, or email hello@siteupdown.com.');
        btn.disabled = false; btn.firstChild.textContent = 'Send message';
      })
      .catch(function () { show('Could not reach the server. Please try again, or email hello@siteupdown.com.'); btn.disabled = false; btn.firstChild.textContent = 'Send message'; });
  });
})();
