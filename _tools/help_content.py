# Help centre content for siteupdown.com. Imported by build.py.
# Each article: slug, cat, title, desc, body (HTML), related (slugs)

CATS = [
    ('errors', 'Error codes explained', 'What the numbers on an error page actually mean, and what to do about them.'),
    ('fix', 'Fix it from your side', 'Step-by-step checks for when a website will not load for you.'),
    ('owners', 'For website owners', 'SSL, DNS, domains, speed and uptime, in plain English.'),
    ('checks', 'How our checks work', 'What we measure, what the verdicts mean, and where the limits are.'),
]

ARTICLES = [
{
'slug': 'http-status-codes-explained', 'cat': 'errors',
'title': 'HTTP status codes explained: what 200, 301, 404 and 503 mean',
'desc': 'A plain-English guide to HTTP status codes: the 2xx, 3xx, 4xx and 5xx families, the common ones, and what each means for a visitor or a site owner.',
'related': ['error-404-not-found', 'server-errors-500-502-503-504', 'website-not-loading-checklist'],
'body': '''
<p class="lead">Every time a browser asks a website for a page, the server answers with a three-digit status code before it sends anything else. Most of the time you never see it. When something goes wrong, it is often the only clue about whose fault it is.</p>
<h2>The five families</h2>
<p>The first digit tells you the general story.</p>
<ul>
<li><b>1xx, informational.</b> The server is working on it. You almost never see these.</li>
<li><b>2xx, success.</b> The request worked. <code>200 OK</code> is the one you want.</li>
<li><b>3xx, redirection.</b> The page has moved and your browser should go somewhere else. <code>301</code> is a permanent move and <code>302</code> is a temporary one.</li>
<li><b>4xx, a problem with the request.</b> The server is up, but it will not give you that page. <code>404</code>, <code>403</code> and <code>429</code> live here.</li>
<li><b>5xx, a problem on the server.</b> The server could not do what you asked. <code>500</code>, <code>502</code>, <code>503</code> and <code>504</code> live here.</li>
</ul>
<h2>The ones you will meet most</h2>
<ul>
<li><b>200 OK</b>: the page loaded normally.</li>
<li><b>301 Moved Permanently</b>: the address has changed for good. Search engines transfer the old address&rsquo;s standing to the new one.</li>
<li><b>302 Found / 307 Temporary Redirect</b>: the page is somewhere else for now. Common for login steps and short-term campaigns.</li>
<li><b>304 Not Modified</b>: your browser already has the latest copy, so nothing was sent again. This is what makes repeat visits fast.</li>
<li><b>400 Bad Request</b>: the server could not understand the request, often because of a broken cookie or a malformed address.</li>
<li><b>401 Unauthorized</b>: you need to sign in first.</li>
<li><b>403 Forbidden</b>: the server understood you but will not let you in. See below.</li>
<li><b>404 Not Found</b>: there is nothing at that address. Read more in <a href="/help/error-404-not-found">What does a 404 mean?</a></li>
<li><b>429 Too Many Requests</b>: you, or a network you share, have made too many requests too quickly. Wait a few minutes.</li>
<li><b>500 Internal Server Error</b>: something broke on the server. <a href="/help/server-errors-500-502-503-504">More on the 5xx errors</a>.</li>
<li><b>502, 503, 504</b>: a gateway, overload or timeout problem between the servers that run the site.</li>
</ul>
<h2>Why 403 deserves a mention</h2>
<p>A <code>403</code> usually means the site is working fine and has chosen not to serve you. Typical causes are a security rule that blocks your country or network, a firewall that flags automated traffic, or a page that needs an account. Our checker reports a blocked request as <b>Inconclusive</b> rather than <b>Down</b>, because the site is clearly answering.</p>
<h2>What it means for site owners</h2>
<p>Search engines read these codes too. A page that returns <code>200</code> but shows an error message (a &ldquo;soft 404&rdquo;) confuses them. A <code>5xx</code> that lasts for days can make a page drop out of search results. Return the code that tells the truth.</p>
<p>Want to see the status code a site returns right now? <a href="/">Run a check</a>: the result shows the HTTP code, response time and redirect chain.</p>'''
},
{
'slug': 'error-404-not-found', 'cat': 'errors',
'title': 'What does a 404 Not Found error mean, and how do you fix it?',
'desc': 'A 404 means the server is working but the page is not there. Learn the common causes, what visitors can try, and how site owners should handle missing pages.',
'related': ['http-status-codes-explained', 'website-not-loading-checklist', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">A <code>404 Not Found</code> error means the server is working, but there is nothing at the address you asked for. The website is not down, the page is missing.</p>
<h2>Why you might see a 404</h2>
<ul>
<li><b>A typo in the address.</b> One wrong letter or a missing hyphen is enough.</li>
<li><b>The page was moved or deleted.</b> Sites reorganise, and old links stop working.</li>
<li><b>A broken link.</b> Someone linked to the page with the wrong address, or the link was cut off when it was pasted.</li>
<li><b>An old bookmark or search result.</b> The page existed when it was saved but has since gone.</li>
</ul>
<h2>What visitors can try</h2>
<ol>
<li>Check the address for typos, and remove anything after a question mark.</li>
<li>Go to the site&rsquo;s home page and use its search or menu to find the page.</li>
<li>Search for the page title on a search engine. The site may have moved it.</li>
<li>If a web archive has an old copy, it may show what the page said.</li>
</ol>
<p>If <i>every</i> page on a site shows a 404, even the home page, that is a different problem, usually a misconfigured server. In that case, <a href="/">run a check</a> to see how the site answers from several countries.</p>
<h2>404 or 410?</h2>
<p>A <code>410 Gone</code> says the page was removed on purpose and will not return. Search engines drop a 410 a little faster than a 404. For most sites the difference is small, and a clear 404 page is fine.</p>
<h2>For site owners</h2>
<ul>
<li><b>Redirect moved pages</b> with a <code>301</code> to the closest matching page, so visitors and search engines follow along.</li>
<li><b>Make the 404 page useful.</b> Add a search box and links to your main sections.</li>
<li><b>Return a real 404 status.</b> If an error page returns <code>200 OK</code>, search engines treat it as a normal page. This is called a soft 404.</li>
<li><b>Fix broken links</b> that you control. Search Console&rsquo;s coverage reports list the missing pages Google has found.</li>
</ul>'''
},
{
'slug': 'server-errors-500-502-503-504', 'cat': 'errors',
'title': '500, 502, 503 and 504 errors: what server errors mean',
'desc': 'Server errors in the 5xx family mean the site itself is struggling. Learn the difference between 500, 502, 503 and 504 and what to try as a visitor or an owner.',
'related': ['http-status-codes-explained', 'how-our-checks-work', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">Errors that start with a 5 are the website&rsquo;s own problem, not yours. The request reached the server, and the server was unable to answer properly.</p>
<h2>500 Internal Server Error</h2>
<p>A catch-all. Something went wrong inside the site&rsquo;s own code or configuration, and the server has no better description. Common causes are a bug after an update, a broken plugin, a script that ran out of memory, or a misconfigured file.</p>
<h2>502 Bad Gateway</h2>
<p>Large sites are often several servers working in a chain: a front server (a proxy or CDN) passes your request to a back server. A 502 means the back server sent the front one an invalid answer, or none at all. It often appears briefly while a site is being updated or restarted.</p>
<h2>503 Service Unavailable</h2>
<p>The server is up but cannot take your request right now. It is either overloaded or switched into maintenance mode on purpose. A 503 is meant to be temporary, and well-run sites send a <code>Retry-After</code> header that says when to try again.</p>
<h2>504 Gateway Timeout</h2>
<p>Like 502, but the front server gave up waiting. The back server was too slow, usually because it is overloaded or stuck on a heavy task such as a database query.</p>
<h2>What visitors can do</h2>
<ol>
<li>Wait a minute and reload. Many 5xx errors clear themselves.</li>
<li>Check whether it is down for everyone: <a href="/">paste the address into the checker</a>.</li>
<li>If it is down for everyone, there is nothing to fix on your side. Come back later, or look for the site&rsquo;s status page or social account.</li>
</ol>
<h2>What owners can do</h2>
<ul>
<li>Check the server error log first. It almost always names the file and line that failed.</li>
<li>If it started after an update, disable the last plugin, theme or change.</li>
<li>Look at memory and CPU use, and at how many requests are hitting the site.</li>
<li>Put a monitor on the site so you hear about it before your visitors do. A <a href="/monitor">free watchlist</a> emails you when a site fails twice in a row.</li>
</ul>'''
},
{
'slug': 'website-not-loading-checklist', 'cat': 'fix',
'title': 'Website not loading? A step-by-step checklist',
'desc': 'A website will not load: is it down for everyone or just you? Work through this checklist to find out and fix the problem on your side.',
'related': ['err-connection-timed-out', 'flush-dns-cache', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">When a page will not load, the cause is either the website, your connection, or something in between. This checklist narrows it down in a few minutes, starting with the quickest checks.</p>
<h2>1. Is it down for everyone?</h2>
<p><a href="/">Paste the address into the checker.</a> We load it from our own server and from twelve probes in different countries. If they can all reach it, the site is up and the problem is on your side. If most fail, the site is down and you can stop troubleshooting.</p>
<h2>2. Check the address</h2>
<p>Look for typos, a missing <code>.com</code>, or <code>http://</code> where the site needs <code>https://</code>.</p>
<h2>3. Try another site</h2>
<p>If nothing loads, your internet connection is the problem. Check Wi-Fi, restart the router (unplug it for 30 seconds), and try again.</p>
<h2>4. Try another device or network</h2>
<p>If the site loads on your phone using mobile data, the problem is your home network, router or DNS. If it fails everywhere, the problem is probably the site.</p>
<h2>5. Reload without the cache</h2>
<p>Press <code>Ctrl + F5</code> (Windows) or <code>Cmd + Shift + R</code> (Mac). An old stored copy can show an error that has already been fixed. A private window gives you a clean test.</p>
<h2>6. Turn off extensions and VPNs</h2>
<p>Ad blockers, privacy tools and VPNs can block a site, or break one part of it. Disable them one at a time and reload.</p>
<h2>7. Flush your DNS cache</h2>
<p>Your device keeps a list of site addresses. If one is out of date, the site can look down. See <a href="/help/flush-dns-cache">how to flush your DNS cache</a>.</p>
<h2>8. Check the date and time</h2>
<p>A wrong clock on your device causes certificate errors on every secure site. Set it to update automatically.</p>
<h2>9. Try again later</h2>
<p>If the checker says the site is down for everyone, nothing you do will fix it. Check the site&rsquo;s status page or social accounts, and try again in a while.</p>
<p>Still stuck on a specific error? See <a href="/help/err-connection-timed-out">ERR_CONNECTION_TIMED_OUT</a> or <a href="/help/server-errors-500-502-503-504">server errors</a>.</p>'''
},
{
'slug': 'err-connection-timed-out', 'cat': 'fix',
'title': 'How to fix ERR_CONNECTION_TIMED_OUT',
'desc': 'ERR_CONNECTION_TIMED_OUT means your browser waited and the site never answered. Learn the common causes and the fixes to try, in order.',
'related': ['website-not-loading-checklist', 'flush-dns-cache', 'server-errors-500-502-503-504'],
'body': '''
<p class="lead">Chrome shows <code>ERR_CONNECTION_TIMED_OUT</code> when it tried to connect to a site and nothing came back before the time limit. Other browsers word it differently, for example &ldquo;The connection has timed out&rdquo;, but the cause is the same.</p>
<h2>What it usually means</h2>
<p>Your browser sent a request, and no answer arrived. That happens when:</p>
<ul>
<li>the site&rsquo;s server is down or too busy to reply;</li>
<li>a firewall, security program or router is blocking the connection;</li>
<li>your internet connection is slow, unstable, or not working;</li>
<li>a proxy or VPN is getting in the way;</li>
<li>your device has a wrong or out-of-date address for the site (a DNS problem).</li>
</ul>
<h2>Fixes to try, in order</h2>
<ol>
<li><b>Check if the site is down for everyone.</b> <a href="/">Run a check.</a> If the result says Timeout or Down from several places, wait and try later. The problem is not on your side.</li>
<li><b>Test another site.</b> If nothing loads, restart your router and check your connection.</li>
<li><b>Try another network.</b> Use mobile data on your phone. If it works there, the problem is your home network.</li>
<li><b>Disable any VPN or proxy,</b> then reload.</li>
<li><b>Pause your security software or firewall</b> for a minute to test. Turn it back on straight afterwards.</li>
<li><b>Flush your DNS cache.</b> See <a href="/help/flush-dns-cache">how to flush DNS</a>.</li>
<li><b>Clear your browser&rsquo;s cache and cookies,</b> or open a private window.</li>
<li><b>Switch to a public DNS server</b> such as Google (<code>8.8.8.8</code>) or Cloudflare (<code>1.1.1.1</code>) in your network settings.</li>
</ol>
<h2>If you run the site</h2>
<p>A timeout from many places means the server is overloaded or unreachable. Check that the server is running, that port 443 is open in your firewall, and that your host is not having an outage. A <a href="/speed">speed test</a> shows whether the server answers slowly rather than not at all.</p>'''
},
{
'slug': 'flush-dns-cache', 'cat': 'fix',
'title': 'How to flush your DNS cache on Windows, Mac and Linux',
'desc': 'Clearing your DNS cache fixes sites that will not load after a move or an outage. Step-by-step commands for Windows, macOS, Linux, plus browsers.',
'related': ['website-not-loading-checklist', 'dns-propagation', 'err-connection-timed-out'],
'body': '''
<p class="lead">Your device remembers the addresses of websites it has visited, so it does not have to look them up every time. That is the DNS cache. If a site has moved to a new server, an old entry can stop it loading. Flushing the cache makes your device look the address up again.</p>
<h2>Windows 10 and 11</h2>
<ol>
<li>Click Start, type <code>cmd</code>, and open <b>Command Prompt</b>.</li>
<li>Type <code>ipconfig /flushdns</code> and press Enter.</li>
<li>You should see &ldquo;Successfully flushed the DNS Resolver Cache&rdquo;.</li>
</ol>
<h2>macOS</h2>
<ol>
<li>Open <b>Terminal</b> (Applications &rarr; Utilities).</li>
<li>Run: <code>sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder</code></li>
<li>Enter your Mac password when asked. Nothing is printed when it works.</li>
</ol>
<h2>Linux</h2>
<p>It depends on how your system handles DNS. On most modern distributions using systemd-resolved, run <code>sudo resolvectl flush-caches</code>. Older systems may use <code>sudo systemd-resolve --flush-caches</code>. If you use dnsmasq or nscd, restart that service instead.</p>
<h2>Chrome&rsquo;s own cache</h2>
<p>Chrome keeps its own list. Go to <code>chrome://net-internals/#dns</code> and press <b>Clear host cache</b>. Some newer versions of Chrome move or hide this page, in which case restarting the browser clears it.</p>
<h2>Your phone</h2>
<p>The simplest way is to turn on Airplane mode for ten seconds and turn it off again. That resets the connection and clears most stored lookups.</p>
<h2>Still not working?</h2>
<ul>
<li>Restart your router. It keeps a DNS cache too.</li>
<li>Switch to a public DNS server such as <code>1.1.1.1</code> or <code>8.8.8.8</code>.</li>
<li>If the site moved very recently, the change may not have reached every network yet. See <a href="/help/dns-propagation">what DNS propagation is</a>.</li>
</ul>
<p>Not sure the problem is yours? <a href="/">Check the site from twelve places</a> first.</p>'''
},
{
'slug': 'ssl-certificate-errors', 'cat': 'owners',
'title': 'SSL certificate errors explained: what they mean and how to fix them',
'desc': 'Why browsers warn that a connection is not private, what common SSL certificate errors mean, and how a site owner can fix an expired or mismatched certificate.',
'related': ['dns-propagation', 'domain-name-expiry', 'how-our-checks-work'],
'body': '''
<p class="lead">An SSL (more precisely TLS) certificate proves that you are talking to the real website and lets your browser encrypt the connection. When something is wrong with it, browsers show a full-page warning such as &ldquo;Your connection is not private&rdquo;.</p>
<h2>The common errors</h2>
<ul>
<li><b>Certificate expired</b> (<code>NET::ERR_CERT_DATE_INVALID</code>). The certificate is past its end date. This is the most common one, and it is nearly always the owner&rsquo;s fault: the renewal did not happen.</li>
<li><b>Name mismatch</b> (<code>NET::ERR_CERT_COMMON_NAME_INVALID</code>). The certificate was issued for a different address, for example <code>example.com</code> but not <code>www.example.com</code>.</li>
<li><b>Untrusted issuer</b> (<code>NET::ERR_CERT_AUTHORITY_INVALID</code>). The certificate was self-signed, or the chain of certificates is incomplete.</li>
<li><b>Wrong date on your device.</b> If your clock is wrong, every certificate looks expired or not yet valid.</li>
<li><b>Mixed content.</b> The page uses https, but loads an image or script over http. The padlock disappears even though the certificate itself is fine.</li>
</ul>
<h2>If you are a visitor</h2>
<p>Check that your device&rsquo;s date and time are right. Then try another network, because public Wi-Fi and some security software can interfere. Do not click through the warning on a site where you enter a password or payment details. If the warning appears on a site you own, read on.</p>
<h2>If you own the site</h2>
<ol>
<li><b>Find the expiry date.</b> <a href="/">Check your site</a>: the result shows the issuer, expiry date, and whether the certificate covers your address.</li>
<li><b>Renew or reinstall.</b> Most hosts include free certificates that renew automatically. If yours did not, reinstall it in your hosting panel.</li>
<li><b>Cover every name.</b> Make sure both the bare domain and the <code>www</code> version are on the certificate.</li>
<li><b>Install the full chain,</b> not only the main certificate, so every browser trusts it.</li>
<li><b>Redirect http to https,</b> and update any links that still use http to fix mixed content.</li>
</ol>
<h2>Never be surprised by an expiry</h2>
<p>Certificates last from a few months to a year. Add your site to the <a href="/monitor">watchlist</a>: the dashboard shows how many days each certificate has left.</p>'''
},
{
'slug': 'dns-propagation', 'cat': 'owners',
'title': 'What is DNS propagation, and why does a change take time?',
'desc': 'DNS propagation explained: why a website move or DNS change can take hours to show everywhere, what TTL is, and how to check where your change has reached.',
'related': ['flush-dns-cache', 'domain-name-expiry', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">The Domain Name System (DNS) is the internet&rsquo;s address book. It turns a name like <code>example.com</code> into the numeric address of the server that hosts the site. When you change a record, the new answer does not appear everywhere at once. That delay is called DNS propagation.</p>
<h2>Why it is not instant</h2>
<p>DNS answers are cached on purpose, so the internet does not have to ask for the same thing millions of times. Your internet provider, your router and your own device all keep a copy. Each copy is kept for as long as the record&rsquo;s <b>TTL</b> (time to live) allows.</p>
<p>So when you change a record, anyone who looked it up recently keeps seeing the old answer until their copy expires. Someone who has never visited sees the new one straight away. That is why a site can work for you and not for a friend.</p>
<h2>How long does it take?</h2>
<ul>
<li>With a short TTL of 300 seconds (five minutes), most places update within minutes.</li>
<li>With a TTL of 3,600 seconds (one hour), expect up to an hour.</li>
<li>With a TTL of 86,400 seconds (a day), expect up to a day.</li>
<li>Changing the <b>name servers</b> of a domain is slower, because the registry has its own cache. It can take up to 24 to 48 hours.</li>
</ul>
<h2>Before you move a website</h2>
<ol>
<li>A day or two before the move, lower the TTL on the records you will change to 300 seconds.</li>
<li>Make the change at a quiet time.</li>
<li>Keep the old server running until the new one is confirmed working.</li>
<li>After everything is stable, raise the TTL again.</li>
</ol>
<h2>Seeing what the world sees</h2>
<p>The <a href="/">checker</a> shows the DNS records we find for a site (A, AAAA, CNAME, MX and name servers). Our regional probes also look the site up from other countries, so differences between places show up as failures in some regions and success in others.</p>
<p>If a site still does not load on your own device after the change has had time to spread, <a href="/help/flush-dns-cache">flush your DNS cache</a>.</p>'''
},
{
'slug': 'uptime-percentages-explained', 'cat': 'owners',
'title': 'Uptime percentages explained: what 99.9% really means',
'desc': 'What 99%, 99.9% and 99.99% uptime mean in real downtime per month and per year, and how to read uptime numbers on a status page or a hosting plan.',
'related': ['how-our-checks-work', 'server-errors-500-502-503-504', 'domain-name-expiry'],
'body': '''
<p class="lead">Uptime is the share of time a website is working. It is usually shown as a percentage, and the small differences between the numbers matter more than they look.</p>
<h2>What each level allows</h2>
<p>This is how much downtime each percentage allows:</p>
<table>
<thead><tr><th>Uptime</th><th>Per month (30 days)</th><th>Per year</th></tr></thead>
<tbody>
<tr><td>99%</td><td>about 7 hours 12 minutes</td><td>about 3 days 15 hours</td></tr>
<tr><td>99.5%</td><td>about 3 hours 36 minutes</td><td>about 1 day 19 hours</td></tr>
<tr><td>99.9%</td><td>about 43 minutes</td><td>about 8 hours 46 minutes</td></tr>
<tr><td>99.99%</td><td>about 4 minutes 19 seconds</td><td>about 52 minutes</td></tr>
<tr><td>99.999%</td><td>about 26 seconds</td><td>about 5 minutes</td></tr>
</tbody></table>
<h2>How it is calculated</h2>
<p>Uptime % = (checks that succeeded &divide; total checks) &times; 100. A monitor that checks every five minutes makes 288 checks a day, so one failed check is about 0.35% of that day. Because checks are spaced out, a short outage between two checks can be missed, and a single failure can be rounded up to five minutes. Treat the figure as an estimate.</p>
<h2>Reading a hosting promise</h2>
<ul>
<li>Most shared hosting plans promise 99.9%. That is roughly 43 minutes of downtime a month before they owe you anything.</li>
<li>Read what is excluded. Planned maintenance, attacks and problems on your own site are usually not counted.</li>
<li>The remedy is usually a small credit, not compensation for lost sales.</li>
<li>Check the figure yourself instead of relying on the promise. A <a href="/monitor">monitor</a> keeps a 24-hour, 7-day and 30-day record.</li>
</ul>
<h2>How much do you need?</h2>
<p>A personal blog is fine at 99.5%. A shop that takes orders around the clock wants 99.9% or better. Each extra nine usually costs much more, because it needs duplicate servers and automatic failover. Choose the level whose downtime you can actually afford.</p>
<h2>Averages hide the pattern</h2>
<p>Ten minutes of downtime every day and one long outage a month give the same percentage, but customers experience them very differently. Look at the incident list as well as the headline number. Each monitored site&rsquo;s status page on siteupdown.com shows both.</p>'''
},
{
'slug': 'domain-name-expiry', 'cat': 'owners',
'title': 'What happens when a domain name expires?',
'desc': 'What happens to a website and its email when a domain registration expires: the grace period, the redemption period, and how to avoid losing your domain.',
'related': ['dns-propagation', 'ssl-certificate-errors', 'uptime-percentages-explained'],
'body': '''
<p class="lead">A domain name is rented, not bought. It is registered for a set period, usually one year, and has to be renewed. If it is not, the website and email attached to it stop working, and eventually somebody else can register it.</p>
<h2>The usual sequence</h2>
<p>Exact rules differ between registrars and endings such as <code>.com</code> or <code>.co.uk</code>, but the pattern is similar:</p>
<ol>
<li><b>Expiry day.</b> The registration runs out. Many registrars switch the site off, or point it at a parked page.</li>
<li><b>Grace period</b> (often up to 30 to 45 days). You can usually still renew at the normal price.</li>
<li><b>Redemption period</b> (often around 30 days). The domain is held back, and getting it restored is possible but costs a lot more.</li>
<li><b>Release.</b> The domain is deleted and becomes available for anyone to register. Domain traders watch for good names at this stage.</li>
</ol>
<h2>What stops working</h2>
<ul>
<li>The website, because the name no longer points to your server.</li>
<li>Email at that domain: messages bounce, or go to whoever holds the name next.</li>
<li>Anything that signs in using the domain, such as some apps and verification links.</li>
</ul>
<h2>How to avoid it</h2>
<ul>
<li><b>Turn on auto-renew,</b> and keep a valid payment card on file.</li>
<li><b>Check the contact email</b> on the registration. Renewal reminders go there, and an old address means you never see them.</li>
<li><b>Register for several years</b> if you plan to keep it.</li>
<li><b>Check the expiry date</b> regularly. Every check on siteupdown.com shows when the domain registration ends, so you can <a href="/">look up your own domain</a> in seconds.</li>
</ul>
<h2>If it has already lapsed</h2>
<p>Contact your registrar immediately and ask about the grace and redemption periods. Do not wait: each stage costs more, and the final one cannot be reversed.</p>'''
},
{
'slug': 'speed-up-your-website', 'cat': 'owners',
'title': 'How to speed up your website: the checks that matter most',
'desc': 'Practical ways to make a website load faster: server response time, caching, compression, image size and fewer requests, and how to measure each one.',
'related': ['how-our-checks-work', 'uptime-percentages-explained', 'server-errors-500-502-503-504'],
'body': '''
<p class="lead">A slow site loses visitors, and search engines take speed into account. Most slow sites have the same few problems, and each one can be measured.</p>
<h2>1. Measure first</h2>
<p>Run the <a href="/speed">website speed test</a>. It loads the page three times and reports the median, then splits the time into stages: finding the server (DNS), connecting, securing the connection (TLS), waiting for the first byte, and downloading. The biggest stage is where to start.</p>
<h2>2. Server response time</h2>
<p>The wait before the first byte arrives (often called TTFB) is mostly the server thinking. If it is more than about half a second, the usual fixes are better hosting, a newer PHP version, a page cache, and fewer or faster database queries.</p>
<h2>3. Turn on caching</h2>
<p>A page cache stores a finished copy of each page, so the server does not rebuild it for every visitor. Browser caching tells visitors&rsquo; browsers to keep images, styles and scripts, so a second visit is quick. Look for <code>Cache-Control</code> headers on your files.</p>
<h2>4. Compress what you send</h2>
<p>Text files (HTML, CSS, JavaScript) shrink by around 70% with gzip or Brotli compression. Most servers offer it as a setting. The speed test shows whether a page is compressed and by how much.</p>
<h2>5. Make images smaller</h2>
<p>Images are usually the heaviest part of a page. Resize them to the size they are shown at, use modern formats such as WebP or AVIF, and load images below the fold lazily.</p>
<h2>6. Fewer, lighter requests</h2>
<ul>
<li>Remove plugins, scripts and fonts you do not need.</li>
<li>Combine or delay third-party scripts such as chat boxes and trackers.</li>
<li>Use HTTP/2 or HTTP/3, which load many files at once. Our check shows which version a site uses.</li>
</ul>
<h2>7. Use a CDN</h2>
<p>A content delivery network keeps copies of your files in many countries, so visitors load them from somewhere close. It matters most when your audience is spread across the world.</p>
<h2>Check again</h2>
<p>Change one thing at a time and re-run the test, so you know what helped. Speed also varies through the day, so compare several runs.</p>'''
},
{
'slug': 'how-our-checks-work', 'cat': 'checks',
'title': 'How siteupdown.com checks a website, and what the verdicts mean',
'desc': 'How our website status checker works: the server check, the twelve regional probes, and what Up, Down, Timeout and Inconclusive each mean.',
'related': ['down-for-some-people-not-others', 'uptime-percentages-explained', 'http-status-codes-explained'],
'body': '''
<p class="lead">We would rather tell you &ldquo;not sure&rdquo; than be wrong. This page explains exactly what happens when you press Check, and what each verdict does and does not prove.</p>
<h2>The server check</h2>
<p>First, our own server looks up the site&rsquo;s address, connects to it and requests the page, as a browser would. We record the HTTP status code, the response time, the redirects followed on the way, and the details of the SSL certificate. We only contact public web addresses on the standard web ports, and we refuse private or internal addresses, so the checker cannot be used to probe someone&rsquo;s private network.</p>
<h2>The regional probes</h2>
<p>Then twelve probes on the public Globalping network, in different countries, request the same address at nearly the same moment. This shows whether a site is reachable from everywhere, or only from some places.</p>
<h2>What the verdicts mean</h2>
<ul>
<li><b>Up.</b> The site answered normally. Any response that is not a server error or a block counts, so even a 404 page means the server is alive.</li>
<li><b>Down.</b> The server returned a server error (5xx) on two attempts in a row. We always retry once before using this word.</li>
<li><b>Timeout.</b> The site did not answer in time. It may be down, overloaded, or just very slow, so we say so instead of declaring it dead.</li>
<li><b>Inconclusive.</b> We could not tell. This happens when a site blocks automated requests (a 401, 403, 429 or 451 response), when the name does not resolve, when we cannot connect or verify the secure connection from our server, or when a site redirects in a loop. None of these proves the site is down, so we do not say it is.</li>
</ul>
<h2>Down for everyone, or just you?</h2>
<p>If the server check and most probes succeed, the site is up and the problem is likely your own network, DNS, browser or device. If most fail, it is down for everyone. Mixed results usually mean a regional problem. See <a href="/help/down-for-some-people-not-others">why a site can be down for some people and not others</a>.</p>
<h2>Watchlist alerts</h2>
<p>Watched sites are re-checked about every minute. To avoid false alarms, a site is only reported as down after <b>two failed checks in a row</b>, and you get a second email when it recovers, with how long it was down. Inconclusive results never trigger an alert, while a Timeout counts as a failed check.</p>
<h2>The limits</h2>
<p>Every result is a snapshot of one moment. A short outage between two checks can be missed, and a site behind a strict firewall may look worse than it is for real visitors. Use the result as strong evidence, not as proof.</p>'''
},
{
'slug': 'down-for-some-people-not-others', 'cat': 'checks',
'title': 'Why a website can be down for some people and not others',
'desc': 'A site that loads for your friend but not for you: the real reasons, from DNS and CDN problems to regional outages, ISP faults, firewalls and blocked countries.',
'related': ['website-not-loading-checklist', 'dns-propagation', 'how-our-checks-work'],
'body': '''
<p class="lead">&ldquo;It works for me&rdquo; and &ldquo;it is down for me&rdquo; can both be true at the same time. A website is not one machine in one place, and the path between each visitor and the site is different.</p>
<h2>The usual reasons</h2>
<ul>
<li><b>DNS differences.</b> Different networks may have different cached answers. After a site moves, some people reach the new server and some still reach the old one. See <a href="/help/dns-propagation">DNS propagation</a>.</li>
<li><b>CDN or regional servers.</b> Large sites run many servers around the world. One region&rsquo;s servers can fail while the rest are fine, so people in that region see errors.</li>
<li><b>Internet provider faults.</b> A broken route between your provider and the site makes it unreachable only for that provider&rsquo;s customers.</li>
<li><b>Blocking and geo-restrictions.</b> A site may block certain countries, networks, VPNs or automated traffic. You get a 403 or a blank page while others do not.</li>
<li><b>Security software.</b> A firewall, antivirus or parental filter on your network or device can block a site that is fine for everyone else.</li>
<li><b>Overload.</b> A busy site may reject some requests and accept others, so it feels random.</li>
<li><b>Certificate or time problems.</b> A wrong clock on your device makes secure sites fail. A certificate problem on only some servers affects only some visitors.</li>
</ul>
<h2>How to find out which one it is</h2>
<ol>
<li><a href="/">Run a check.</a> If the regional probes show a mix of successes and failures, the problem is regional. Our <b>regional map</b> shows where the failures are.</li>
<li>Try your phone on mobile data. If it works there, the problem is your network.</li>
<li>Try a different DNS server and <a href="/help/flush-dns-cache">flush your DNS cache</a>.</li>
<li>Turn off any VPN, and test without extensions.</li>
</ol>
<h2>What it means for site owners</h2>
<p>If visitors in one country report problems and your own tests are fine, check your CDN&rsquo;s status page, your firewall rules, and any country blocks. Monitoring from several regions, as our worldwide check does, catches these problems that a single-location monitor misses.</p>'''
},
]

BY_SLUG = {a['slug']: a for a in ARTICLES}
