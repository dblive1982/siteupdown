# Extra depth appended to the thinnest guides (causes, worked examples, next steps).
EXTRA = {
'works-on-mobile-data-not-wifi': '''
<h2>A worked example</h2>
<p>Sam can open a shop site on 4G but gets &ldquo;This site can&rsquo;t be reached&rdquo; at home. Other sites work fine on the Wi-Fi. Sam restarts the router, which changes nothing. Then Sam changes the router&rsquo;s DNS to a public resolver and the shop loads. The cause was the provider&rsquo;s DNS server holding a bad or outdated address for that one site. Because the problem was limited to one site on one network, it was never the shop&rsquo;s fault.</p>
<h2>How to narrow it down quickly</h2>
<ul>
<li><b>Only one site fails:</b> usually DNS, filtering, or a routing problem between your provider and that site.</li>
<li><b>Many sites fail, but not all:</b> often IPv6 or a filter. Try turning off IPv6 on the device, or a VPN or security app.</li>
<li><b>Everything fails on Wi-Fi:</b> the router or the provider line is the problem, not a single site. Check whether the router&rsquo;s internet light is on.</li>
<li><b>Only one device fails:</b> the device has a stale cache, a wrong clock, a proxy setting or a security app in the way. Other devices on the same Wi-Fi tell you this at once.</li>
</ul>
<h2>What to tell your provider</h2>
<p>Give them the site address, the time you tried, what the error says, and that the site works on mobile data and in the siteupdown.com checker. That lets them skip the standard &ldquo;restart your router&rdquo; script and look at routing and DNS directly.</p>
''',
'dns-probe-finished-nxdomain': '''
<h2>What the error really means</h2>
<p>NXDOMAIN stands for &ldquo;non-existent domain&rdquo;. Your device asked a DNS server for the address of the site and the answer was &ldquo;no such name&rdquo;. The browser never even tried to connect, so this is not a slow server or a blocked page. It is a failed name lookup.</p>
<h2>Common causes</h2>
<ul>
<li><b>A typo</b> in the address, such as a missing letter or the wrong ending (.com instead of .co.uk).</li>
<li><b>The domain has expired or was never registered.</b> The registry no longer lists it, so every resolver says it does not exist.</li>
<li><b>DNS records were deleted or are being changed.</b> A site owner who moves host can leave a gap where the records are missing.</li>
<li><b>Your resolver is wrong or stale.</b> Your router, provider or a filter returns NXDOMAIN for a site that exists. This is the case where the site works for other people.</li>
<li><b>A security or family filter</b> that deliberately answers &ldquo;does not exist&rdquo; for blocked sites.</li>
</ul>
<h2>A worked example</h2>
<p>A visitor types <code>exmaple.com</code> and sees the error. The domain they wanted was <code>example.com</code>, so the answer is correct: the misspelt name really does not exist. In a second case, the address is right and works on a phone using mobile data but not on the home Wi-Fi. That points to the router&rsquo;s DNS, so changing it to a public resolver fixes it.</p>
<h2>What to do next</h2>
<ol>
<li>Check the spelling and the domain ending.</li>
<li>Test the same address on another network or device.</li>
<li><a href="/help/flush-dns-cache">Flush your DNS cache</a>.</li>
<li>If you own the site, check that the domain is not <a href="/help/domain-name-expiry">expired</a> and that its DNS records exist at your registrar.</li>
<li>If you only changed the records recently, read about <a href="/help/dns-propagation">DNS propagation</a>; it can take hours.</li>
</ol>
''',
'clear-browser-cache-and-cookies': '''
<h2>What the cache and cookies actually are</h2>
<p>The <b>cache</b> stores copies of files such as images, scripts and stylesheets so pages load faster next time. The problem is that the browser sometimes keeps using an old copy after the site has changed. <b>Cookies</b> are small notes a site stores, such as your login or your preferences. A broken or outdated cookie can leave you stuck in a login loop or looking at the wrong account.</p>
<h2>Signs it is worth clearing</h2>
<ul>
<li>The page looks broken or half-styled, but works in a private window.</li>
<li>You keep being logged out, or a login page reloads without letting you in.</li>
<li>You see an old version of a page that others say has changed.</li>
<li>Errors such as &ldquo;too many redirects&rdquo; appear for just one site.</li>
</ul>
<h2>The quick test first</h2>
<p>Open the page in a private or incognito window. If it works there, the cache, cookies or an extension in your normal window is the cause, so clearing just that one site&rsquo;s data is usually enough. You do not need to wipe everything.</p>
<h2>What you will lose</h2>
<p>Clearing cookies signs you out of sites and may reset saved preferences. Clearing the cache costs nothing except that the next visit loads a little slower while files download again. Saved passwords are separate and are not removed unless you tick that box.</p>
<h2>If it does not help</h2>
<p>If the problem remains in a private window and on another device, then it is not your browser. Check the site with the <a href="/">checker</a> to see whether it is <a href="/help/is-it-down-or-just-me">down for everyone</a>.</p>
''',
'is-it-down-or-just-me': '''
<h2>Why this is hard to tell from one device</h2>
<p>A site can fail for you without being down. The fault can be on your device, your Wi-Fi, your provider, a DNS server, or the site itself. From one browser you cannot tell which, so the quickest test is to ask machines in other places and networks to try it for you. That is what the checker does.</p>
<h2>Reading the result</h2>
<ul>
<li><b>Up everywhere:</b> the site is fine. The problem is on your side, so try <a href="/help/works-on-mobile-data-not-wifi">another network</a> and <a href="/help/clear-browser-cache-and-cookies">clear the cache</a>.</li>
<li><b>Down everywhere:</b> the site really is down. Wait, check its status page or social media, and try again later. Nothing you do on your device will fix it.</li>
<li><b>Up in some places, down in others:</b> a regional or routing problem. Read <a href="/help/down-for-some-people-not-others">why it&rsquo;s down for some people</a>.</li>
<li><b>An error code:</b> the site answered but with a problem. A 5xx code is a server fault; a 4xx code is usually about the request or about being blocked. See the <a href="/help/http-status-codes-explained">status code guide</a>.</li>
</ul>
<h2>A worked example</h2>
<p>A game will not log in. The checker shows the website is up, but the login server returns a 503 from every location. That tells you the service is overloaded or in maintenance and that restarting your console or router will not help. You wait and check again in ten minutes.</p>
<h2>Why a quick re-check matters</h2>
<p>Short outages are common. If a check fails, run it again after a minute: a single failed attempt is not proof. Our system confirms a failure from more than one location before calling a site down for the same reason.</p>
''',
'what-to-do-when-an-app-or-service-is-down': '''
<h2>First, decide whose problem it is</h2>
<p>Before changing any settings, confirm that the service itself is failing. Use the <a href="/">checker</a>. The page also shows the app and login servers for many services, so you can see whether the website is up while the app&rsquo;s sign-in is not. See <a href="/help/is-it-down-or-just-me">is it down or just me</a>.</p>
<h2>If the service is down for everyone</h2>
<ul>
<li><b>Do not keep retrying logins.</b> Repeated failed attempts can lock your account or trigger rate limits (see <a href="/help/error-429-too-many-requests">error 429</a>).</li>
<li><b>Do not reinstall the app.</b> It almost never helps and you may lose local data.</li>
<li><b>Check the official status page</b> and the company&rsquo;s social accounts for updates and an estimated fix time.</li>
<li><b>Save your work</b> if the app has an offline mode, and avoid actions that cannot be repeated, such as payments.</li>
<li>Check back in 10 to 15 minutes. Most incidents are fixed within the hour.</li>
</ul>
<h2>If it is just you</h2>
<ol>
<li>Restart the app, then your device.</li>
<li>Check your connection and try mobile data instead of Wi-Fi.</li>
<li>Update the app and your operating system.</li>
<li>Clear the app cache, or sign out and in again.</li>
<li>Turn off a VPN, which some services block.</li>
</ol>
<h2>A worked example</h2>
<p>A messaging app will not send. The checker shows its website up but its API returning errors from every region. That is a service outage, so the sensible move is to wait and watch the official status page rather than reinstall.</p>
<h2>When to contact support</h2>
<p>Contact support if the service is up for everyone else but not for you after trying the steps above. Include the time, the error message and what device and network you used.</p>
''',
'how-to-monitor-your-own-website': '''
<h2>What to monitor</h2>
<ul>
<li><b>Availability:</b> does the home page answer with a 200 status?</li>
<li><b>Key pages:</b> the checkout, login or contact page matter more than the home page. A site can be &ldquo;up&rdquo; while the pages that make money are broken.</li>
<li><b>Response time:</b> a slowdown is often the first sign of trouble. See <a href="/help/what-is-a-good-response-time">what is a good response time</a>.</li>
<li><b>SSL expiry:</b> a lapsed certificate makes browsers show a warning that scares visitors away. See <a href="/help/ssl-certificate-errors">SSL errors</a>.</li>
<li><b>Domain expiry:</b> losing a domain takes everything offline. See <a href="/help/domain-name-expiry">domain expiry</a>.</li>
</ul>
<h2>How often to check</h2>
<p>Every one to five minutes is typical. Checking more often finds problems sooner but adds load; checking every hour can miss an outage altogether. Check from more than one location, so a local network issue does not look like an outage.</p>
<h2>Setting up alerts that you will act on</h2>
<ol>
<li>Add your site to a free watchlist on siteupdown.com.</li>
<li>Choose email alerts for down and recovered.</li>
<li>Ask for a confirmation before alerting, so one blip does not wake you.</li>
<li>Send the alert somewhere you really read, not an inbox you ignore.</li>
</ol>
<h2>A worked example</h2>
<p>A small shop has 99.5% uptime over a month. That sounds high, but it is about 3 hours and 40 minutes of downtime, which could easily include a busy sale day. Seeing the detail, the owner moves to better hosting. Read <a href="/help/uptime-percentages-explained">uptime percentages explained</a> for the arithmetic.</p>
<h2>What to do when an alert arrives</h2>
<p>Check the page yourself, then look at your host&rsquo;s status page, then at recent changes you made. Roll back the last change if the timing matches. See the <a href="/help/server-errors-500-502-503-504">server error guide</a> for each code.</p>
''',
'what-is-a-good-response-time': '''
<h2>Rough guide</h2>
<ul>
<li><b>Under 200 ms:</b> excellent. Typical of a well-cached site close to the visitor.</li>
<li><b>200 to 500 ms:</b> good. Most visitors will not notice.</li>
<li><b>500 ms to 1 second:</b> acceptable, but worth looking at.</li>
<li><b>1 to 3 seconds:</b> slow. Visitors begin to leave and search engines notice.</li>
<li><b>Over 3 seconds:</b> poor, and often a sign of an overloaded server or a slow database.</li>
</ul>
<h2>What our number measures</h2>
<p>The figure we show is how long the server took to respond to a request from one of our probes. It is not the full time a page takes to display, because that also includes images, scripts and rendering in the browser. Think of it as how quickly the server answers the door, not how long dinner takes.</p>
<h2>Why it varies</h2>
<ul>
<li><b>Distance:</b> a server in London answers a London probe faster than one in Sydney.</li>
<li><b>Time of day:</b> busy periods slow shared hosting.</li>
<li><b>Caching:</b> a cached page is much quicker than one built from the database each time.</li>
<li><b>The first request is slower</b> because it sets up the connection and encryption.</li>
</ul>
<h2>A worked example</h2>
<p>A blog answers in 180 ms in the morning and 1,400 ms in the evening. The pattern points to a server that struggles under load rather than a broken page. Adding page caching or moving up from the cheapest hosting plan usually fixes it. See <a href="/help/speed-up-your-website">how to speed up your website</a>.</p>
<h2>What matters more than one number</h2>
<p>Look at the trend. One slow reading is noise, but a response time that creeps upward over days is an early warning of a growing problem.</p>
''',
'error-429-too-many-requests': '''
<h2>What triggers it</h2>
<p>A 429 means you, or the network you share, sent more requests than the site allows in a given period. Sites use rate limits to protect themselves from abuse and overload. Common triggers are refreshing repeatedly, failed login attempts, browser extensions that make many requests, scraping tools, and several people behind one shared IP address such as an office or mobile network.</p>
<h2>What to do as a visitor</h2>
<ol>
<li>Stop refreshing. Every attempt can extend the wait.</li>
<li>Wait a few minutes. Some responses include a Retry-After header saying how long.</li>
<li>Turn off extensions or tools that auto-refresh or make bulk requests.</li>
<li>Switch networks, for example from Wi-Fi to mobile data, if you are sharing an address with heavy users.</li>
<li>Check that a VPN is not putting you on a busy shared address.</li>
</ol>
<h2>What to do as a site owner</h2>
<ul>
<li>Check whether the limit is too strict for normal visitors.</li>
<li>Send a Retry-After header so well-behaved clients know when to return.</li>
<li>Use caching so repeated requests do not hit the application.</li>
<li>Look at logs for one address making most of the requests.</li>
</ul>
<h2>A worked example</h2>
<p>A user fails to log in three times, then keeps pressing the button. After a few more tries the site shows 429 for fifteen minutes. Waiting out the lockout works; hammering the button only extends it. Our own checker rate-limits repeated checks for the same reason.</p>
<p>See also the <a href="/help/http-status-codes-explained">status code guide</a>.</p>
''',
'sites-that-block-automated-checks': '''
<h2>Why sites do this</h2>
<p>Many sites use bot protection from services such as Cloudflare or Akamai to stop scrapers, attackers and fake traffic. These systems look at where a request comes from, how it behaves and whether it looks like a real browser. A monitoring request from a data centre can look like a bot, even though it is harmless.</p>
<h2>What it looks like in a check</h2>
<ul>
<li>A <b>403 Forbidden</b> or <b>429</b> from some or all probes, while the site opens fine in your browser.</li>
<li>A <b>challenge page</b> asking to prove you are human.</li>
<li>Different results from different locations, because the protection treats some networks as riskier.</li>
</ul>
<h2>How we treat it</h2>
<p>A block is not an outage. When a site answers us but refuses the request, we show it as blocked or unclear, not down, because the server is clearly alive. We do not try to bypass protection or solve challenges. That would be inappropriate and is not something a monitoring service should do.</p>
<h2>If you own the site</h2>
<ol>
<li>Allow-list your monitoring service, or add a rule that lets known monitors through.</li>
<li>Monitor a simple page, such as a health-check URL, that bot rules do not cover.</li>
<li>Check your firewall logs for blocked probe addresses.</li>
</ol>
<h2>If you are a visitor</h2>
<p>If the site opens for you, it is up. Trust your own browser over a blocked probe. See <a href="/help/error-403-forbidden">error 403</a> and <a href="/help/how-our-checks-work">how our checks work</a>.</p>
''',
'domain-name-expiry': '''
<h2>What happens when a domain expires</h2>
<p>Domains are rented, usually yearly. When the rent is not paid the domain goes through stages, and the details vary by ending (.com, .co.uk and so on):</p>
<ol>
<li><b>Expiry day:</b> the site often stops working, or shows a registrar&rsquo;s parking page, but you can still renew at the normal price.</li>
<li><b>Grace period:</b> typically up to about 30 days, in which renewing is still allowed, sometimes with a late fee.</li>
<li><b>Redemption period:</b> roughly another 30 days, where recovery is possible but costs much more.</li>
<li><b>Release:</b> the domain is deleted and anyone can register it, including someone who may misuse the old name.</li>
</ol>
<h2>Why it is dangerous</h2>
<p>Email on the domain stops working at the same time as the website. Search rankings, links and customers&rsquo; trust built over years can be lost, and a competitor or spammer may pick up the name.</p>
<h2>How to prevent it</h2>
<ul>
<li>Turn on <b>auto-renew</b> and keep a valid card on file.</li>
<li>Use an email address you check for registrar reminders, not a past employee&rsquo;s.</li>
<li>Renew for several years at once for important domains.</li>
<li>Put the expiry date in a calendar with a reminder a month ahead.</li>
</ul>
<h2>A worked example</h2>
<p>A card expires, auto-renew fails, and the reminder goes to an old inbox. The site goes offline on expiry day and the owner assumes the host has failed. A check for the domain shows a lookup failure (see <a href="/help/dns-probe-finished-nxdomain">NXDOMAIN</a>), and the registrar&rsquo;s dashboard shows the real cause. Paying within the grace period restores the site once DNS settles (<a href="/help/dns-propagation">DNS propagation</a>).</p>
''',
'err-connection-timed-out': '''
<h2>What a timeout means</h2>
<p>Your browser found the site&rsquo;s address and tried to connect, but the server never answered within the allowed time. Unlike an error code, nothing came back at all. That points to something swallowing the request: a server that is overloaded or switched off, a firewall dropping traffic, or a network path that is broken.</p>
<h2>Likely causes</h2>
<ul>
<li><b>The server is down or overloaded</b> and cannot accept new connections.</li>
<li><b>A firewall</b> on the server or your network silently drops your traffic.</li>
<li><b>Your own connection</b> is weak, or the router needs a restart.</li>
<li><b>A VPN or proxy</b> that cannot reach the site.</li>
<li><b>A routing fault</b> between your provider and the site. This is why the site may work for others (<a href="/help/down-for-some-people-not-others">down for some people</a>).</li>
</ul>
<h2>What to try</h2>
<ol>
<li>Run the site through the <a href="/">checker</a> to see if it is down for everyone.</li>
<li>Try another network, such as mobile data.</li>
<li>Turn off VPNs, proxies and security software for a moment.</li>
<li>Restart the router and flush DNS (<a href="/help/flush-dns-cache">guide</a>).</li>
<li>Wait and retry; short overloads clear themselves.</li>
</ol>
<h2>Site owners</h2>
<p>Check that the server is running, the web service is listening on its port, the host&rsquo;s firewall allows traffic on ports 80 and 443, and the server has free memory and CPU. A timeout from all locations nearly always means the server or its firewall.</p>
<h2>Timeout versus other errors</h2>
<p>A 504 means a gateway got no answer from a server behind it; a timeout means you got no answer at all. See the <a href="/help/server-errors-500-502-503-504">server error guide</a>.</p>
''',
'why-big-websites-go-down': '''
<h2>The most common causes</h2>
<ul>
<li><b>Configuration changes.</b> A routine update with one wrong setting is behind many large outages, because small changes can spread to thousands of servers in seconds.</li>
<li><b>Shared dependencies.</b> Many sites rely on the same cloud, DNS or content-delivery provider, so one failure there takes down many sites at once.</li>
<li><b>Traffic spikes.</b> A launch, a sale or a news event can exceed what the system was built for.</li>
<li><b>Expired certificates or domains,</b> an embarrassingly simple cause that still happens.</li>
<li><b>Software bugs</b> that appear only at huge scale.</li>
<li><b>Attacks,</b> such as <a href="/help/what-is-a-ddos-attack">DDoS</a>, though they are less common than self-inflicted faults.</li>
<li><b>Hardware, power or network faults</b> in a data centre.</li>
</ul>
<h2>Why a big fix takes time</h2>
<p>Large systems are made of many services that depend on each other. Recovery has to be done in order, and restarting everything at once can cause a second overload. Teams also verify each step to avoid making it worse.</p>
<h2>Why you see it before they say anything</h2>
<p>Status pages are often updated by hand after engineers confirm the cause. Independent checks like ours see the symptoms immediately, which is why a site can show as down here before an official notice appears.</p>
<h2>A worked example</h2>
<p>One cloud provider has a fault in one region. Dozens of unrelated apps fail at the same moment, because they all run there. Our map shows many sites down in the same area and time, which is the sign of a shared cause instead of separate problems.</p>
<h2>What you can do</h2>
<p>Not much except wait. Avoid repeated logins and refreshes, and check the <a href="/help/what-to-do-when-an-app-or-service-is-down">what to do guide</a>.</p>
''',
'down-for-some-people-not-others': '''
<h2>A worked example</h2>
<p>A news site loads for your friend in Manchester but not for you in Leeds, and the checker shows green from the US and red from Europe. That pattern suggests a regional routing or CDN problem, not a dead server. In that case there is nothing wrong with your device.</p>
<h2>Quick tests to separate the causes</h2>
<ul>
<li><b>Other network, same device:</b> works on mobile data means your network or provider.</li>
<li><b>Same network, other device:</b> works means your device, cache or an extension.</li>
<li><b>A VPN to another country:</b> works means a regional block or routing fault.</li>
</ul>
''',
'uptime-percentages-explained': '''
<h2>The numbers, in real time</h2>
<ul>
<li><b>99%</b> uptime = about 3 days 15 hours of downtime per year (7 hours a month).</li>
<li><b>99.5%</b> = about 1 day 20 hours a year (3 hours 40 minutes a month).</li>
<li><b>99.9%</b> (&ldquo;three nines&rdquo;) = about 8 hours 46 minutes a year (43 minutes a month).</li>
<li><b>99.99%</b> (&ldquo;four nines&rdquo;) = about 53 minutes a year (4 minutes a month).</li>
</ul>
<h2>Why the last decimal matters</h2>
<p>Every extra nine is roughly ten times harder and more expensive to deliver. A shop making money every hour needs to know whether a month at 99.5% cost it a day-long sale.</p>
<h2>How to calculate it</h2>
<p>Uptime % = (minutes up &divide; total minutes) &times; 100. A site that was down for 90 minutes in a 30-day month (43,200 minutes) has 1 &minus; 90/43,200 = 99.79% uptime.</p>
<h2>What the percentage hides</h2>
<ul>
<li>One long outage and many short ones can share the same percentage but feel very different to visitors.</li>
<li>A site can be &ldquo;up&rdquo; yet very slow or broken on key pages.</li>
<li>Planned maintenance may or may not be counted, depending on who reports it.</li>
</ul>
<p>Read <a href="/help/how-to-monitor-your-own-website">how to monitor your own website</a> for how to track it yourself.</p>
''',
}

EXTRA.update({
'error-404-not-found': '''
<h2>Soft 404s and why they matter</h2>
<p>A <b>soft 404</b> is a page that says &ldquo;not found&rdquo; but sends a 200 (OK) code. Search engines treat these as low quality, and monitors cannot tell the page is broken. A proper missing page should return a real 404 so that browsers and search engines know it is gone.</p>
<h2>A worked example</h2>
<p>A shop renames a product and its link changes from <code>/shoes/red</code> to <code>/shoes/crimson</code>. Old links from other sites now return 404. Adding a permanent (301) redirect from the old address to the new one keeps visitors and search ranking. See <a href="/help/http-status-codes-explained">status codes explained</a> for redirects.</p>
<h2>Fixing 404s you own</h2>
<ol>
<li>Find them in your search console or server logs.</li>
<li>Redirect moved pages with a 301 to the closest matching page, not always the home page.</li>
<li>Let truly deleted pages return 404 or 410, and offer a helpful custom page with search and links.</li>
<li>Fix internal links that point to missing pages.</li>
</ol>
''',
'ssl-certificate-errors': '''
<h2>Common error messages and what they mean</h2>
<ul>
<li><b>Certificate expired:</b> the renewal did not happen. Certificates last from a few months to a year, and a missed renewal blocks visitors.</li>
<li><b>Name mismatch:</b> the certificate is for another address, for example <code>example.com</code> but not <code>www.example.com</code>.</li>
<li><b>Not trusted / unknown authority:</b> a self-signed certificate, or a missing intermediate certificate on the server.</li>
<li><b>Your clock is wrong:</b> a device with the wrong date sees valid certificates as expired. Fix the date and time first.</li>
</ul>
<h2>Visitors: what to do</h2>
<p>Check your device&rsquo;s date and time, try another network (public Wi-Fi sometimes interferes), and do not enter passwords or card details on a page showing a warning. Clicking through the warning is only reasonable for a site you run yourself.</p>
<h2>Owners: how to fix and prevent it</h2>
<ol>
<li>Turn on automatic renewal with your host or Let&rsquo;s Encrypt.</li>
<li>Install the full chain, including intermediates.</li>
<li>Cover every name you use, including www and subdomains.</li>
<li>Monitor expiry so you are warned weeks ahead.</li>
</ol>
''',
'server-errors-500-502-503-504': '''
<h2>A worked example for each code</h2>
<ul>
<li><b>500:</b> a plugin update breaks a PHP page. The server runs it, the code crashes, and visitors see 500. Check the error log and roll back the update.</li>
<li><b>502:</b> a web server passes requests to an app that has crashed. Restart the app and look at why it stopped, often memory.</li>
<li><b>503:</b> a site in maintenance mode, or one overwhelmed by a traffic spike, asks visitors to come back later.</li>
<li><b>504:</b> a slow database query makes the app take longer than the gateway will wait. Optimise the query or raise the limit.</li>
</ul>
<h2>What visitors should do</h2>
<p>Wait a minute and refresh once. If it persists, check the <a href="/">checker</a> to see whether others see it. These are the site&rsquo;s faults, not yours, so clearing your cache will not help.</p>
<h2>What owners should check first</h2>
<ol>
<li>The latest change you made. Most 5xx errors follow a deploy or update.</li>
<li>Server error logs, free disk space, memory and CPU.</li>
<li>Whether the database is running and accepting connections.</li>
<li>Your host&rsquo;s status page.</li>
</ol>
''',
'website-not-loading-checklist': '''
<h2>How to use this checklist</h2>
<p>Work from the cheapest test to the most involved, and stop when the site loads. Most problems are fixed in the first four steps. The order also tells you whose fault it is: steps 1 to 3 find out whether the site is really down, and the rest fix things on your side.</p>
<h2>A worked example</h2>
<p>A page will not open. The checker says it is up from everywhere, so the fault is local. It opens on mobile data, so the router or provider is involved. Restarting the router and changing DNS fixes it. Total time: five minutes, and no one needed to contact the site.</p>
<h2>If nothing on the list helps</h2>
<p>Note the exact error text, the time, the device and the network. That is what support teams need to help you. See <a href="/help/is-it-down-or-just-me">is it down or just me</a> and <a href="/help/err-connection-timed-out">connection timed out</a>.</p>
''',
'dns-propagation': '''
<h2>Why it takes time</h2>
<p>When you change a DNS record, servers around the world keep the old answer until its <b>TTL</b> (time to live) runs out. A TTL of 3600 means one hour; 86400 means a full day. Until each resolver&rsquo;s copy expires, some visitors see the old address and others the new one.</p>
<h2>How to make a move smoother</h2>
<ol>
<li>A day or two before the change, lower the TTL to 300 (five minutes).</li>
<li>Make the change and keep the old server running until the traffic has moved.</li>
<li>After it has settled, raise the TTL again.</li>
</ol>
<h2>A worked example</h2>
<p>You move your site to a new host and update the A record. You see the new site, but a customer still sees the old one. Their resolver has a cached copy with hours left. Nothing is wrong, and the old server must stay online until the cache expires.</p>
<h2>Checking progress</h2>
<p>Use the checker: probes in different countries ask different resolvers, so you can watch the change spread. See also <a href="/help/flush-dns-cache">flush your DNS cache</a> for your own device.</p>
''',
'speed-up-your-website': '''
<h2>Where to start: measure first</h2>
<p>Find out whether the slow part is the server (a long wait before anything arrives) or the page (a lot of heavy files). Our <a href="/">checker</a> shows server response time. If it is over about a second, work on the server; if it is fast but the page still feels slow, the page itself is too heavy.</p>
<h2>Highest-impact fixes</h2>
<ul>
<li><b>Compress and resize images.</b> Use modern formats such as WebP and never upload a 4000-pixel photo to show it at 400.</li>
<li><b>Turn on caching</b> so repeat visitors and the server reuse work.</li>
<li><b>Use a CDN</b> to serve files from near the visitor.</li>
<li><b>Remove unused plugins and scripts,</b> especially third-party trackers and widgets.</li>
<li><b>Upgrade hosting</b> if the server itself is slow under load.</li>
</ul>
<h2>A worked example</h2>
<p>A homepage is 6 MB because of five large photos. Compressing them to 300 KB each cuts the page to under 2 MB and halves the load time on a phone, with no visible loss. See <a href="/help/what-is-a-good-response-time">what is a good response time</a>.</p>
''',
'flush-dns-cache': '''
<h2>When flushing actually helps</h2>
<p>Flushing is worth doing when a site works for others but not for you, when a site has just moved to a new host, or when you see a <a href="/help/dns-probe-finished-nxdomain">DNS error</a> that should not be there. It is not a cure for a site that is down for everyone.</p>
<h2>A worked example</h2>
<p>You are moving a site to a new server. Everyone else sees the new site, but your computer still shows the old one. Your device remembers the old address, so the flush clears that memory and the next lookup gets the new one.</p>
<h2>If it does not help</h2>
<p>The browser, router and your provider each keep their own cache. Restart the browser, then the router, and try another DNS server. Remember that the <a href="/help/dns-propagation">propagation time</a> can also be the reason.</p>
''',
'error-403-forbidden': '''
<h2>A worked example</h2>
<p>A visitor on a VPN reaches a store and sees 403. The store blocks the VPN&rsquo;s address range because of past fraud. Turning the VPN off makes the page load. The server was up and working the whole time; it simply refused that visitor.</p>
<h2>Owner checklist</h2>
<ol>
<li>Check file permissions (<code>644</code> for files, <code>755</code> for folders).</li>
<li>Look for a missing index file in a folder where directory listing is off.</li>
<li>Check security plugins, firewall and country or IP block rules.</li>
<li>Check the <code>.htaccess</code> file for deny rules.</li>
</ol>
<p>See also <a href="/help/sites-that-block-automated-checks">sites that block automated checks</a>.</p>
''',
})
