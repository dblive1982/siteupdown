# More help-centre guides (batch E). Merged into ARTICLES by help_content.py.
ARTICLES_E = [
{
'slug': 'uptime-alerts-without-alert-fatigue', 'cat': 'owners',
'title': 'How to set up uptime alerts without alert fatigue',
'desc': 'Practical rules for monitoring alerts that people actually act on: what to check, how often, how many failures to wait for, and who to tell.',
'related': ['how-to-monitor-your-own-website', 'uptime-percentages-explained', 'how-to-write-an-outage-update'],
'body': '''
<p class="lead">Monitoring is only useful if the alerts are trusted. If your phone buzzes for every blip, you will soon ignore it, and the one alert that matters will be missed. If alerts are too rare, customers tell you about outages before your own tools do. This guide covers how to find the balance.</p>
<h2>Start with what matters to users</h2>
<p>Do not begin with a list of servers. Begin with what your visitors need to do: load the home page, sign in, search, pay. Each of those journeys is worth watching, because a site can respond to a simple request while a key feature is broken. A page that returns a normal response but shows an error message is a very common failure, so check for a specific word on the page as well as the status code. Our <a href="/monitor">monitor</a> supports keyword and port checks for this reason.</p>
<h2>How often to check</h2>
<p>Frequency is a trade-off. Checking every minute detects a problem within about a minute, but small, brief problems will trigger more alerts. Checking every five minutes is calmer and is plenty for most small sites. A rough guide:</p>
<ul>
<li><b>Business-critical services</b> (payments, sign-in): every minute.</li>
<li><b>Normal websites and shops:</b> every one to five minutes.</li>
<li><b>Blogs, brochure sites, internal tools:</b> five to fifteen minutes.</li>
</ul>
<h2>Wait for confirmation before alerting</h2>
<p>The biggest single cause of false alarms is alerting on one failed check. The internet is not perfectly reliable: a lost packet, a busy moment or a short network blip can fail a single request without any real problem. A better rule is to alert only after two or three consecutive failures, or when several locations agree. That adds a few minutes of delay and removes most of the noise. It is the same principle we use: we count a site as down only after repeated failed checks, as described in <a href="/help/how-our-checks-work">how our checks work</a>.</p>
<h2>Check from more than one place</h2>
<p>If the only thing watching your site sits next to it in the same data centre, it will happily report that everything is fine while visitors elsewhere cannot get through. Checking from outside, and from a few regions, shows what real people see. It also helps you tell a partial problem, such as one region or one provider, from a total outage. See <a href="/help/down-for-some-people-not-others">why a site can be down for some people and not others</a>.</p>
<h2>Separate urgent from informational</h2>
<p>Not every event deserves the same noise. Sort alerts into levels:</p>
<ul>
<li><b>Wake someone up:</b> the site is down or checkout is failing.</li>
<li><b>Look at it today:</b> responses are slow, a certificate expires in two weeks, a domain renews soon.</li>
<li><b>Just record it:</b> a short blip that recovered by itself.</li>
</ul>
<p>Routing the second and third groups to email rather than a phone alarm keeps the urgent channel meaningful. Certificate and domain expiry in particular should alert well in advance, since they are entirely preventable. See <a href="/help/domain-name-expiry">domain name expiry</a> and <a href="/help/ssl-certificate-errors">SSL certificate errors</a>.</p>
<h2>Tell the right people, in the right place</h2>
<p>Decide in advance who receives each alert and what they should do first. One named person on call is better than a group that each assumes someone else will respond. Send alerts to the place people already look, such as email, Telegram, Slack or Discord, and include in the message what failed, since when, and a link to the status or runbook.</p>
<h2>Alert on recovery too</h2>
<p>A &ldquo;back up&rdquo; message tells the team they can stop investigating and gives you the length of the outage for your records. It also confirms that the problem was real. Without it, a quiet channel is ambiguous.</p>
<h2>Review regularly</h2>
<ul>
<li>Once a month, look at which alerts fired and which needed action. Any alert that never needs action should be loosened or removed.</li>
<li>After each real incident, ask whether you heard about it quickly enough, and whether an earlier warning, such as slow responses, was missed.</li>
<li>Keep an eye on the trend of your uptime. Our guide to <a href="/help/uptime-percentages-explained">uptime percentages</a> shows what each figure means in minutes of real downtime.</li>
</ul>
<p>Good alerting is quiet most of the time, specific when it speaks, and impossible to ignore when it matters. When something does go wrong, tell your own users promptly, using the approach in <a href="/help/how-to-write-an-outage-update">how to write an outage update</a>.</p>
'''
},
{
'slug': 'wifi-keeps-disconnecting', 'cat': 'fix',
'title': 'Wi-Fi keeps disconnecting: causes and fixes',
'desc': 'Why a Wi-Fi connection drops again and again, how to tell whether the router, the device or the provider is at fault, and what to try in order.',
'related': ['is-it-my-wifi-router-or-isp', 'why-is-my-internet-slow', 'latency-packet-loss-and-jitter-explained'],
'body': '''
<p class="lead">A connection that works, drops, and returns again is more frustrating than one that is simply slow. Video calls freeze, downloads restart and pages stall. The cause could be your device, your router, interference or your provider, and the fix depends on which. This guide helps you narrow it down, then work through the likely remedies in a sensible order.</p>
<h2>First, work out how widespread it is</h2>
<ul>
<li><b>Only one device drops.</b> The problem is likely with that device: its Wi-Fi adapter, its settings, or its software.</li>
<li><b>Every device drops at the same moments.</b> The router, the wiring or the internet service is more likely.</li>
<li><b>Wi-Fi drops but a cable stays steady.</b> That points to wireless problems such as distance, interference or a failing router radio, not your provider.</li>
<li><b>Even a cable drops.</b> The router, modem or provider is the suspect. See <a href="/help/is-it-my-wifi-router-or-isp">is it my Wi-Fi, router or ISP?</a></li>
</ul>
<h2>Fixes to try, quick ones first</h2>
<ol>
<li><b>Restart the router.</b> Switch it off at the power for thirty seconds, then on again. Routers run for months and slowly accumulate faults, and a restart clears a surprising number of them.</li>
<li><b>Move closer, or move the router.</b> Walls, floors, mirrors, fish tanks and large metal objects weaken the signal. A router in a cupboard or on the floor performs worse than one that is raised and in the open, near the middle of the home.</li>
<li><b>Change the Wi-Fi channel or band.</b> In crowded buildings, neighbouring networks interfere. The 5&nbsp;GHz band is faster and less crowded but has shorter range; 2.4&nbsp;GHz reaches further but is easily disturbed by microwaves, baby monitors and Bluetooth devices. Try switching, or set the channel manually in the router settings rather than leaving it on automatic.</li>
<li><b>Update the router&rsquo;s firmware</b> and your device&rsquo;s network drivers. Many drop-out bugs are fixed in updates.</li>
<li><b>Forget the network and rejoin.</b> On your device, remove the saved network and connect again with the password. This clears a corrupted saved profile.</li>
<li><b>Turn off power saving for the Wi-Fi adapter.</b> On some laptops, the setting that lets Windows switch the adapter off to save power causes repeated drops. It is found in the adapter&rsquo;s properties in Device Manager.</li>
<li><b>Check for too many devices.</b> Dozens of connected gadgets, especially older ones, can overload a basic router. Disconnect devices you do not use, or upgrade to a router that handles more.</li>
<li><b>Check cables and filters.</b> A loose or damaged cable between the wall and the router, or a missing or faulty filter on a broadband phone line, can cause regular drops that look like a wireless problem.</li>
<li><b>Try another DNS server.</b> If pages fail to load while the Wi-Fi symbol still shows connected, the problem may be name lookups, not the connection. See <a href="/help/how-to-change-your-dns-server">how to change your DNS server</a>.</li>
</ol>
<h2>Signs it is your internet provider</h2>
<p>If the router&rsquo;s own status lights show that the internet connection is lost, if the problem happens at the same time of day, or if neighbours report the same, the fault is outside your home. Note the times and run a test while it is happening. A steady ping to a reliable address that shows lost replies is useful evidence: see <a href="/help/latency-packet-loss-and-jitter-explained">latency, packet loss and jitter explained</a>. You can also try our <a href="/internet-speed-test">internet speed test</a>, and use our <a href="/outage-map">outage map</a> to see whether problems are widespread. Contact your provider with the times and your findings, and ask them to test the line.</p>
<h2>Is it the website, not your Wi-Fi?</h2>
<p>If only one site or app seems to fail while everything else works, your Wi-Fi is fine. Paste the address into the <a href="/">website checker</a> to see whether it is down for everyone, and read <a href="/help/why-is-my-internet-slow">why is my internet slow</a> for slowness that comes and goes.</p>
<h2>When to replace the router</h2>
<p>A router more than five or six years old, one that overheats, or one that needs restarting every few days is a good candidate for replacement. Many providers will send a new one on request. If your home is large or has thick walls, a mesh system or a wired access point in the far end of the house often fixes drops more reliably than a stronger single router.</p>
'''
},
{
'slug': 'how-to-choose-reliable-web-hosting', 'cat': 'owners',
'title': 'How to choose reliable web hosting',
'desc': 'What to look for in a web host if uptime matters: uptime promises, support, backups, location, scaling and the questions to ask before you sign up.',
'related': ['how-websites-stay-up', 'uptime-percentages-explained', 'speed-up-your-website'],
'body': '''
<p class="lead">Your host decides, more than anything else you control, how often your site is available and how quickly it responds. Marketing pages all promise reliability, so it helps to know what is meaningful. This guide explains what to look for and what to ask, whether you are starting a first site or moving away from a host that keeps letting you down.</p>
<h2>Understand the types of hosting</h2>
<ul>
<li><b>Shared hosting.</b> Many sites share one server. It is cheap and suitable for small sites, but a busy neighbour can slow yours, and you have less control.</li>
<li><b>Virtual private servers (VPS).</b> You get a guaranteed slice of a server. More control and more consistent performance, but you manage more yourself.</li>
<li><b>Managed hosting.</b> The provider looks after the software, updates and security for a specific platform such as WordPress. Costs more, saves time.</li>
<li><b>Cloud hosting.</b> Resources spread across a provider&rsquo;s infrastructure and can grow with demand. Flexible, but pricing and set-up can be complex.</li>
</ul>
<p>The right choice depends on traffic, budget and how much you want to look after. A small brochure site rarely needs more than good shared or managed hosting. A shop that loses money for every minute offline deserves more.</p>
<h2>What an uptime guarantee really means</h2>
<p>Hosts often advertise 99.9% uptime. That sounds almost perfect, but it allows about 43 minutes of downtime each month and around 8 hours 46 minutes a year, and 99.99% allows under 5 minutes a month. See <a href="/help/uptime-percentages-explained">uptime percentages explained</a> for the full table. Read the fine print:</p>
<ul>
<li><b>What counts as downtime?</b> Planned maintenance is often excluded.</li>
<li><b>What is the remedy?</b> Usually a small credit, not compensation for lost sales.</li>
<li><b>Who measures it?</b> A promise measured by the host itself is weaker than independent monitoring.</li>
</ul>
<p>Treat the number as a statement of intent. A better test is how the host behaves when something goes wrong.</p>
<h2>Questions worth asking</h2>
<ol>
<li><b>How do you handle failures?</b> Ask whether servers are redundant, what happens if hardware dies, and whether sites move automatically.</li>
<li><b>How good is support, and when is it available?</b> Look for human support at the hours you need it, not only a chatbot. Test it with a pre-sales question and see how quickly and clearly it is answered.</li>
<li><b>Are backups included, and how do I restore them?</b> Daily backups stored away from the server are the minimum. Ask how long a restore takes and whether you can do it yourself.</li>
<li><b>Where are the servers?</b> Choosing a location close to most visitors reduces response time. A <a href="/help/what-is-a-cdn-and-why-outages-spread">content delivery network</a> can reduce that effect.</li>
<li><b>What are the limits?</b> Ask about caps on visitors, processing time, memory and storage, and what happens when you reach them: slowdown, extra charge or suspension.</li>
<li><b>How do renewals and upgrades work?</b> Introductory prices often rise sharply at renewal. Check the long-term cost, not just the first-year price.</li>
<li><b>Is there a status page?</b> A host that publishes incidents openly is usually one that takes reliability seriously. See <a href="/help/how-to-use-a-status-page">how to use a status page</a>.</li>
</ol>
<h2>Judge it with evidence</h2>
<p>Look for independent reviews that describe problems as well as praise, and be cautious of lists that exist mainly to earn referral commissions. After signing up, do not take reliability on trust: set up <a href="/help/how-to-monitor-your-own-website">your own monitoring</a> from outside the host, and use the <a href="/speed">speed test</a> now and then to see how response times change through the day. A few weeks of data tells you far more than any brochure.</p>
<h2>Protect yourself whichever host you pick</h2>
<ul>
<li>Keep your own copy of backups, not only the host&rsquo;s.</li>
<li>Register your domain separately from the host, so you can move without losing control. See <a href="/help/domain-name-expiry">domain name expiry</a>.</li>
<li>Know how to change your DNS records quickly, and keep the time-to-live short before a planned move. See <a href="/help/dns-propagation">DNS propagation</a>.</li>
<li>Keep software up to date, because many outages are caused by compromised or outdated sites, not by the host.</li>
</ul>
<p>Reliability is a combination of the host, your own set-up and how quickly you notice problems. The right host makes the first part easy. Monitoring takes care of the third.</p>
'''
},
{
'slug': 'website-blocked-in-your-country', 'cat': 'fix',
'title': 'Why a website may be blocked in your country, and how to tell',
'desc': 'How to tell whether a site is blocked by your network, your country or the site itself, what the different errors suggest and what is reasonable to do.',
'related': ['down-for-some-people-not-others', 'vpns-and-websites-that-stop-working', 'works-on-mobile-data-not-wifi'],
'body': '''
<p class="lead">Sometimes a website works for friends overseas but not for you. It may not be broken at all. It can be blocked on your network, restricted in your country, or set to refuse visitors from your region. This guide explains the different kinds of blocking, how to tell them apart from a real outage, and what is sensible to do about each.</p>
<h2>Down, or blocked?</h2>
<p>Start by establishing whether the site works anywhere else. Paste the address into the <a href="/">website checker</a>, which tests from our server, and look at the <a href="/outage-map">outage map</a>, which shows how sites respond from fifteen places around the world. If a site loads from other countries but not from yours, or fails only on your connection, you are probably dealing with a block or a regional restriction, not an outage. See also <a href="/help/down-for-some-people-not-others">why a site can be down for some people and not others</a>.</p>
<h2>The main kinds of blocking</h2>
<ul>
<li><b>Network blocking by the place you are connected.</b> Schools, workplaces, libraries and public Wi-Fi often filter categories such as social media, gaming or streaming. If the site works on mobile data or at home, this is the cause. See <a href="/help/works-on-mobile-data-not-wifi">works on mobile data but not Wi-Fi</a>.</li>
<li><b>Internet provider filters.</b> Some providers apply filters, sometimes by default and sometimes because a court has ordered certain sites to be blocked. Many let you review or switch off optional filters in your account.</li>
<li><b>Country-level restrictions.</b> A government may require providers to block particular sites or services, either temporarily or permanently. This is a legal and political matter, and the experience varies a great deal between countries and over time.</li>
<li><b>The site restricting you.</b> Some websites deliberately refuse visitors from certain countries, because of licensing, law, or security policy. The site, not your network, makes that choice, and it usually shows a message such as &ldquo;not available in your region&rdquo; or &ldquo;access denied&rdquo;. See <a href="/help/error-403-forbidden">error 403 forbidden</a>.</li>
<li><b>Security services in front of the site.</b> Some sites sit behind protection that blocks addresses with a poor reputation. Shared networks, some VPNs and compromised devices can get caught by this.</li>
</ul>
<h2>What different symptoms suggest</h2>
<ul>
<li><b>A page that says the site is blocked, restricted or filtered</b> comes from your network or provider.</li>
<li><b>A message from the site itself about your region</b> means the site is restricting access.</li>
<li><b>A connection that simply times out or resets</b> is ambiguous. It might be an outage, a firewall or a block. Compare with another connection, and see <a href="/help/err-connection-timed-out">connection timed out</a>.</li>
<li><b>A name that does not resolve</b> may be caused by DNS filtering by your provider or network. Our <a href="/tools/dns-lookup">DNS lookup</a> shows what the name should return, and you can compare with what your device gets.</li>
</ul>
<h2>What is reasonable to do</h2>
<ol>
<li><b>Check with another connection.</b> Try mobile data, or another network, to learn whether the block is tied to where you are.</li>
<li><b>Look at your provider or network settings.</b> Filters that are optional can be changed in your account or by asking the administrator.</li>
<li><b>Contact the site.</b> If the site is refusing your region, its support pages usually explain why and which countries are affected.</li>
<li><b>Think about the rules before using a workaround.</b> A VPN can change where a site thinks you are, and many people use one for privacy. But bypassing a restriction can break a service&rsquo;s terms of use, and in some countries or workplaces it is against the rules. Read <a href="/help/vpns-and-websites-that-stop-working">why a VPN can break websites</a>, and make an informed decision about the risks in your situation.</li>
</ol>
<h2>If you run a website</h2>
<p>If visitors in one country report they cannot reach you, test from that region. The outage map and regional checks help. Look at any country or address rules in your security settings, and check that a protection service is not treating a whole network as hostile. Tell visitors plainly when you restrict access, and why, so they are not left guessing.</p>
<p class="note">We report whether our own checks can reach a site. We cannot say why a particular country blocks a site, and we make no claims about the laws of any place.</p>
'''
},
{
'slug': 'website-changes-not-showing', 'cat': 'owners',
'title': 'Why changes to your website are not showing up',
'desc': 'The layers of caching between you and your visitors, how to find which one is holding an old version, and how to clear each safely.',
'related': ['clear-browser-cache-and-cookies', 'dns-propagation', 'what-is-a-cdn-and-why-outages-spread'],
'body': '''
<p class="lead">You updated your website, but when you load it, the old version is still there. Or you see the change, and a customer does not. This is almost never a failed update. It is caching: copies of your pages stored in several places between your server and a visitor&rsquo;s screen, each of which may hold on to the old version for a while. This guide walks through those layers so you can find the one responsible.</p>
<h2>Why caching exists</h2>
<p>Fetching a fresh copy of every file for every visitor would be slow and expensive. So copies are kept: in the browser, on a content network, in the server&rsquo;s software, and sometimes inside the site itself. Caching is the reason big sites are fast. The price is that a change can take time to appear everywhere.</p>
<h2>The layers, from nearest the visitor to nearest the server</h2>
<ol>
<li><b>The browser.</b> Browsers store images, styles and scripts, and sometimes whole pages, for hours or days. Try a hard refresh (Ctrl+F5, or Cmd+Shift+R on a Mac), or open the page in a private window. If the new version appears there, your normal browser is holding an old copy. See <a href="/help/clear-browser-cache-and-cookies">how to clear cache and cookies</a>.</li>
<li><b>A device or network.</b> Phones, some work networks and mobile carriers also keep copies. Testing on mobile data, away from your usual network, helps rule this in or out.</li>
<li><b>A content delivery network.</b> If your site uses one, copies live at locations around the world and are refreshed according to rules you set. Most have a &ldquo;purge&rdquo; or &ldquo;clear cache&rdquo; button, and some let you purge a single page. See <a href="/help/what-is-a-cdn-and-why-outages-spread">what is a CDN</a>.</li>
<li><b>Your site&rsquo;s caching plugin or server cache.</b> Many platforms save finished pages so they do not rebuild them for each visit. Clear it after any significant change, and check whether more than one layer is configured, since a plugin and the host may each keep their own.</li>
<li><b>Your own files.</b> Check that you changed the file that is actually live. Editing a copy, a staging site or the wrong folder is a surprisingly common reason a change &ldquo;does not work&rdquo;.</li>
</ol>
<h2>When it is DNS, not caching</h2>
<p>If you changed hosting, moved a domain or edited address records, some visitors may still be sent to the old server for a while, because DNS answers are also cached, for as long as the record&rsquo;s time-to-live allows. This is why some people see the new site and others the old one for a day or so. Read <a href="/help/dns-propagation">DNS propagation</a> and use our <a href="/tools/dns-lookup">DNS lookup</a> to see what address the name returns now. To make future moves smoother, lower the time-to-live a day or two before the change.</p>
<h2>How to find the layer holding the old version</h2>
<ul>
<li><b>Private window, same computer:</b> new version means a browser cache.</li>
<li><b>Different device on mobile data:</b> new version means your own network or device was the cause.</li>
<li><b>The server&rsquo;s address directly, or a staging address:</b> new version there but not on the live address points to the CDN or the page cache.</li>
<li><b>Response headers.</b> Look at the cache-related headers a page returns. Our <a href="/tools/http-header-checker">HTTP header checker</a> shows them, including how long a copy may be kept and whether a CDN served it.</li>
</ul>
<h2>Stopping it happening again</h2>
<ul>
<li><b>Version your files.</b> Adding a changing number to style and script file names, such as <code>style.css?v=12</code>, makes browsers fetch the new file immediately. Many build tools do this automatically.</li>
<li><b>Choose sensible cache lifetimes.</b> Long lifetimes for files that rarely change, such as images, and short ones for pages that change often.</li>
<li><b>Purge as part of publishing.</b> Make clearing the caches a routine step of every release, not an afterthought.</li>
<li><b>Test after each change</b> from a clean browser and, for important changes, from another network. A <a href="/help/how-to-monitor-your-own-website">monitor</a> with a keyword check can confirm that the new text is live.</li>
</ul>
<p>Remember that your visitors may not do a hard refresh. If you change something urgent, such as a price or a notice, purge the layers you control and test it rather than assuming everyone sees what you see.</p>
'''
},
]
