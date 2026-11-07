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
<p><a href="/">Paste the address into the checker.</a> We load it from our own server and from fifteen probes in different countries. If they can all reach it, the site is up and the problem is on your side. If most fail, the site is down and you can stop troubleshooting.</p>
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
<p>Not sure the problem is yours? <a href="/">Check the site from fifteen places</a> first.</p>'''
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
'desc': 'How our website status checker works: the server check, the fifteen regional probes, and what Up, Down, Timeout and Inconclusive each mean.',
'related': ['down-for-some-people-not-others', 'uptime-percentages-explained', 'http-status-codes-explained'],
'body': '''
<p class="lead">We would rather tell you &ldquo;not sure&rdquo; than be wrong. This page explains exactly what happens when you press Check, and what each verdict does and does not prove.</p>
<h2>The server check</h2>
<p>First, our own server looks up the site&rsquo;s address, connects to it and requests the page, as a browser would. We record the HTTP status code, the response time, the redirects followed on the way, and the details of the SSL certificate. We only contact public web addresses on the standard web ports, and we refuse private or internal addresses, so the checker cannot be used to probe someone&rsquo;s private network.</p>
<h2>The regional probes</h2>
<p>Then fifteen probes on the public Globalping network, in different countries, request the same address at nearly the same moment. This shows whether a site is reachable from everywhere, or only from some places.</p>
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
{
'slug': 'error-403-forbidden', 'cat': 'errors',
'title': 'What does a 403 Forbidden error mean?',
'desc': 'A 403 means the website understood your request but refused it. Here are the common causes, from blocked networks and VPNs to permissions, and what you can try.',
'related': ['http-status-codes-explained', 'down-for-some-people-not-others', 'website-not-loading-checklist'],
'body': '''
<p class="lead">A <code>403 Forbidden</code> error means the server is working and received your request, but it has decided not to let you have the page. That is different from a 404, where the page does not exist, and from a 5xx error, where the server itself is struggling.</p>
<h2>Common causes</h2>
<ul>
<li><b>You are not allowed to see that page.</b> Some pages are for signed-in users, staff or members only.</li>
<li><b>Your network or country is blocked.</b> Websites sometimes refuse traffic from certain countries, hosting providers, VPNs or shared networks that have caused trouble before.</li>
<li><b>A security filter flagged the request.</b> Firewalls and bot protection can block a visitor who looks like an automated program. A browser with unusual settings, extensions or a very old version can trigger this.</li>
<li><b>Wrong permissions on the server.</b> If you run the site, a file or folder may be set so the web server cannot read it. This is a very common cause for new sites.</li>
<li><b>A missing index file.</b> If a folder has no default page and directory listing is switched off, many servers answer 403.</li>
</ul>
<h2>What visitors can try</h2>
<ol>
<li>Reload the page, then check the address for typing mistakes.</li>
<li>Sign in if the page belongs to an account area.</li>
<li>Turn off any VPN or proxy and try again. Then try mobile data instead of Wi-Fi.</li>
<li><a href="/help/clear-browser-cache-and-cookies">Clear the site&rsquo;s cookies and cache</a>, which can remove a stale login that causes the refusal.</li>
<li>If the page works for other people, it is probably something about your network. Contact the site&rsquo;s support and tell them roughly when it happened.</li>
</ol>
<h2>What site owners should check</h2>
<ul>
<li>File permissions: folders are usually 755 and files 644.</li>
<li>That the folder has an index file such as <code>index.html</code> or <code>index.php</code>.</li>
<li>Firewall, security plugin and CDN rules that might be blocking legitimate visitors or tools.</li>
<li>Any country or IP blocks you have set up.</li>
</ul>
<h2>403 and uptime checks</h2>
<p>Many large websites answer automated checks with a 403 on purpose, even when they work perfectly for people. When our server gets a 403 we do not call the site down. We report that it blocks automated checks, because a refusal is not an outage. See <a href="/help/sites-that-block-automated-checks">Why some sites block automated checks</a>.</p>
'''
},
{
'slug': 'error-429-too-many-requests', 'cat': 'errors',
'title': 'What does a 429 Too Many Requests error mean?',
'desc': 'A 429 error means you, or the network you share, sent too many requests too quickly. Learn why it happens and how long to wait.',
'related': ['http-status-codes-explained', 'error-403-forbidden', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">A <code>429 Too Many Requests</code> error is the website asking you to slow down. It is a deliberate limit, not a breakage. Servers use these limits, called rate limits, to stay fast for everyone and to stop abuse.</p>
<h2>Why you might see it</h2>
<ul>
<li><b>You refreshed or clicked very quickly.</b> Repeated reloads can reach the limit within seconds.</li>
<li><b>You share a network.</b> Offices, schools, mobile networks and VPNs put many people behind one address, so their combined traffic can hit the limit even when you have done little.</li>
<li><b>A browser extension or app is making extra requests</b> in the background.</li>
<li><b>An automated tool or script is calling the site</b> too often.</li>
<li><b>The site is under heavy load</b> and has tightened its limits temporarily.</li>
</ul>
<h2>What to do</h2>
<ol>
<li>Wait a few minutes without reloading. Some sites say how long in a <code>Retry-After</code> message.</li>
<li>Close extra tabs and pause any extensions that interact with the site.</li>
<li>Switch from a VPN or shared network to your own connection, or the other way round.</li>
<li>Try again later. Limits usually reset within minutes or an hour.</li>
</ol>
<h2>If you run the site or write the tool</h2>
<p>Slow your requests down, spread them out, and respect the <code>Retry-After</code> header. If real visitors are being limited, raise the limit or give known users a higher one. Rate limits that are too tight look like an outage to visitors.</p>
<h2>How we treat 429 answers</h2>
<p>A 429 from our checking server does not mean a site is down. It means the site declined to answer us at that moment, so we mark the result as inconclusive rather than reporting an outage.</p>
'''
},
{
'slug': 'dns-probe-finished-nxdomain', 'cat': 'fix',
'title': 'Fix &ldquo;server not found&rdquo; and DNS_PROBE_FINISHED_NXDOMAIN',
'desc': 'What the DNS errors in Chrome, Edge, Firefox and Safari mean, and a step-by-step way to fix them on your device, your router or the website itself.',
'related': ['flush-dns-cache', 'dns-propagation', 'website-not-loading-checklist'],
'body': '''
<p class="lead">Messages such as <code>DNS_PROBE_FINISHED_NXDOMAIN</code>, &ldquo;Server not found&rdquo; and &ldquo;We can&rsquo;t find that site&rdquo; all mean the same thing: your device could not turn the website&rsquo;s name into an address. The website may be fine. The lookup failed.</p>
<h2>Why a lookup fails</h2>
<ul>
<li>The address was typed wrongly.</li>
<li>The domain has expired or has not been set up yet.</li>
<li>Your device or router has a stale or broken DNS cache.</li>
<li>Your internet provider&rsquo;s DNS server is having trouble.</li>
<li>A VPN, security tool or parental filter is intercepting the lookup.</li>
</ul>
<h2>Fixes, in the order to try them</h2>
<ol>
<li><b>Check the spelling</b> of the address, including the ending such as .com or .co.uk.</li>
<li><b>Run a check on siteupdown.com.</b> If our probes reach the site, the problem is on your side. If none do, the site&rsquo;s DNS or hosting is the problem.</li>
<li><b>Try another network.</b> Switch from Wi-Fi to mobile data. If it works, your router or provider is the issue.</li>
<li><b>Restart your router</b> and wait two minutes.</li>
<li><b><a href="/help/flush-dns-cache">Flush your DNS cache.</a></b></li>
<li><b>Change your DNS server</b> to a public one in your network settings, then try again.</li>
<li><b>Turn off VPNs and filters</b> for a minute to see whether they are the cause.</li>
</ol>
<h2>If the website is yours</h2>
<p>Check that the domain has not expired, the nameservers are correct, and the right A or CNAME record exists. Remember that changes can take a while to spread, as explained in <a href="/help/dns-propagation">DNS propagation</a>.</p>
'''
},
{
'slug': 'works-on-mobile-data-not-wifi', 'cat': 'fix',
'title': 'A website works on mobile data but not on Wi-Fi: why and how to fix it',
'desc': 'When a site loads on your phone&rsquo;s data but not on your home or office Wi-Fi, the problem is almost always your network. Here are the usual causes and fixes.',
'related': ['website-not-loading-checklist', 'dns-probe-finished-nxdomain', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">If a website loads on mobile data but not on Wi-Fi, you have already learned the most useful fact: the site is up, and the fault is somewhere between your device and the internet on that Wi-Fi network.</p>
<h2>The usual causes</h2>
<ul>
<li><b>A stale DNS cache on the router.</b> The router remembers an old address for the site.</li>
<li><b>Your provider&rsquo;s DNS or routing.</b> Some providers have problems reaching particular sites.</li>
<li><b>Filtering.</b> Parental controls, network-level ad blockers or security services may block the site.</li>
<li><b>IPv6 trouble.</b> Some networks hand out IPv6 addresses that do not work properly with certain sites.</li>
<li><b>A wrong clock or a captive-portal login</b> on public Wi-Fi.</li>
</ul>
<h2>What to try</h2>
<ol>
<li>Restart the router and wait a couple of minutes.</li>
<li>Disconnect and reconnect your device to the Wi-Fi.</li>
<li><a href="/help/flush-dns-cache">Flush the DNS cache</a> on your device.</li>
<li>Switch your DNS server to a public one in the router or device settings.</li>
<li>Check whether a filter, VPN or security app is blocking the site.</li>
<li>On public Wi-Fi, open a plain website to trigger the sign-in page.</li>
<li>If nothing helps, contact your internet provider and tell them which site and the time you tried.</li>
</ol>
<h2>Prove it is not the site</h2>
<p>Run the address through the <a href="/">checker</a>. If the probes around the world reach the site, you can tell your provider or network admin with confidence that the site works elsewhere.</p>
'''
},
{
'slug': 'clear-browser-cache-and-cookies', 'cat': 'fix',
'title': 'How to clear the cache and cookies for one website',
'desc': 'Clearing the cache and cookies for a single site can fix pages that look broken, keep redirecting or refuse to log in. Steps for Chrome, Edge, Firefox and Safari.',
'related': ['website-not-loading-checklist', 'error-403-forbidden', 'flush-dns-cache'],
'body': '''
<p class="lead">Your browser keeps copies of pages and small files, called the cache, plus cookies that remember who you are. When they go stale they can cause pages that look broken, endless redirects and sign-in problems, even when the website is working.</p>
<h2>The quick test first</h2>
<p>Open the site in a private or incognito window. If it works there, the cause is something saved in your normal browser: the cache, cookies or an extension.</p>
<h2>Clear it for one site</h2>
<ul>
<li><b>Chrome and Edge:</b> click the icon to the left of the address, choose <i>Cookies and site data</i> or <i>Site settings</i>, then <i>Clear data</i>.</li>
<li><b>Firefox:</b> click the padlock, choose <i>Clear cookies and site data</i>.</li>
<li><b>Safari on Mac:</b> Settings, Privacy, <i>Manage Website Data</i>, search for the site and remove it.</li>
<li><b>iPhone and iPad:</b> Settings, Safari, Advanced, <i>Website Data</i>, search for the site and remove it.</li>
<li><b>Android Chrome:</b> tap the menu, Settings, Site settings, All sites, find the site and clear its data.</li>
</ul>
<h2>A hard refresh</h2>
<p>On a computer, press <b>Ctrl+Shift+R</b> (or <b>Cmd+Shift+R</b> on a Mac) to reload the page and ignore the saved copy.</p>
<h2>What you lose</h2>
<p>Clearing a site&rsquo;s cookies signs you out and removes saved preferences for that site only. Other sites are not touched.</p>
<h2>If it still fails</h2>
<p>Turn off extensions one by one, then use the <a href="/help/website-not-loading-checklist">website not loading checklist</a>. Running the address through our <a href="/">checker</a> tells you whether the site is down for everyone.</p>
'''
},
{
'slug': 'sites-that-block-automated-checks', 'cat': 'checks',
'title': 'Why some sites block automated checks, and what we say when that happens',
'desc': 'Many big websites refuse requests from monitoring tools. Here is why, how it shows up as a 403, 429 or timeout, and how siteupdown.com avoids calling those sites down.',
'related': ['how-our-checks-work', 'error-403-forbidden', 'down-for-some-people-not-others'],
'body': '''
<p class="lead">A site that loads perfectly for you can still refuse to answer a checking tool. This is one of the main reasons uptime checkers disagree with each other, and it is why we are careful about the word &ldquo;down&rdquo;.</p>
<h2>Why sites do this</h2>
<ul>
<li><b>Bot protection.</b> Security services look for traffic from data centres and block anything that does not look like a normal person with a normal browser.</li>
<li><b>Scraping and abuse.</b> Sites protect their content and prices from copying.</li>
<li><b>Rate limits.</b> Too many requests from one address earn a refusal.</li>
<li><b>Country or network rules.</b> Some sites only answer certain regions.</li>
</ul>
<h2>What it looks like to us</h2>
<ul>
<li>A <code>403</code>, <code>429</code> or similar refusal.</li>
<li>A page that never answers, which shows as a timeout.</li>
<li>A challenge page instead of the real page.</li>
</ul>
<h2>What we do about it</h2>
<ol>
<li>A site is only called <b>down</b> after it returns a server error twice. A refusal is not an error of that kind.</li>
<li>Refusals and timeouts are labelled <b>blocked</b>, <b>no answer</b> or <b>inconclusive</b>, never down.</li>
<li>If our server cannot reach a site but probes in other countries can, we say so.</li>
<li>If we cannot be sure, we say we cannot be sure, and give you a link to open the site yourself.</li>
</ol>
<h2>What you can do</h2>
<p>Open the site in your own browser. If it loads, it is up for you. If it does not, try the <a href="/help/website-not-loading-checklist">checklist</a> and look at the site&rsquo;s official status page or social account, which are the most reliable sources during a large outage.</p>
<p>We do not disguise our checks as a browser. Being open about what we are is part of how we keep our results honest.</p>
'''
},
{
'slug': 'is-it-down-or-just-me', 'cat': 'checks',
'title': 'How to tell if a website is down for everyone or just you',
'desc': 'A simple four-step method to work out whether a site is down for everyone or only for you, using a checker, another network, another device and the site&rsquo;s own status page.',
'related': ['website-not-loading-checklist', 'down-for-some-people-not-others', 'how-our-checks-work'],
'body': '''
<p class="lead">When a page will not load, the first question is whose problem it is. These four steps answer it in about a minute.</p>
<h2>Step 1: ask a checker</h2>
<p>Enter the address into the <a href="/">siteupdown.com checker</a>. We load it from our own server and from probes in several countries at the same time. If most of them reach the site, it is up and the problem is likely on your side. If most fail, it is down for everyone.</p>
<h2>Step 2: change your network</h2>
<p>Turn off Wi-Fi and try on mobile data, or the other way round. If it loads on one but not the other, your network or provider is the cause.</p>
<h2>Step 3: change your device or browser</h2>
<p>Try another browser, a private window or another device. If that works, the cause is your browser&rsquo;s saved data or an extension. See <a href="/help/clear-browser-cache-and-cookies">how to clear it</a>.</p>
<h2>Step 4: check the source</h2>
<p>Large services have an official status page or a social media account that announces problems. These are the best source during a big outage, and they are often updated before any checker notices.</p>
<h2>Reading the results</h2>
<ul>
<li><b>Up for everyone:</b> every probe reached it. Look at your own connection.</li>
<li><b>Reachable from some places:</b> a regional problem. Your region may be affected.</li>
<li><b>Down for everyone:</b> nothing reaches it. Wait and try again later.</li>
<li><b>Blocking automated checks or no answer:</b> the site may be fine but refuses tools. Open it in your browser to be sure.</li>
</ul>
'''
},
{
'slug': 'why-big-websites-go-down', 'cat': 'owners',
'title': 'Why big websites go down: cloud, CDN and DNS failures',
'desc': 'Even huge services have outages. The usual causes are configuration mistakes, overloaded servers, cloud and CDN failures and DNS problems. Here is how they work and why they spread.',
'related': ['server-errors-500-502-503-504', 'dns-propagation', 'uptime-percentages-explained'],
'body': '''
<p class="lead">Large websites are run by experienced teams on very reliable systems, and they still go down. When they do, the cause is usually one of a small number of things.</p>
<h2>Common causes</h2>
<ul>
<li><b>A configuration change.</b> The most common cause by far. A setting pushed to many servers at once can break them all.</li>
<li><b>A software update or release.</b> A new version with a hidden bug can cause errors that only appear under real traffic.</li>
<li><b>Overload.</b> A sudden surge in visitors, such as a major event or a promotion, can exceed what the servers can handle.</li>
<li><b>A cloud provider fault.</b> Many sites rely on the same cloud platforms. When one region has trouble, every service that depends on it can be affected together.</li>
<li><b>A CDN problem.</b> Content delivery networks sit between visitors and websites. If one fails, thousands of sites can show errors at once.</li>
<li><b>DNS failures.</b> If the system that turns names into addresses fails, the site can be perfectly healthy and still unreachable.</li>
<li><b>Expired certificates or domains.</b> A simple lapse can make a site unavailable until it is renewed.</li>
</ul>
<h2>Why one fault affects so many sites</h2>
<p>Modern sites share infrastructure. A single failing component, such as a login service, a database or a DNS provider, can sit underneath many different websites and apps. That is why unrelated sites sometimes go down in the same hour.</p>
<h2>What you can do as a visitor</h2>
<ul>
<li>Check whether other sites that use the same provider are also affected.</li>
<li>Read the service&rsquo;s official status page for updates.</li>
<li>Avoid repeating actions such as payments or form submissions during an outage.</li>
</ul>
<h2>What you can do as an owner</h2>
<p>Monitor from several locations, keep certificates and domains renewing automatically, and avoid depending on a single provider for everything. See <a href="/help/uptime-percentages-explained">uptime percentages explained</a> for what different levels mean in practice.</p>
'''
},
{
'slug': 'what-is-a-good-response-time', 'cat': 'owners',
'title': 'What is a good website response time?',
'desc': 'What response time means, which numbers are good, average or slow, and what usually makes a site respond slowly. Written for site owners and curious visitors.',
'related': ['speed-up-your-website', 'uptime-percentages-explained', 'how-our-checks-work'],
'body': '''
<p class="lead">Response time is how long a website takes to start answering after you ask for a page. It is measured in milliseconds, where 1,000 ms is one second. It is not the same as total page load time, which also includes images, scripts and rendering.</p>
<h2>Rough guide</h2>
<ul>
<li><b>Under 200 ms:</b> very fast. The server answers almost at once.</li>
<li><b>200 to 500 ms:</b> good for most sites.</li>
<li><b>500 ms to 1 second:</b> acceptable, but noticeable on a slow connection.</li>
<li><b>Over 1 second:</b> slow. Visitors begin to notice, and some leave.</li>
</ul>
<p>These figures are rules of thumb. A very busy checkout page or a search engine has different needs from a simple blog.</p>
<h2>Why the number changes</h2>
<ul>
<li><b>Distance.</b> A visitor on the other side of the world takes longer to reach a single server than one nearby. That is why we show response times from several regions.</li>
<li><b>Server load.</b> A busy server answers more slowly.</li>
<li><b>Page generation.</b> Sites that build each page from a database take longer than sites that serve saved pages.</li>
<li><b>Connection setup.</b> Finding the server, connecting and securing the link all add time before any content arrives.</li>
<li><b>Your own connection.</b> Weak Wi-Fi and mobile signal add delay that has nothing to do with the site.</li>
</ul>
<h2>How to improve it</h2>
<p>Use caching, a CDN, compressed responses and a fast host. The <a href="/help/speed-up-your-website">speed-up guide</a> goes through the changes that make the biggest difference.</p>
<h2>How we measure it</h2>
<p>Our live graph shows the response time of our own checks, which include network travel. A single slow reading is normal. Look at the average over a day or a week.</p>
'''
},
{
'slug': 'what-to-do-when-an-app-or-service-is-down', 'cat': 'fix',
'title': 'What to do when an app or online service stops working',
'desc': 'A calm checklist for when a popular app or service is not working: confirm whether it is an outage, avoid common mistakes, and know when to try again.',
'related': ['is-it-down-or-just-me', 'why-big-websites-go-down', 'website-not-loading-checklist'],
'body': '''
<p class="lead">When an app that you use every day stops working, it helps to work out quickly whether the fault is yours or the service&rsquo;s. This keeps you from wasting time on fixes that cannot help.</p>
<h2>1. Confirm it is an outage</h2>
<p>Use the <a href="/">checker</a> or the service&rsquo;s page on this site. Then see whether the website works while the app does not, or the other way round. Outages often affect only one of them.</p>
<h2>2. Look at the official source</h2>
<p>Most services run a status page or a support account on social media. They announce problems and say when they are fixed.</p>
<h2>3. Do not make things worse</h2>
<ul>
<li>Do not reinstall the app or reset your device unless the service says to.</li>
<li>Do not change your password just because a sign-in fails during an outage.</li>
<li>Do not repeat orders, payments or messages that seem stuck. Check your history first, because the first attempt may have gone through.</li>
<li>Be careful with emails or messages claiming to fix an outage. Scammers use outages as cover.</li>
</ul>
<h2>4. Simple things worth one try</h2>
<ol>
<li>Close the app completely and reopen it.</li>
<li>Switch between Wi-Fi and mobile data.</li>
<li>Update the app to the latest version.</li>
<li>Restart your device.</li>
</ol>
<h2>5. Wait, then try again</h2>
<p>If the service is down for everyone, only the service can fix it. Most outages are over within an hour or two. If yours continues after the service reports it fixed, contact its support and mention your device, your network and the time.</p>
'''
},
{
'slug': 'how-to-monitor-your-own-website', 'cat': 'owners',
'title': 'How to monitor your own website: what to check and how often',
'desc': 'A practical guide for site owners: what to monitor, how often to check, how to avoid false alarms and what to do when an alert arrives.',
'related': ['uptime-percentages-explained', 'ssl-certificate-errors', 'domain-name-expiry'],
'body': '''
<p class="lead">The worst way to learn that your website is down is from a customer. A little monitoring tells you first. This guide covers what is worth watching and how to keep alerts useful.</p>
<h2>What to monitor</h2>
<ul>
<li><b>Availability.</b> Does the home page answer with a success code?</li>
<li><b>Response time.</b> A slowdown often comes before an outage.</li>
<li><b>Your important pages.</b> Check the login, checkout or contact page as well as the home page, since they can fail separately.</li>
<li><b>SSL certificate expiry.</b> An expired certificate makes browsers warn visitors away. See <a href="/help/ssl-certificate-errors">SSL certificate errors</a>.</li>
<li><b>Domain expiry.</b> Losing a domain takes everything offline. See <a href="/help/domain-name-expiry">domain name expiry</a>.</li>
</ul>
<h2>How often</h2>
<p>Every minute catches short outages. Every five minutes is enough for most small sites. Checking less often than that risks missing a problem entirely.</p>
<h2>Avoid false alarms</h2>
<ul>
<li>Require two failures in a row before alerting, which filters out one-off blips.</li>
<li>Check from more than one location so a local network problem does not look like an outage.</li>
<li>Do not alert on a slow response alone. Alert on errors, then track slowness separately.</li>
</ul>
<h2>When an alert arrives</h2>
<ol>
<li>Confirm with a second check and a different network.</li>
<li>Check recent changes, such as a new release, a plugin update or a settings change.</li>
<li>Look at your host&rsquo;s status page and your CDN or DNS provider.</li>
<li>Write down the start and end time so you can measure uptime later.</li>
</ol>
<h2>Using siteupdown.com</h2>
<p>A free account lets you add sites to a watchlist, see their uptime history and receive an email when one goes down and when it recovers.</p>
'''
},

]

from help_more_a import ARTICLES_A
from help_more_b import ARTICLES_B
from help_more_c import ARTICLES_C
ARTICLES = ARTICLES + ARTICLES_A + ARTICLES_B + ARTICLES_C
BY_SLUG = {a['slug']: a for a in ARTICLES}
