# Extra static pages: the About additions, How we check, and the FAQ. Imported by build.py.
ABOUT_MORE = """<h2>What you will find here</h2>
<ul>
<li>The <a href="/">website checker</a>, which tests any public address from our server and fifteen places around the world.</li>
<li>Live <a href="/is-it-down/">status pages</a> for popular sites, apps and games, with uptime history and problem reports from other visitors.</li>
<li>Free <a href="/tools/">tools</a>: DNS lookup, DNS propagation, ping, traceroute, SSL, headers, redirects, WHOIS and more.</li>
<li>A <a href="/help/">help centre</a> of plain-English guides to website errors, DNS, SSL, uptime and speed.</li>
<li>A free <a href="/monitor">monitor</a> with email, Telegram, Slack and Discord alerts, for the sites you care about.</li>
</ul>
<h2>Our principles</h2>
<ul>
<li><b>Honest results.</b> A result that is only a guess is labelled as one. Read exactly how in <a href="/how-we-check">How we check</a>.</li>
<li><b>Original, useful guides.</b> The help articles are written for this site, to help you fix a problem or understand a result.</li>
<li><b>Light on data.</b> We store as little as we can. See the <a href="/privacy">privacy page</a>.</li>
<li><b>Independent.</b> We are not owned by, paid by or connected to the sites we check.</li>
</ul>
<h2>Get in touch</h2>
<p>Found a bug, spotted a wrong result, or want a site added to the lists? Use the <a href="/contact">contact page</a> or email <a href="mailto:hello@siteupdown.com">hello@siteupdown.com</a>.</p>"""

HOW = """<p class="lead">A status checker is only useful if you can trust it. This page explains, step by step, how we reach a result, and where we choose to say &ldquo;not sure&rdquo; instead of guessing.</p>
<h2>1. Our own server asks first</h2>
<p>When you check an address, our server requests the page over a secure connection, follows any redirects, and records the status code and how long it took. If nothing answers, we also try the other form of the address (with or without &ldquo;www&rdquo;), because some sites only reply on one. We only fetch public web addresses.</p>
<h2>2. Fifteen probes ask too</h2>
<p>At the same moment, probes on the public <a href="https://globalping.io" rel="noopener">Globalping</a> network request the same page from fifteen countries across six continents: the United States, Canada, Mexico, Brazil, Argentina, the United Kingdom, Germany, France, South Africa, the United Arab Emirates, India, Singapore, Japan, South Korea and Australia. If one is unavailable we use a nearby place, and we only show the places that really answered.</p>
<h2>3. What each result means</h2>
<div class="rt-wrap"><table class="rt"><thead><tr><th>Result</th><th>What it means</th></tr></thead><tbody>
<tr><td data-l="Result"><b>Up</b></td><td data-l="Meaning">The page answered normally.</td></tr>
<tr><td data-l="Result"><b>Slow</b></td><td data-l="Meaning">It answered, but took longer than usual.</td></tr>
<tr><td data-l="Result"><b>Down</b></td><td data-l="Meaning">Our server got server errors (such as 500, 502 or 503) on repeated attempts, or a site that had been answering stopped, and probes in other countries could not reach it either.</td></tr>
<tr><td data-l="Result"><b>No answer</b></td><td data-l="Meaning">Nothing replied. The site may be down, or it may be ignoring automated checks. We do not call this down.</td></tr>
<tr><td data-l="Result"><b>Not sure</b></td><td data-l="Meaning">The site replied with a block or limit (such as 403 or 429), so we cannot tell what a real visitor sees.</td></tr>
<tr><td data-l="Result"><b>Collecting data</b></td><td data-l="Meaning">A new history graph needs a few checks before it can show anything honest.</td></tr>
</tbody></table></div>
<h2>4. We avoid false alarms</h2>
<ul>
<li>A site is only recorded as down after repeated failures, not a single bad moment.</li>
<li>Before we record an outage, we ask probes in other countries. If any of them can reach the site, it is our server that is being blocked, so we do not call it down.</li>
<li>Large sites often ignore automated requests. We say so, and link you to the site so you can try it yourself.</li>
<li>Our checker says who it is. We do not pretend to be a browser to get around a site&rsquo;s protection.</li>
</ul>
<h2>5. How often we check</h2>
<ul>
<li><b>Popular sites</b> listed on our status pages are re-checked about every five minutes.</li>
<li><b>Sites on a watchlist</b> are re-checked about every minute.</li>
<li><b>The live graph</b> samples about every ten seconds while someone is watching it, and slows down if the site looks stressed.</li>
<li><b>The worldwide picture</b> on each status page is refreshed in the background, a few sites at a time, so it can be a few hours old. Its age is shown.</li>
<li><b>Certificates and domain dates</b> are checked about once a day.</li>
</ul>
<h2>6. Problem reports from visitors</h2>
<p>On each status page, visitors can report that a site is not working. Reports are anonymous and unverified, and each person can report once every 30 minutes. We show them as counts over time, so you can see whether many people are affected, but we never treat reports as proof of an outage.</p>
<h2>7. What we cannot know</h2>
<ul>
<li>A result is a snapshot of one moment, from our servers and the probes, not from your network.</li>
<li>A site that works for the probes can still fail for you because of your connection, DNS, browser or device. A site that fails for the probes can still work for you.</li>
<li>We test the page address, not every feature. A site can be reachable while its login, app or payments are broken.</li>
</ul>
<h2>Keep reading</h2>
<ul>
<li><a href="/help/how-our-checks-work">How our checks work (guide)</a></li>
<li><a href="/help/sites-that-block-automated-checks">Why some sites block automated checks</a></li>
<li><a href="/help/down-for-some-people-not-others">Why a site can be down for some people and not others</a></li>
<li><a href="/faq">Frequently asked questions</a></li>
</ul>"""

FAQ = [
    ('Is siteupdown.com free?', 'Yes. The checker, speed test, tools and status pages are free and need no sign-up. A free account adds a watchlist, uptime history and alerts.'),
    ('How do I know if a website is down for everyone or just me?', 'Paste the address into the checker. We load it from our server and from fifteen places around the world. If they can all reach it, the problem is probably on your side.'),
    ('Why is a website down?', 'Common causes are a server overloaded by traffic, a failed update, a problem at the hosting company or CDN, an expired domain or certificate, or a DNS fault. Our guide to <a href="/help/why-big-websites-go-down">why big websites go down</a> explains each.'),
    ('Why does it say No answer or Not sure instead of Down?', 'A slow or blocked reply is not proof of an outage. We only say Down when there is real evidence, so you are never told something we cannot be sure of.'),
    ('A site works for me but you say it is down. Why?', 'The site may be blocking our server, or a problem may affect some regions only. Check the worldwide results, and see <a href="/help/down-for-some-people-not-others">why a site can be down for some people and not others</a>.'),
    ('How often are sites checked?', 'Popular sites about every five minutes, and watchlist sites about every minute. The live graph updates about every ten seconds while you watch.'),
    ('Where are the checks made from?', 'From our own server, and from fifteen probes in different countries on the public Globalping network.'),
    ('Can I get an alert when my site goes down?', 'Yes. Add the site to your free watchlist on the <a href="/monitor">Monitor page</a> and choose email, Telegram, Slack or Discord alerts.'),
    ('Can you check SSL certificates and domain expiry?', 'Yes. Every check shows the certificate and the domain registration date, and the <a href="/tools/">free tools</a> go deeper.'),
    ('How can I check if my DNS change has spread?', 'Use the <a href="/tools/dns-propagation-checker">DNS propagation checker</a>, which asks DNS from fifteen places.'),
    ('Do you store my searches?', 'We keep the website name and the result in a public recent-checks list, not who asked. See the <a href="/privacy">privacy page</a>.'),
    ('Are you affiliated with the sites you check?', 'No. siteupdown.com is independent, and all names belong to their owners.'),
    ('Why are there adverts?', 'Advertising keeps the site free. Advertising cookies are only used if you allow them in our cookie choices.'),
    ('How do I report a wrong result or suggest a site?', 'Use the <a href="/contact">contact page</a>.'),
]


def build(prose, head, write, foot, html, json, re):
    prose('how-we-check.html', 'How we check', 'Exactly how siteupdown.com checks whether a website is down: our server check, fifteen worldwide probes, what each result means and what we cannot know.', '/how-we-check', HOW)
    ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in FAQ]}) + '</script>'
    h = head('Frequently asked questions — siteupdown.com', 'Answers to common questions about checking whether a website is down, how our checks work, alerts, privacy and more.', '/faq', ld).replace('{BODYATTR}', '')
    body = ('<section class="page"><div class="wrap prose"><span class="eyebrow"><i></i>siteupdown.com</span><h1 style="margin:14px 0 20px">Frequently asked questions<span class="dot">.</span></h1><div class="faq">'
            + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), a) for q, a in FAQ) +
            '</div><p style="margin-top:34px"><a href="/how-we-check">How we check</a> &middot; <a href="/help/">Help centre</a> &middot; <a href="/contact">Contact</a></p><p><a href="/">&larr; Back to the website checker</a></p></div></section>')
    write('faq.html', h + body + foot('<script src="/assets/app.js"></script>'))
