# More help-centre guides (batch B). Merged into ARTICLES by help_content.py.
ARTICLES_B = [
{
'slug': 'why-is-my-internet-slow', 'cat': 'fix',
'title': 'Why is my internet slow? A step-by-step way to find out',
'desc': 'Work out whether slow internet is your Wi-Fi, your router, your provider or the website, with a short series of tests that each rule something out.',
'related': ['is-it-my-wifi-router-or-isp', 'latency-packet-loss-and-jitter-explained', 'what-is-a-good-response-time'],
'body': '''
<p class="lead">&ldquo;The internet is slow&rdquo; can mean a dozen different things. Pages crawl, video buffers, calls stutter, downloads stall. The trick is to work in order, from the thing closest to you outwards, so each test rules something out.</p>
<h2>First: is it everything, or one site?</h2>
<p>Open two or three unrelated sites. If only one is slow, the problem is probably that site or the route to it, not your connection. Paste it into our <a href="/">website checker</a> to see how it responds from our server and from other countries. If it is quick for us and slow for you, keep reading. If it is slow for everyone, nothing you change at home will help, and it is worth looking at the <a href="/outage-map">outage map</a> and the <a href="/help/what-to-do-when-an-app-or-service-is-down">advice for when a service is down</a>.</p>
<h2>Second: is it one device, or all of them?</h2>
<p>Try another phone or laptop on the same Wi-Fi. If only one device is slow, the cause is on that device: a browser that needs restarting, a full storage drive, a background update, a VPN or a security tool. Restart the device and the browser first, then try a private window to rule out extensions.</p>
<h2>Third: is it the Wi-Fi?</h2>
<p>Run our <a href="/internet-speed-test">speed test</a> standing next to the router, then again in the room where it is slow. A big drop means a Wi-Fi problem, not an internet problem. Common causes:</p>
<ul>
<li><b>Distance and walls.</b> Thick walls, floors and mirrors weaken the signal, and the 5 GHz band is faster but travels less far than 2.4 GHz.</li>
<li><b>Crowded channels.</b> In flats, dozens of neighbouring networks compete for the same airspace. Choosing a different channel, or letting the router pick one automatically, can help.</li>
<li><b>Interference.</b> Microwaves, cordless phones and baby monitors can disturb 2.4 GHz.</li>
<li><b>Too many devices.</b> Many connected gadgets share the same bandwidth, and older ones can slow everyone down.</li>
</ul>
<p>If you can, connect a laptop to the router with a cable and test again. A cable removes Wi-Fi from the picture completely.</p>
<h2>Fourth: is it the router?</h2>
<p>Routers run for months without a break and can slow down or develop faults. Restart yours: unplug it for thirty seconds, plug it back in and wait a few minutes. Check for a firmware update in its settings. If the router is many years old, it may simply not keep up with your plan. Our guide to <a href="/help/is-it-my-wifi-router-or-isp">telling a router fault from an internet provider fault</a> goes deeper.</p>
<h2>Fifth: is it your plan or your provider?</h2>
<p>With a cable connection, a speed test far below what you pay for, at several different times of day, points at the provider or the line. Note the download speed, the upload speed and the ping, then compare them with your plan. Speeds that drop at busy evening hours suggest congestion in your area. A very high ping, or ping that jumps around, suggests a line or routing problem, which our guide to <a href="/help/latency-packet-loss-and-jitter-explained">latency, packet loss and jitter</a> explains.</p>
<h2>Sixth: could something be using your bandwidth?</h2>
<p>A device in the house downloading a large update, backing up photos, or streaming in high quality can use most of your connection, leaving little for everyone else. Pause big downloads and cloud backups and test again. Check that nobody on the network is running something heavy.</p>
<h2>Seventh: could it be DNS?</h2>
<p>If the first page of a site takes a long time to start but then loads fine, slow name lookups are a common cause. Trying a different public DNS resolver in your router or device settings sometimes makes browsing feel snappier. <a href="/help/what-is-dns-and-why-it-fails">What DNS is and why it fails</a> has the background.</p>
<h2>What the numbers mean</h2>
<ul>
<li><b>Download speed</b> matters for streaming, browsing and large files.</li>
<li><b>Upload speed</b> matters for video calls, sending large files and cloud backups.</li>
<li><b>Ping, or latency</b> matters for gaming, calls and how responsive pages feel. Lower is better.</li>
<li><b>Consistency</b> often matters more than the peak number. A steady connection feels faster than a fast one that keeps stalling.</li>
</ul>
<h2>When to contact your provider</h2>
<p>If you have tested with a cable, restarted the router, ruled out your devices and still see speeds well below your plan at several times of day, contact your provider. Having a few speed-test results with dates and times, and saying you tested on a cable, makes the conversation much faster.</p>
<h2>Quick checklist</h2>
<ol>
<li>One site or all sites?</li>
<li>One device or all devices?</li>
<li>Test next to the router, then where it is slow.</li>
<li>Test on a cable if you can.</li>
<li>Restart the router and check for updates.</li>
<li>Pause large downloads and backups.</li>
<li>Test at different times of day and keep the results.</li>
</ol>
'''
},
{
'slug': 'is-it-my-wifi-router-or-isp', 'cat': 'fix',
'title': 'Is it my Wi-Fi, my router or my internet provider?',
'desc': 'A simple method to tell whether an internet problem lives in your Wi-Fi, your router, your provider or the website you are visiting.',
'related': ['why-is-my-internet-slow', 'website-not-loading-checklist', 'works-on-mobile-data-not-wifi'],
'body': '''
<p class="lead">When the internet stops working at home, it helps to know who can fix it. Is it something you can change in a minute, something to ask your provider about, or something that is nothing to do with you? Think of your connection as a chain of links and test them one at a time.</p>
<h2>The chain</h2>
<ol>
<li><b>Your device</b> (phone, laptop, TV).</li>
<li><b>Your Wi-Fi</b>, the wireless link from the device to the router.</li>
<li><b>Your router</b>, the box that joins your home to the wider network.</li>
<li><b>Your provider&rsquo;s network</b>, the line into your home and the equipment beyond it.</li>
<li><b>The wider internet</b>, including the website or service you are trying to reach.</li>
</ol>
<p>A fault at any link looks like &ldquo;the internet is down&rdquo; from the chair you are sitting in. The goal is to find the first broken link.</p>
<h2>Test 1: another site, another device</h2>
<p>If one site fails but others load, the break is almost certainly beyond your provider: the site itself, or the route to it. Use our <a href="/">website checker</a> to see whether it is reachable from elsewhere. If other devices on your Wi-Fi work, the fault is in the first device.</p>
<h2>Test 2: Wi-Fi or mobile data</h2>
<p>Switch a phone from Wi-Fi to mobile data and try the same site. If it works on mobile data but not on Wi-Fi, the problem is in your home setup or your provider, not the site. We cover this in <a href="/help/works-on-mobile-data-not-wifi">why a site works on mobile data but not Wi-Fi</a>. If it fails on both, the site is the more likely cause.</p>
<h2>Test 3: a cable</h2>
<p>Connect a laptop to the router with an Ethernet cable and test again. If the cable connection works well and Wi-Fi does not, the router is fine and the wireless link is the problem. Move closer, change the channel or band, or consider a mesh system for large or awkward homes.</p>
<h2>Test 4: the router&rsquo;s own lights and menu</h2>
<p>Look at the status lights. Most routers show a light for the internet connection. If it is red, amber, off or flashing in a way your manual describes as a fault, the router cannot reach your provider. Restart it and give it several minutes. If the light stays in the fault state, the issue is with the line or the provider. Many routers also have a status page, reached by typing an address printed on the label into your browser, which lists whether the internet connection is up.</p>
<h2>Test 5: your provider&rsquo;s status</h2>
<p>Check your provider&rsquo;s status page or support channels using mobile data. Providers often post known faults by area. Our <a href="/outage-map">outage map</a> may also show reports from other people near you. If there is a known fault, waiting is the right move.</p>
<h2>Test 6: signs that point at the provider</h2>
<ul>
<li>The router&rsquo;s internet light shows a fault even after a restart.</li>
<li>Several different sites fail on every device, on a cable.</li>
<li>Speeds are far below your plan at many different times.</li>
<li>Neighbours on the same provider have the same problem.</li>
</ul>
<h2>Test 7: signs that point at the router</h2>
<ul>
<li>It needs regular restarts to work properly.</li>
<li>Wi-Fi drops while the cable still works.</li>
<li>It is very old, hot to the touch, or has had no updates for years.</li>
<li>Some devices cannot connect at all while others are fine.</li>
</ul>
<h2>Test 8: signs that point at the website</h2>
<ul>
<li>Only one site or app fails.</li>
<li>It fails on mobile data as well.</li>
<li>Other people are reporting the same on our site pages or <a href="/outage-history">outage history</a>.</li>
<li>Our check shows an error from several countries.</li>
</ul>
<h2>What not to do</h2>
<p>Resist the urge to reset the router to factory settings as a first step. It wipes your Wi-Fi name, password and any provider-specific settings, and can leave you with a bigger problem than you started with. Restarting is harmless. A factory reset is a last resort, and only after checking you know your login details.</p>
<h2>Useful things to tell support</h2>
<ul>
<li>What you tested: cable, Wi-Fi, mobile data, which devices.</li>
<li>What the router lights show.</li>
<li>Speed-test results with times, from our <a href="/internet-speed-test">speed test</a> or another.</li>
<li>Whether it started suddenly or got worse over time.</li>
</ul>
<p>With that information, support can skip the basic questions and start with the actual problem.</p>
'''
},
{
'slug': 'latency-packet-loss-and-jitter-explained', 'cat': 'fix',
'title': 'Latency, packet loss and jitter explained',
'desc': 'What ping, packet loss and jitter mean, why they matter for games and video calls even when speed is fine, and how to test for them.',
'related': ['why-is-my-internet-slow', 'what-is-a-good-response-time', 'how-to-read-a-traceroute'],
'body': '''
<p class="lead">Internet speed is only one part of how a connection feels. You can have a very fast plan and still suffer lag in a game, robotic voices on a call or pages that hesitate. The usual reasons are latency, packet loss and jitter. They are easy to measure once you know what they mean.</p>
<h2>Latency</h2>
<p>Latency is the time it takes for a small message to travel to a server and for the answer to come back. It is usually measured in milliseconds and is often called <b>ping</b>. Lower is better.</p>
<p>Part of latency is just distance. Signals in cables travel fast but not instantly, so a server in the same country will normally answer faster than one on another continent. Other parts come from the number of devices on the way, how busy they are, and the quality of your own connection. Wi-Fi often adds a few milliseconds and, when the signal is poor, much more.</p>
<p>As a rough guide: under about 30 milliseconds feels instant, up to about 80 feels good for nearly everything, and above 150 starts to hurt fast-paced games and live conversation. These are rules of thumb, not strict limits. See also <a href="/help/what-is-a-good-response-time">what a good response time is for a website</a>.</p>
<h2>Packet loss</h2>
<p>Data travels in small pieces called packets. Packet loss is the share of those pieces that never arrive. Some protocols quietly resend lost pieces, which hides the problem but adds delay. Others, such as many games and voice or video calls, cannot wait, so lost pieces cause glitches: a character that jumps, a word that drops out, a frozen frame.</p>
<p>Even one or two per cent loss can be noticeable in a live call. Common causes are weak Wi-Fi, a faulty cable or connector, an overloaded router, a congested part of your provider&rsquo;s network, or a problem further along the route.</p>
<h2>Jitter</h2>
<p>Jitter is how much latency varies from one message to the next. A connection that answers in a steady 40 milliseconds every time is much easier to use than one that swings between 20 and 200, even if the average is the same. Voice and video need the pieces to arrive at an even pace, so jitter causes choppy calls and rubber-banding in games.</p>
<h2>Why speed tests do not tell the whole story</h2>
<p>A speed test measures how much data can move per second. It says little about how steady the connection is. A line shared by a busy household can give a great download number and still have bad jitter the moment someone starts a large upload. This effect is sometimes called bufferbloat: the router queues up so much data that every other message waits in line behind it.</p>
<h2>How to test</h2>
<ul>
<li>Run our <a href="/game-ping-test">game ping test</a> or <a href="/tools/ping-test">ping test</a> several times and look at the spread of results, not just the average.</li>
<li>Run the <a href="/internet-speed-test">speed test</a> and look at the ping value as well as the download and upload.</li>
<li>Test on a cable and on Wi-Fi to see how much the wireless link adds.</li>
<li>Test while someone else is using the connection, and while nothing else is, to see whether load makes it worse.</li>
<li>Use a <a href="/help/how-to-read-a-traceroute">traceroute</a> to see where along the route delays or losses begin.</li>
</ul>
<h2>What can improve it</h2>
<ul>
<li><b>Use a cable</b> for gaming consoles, PCs and work computers whenever possible.</li>
<li><b>Improve Wi-Fi</b> by moving closer, changing channel or band, or adding a mesh node.</li>
<li><b>Reduce load.</b> Pause large uploads and backups during calls or games.</li>
<li><b>Check router settings.</b> Some routers have smart queue or quality-of-service options that reduce delays under load.</li>
<li><b>Restart equipment</b> that has been running for a long time.</li>
<li><b>Pick a nearer server</b> in games and apps that let you choose a region.</li>
</ul>
<h2>When it is not your fault</h2>
<p>Sometimes a problem sits in the middle of the route, between your provider and the service. In that case you will see delays or losses at one specific point in a traceroute and little you can do except wait or contact your provider with the evidence. If a particular game or app has problems for many people at once, our <a href="/outage-map">outage map</a> and the service&rsquo;s own status page are the places to look.</p>
<h2>Summary</h2>
<p>Latency is how long a round trip takes, packet loss is how much data goes missing, and jitter is how uneven the delay is. A good connection for live use has low latency, close to zero loss and steady timing. Speed matters for downloads, but for games and calls these three matter at least as much.</p>
'''
},
{
'slug': 'how-to-read-a-traceroute', 'cat': 'fix',
'title': 'How to read a traceroute',
'desc': 'What a traceroute shows, how to read the hops and times, why stars are not always a problem, and how to use the results when talking to support.',
'related': ['latency-packet-loss-and-jitter-explained', 'err-connection-timed-out', 'is-it-my-wifi-router-or-isp'],
'body': '''
<p class="lead">A traceroute shows the path your data takes from one computer to another, one step at a time, and how long each step takes. It looks cryptic at first, but with a few rules you can use it to see roughly where a delay or a break begins. You can run one with our <a href="/tools/traceroute">traceroute tool</a>.</p>
<h2>What it does</h2>
<p>Every message on the internet carries a counter, called a time to live, that goes down by one each time the message passes through a router. When the counter reaches zero the router discards the message and sends a small error back. Traceroute uses that. It sends messages with a counter of 1, then 2, then 3 and so on, and records which router replies at each step. The result is a list of the routers, called hops, between you and the destination.</p>
<h2>Reading the output</h2>
<p>Each line is one hop. It normally shows the hop number, the name or address of the router that replied and several times in milliseconds, usually three, because three probes are sent per hop. A typical journey starts with a router in your own home, then your provider&rsquo;s equipment, then the networks that carry traffic between providers, and finally the destination&rsquo;s network.</p>
<ul>
<li><b>The first hop</b> is usually your own router. If this one is slow or lossy, the problem is in your home network.</li>
<li><b>The next few hops</b> belong to your provider.</li>
<li><b>The middle hops</b> belong to larger networks that carry traffic between providers.</li>
<li><b>The last hops</b> belong to the destination.</li>
</ul>
<h2>What to look for</h2>
<p>The key thing is whether the times <b>stay high from some point onwards</b>.</p>
<ul>
<li>If the time jumps at one hop and every later hop is also high, the delay begins at or just before that hop.</li>
<li>If one hop is high but the hops after it are normal, that router is probably just slow to answer traceroute messages and is not actually causing a delay.</li>
<li>A gradual increase over several hops is normal. Distance adds time, and a big jump when the route crosses an ocean is expected.</li>
</ul>
<h2>Stars</h2>
<p>A line of stars, <code>* * *</code>, means no reply came back for that hop. This is often harmless, because many routers are configured to ignore these probes. It matters only if the stars continue to the end and the destination is never reached. Then something along the route, or at the destination, is blocking or dropping the traffic.</p>
<h2>Where the trace stops</h2>
<ul>
<li><b>It stops at your first hop or two.</b> Your router or the line to your provider has a problem.</li>
<li><b>It stops inside your provider&rsquo;s network.</b> Report it with the trace attached.</li>
<li><b>It stops in the middle of the internet.</b> Often a transient routing issue that fixes itself. Retry in a while.</li>
<li><b>It reaches the last hop and then stars.</b> The destination&rsquo;s network may be dropping or filtering your probes. Many servers deliberately do not answer them, so this does not prove the site is down. Check with the <a href="/">website checker</a>, which tests the real page rather than the probe.</li>
</ul>
<h2>Limits to keep in mind</h2>
<ul>
<li>Traceroute shows the path <b>to</b> the destination. Return traffic can take a different path, so the picture is incomplete.</li>
<li>Routes can change from one run to the next, because networks balance traffic across several paths.</li>
<li>Times at middle hops can be misleading, because routers give these replies low priority.</li>
<li>A clean traceroute does not prove a website works. A site can answer probes and still return errors to real visitors.</li>
</ul>
<h2>Getting the most from it</h2>
<ol>
<li>Run the trace a few times and compare the results, not just one.</li>
<li>Run it at a time the problem is happening and again when it is fine.</li>
<li>Try both Wi-Fi and a cable if you can.</li>
<li>Save the full text, not a screenshot of part of it.</li>
<li>If you contact your provider, include the destination, the time and the trace.</li>
</ol>
<h2>Summary</h2>
<p>A traceroute is a list of the steps between you and a destination, with the time taken at each step. Look for the point from which times stay high or replies stop, and remember that a single slow or silent hop in the middle is usually normal. It is one clue among several, best combined with our <a href="/tools/ping-test">ping test</a> and a check of the site itself.</p>
'''
},
{
'slug': 'how-websites-stay-up', 'cat': 'owners',
'title': 'How websites stay up: redundancy, failover and backups',
'desc': 'The ideas behind reliable websites, including redundancy, load balancing, failover, backups and testing, explained without jargon.',
'related': ['why-big-websites-go-down', 'uptime-percentages-explained', 'how-to-monitor-your-own-website'],
'body': '''
<p class="lead">No website is up all the time. What separates a reliable site from a fragile one is how it is designed to cope when something breaks. The main ideas are old and simple: do not rely on one of anything, notice problems quickly, and practise recovering before you need to.</p>
<h2>Single points of failure</h2>
<p>A single point of failure is any one component whose failure stops everything. A lone web server, a single database, one internet connection, one DNS provider, one person who knows the passwords. Reliability work is largely about finding these and deciding which ones are worth removing.</p>
<h2>Redundancy</h2>
<p>Redundancy means having more than one of something. Two or more web servers can serve the same site, so if one fails the others carry on. Databases can have a copy that follows the main one, ready to take over. Important sites often run in more than one data centre, or even with more than one cloud provider, so a fault in one place does not take everything down.</p>
<p>Redundancy has a cost, in money and in complexity. More moving parts means more things to configure and more ways for the redundancy itself to fail. The aim is to remove the failures that would hurt most, not to duplicate everything.</p>
<h2>Load balancing</h2>
<p>A load balancer sits in front of several servers and spreads visitors between them. It also checks whether each server is healthy and stops sending traffic to any that are not. For visitors this is invisible: one address, many machines behind it.</p>
<h2>Failover</h2>
<p>Failover is the switch from a failed component to its backup. It can be automatic, where the system notices and moves on its own, or manual, where a person decides. Automatic failover is faster but can misfire, for example by switching when there was only a brief blip. Whichever you choose, you need to test it. A failover that has never been tried is a theory, not a plan.</p>
<h2>Backups</h2>
<p>Redundancy and backups solve different problems. Redundancy protects against a machine failing. Backups protect against data being deleted, corrupted or encrypted by an attacker, where a live copy would simply copy the damage. A useful backup routine has these features:</p>
<ul>
<li>It runs automatically and regularly.</li>
<li>Copies are stored somewhere separate from the main system.</li>
<li>Several older versions are kept, not just the latest.</li>
<li>Someone has actually restored from one to prove it works.</li>
</ul>
<h2>Caching and content delivery</h2>
<p>Serving saved copies of pages and files takes load off the main servers and can keep a site partly working when the origin is struggling. A content delivery network spreads those saved copies around the world. The trade-off is that you add another provider that your site depends on. See <a href="/help/what-is-a-cdn-and-why-outages-spread">what a CDN is and why outages spread</a>.</p>
<h2>Graceful degradation</h2>
<p>Even when something fails, a site does not need to fail completely. A shop can keep showing products while checkout is unavailable. A news site can serve cached articles when the comments system is down. Designing for partial failure means the loss of one feature is an annoyance rather than an outage.</p>
<h2>The boring causes</h2>
<p>Many outages are caused by routine things rather than dramatic failures:</p>
<ul>
<li>An <a href="/help/ssl-certificate-errors">expired certificate</a>.</li>
<li>A <a href="/help/domain-name-expiry">domain that was not renewed</a>.</li>
<li>A full disk or exhausted database connections.</li>
<li>A change released with no quick way to undo it.</li>
<li>A <a href="/help/what-is-dns-and-why-it-fails">DNS</a> record edited by mistake.</li>
</ul>
<p>Simple habits fix most of these: automatic renewals, alerts for disk space and expiry dates, and releasing changes gradually.</p>
<h2>Monitoring and communication</h2>
<p>You cannot fix what you do not know about. Monitor your site from outside your own network, with alerts that go to more than one person and do not depend on the same provider as the site. Our <a href="/help/how-to-monitor-your-own-website">monitoring guide</a> explains how, and a free account here can <a href="/monitor">watch your sites</a> and email you when one goes down or recovers.</p>
<p>When something does go wrong, tell people. A short, honest status update early on is worth more than a perfect explanation hours later. See <a href="/help/how-to-write-an-outage-update">how to write an outage update</a>.</p>
<h2>What uptime numbers mean</h2>
<p>Availability is usually quoted as a percentage. 99.9% sounds high but allows about 8 hours and 45 minutes of downtime a year, or about 43 minutes a month. 99.99% allows under an hour a year. Each extra nine is much more expensive than the one before. Our guide to <a href="/help/uptime-percentages-explained">uptime percentages</a> shows what each level means in minutes, and the <a href="/tools/uptime-sla-calculator">uptime SLA calculator</a> does the arithmetic for you.</p>
<h2>A sensible order of priorities</h2>
<ol>
<li>Automatic renewals and expiry alerts.</li>
<li>Tested backups kept off the main system.</li>
<li>Outside monitoring with alerts to more than one person.</li>
<li>A way to roll back a bad change quickly.</li>
<li>Redundancy for the components that hurt most when they fail.</li>
<li>A written plan for who does what in an incident.</li>
</ol>
'''
},
{
'slug': 'website-works-in-one-browser-not-another', 'cat': 'fix',
'title': 'A website works on one browser or device but not another',
'desc': 'Why a site can load on one browser, phone or network but fail on another, and a quick way to find the cause: cache, extensions, VPNs, DNS and more.',
'related': ['down-for-some-people-not-others', 'clear-browser-cache-and-cookies', 'works-on-mobile-data-not-wifi'],
'body': '''
<p class="lead">If a site loads on your phone but not your laptop, or in one browser but not another, the website itself is almost certainly fine. Something specific to the failing device or browser is getting in the way. That is good news, because it narrows the search a lot.</p>
<h2>Start with what is different</h2>
<p>Whatever works and whatever fails differ in some way, and the cause is hiding in that difference. Make a short list: the device, the browser, the network, whether a VPN or security tool is on, whether you are signed in. Then change one thing at a time.</p>
<h2>Common causes</h2>
<h3>Cached or stale data</h3>
<p>Your browser saves copies of pages, scripts and cookies. If the site has changed since, an old saved file can clash with the new page and leave it blank or broken. Try a private window first. If the site works there, clear the cache and cookies for that site. Our guide on <a href="/help/clear-browser-cache-and-cookies">clearing browser cache and cookies</a> shows how.</p>
<h3>Browser extensions</h3>
<p>Ad blockers, privacy tools, script blockers and password managers can break pages by blocking something the page needs. A private window usually runs without extensions, so if the site works there, switch extensions off one by one in the normal window until the culprit shows up.</p>
<h3>VPNs, proxies and security software</h3>
<p>A VPN changes where your traffic appears to come from, and some sites block or limit VPN addresses. Antivirus and web-protection tools can also intercept secure connections and sometimes block sites by mistake. Turn the tool off briefly to test, then turn it back on and adjust its settings instead of leaving it disabled.</p>
<h3>Different networks</h3>
<p>Wi-Fi, mobile data and work or school networks can behave differently. Some networks filter certain categories of site, use their own DNS resolver or block particular ports. If it works on mobile data and not on Wi-Fi, see <a href="/help/works-on-mobile-data-not-wifi">why a site works on mobile data but not Wi-Fi</a>.</p>
<h3>DNS problems on one device</h3>
<p>Each device and router remembers its own DNS answers. One device can have a stale or wrong answer while others have the correct one. A <a href="/help/flush-dns-cache">DNS cache flush</a> on the affected device often fixes it. Our <a href="/help/what-is-dns-and-why-it-fails">DNS guide</a> explains why.</p>
<h3>Wrong date and time</h3>
<p>Secure connections depend on certificates that are valid between two dates. If your device clock is wrong, a perfectly good site can show a certificate error. Set the date and time to automatic. See <a href="/help/ssl-certificate-errors">SSL certificate errors</a>.</p>
<h3>Out-of-date browsers and systems</h3>
<p>Very old browsers or operating systems may not support the security settings modern sites require, or may lack the root certificates needed to trust newer certificates. Update the browser and the system.</p>
<h3>The IP address or region</h3>
<p>A site can block specific addresses, countries or networks, often as a security measure. Your address may have been caught by an automatic filter, or your provider&rsquo;s address range may be blocked. Our guide on <a href="/help/error-403-forbidden">the 403 forbidden error</a> and <a href="/help/error-429-too-many-requests">the 429 too many requests error</a> covers the typical messages.</p>
<h2>A quick method</h2>
<ol>
<li>Open the site in a private window in the same browser.</li>
<li>Open it in a different browser on the same device.</li>
<li>Open it on a different device on the same network.</li>
<li>Open it on the same device on a different network, such as mobile data.</li>
<li>Check our <a href="/">website checker</a> to see if the site answers from elsewhere.</li>
</ol>
<p>Each step eliminates one group of causes. If it fails in every browser on every device on your home network but works on mobile data, look at the network. If it fails only in one browser, look at that browser&rsquo;s cache, extensions and settings. If it fails everywhere and our check also fails, the site really is down.</p>
<h2>When it is the site after all</h2>
<p>Sometimes a site has a fault that affects only some visitors: one region, one browser version, one network. The signs are people reporting the same problem and our check showing different results from different countries. Our guide to <a href="/help/down-for-some-people-not-others">sites that are down for some people but not others</a> describes why this happens and what to do about it.</p>
<h2>Summary</h2>
<p>If it works somewhere, the site is up. Compare what is different between the working and failing setups and change one thing at a time. Cache, extensions, VPNs, DNS and the clock account for most cases.</p>
'''
},
{
'slug': 'how-to-write-an-outage-update', 'cat': 'owners',
'title': 'How to write an outage update that people will trust',
'desc': 'A practical guide for site owners on what to say when your site or service is down, with templates and the mistakes to avoid.',
'related': ['how-websites-stay-up', 'how-to-monitor-your-own-website', 'why-big-websites-go-down'],
'body': '''
<p class="lead">When your site or service goes down, the first thing customers want to know is not why. It is whether you know and whether anyone is dealing with it. A clear, honest update in the first few minutes builds trust. Silence, or a vague message, erodes it. This guide covers what to say, where to say it and the mistakes to avoid.</p>
<h2>Say something quickly</h2>
<p>You do not need the cause to send a first message. You need three things: that you are aware, what is affected and when you will update next. Waiting until you understand everything usually means waiting too long.</p>
<p><b>First message, example:</b> &ldquo;We are aware that some customers cannot sign in. We are investigating and will post another update within 30 minutes.&rdquo;</p>
<h2>What every update should contain</h2>
<ul>
<li><b>What is affected.</b> Be specific: sign-in, checkout, the mobile app, a region.</li>
<li><b>What is not affected.</b> This stops people worrying about things that are fine.</li>
<li><b>What you are doing.</b> One sentence is enough.</li>
<li><b>When you will update next.</b> Then keep to it, even if the update is &ldquo;no change&rdquo;.</li>
<li><b>What customers can do meanwhile,</b> if anything.</li>
</ul>
<h2>Where to post it</h2>
<p>Use a place that does not depend on the thing that is broken. If your status page lives on the same servers as your site, it will vanish when you need it most. Good options are a status page hosted with a separate provider, a social account customers already follow and an email to affected customers. Mention the status address in your site footer and support replies ahead of time, so people know where to look.</p>
<h2>A simple structure for the whole incident</h2>
<ol>
<li><b>Investigating.</b> You know there is a problem and are looking into it.</li>
<li><b>Identified.</b> You know the cause and are working on a fix.</li>
<li><b>Monitoring.</b> A fix is in and you are watching to make sure it holds.</li>
<li><b>Resolved.</b> Everything is back to normal.</li>
</ol>
<p>These four states are a widely used convention and customers recognise them. Use the same words each time.</p>
<h2>Tone</h2>
<ul>
<li><b>Plain words.</b> Say &ldquo;some people cannot log in&rdquo;, not &ldquo;we are experiencing degraded authentication throughput&rdquo;.</li>
<li><b>Own it.</b> A short, sincere apology is better than excuses or blaming a supplier.</li>
<li><b>Do not over-promise.</b> &ldquo;We expect this to be fixed within the hour&rdquo; becomes a problem if it is not. Commit to when you will next update rather than when it will be fixed.</li>
<li><b>Do not guess about the cause.</b> If you are unsure, say you are investigating.</li>
</ul>
<h2>Mistakes to avoid</h2>
<ul>
<li>Saying nothing and hoping nobody notices.</li>
<li>Describing a serious outage as &ldquo;minor&rdquo; or &ldquo;a brief issue&rdquo; while customers can see otherwise.</li>
<li>Using different words for the same problem across channels.</li>
<li>Posting a fix as complete before it is confirmed.</li>
<li>Blaming individuals. Describe the system, not the person.</li>
</ul>
<h2>After it is fixed</h2>
<p>Once things are stable, post a short summary: what happened, when it started and ended, what was affected and what you are changing to prevent a repeat. You do not need to share every technical detail, but a truthful, specific account earns more trust than a polished one. Inside your team, hold a review focused on how the system allowed the failure, not on who made the mistake.</p>
<h2>Templates</h2>
<p><b>Investigating:</b> &ldquo;We are investigating reports that [what] is not working for some customers. Next update by [time].&rdquo;</p>
<p><b>Identified:</b> &ldquo;We have identified the cause of the [what] problem and are working on a fix. [What customers can do.] Next update by [time].&rdquo;</p>
<p><b>Monitoring:</b> &ldquo;A fix has been applied and [what] is working again. We are monitoring to be sure it holds.&rdquo;</p>
<p><b>Resolved:</b> &ldquo;This incident is resolved. [What happened, in a sentence or two.] We are sorry for the disruption and will [what you are changing].&rdquo;</p>
<h2>Know before they tell you</h2>
<p>The best update is the one you send before customers write in. That needs monitoring that checks your site from outside and alerts you the moment it fails. A free account here lets you <a href="/monitor">watch your sites</a> and receive an email when one goes down and when it comes back. Our guide to <a href="/help/how-to-monitor-your-own-website">monitoring your own website</a> covers the rest.</p>
'''
},
]
