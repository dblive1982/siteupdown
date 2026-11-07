# More help-centre guides (batch C). Merged into ARTICLES by help_content.py.
ARTICLES_C = [
{
'slug': 'how-to-change-your-dns-server', 'cat': 'fix',
'title': 'How to change your DNS server on a computer, phone or router',
'desc': 'Step-by-step instructions for switching to a public DNS resolver on Windows, Mac, iPhone, Android and your home router, and how to undo it.',
'related': ['what-is-dns-and-why-it-fails', 'flush-dns-cache', 'dns-probe-finished-nxdomain'],
'body': '''
<p class="lead">Your device normally uses the DNS resolver your internet provider hands out. Usually that is fine, but if lookups are slow, some names fail to resolve or a stale answer will not clear, switching to a public resolver is a quick and reversible fix. This guide shows how, and how to put things back.</p>
<h2>Before you change anything</h2>
<ul>
<li>Note the current settings, or take a screenshot, so you can restore them.</li>
<li>A DNS change affects <b>name lookups only</b>. It does not change your speed or your connection, though faster lookups can make pages start sooner.</li>
<li>Public resolvers are run by companies who can, depending on their policies, see the names you look up. Read the provider&rsquo;s privacy statement if that matters to you.</li>
</ul>
<h2>Commonly used public resolvers</h2>
<ul>
<li><b>Cloudflare:</b> <code>1.1.1.1</code> and <code>1.0.0.1</code></li>
<li><b>Google:</b> <code>8.8.8.8</code> and <code>8.8.4.4</code></li>
<li><b>Quad9:</b> <code>9.9.9.9</code> and <code>149.112.112.112</code>, which also blocks known malicious sites</li>
</ul>
<p>Always enter a primary and a secondary address, so lookups continue if one is unreachable.</p>
<h2>Windows 11</h2>
<ol>
<li>Open <b>Settings</b>, then <b>Network &amp; internet</b>.</li>
<li>Choose <b>Wi-Fi</b> or <b>Ethernet</b>, then open the properties of your connection.</li>
<li>Next to <b>DNS server assignment</b>, choose <b>Edit</b> and switch from automatic to <b>Manual</b>.</li>
<li>Turn on <b>IPv4</b>, enter the preferred and alternate addresses, and save.</li>
</ol>
<p>To undo, choose Edit again and set it back to <b>Automatic (DHCP)</b>.</p>
<h2>Mac</h2>
<ol>
<li>Open <b>System Settings</b>, then <b>Network</b>.</li>
<li>Select your connection and click <b>Details</b>.</li>
<li>Choose <b>DNS</b>, press the plus button and add the addresses.</li>
<li>Remove any old entries you want to replace, then click <b>OK</b>.</li>
</ol>
<p>To undo, remove the entries you added and the Mac goes back to using what the network provides.</p>
<h2>iPhone and iPad</h2>
<ol>
<li>Open <b>Settings</b> and tap <b>Wi-Fi</b>.</li>
<li>Tap the information icon next to your network.</li>
<li>Choose <b>Configure DNS</b> and switch to <b>Manual</b>.</li>
<li>Remove existing servers, add the new ones and save.</li>
</ol>
<p>This applies to that one Wi-Fi network only. It does not change mobile data. To undo, set Configure DNS back to <b>Automatic</b>.</p>
<h2>Android</h2>
<p>Recent versions of Android have a <b>Private DNS</b> setting, usually under <b>Settings</b>, <b>Network &amp; internet</b>. Choose the private DNS provider hostname option and enter a provider&rsquo;s hostname, such as <code>one.one.one.one</code> for Cloudflare or <code>dns.google</code> for Google. Unlike the per-network setting above, this works on both Wi-Fi and mobile data. To undo, set it back to <b>Automatic</b> or <b>Off</b>. Menu names vary by manufacturer, so use the search box in Settings if you cannot find it.</p>
<h2>On your home router</h2>
<p>Changing it on the router applies to every device at home. Log in to the router&rsquo;s settings page, using the address and login printed on its label, and look for <b>DNS</b>, usually under internet or WAN settings. Enter the primary and secondary addresses and save. The router may restart. Some provider-supplied routers do not allow this change, in which case change it on individual devices instead.</p>
<h2>After you change it</h2>
<ol>
<li>Flush your device&rsquo;s cache so it forgets old answers. See <a href="/help/flush-dns-cache">how to flush your DNS cache</a>.</li>
<li>Restart your browser.</li>
<li>Try the site that was failing, or run it through our <a href="/">website checker</a>.</li>
</ol>
<h2>Checking it worked</h2>
<p>Our <a href="/tools/dns-lookup">DNS lookup tool</a> shows what a name resolves to from our servers, so you can compare it with what your own device gets. If your device returns a different or missing answer, the cache or the resolver is the cause.</p>
<h2>If it did not help</h2>
<ul>
<li>The site may genuinely be down. Check from elsewhere with our tool.</li>
<li>A VPN or security app may be overriding your DNS settings.</li>
<li>Some networks, such as workplaces and schools, force their own resolver and block others.</li>
<li>If the name is unknown everywhere, the problem is the site&rsquo;s own DNS. See <a href="/help/dns-probe-finished-nxdomain">what DNS_PROBE_FINISHED_NXDOMAIN means</a>.</li>
</ul>
<p>If a public resolver makes no difference, put your settings back to automatic. There is no benefit in keeping a change that does nothing.</p>
'''
},
{
'slug': 'vpns-and-websites-that-stop-working', 'cat': 'fix',
'title': 'Why a VPN can break websites, and how to fix it',
'desc': 'How VPNs change where your traffic comes from, why some sites block them or load slowly, and a checklist for fixing problems.',
'related': ['website-works-in-one-browser-not-another', 'error-403-forbidden', 'sites-that-block-automated-checks'],
'body': '''
<p class="lead">A virtual private network, or VPN, sends your traffic through an encrypted tunnel to a server run by the VPN provider, and websites see that server&rsquo;s address instead of yours. This is useful for privacy on public Wi-Fi and for reaching services from other regions. It also explains many &ldquo;this site does not work for me&rdquo; moments.</p>
<h2>What a VPN changes</h2>
<ul>
<li><b>Your apparent location.</b> Sites see the VPN server&rsquo;s country and city, not yours.</li>
<li><b>Your address.</b> It is shared with many other users of the same server.</li>
<li><b>The route.</b> Your traffic takes a detour through the VPN server, which adds distance and can add delay.</li>
<li><b>Your DNS.</b> Many VPNs also use their own name resolvers.</li>
</ul>
<h2>Why sites misbehave over a VPN</h2>
<h3>The address is on a block list</h3>
<p>VPN addresses are shared, so if someone else on the same server behaves badly, the address can be flagged. Banks, shops, streaming services and security filters often block or challenge known VPN ranges. You may see an access denied message, a repeating human-check, or a page that never loads. Our guide to the <a href="/help/error-403-forbidden">403 forbidden error</a> explains one common form.</p>
<h3>Too many requests from one address</h3>
<p>Many people sharing one address can together trip rate limits that no single user would. See <a href="/help/error-429-too-many-requests">what a 429 error means</a>.</p>
<h3>Location mismatches</h3>
<p>If your account, payment card or device says one country and the VPN says another, some services will ask for extra verification or lock the account until you confirm it is really you.</p>
<h3>Slower speeds and higher latency</h3>
<p>Every extra mile adds delay. Choosing a server far from you, or a busy one, can make browsing sluggish, video buffer and games lag. See <a href="/help/latency-packet-loss-and-jitter-explained">latency, packet loss and jitter</a>.</p>
<h3>Broken connections after a drop</h3>
<p>If the VPN connection drops and your device sends traffic outside the tunnel, or a kill switch blocks everything, sites may appear to stop loading entirely until the tunnel is restored.</p>
<h3>DNS conflicts</h3>
<p>A VPN&rsquo;s resolver can disagree with your usual one, so a name may resolve differently or fail. See <a href="/help/what-is-dns-and-why-it-fails">what DNS is and why it fails</a>.</p>
<h2>A quick way to tell if the VPN is the cause</h2>
<ol>
<li>Disconnect the VPN and try the site again.</li>
<li>If it now works, the VPN or its address was the problem.</li>
<li>Connect again and pick a different server, ideally in your own country.</li>
<li>If a particular site still blocks you, contact the VPN provider and the site, and consider using the VPN only when you need it.</li>
</ol>
<h2>Fixes to try</h2>
<ul>
<li><b>Change server.</b> A different server means a different address with a different history.</li>
<li><b>Change protocol.</b> Most VPN apps offer several connection methods, and one may work better on a restrictive network.</li>
<li><b>Use split tunnelling,</b> if your app offers it, so only chosen apps go through the VPN and everything else uses your normal connection.</li>
<li><b>Update the app.</b> Old versions can have bugs and may use outdated settings.</li>
<li><b>Flush DNS</b> after connecting or disconnecting. See <a href="/help/flush-dns-cache">how to flush your DNS cache</a>.</li>
<li><b>Check the clock.</b> A wrong date and time breaks secure connections.</li>
</ul>
<h2>Why our checker may say &ldquo;blocked&rdquo;</h2>
<p>Automated tools, including ours, can run into the same kind of filters, since our probes also come from shared addresses in data centres. When a site answers our check with a challenge page rather than the real page, we report <b>Blocked</b> and explain it does not mean the site is down. See <a href="/help/sites-that-block-automated-checks">why some sites block automated checks</a>.</p>
<h2>VPN and privacy: what it does and does not do</h2>
<ul>
<li>It hides your traffic from the local network, which is helpful on public Wi-Fi.</li>
<li>It hides your address from the sites you visit.</li>
<li>It does <b>not</b> make you anonymous. The VPN provider can see your traffic, and sites can still recognise you from accounts, cookies and browser details.</li>
<li>Choose a provider whose privacy practices you have read and understood.</li>
</ul>
<h2>Summary</h2>
<p>If a site misbehaves, turn the VPN off and try again. If that fixes it, change server or settings, or use the VPN only where it is needed. Most VPN problems come down to a blocked shared address, a distant server or a DNS mismatch.</p>
'''
},
{
'slug': 'how-https-and-certificates-work', 'cat': 'owners',
'title': 'How HTTPS and SSL certificates work',
'desc': 'What the padlock really means, how certificates are issued and checked, why they expire, and how to avoid a certificate outage.',
'related': ['ssl-certificate-errors', 'what-happens-when-you-open-a-website', 'how-websites-stay-up'],
'body': '''
<p class="lead">The padlock in your browser tells you the connection to a site is encrypted and that the site proved who it is. Behind that small icon is a system of certificates, authorities and expiry dates. Understanding it helps both when you see a warning as a visitor and when you run a site and want to avoid an embarrassing outage.</p>
<h2>What HTTPS adds</h2>
<p>HTTP is the language browsers and servers use. HTTPS is the same language wrapped in encryption, using a protocol called TLS. (SSL is the older name, still widely used in everyday speech.) The wrapper provides three things:</p>
<ul>
<li><b>Privacy.</b> Anyone watching the network sees scrambled data, not your passwords or card details.</li>
<li><b>Integrity.</b> The data cannot be altered on the way without detection.</li>
<li><b>Identity.</b> The server proves it is the site you meant to visit, and not an impostor.</li>
</ul>
<h2>What a certificate is</h2>
<p>A certificate is a small digital document that ties a website&rsquo;s name to a cryptographic key. It states which names it covers, who issued it, and the dates between which it is valid. The server presents it at the start of every secure connection.</p>
<h2>Who vouches for it</h2>
<p>Anyone can create a certificate that claims to be for any name. What makes one trustworthy is the signature of a <b>certificate authority</b>, an organisation that checks the applicant controls the name before signing. Your browser and operating system ship with a list of authorities they trust. When a site presents a certificate, the browser checks that it is signed by one of them, directly or through a chain of intermediate certificates.</p>
<h2>What your browser checks</h2>
<ol>
<li><b>The name matches.</b> The certificate must cover the exact address you typed.</li>
<li><b>It is within its dates.</b> Not yet valid and expired certificates both fail.</li>
<li><b>It is signed by a trusted authority,</b> with a complete chain.</li>
<li><b>It has not been revoked,</b> meaning cancelled early by the issuer.</li>
</ol>
<p>Fail any of these and you see a full-page warning. See <a href="/help/ssl-certificate-errors">SSL certificate errors explained</a> for what each message means.</p>
<h2>Why certificates expire</h2>
<p>Certificates are deliberately short-lived. If a key is stolen or a site changes hands, the old certificate stops being valid soon on its own. Lifetimes have been getting shorter across the industry, so renewal needs to be routine, not a yearly scramble. Free authorities issue certificates valid for a matter of weeks to months, with tools that renew them automatically.</p>
<h2>The most common certificate outage</h2>
<p>An expired certificate is one of the most common and most avoidable causes of a site becoming unusable. The site is running, the server is healthy, but every visitor gets a security warning. It usually happens because a manual renewal was forgotten, an automatic renewal quietly failed, or a certificate on a less obvious system, such as an API or a mail server, was missed.</p>
<h2>Avoiding it</h2>
<ul>
<li><b>Automate renewal,</b> and check it actually ran.</li>
<li><b>Monitor expiry dates</b> and alert at least two weeks ahead. Our <a href="/tools/ssl-certificate-checker">SSL certificate checker</a> shows the date for any site.</li>
<li><b>List every certificate you rely on,</b> including subdomains, APIs and email.</li>
<li><b>Serve the full chain,</b> not just your own certificate, or some devices will reject it.</li>
<li><b>Cover every name you use,</b> including the version with and without <code>www</code>.</li>
<li><b>Redirect HTTP to HTTPS</b> so visitors always end up on the secure version. Our <a href="/tools/redirect-checker">redirect checker</a> can confirm it.</li>
</ul>
<h2>Related protections</h2>
<p>Once HTTPS works, there are extra headers that tell browsers to behave safely, for example always use HTTPS for your site, or restrict where scripts can load from. You can review them with our <a href="/tools/security-headers-checker">security headers checker</a>.</p>
<h2>For visitors: what to do about a warning</h2>
<ul>
<li>Check your device&rsquo;s date and time first. A wrong clock is a common cause.</li>
<li>Try another network. Public Wi-Fi can interfere with secure connections.</li>
<li>If the warning appears on a site you trust and nobody else sees it, your network or device is the likely cause.</li>
<li>If it appears for everyone, the site has a problem. Do not enter passwords or payment details until it is fixed.</li>
</ul>
<h2>Summary</h2>
<p>HTTPS encrypts the connection and a certificate proves the site&rsquo;s identity. Certificates are vouched for by trusted authorities and are valid only for a limited time. Most certificate problems are expiry, a mismatched name or an incomplete chain, and all three are easy to prevent with automatic renewal and monitoring.</p>
'''
},
{
'slug': 'game-or-online-service-not-working', 'cat': 'fix',
'title': 'Online game or app not working? How to tell if it is down',
'desc': 'A practical guide for gamers and app users to work out whether a game server is down, whether lag is your connection, and what to try first.',
'related': ['latency-packet-loss-and-jitter-explained', 'what-to-do-when-an-app-or-service-is-down', 'why-is-my-internet-slow'],
'body': '''
<p class="lead">You launch your game and it will not connect, or it connects and lags so badly it is unplayable. Is it the game&rsquo;s servers, your internet or your console? A few quick checks tell you, and save you resetting equipment that was never the problem.</p>
<h2>Step 1: see what others are saying</h2>
<p>Large online services usually have many players affected at once when something goes wrong. Look at our <a href="/outage-map">outage map</a> and the <a href="/outage-history">outage history</a> to see whether people are reporting problems with the same game or platform. Also check the official status page and social account for the game, console network or launcher, since studios often post updates there first.</p>
<h2>Step 2: separate the platform from the game</h2>
<p>Problems can sit at different layers:</p>
<ul>
<li><b>The platform:</b> your console network, PC launcher or app store. If signing in fails everywhere, this is likely.</li>
<li><b>The game&rsquo;s own servers:</b> matchmaking, login or the game world itself. Other games work, only this one fails.</li>
<li><b>A dependency:</b> a cloud provider or content delivery network used by many services. When many unrelated apps fail together, suspect this. See <a href="/help/what-is-a-cdn-and-why-outages-spread">why outages spread</a>.</li>
<li><b>Your own connection or device.</b></li>
</ul>
<h2>Step 3: check your own connection</h2>
<ol>
<li>Open a few ordinary websites. If they load slowly or not at all, your connection is the problem. Work through <a href="/help/why-is-my-internet-slow">why your internet is slow</a>.</li>
<li>Run our <a href="/game-ping-test">game ping test</a> and note the ping and how much it varies.</li>
<li>Try the same game on another device or network, such as a phone hotspot, to see whether the problem follows you.</li>
</ol>
<h2>Step 4: understand lag</h2>
<p>Lag in online games comes from three sources, which feel different:</p>
<ul>
<li><b>High ping:</b> a steady delay between pressing a button and seeing the result.</li>
<li><b>Jitter:</b> uneven delay, which makes movement stutter or characters snap back.</li>
<li><b>Packet loss:</b> pieces of data that never arrive, causing freezes and rubber-banding.</li>
</ul>
<p>Our guide to <a href="/help/latency-packet-loss-and-jitter-explained">latency, packet loss and jitter</a> explains how to measure each one.</p>
<h2>Step 5: quick fixes for your side</h2>
<ul>
<li><b>Use a cable</b> instead of Wi-Fi if you can. It is the single biggest improvement for most players.</li>
<li><b>Pause downloads and updates</b> on every device in the house.</li>
<li><b>Restart</b> the game, the console or PC, and the router.</li>
<li><b>Choose a nearer server region</b> if the game lets you.</li>
<li><b>Turn off the VPN</b> or try a different server. See <a href="/help/vpns-and-websites-that-stop-working">how VPNs can break services</a>.</li>
<li><b>Check the NAT type</b> in your console&rsquo;s network settings. A strict setting can block matchmaking, and router settings can usually fix it.</li>
<li><b>Update</b> the game, the launcher and the system software.</li>
</ul>
<h2>Step 6: scheduled maintenance and updates</h2>
<p>Many games and platforms go offline at set times for maintenance, and new releases and major updates can overload logins for hours. Check the announcement channels. Waiting for a launch-day rush to calm down is often the only fix.</p>
<h2>Signs it is the game, not you</h2>
<ul>
<li>Other games and websites work fine on the same network.</li>
<li>Friends on different providers have the same error at the same time.</li>
<li>The error message mentions servers, capacity or maintenance.</li>
<li>Reports are climbing on our site pages and the outage map.</li>
</ul>
<h2>Signs it is you</h2>
<ul>
<li>Everything online is slow or flaky, not just one game.</li>
<li>Only one device is affected.</li>
<li>Problems are worst in the evening or when others use the connection.</li>
<li>The game works on a mobile hotspot but not at home.</li>
</ul>
<h2>What to do when it is the servers</h2>
<p>Wait. Repeatedly restarting and reconnecting adds to the load, and it can prolong the problem for everyone. Check for updates from the studio, and try again in a little while. If you want to be told the moment a service comes back, a free account here lets you <a href="/monitor">monitor sites</a> and get an email when they recover.</p>
'''
},
{
'slug': 'email-not-working-checklist', 'cat': 'owners',
'title': 'Email not arriving or not sending? A checklist for site owners',
'desc': 'How email delivery depends on DNS records such as MX, SPF and DKIM, and a step-by-step checklist for finding out why messages are missing.',
'related': ['what-is-dns-and-why-it-fails', 'dns-propagation', 'domain-name-expiry'],
'body': '''
<p class="lead">If your own domain&rsquo;s email stops working, either nothing arrives or what you send lands in spam, and the cause is usually in the DNS records rather than in your mailbox. This checklist works from the simplest causes to the more technical ones. You can check most of it with our <a href="/tools/email-checker">email checker</a> and <a href="/tools/mx-record-lookup">MX record lookup</a>.</p>
<h2>How email finds you</h2>
<p>When someone sends a message to you@yourdomain.com, their mail system looks up your domain&rsquo;s <b>MX records</b> in DNS. These list the servers that accept mail for you. The sender connects to one of them and hands the message over. If the records are missing, wrong or point to a service you no longer use, mail has nowhere to go.</p>
<h2>Step 1: is the domain itself healthy?</h2>
<ul>
<li>Has the domain expired? An expired domain stops its DNS working, and email stops with it. See <a href="/help/domain-name-expiry">what happens when a domain expires</a>.</li>
<li>Does the website load? If the whole domain has disappeared, email will not work either. Check with our <a href="/">website checker</a>.</li>
<li>Were the name servers changed recently? New name servers need all your records recreated, including mail ones.</li>
</ul>
<h2>Step 2: check the MX records</h2>
<p>Use the MX lookup to see what your domain publishes. You should see the servers your email provider told you to use. Common problems:</p>
<ul>
<li><b>No MX records at all.</b> Mail cannot be delivered.</li>
<li><b>Old provider&rsquo;s records still present.</b> Mail may go to the wrong place, or only some of it arrives.</li>
<li><b>Typos or wrong priority numbers.</b> Lower numbers are tried first.</li>
<li><b>Records pointing at an address instead of a name,</b> which is not permitted for MX.</li>
</ul>
<p>After a change, allow time for caches to refresh. See <a href="/help/dns-propagation">what DNS propagation means</a>.</p>
<h2>Step 3: check SPF, DKIM and DMARC</h2>
<p>These three records are how receiving servers decide whether a message from your domain is genuine. Without them, even legitimate mail is often sent to spam or refused.</p>
<ul>
<li><b>SPF</b> lists which servers are allowed to send mail for your domain. It is a TXT record that starts with <code>v=spf1</code>. A domain should have only one.</li>
<li><b>DKIM</b> adds a digital signature to each message, which the receiver checks against a key published in your DNS. Your email provider supplies the record.</li>
<li><b>DMARC</b> tells receivers what to do when SPF and DKIM checks fail, and where to send reports. A cautious starting policy is monitoring only, then tightening it once you are sure all your mail passes.</li>
</ul>
<h2>Step 4: if mail you send goes to spam or bounces</h2>
<ul>
<li>Read the bounce message. It usually says why in plain words, such as a failed SPF check or a blocked address.</li>
<li>Check that every service sending mail on your behalf, such as a newsletter tool or a contact form, is included in your SPF record and set up for DKIM.</li>
<li>Avoid sending from your domain through a service that has not been authorised.</li>
<li>Check whether the sending address is on a public block list, which can happen with shared hosting.</li>
</ul>
<h2>Step 5: if mail you expect does not arrive</h2>
<ul>
<li>Look in the spam or junk folder.</li>
<li>Check that the mailbox is not full or suspended.</li>
<li>Ask the sender for the bounce message if they received one.</li>
<li>Check filters and forwarding rules in your mailbox for something that diverts or deletes messages.</li>
<li>Check the email provider&rsquo;s status page for an outage.</li>
</ul>
<h2>Step 6: the website form that sends you email</h2>
<p>If it is a contact form on your website that has stopped sending, the likely culprits are a hosting change that blocked outgoing mail, a form plugin sending from an address that fails SPF checks, or an account password that changed. Sending through an authenticated mail service is more reliable than relying on the web server to send directly.</p>
<h2>Prevent it happening again</h2>
<ul>
<li>Turn on auto-renew for your domain and keep contact details current.</li>
<li>Keep a copy of your DNS records, especially MX, SPF, DKIM and DMARC, somewhere outside your DNS provider.</li>
<li>Send yourself a test from an outside address after every DNS change.</li>
<li>Review your records after you add or remove any service that sends or receives mail.</li>
</ul>
<h2>Summary</h2>
<p>Missing email almost always comes down to the domain, the MX records or the authentication records. Check that the domain is healthy, look up the MX records, confirm SPF, DKIM and DMARC are present and correct, and read any bounce message carefully. It tells you what the receiving server thinks is wrong.</p>
'''
},
{
'slug': 'website-and-network-terms-glossary', 'cat': 'checks',
'title': 'Website and network terms explained: a plain-English glossary',
'desc': 'Short, clear definitions of the terms you meet when a website or connection misbehaves, from DNS and latency to CDNs and TLS.',
'related': ['what-happens-when-you-open-a-website', 'http-status-codes-explained', 'how-our-checks-work'],
'body': '''
<p class="lead">Websites and networks come with a lot of jargon. This glossary explains the terms you are most likely to meet, in plain words, with links to longer guides where we have them. Skim it, or come back when a word in an error message or a status page is unfamiliar.</p>
<h2>A to C</h2>
<dl>
<dt>Availability</dt><dd>The share of time a site or service is working. Usually shown as a percentage. See <a href="/help/uptime-percentages-explained">uptime percentages explained</a>.</dd>
<dt>Bandwidth</dt><dd>How much data a connection can carry per second. Often confused with speed, but a connection can have plenty of bandwidth and still feel slow if latency is high.</dd>
<dt>Blocked (in our results)</dt><dd>The site answered our check but refused to show us the real page, usually because it filters automated traffic. It does not mean the site is down. See <a href="/help/sites-that-block-automated-checks">why some sites block automated checks</a>.</dd>
<dt>Cache</dt><dd>A saved copy of something, kept so it can be reused instead of fetched again. Browsers, DNS resolvers and content delivery networks all keep caches.</dd>
<dt>CDN (content delivery network)</dt><dd>A network of servers around the world that keep copies of a site&rsquo;s files close to visitors. See <a href="/help/what-is-a-cdn-and-why-outages-spread">what a CDN is</a>.</dd>
<dt>Certificate</dt><dd>A digital document that proves a website&rsquo;s identity and enables encrypted connections. See <a href="/help/how-https-and-certificates-work">how HTTPS and certificates work</a>.</dd>
<dt>Cookie</dt><dd>A small piece of data a site stores in your browser, used for things like staying signed in. See <a href="/help/clear-browser-cache-and-cookies">clearing cache and cookies</a>.</dd>
</dl>
<h2>D to H</h2>
<dl>
<dt>DNS (Domain Name System)</dt><dd>The system that turns names like example.com into numeric addresses. See <a href="/help/what-is-dns-and-why-it-fails">what DNS is and why it fails</a>.</dd>
<dt>Downtime</dt><dd>A period when a site or service is not working for its users.</dd>
<dt>Failover</dt><dd>Automatically or manually switching to a backup when the main system fails. See <a href="/help/how-websites-stay-up">how websites stay up</a>.</dd>
<dt>Firewall</dt><dd>Software or hardware that allows or blocks network traffic according to rules.</dd>
<dt>Gateway</dt><dd>A server or device that passes traffic between networks or between parts of a system. A &ldquo;bad gateway&rdquo; error means one server got an invalid answer from another.</dd>
<dt>Hop</dt><dd>One step along the route between two computers, usually a router. See <a href="/help/how-to-read-a-traceroute">how to read a traceroute</a>.</dd>
<dt>HTTP and HTTPS</dt><dd>The language browsers and servers use. HTTPS is the same thing with encryption added.</dd>
</dl>
<h2>I to M</h2>
<dl>
<dt>IP address</dt><dd>The numeric address of a device or server on a network. Look up yours with our <a href="/what-is-my-ip">what is my IP</a> page.</dd>
<dt>ISP (internet service provider)</dt><dd>The company that supplies your internet connection.</dd>
<dt>Jitter</dt><dd>Variation in delay from one message to the next. See <a href="/help/latency-packet-loss-and-jitter-explained">latency, packet loss and jitter</a>.</dd>
<dt>Latency</dt><dd>The time a message takes to travel to a server and back. Often called ping.</dd>
<dt>Load balancer</dt><dd>A system that spreads visitors across several servers and avoids unhealthy ones.</dd>
<dt>MX record</dt><dd>A DNS record that says which servers receive email for a domain. See <a href="/help/email-not-working-checklist">email not working checklist</a>.</dd>
</dl>
<h2>N to R</h2>
<dl>
<dt>Name server</dt><dd>A server that holds a domain&rsquo;s DNS records and answers questions about them.</dd>
<dt>NXDOMAIN</dt><dd>A DNS answer meaning the name does not exist. See <a href="/help/dns-probe-finished-nxdomain">what it means</a>.</dd>
<dt>Origin server</dt><dd>The real server behind a CDN, where a site&rsquo;s files and data actually live.</dd>
<dt>Packet</dt><dd>A small chunk of data. Everything sent over a network is split into packets.</dd>
<dt>Packet loss</dt><dd>The share of packets that never arrive.</dd>
<dt>Ping</dt><dd>A simple test that sends a small message and measures the time for the reply. Also used as another word for latency. Try our <a href="/tools/ping-test">ping test</a>.</dd>
<dt>Probe</dt><dd>A machine that runs our checks from a particular location, so we can see a site from many places.</dd>
<dt>Rate limit</dt><dd>A cap on how many requests are allowed in a given time. See <a href="/help/error-429-too-many-requests">the 429 error</a>.</dd>
<dt>Redirect</dt><dd>An instruction telling a browser to go to a different address. Test one with our <a href="/tools/redirect-checker">redirect checker</a>.</dd>
<dt>Resolver</dt><dd>The server that looks up DNS answers for your device.</dd>
<dt>Router</dt><dd>A device that directs traffic between networks. The box in your home is one.</dd>
</dl>
<h2>S to Z</h2>
<dl>
<dt>SLA (service level agreement)</dt><dd>A promise about service quality, such as a minimum uptime, often with compensation if it is missed. Use our <a href="/tools/uptime-sla-calculator">uptime SLA calculator</a>.</dd>
<dt>SSL and TLS</dt><dd>The technology that encrypts HTTPS connections. TLS is the modern name and SSL the older one people still use.</dd>
<dt>Status code</dt><dd>The three-digit number a server sends to say how a request went. See <a href="/help/http-status-codes-explained">HTTP status codes explained</a>.</dd>
<dt>Timeout</dt><dd>What happens when something takes too long to answer, so the attempt is abandoned. See <a href="/help/err-connection-timed-out">connection timed out</a>.</dd>
<dt>TTL (time to live)</dt><dd>How long a DNS answer may be reused before it must be checked again.</dd>
<dt>Uptime</dt><dd>The opposite of downtime: the time a service is working, often shown as a percentage.</dd>
<dt>VPN</dt><dd>A service that sends your traffic through an encrypted tunnel to another server. See <a href="/help/vpns-and-websites-that-stop-working">why a VPN can break websites</a>.</dd>
</dl>
<p>Missing a term? <a href="/contact">Let us know</a> and we will add it.</p>
'''
},
]
