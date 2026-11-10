# More help-centre guides (batch F). Merged into ARTICLES by help_content.py.
ARTICLES_F = [
{
'slug': 'ai-chatbot-or-ai-tool-not-working', 'cat': 'fix',
'title': 'ChatGPT, Claude or another AI tool not working? What to check',
'desc': 'Why AI chat tools slow down, error out or stop answering, how to tell an outage from a problem on your side, and what to do while you wait.',
'related': ['is-it-down-or-just-me', 'error-429-too-many-requests', 'what-to-do-when-an-app-or-service-is-down'],
'body': '''
<p class="lead">AI chat tools are some of the busiest services on the internet. When one stops answering, it is usually capacity or a service fault, not your device, but a few local causes are worth ruling out first.</p>
<h2>What the symptoms usually mean</h2>
<ul>
<li><b>Endless spinner or &ldquo;something went wrong&rdquo;:</b> the service accepted your request but could not complete it. Typical of overload or a partial outage.</li>
<li><b>&ldquo;At capacity&rdquo; or a queue message:</b> too many people at once. It clears as demand drops.</li>
<li><b>Replies stop halfway:</b> the connection dropped while the answer was being streamed. Your network, a VPN, or a server restart can cause it.</li>
<li><b>Error 429:</b> you or your network sent too many requests. See <a href="/help/error-429-too-many-requests">error 429</a>.</li>
<li><b>Error 5xx:</b> the service itself failed. Read the <a href="/help/server-errors-500-502-503-504">server error guide</a>.</li>
<li><b>Login loops:</b> often a stale cookie or a problem at the sign-in provider rather than the chat tool itself.</li>
</ul>
<h2>Why AI services are fragile under load</h2>
<p>Each answer needs a lot of computing power, and that cannot be cached the way a web page can. A sudden surge, for example after a new model launch or a news story, can use up capacity. The website, the sign-in system and the model that writes the answers are separate parts, and any one of them can fail while the others work. That is why a site can load fine while the chat itself errors.</p>
<h2>Step by step</h2>
<ol>
<li>Run the tool&rsquo;s address through the <a href="/">checker</a>. If it fails from many places, it is the service.</li>
<li>Check the provider&rsquo;s own status page. These often name which part is affected, such as the API, logins or one model.</li>
<li>If the service is up, refresh once, then try a private window to rule out cookies and extensions.</li>
<li>Turn off a VPN or ad blocker for a moment. Some AI sites treat VPN traffic as risky.</li>
<li>Try another network, such as mobile data.</li>
<li>Start a new chat. A very long conversation can hit limits that a new one does not.</li>
</ol>
<h2>A worked example</h2>
<p>You send a prompt and see &ldquo;network error&rdquo; after ten seconds. The checker shows the website up but the status page lists &ldquo;elevated errors&rdquo; for the chat feature. That is a partial outage. Retrying repeatedly will not help and can trigger rate limits, so you wait and check again in 15 minutes. If the status page showed nothing, but the problem only happened on Wi-Fi, a router restart or a different DNS server would be the next test.</p>
<h2>While you wait</h2>
<ul>
<li>Copy any long prompt you wrote somewhere safe so you do not lose it.</li>
<li>Avoid resubmitting the same request many times.</li>
<li>If you rely on the tool for work, keep an alternative ready and use the <a href="/account">watchlist</a> to get an email when it recovers.</li>
</ul>
<h2>If you build on an AI API</h2>
<p>Add retries with increasing delays, set sensible timeouts, handle 429 and 5xx responses separately, and avoid sending bursts of requests. Monitoring your own endpoint, plus the provider&rsquo;s, tells you quickly whether a failure is yours or theirs. See <a href="/help/how-to-monitor-your-own-website">how to monitor your own website</a>.</p>
'''
},
{
'slug': 'social-media-app-not-loading', 'cat': 'fix',
'title': 'Instagram, WhatsApp, TikTok or Facebook not loading? How to tell what is wrong',
'desc': 'A clear guide to social media outages: the difference between the app, the feed and messages failing, and what to try on your phone before you blame the service.',
'related': ['what-to-do-when-an-app-or-service-is-down', 'works-on-mobile-data-not-wifi', 'is-it-down-or-just-me'],
'body': '''
<p class="lead">When a social app misbehaves, millions of people reach for their phone to check if it is just them. The answer depends on which part is failing, because an app is made of several services that can break separately.</p>
<h2>Which part is broken?</h2>
<ul>
<li><b>The app will not open or crashes:</b> usually the app or phone, not a server outage. Update the app and restart the phone.</li>
<li><b>Feed will not refresh, or shows old posts:</b> the app cannot reach its servers. This can be your connection or a service fault.</li>
<li><b>Photos and videos will not load but text does:</b> the media delivery network is struggling. This is typical of partial outages.</li>
<li><b>Messages will not send or arrive:</b> messaging servers are separate from the feed. Messaging can fail while everything else works.</li>
<li><b>You are logged out or asked to verify:</b> a sign-in problem, or a security check triggered by a new device or VPN.</li>
<li><b>&ldquo;Try again later&rdquo; after many actions:</b> you hit a limit on likes, follows or messages. Wait and slow down.</li>
</ul>
<h2>Checks on your phone first</h2>
<ol>
<li>Switch between Wi-Fi and mobile data. If it works on one, the other connection has a problem (see <a href="/help/works-on-mobile-data-not-wifi">works on mobile data but not Wi-Fi</a>).</li>
<li>Turn on airplane mode for ten seconds, then off, to reset the connection.</li>
<li>Close the app completely and reopen it.</li>
<li>Update the app and check that your phone has free storage. A nearly full phone makes apps misbehave.</li>
<li>Check the date and time are set automatically. A wrong clock breaks secure connections.</li>
<li>Clear the app&rsquo;s cache in the phone&rsquo;s app settings. This does not delete your account.</li>
</ol>
<h2>Check the service</h2>
<p>Use the <a href="/">checker</a> for the service&rsquo;s website, and the app servers card on each service page to see its login and API servers. If the website is up but the app servers fail, the problem is in the app&rsquo;s back end, which explains why the app fails while the website works.</p>
<h2>A worked example</h2>
<p>Your friend can post photos but you cannot, and the app shows an error after you tap Share. The checker shows the service up. You switch from Wi-Fi to mobile data and the post goes through. The Wi-Fi path to the upload servers was the issue, so a router restart is the next step. If both networks failed and many others reported the same, it would be a service outage and waiting would be the right answer.</p>
<h2>Why social outages feel so big</h2>
<p>These services run on huge networks that depend on shared systems, so one configuration mistake can take down several apps owned by the same company at once. That is why WhatsApp, Instagram and Facebook sometimes fail together. See <a href="/help/why-big-websites-go-down">why big websites go down</a>.</p>
<h2>What not to do</h2>
<ul>
<li>Do not delete the app unless it is clearly a local fault. You could lose unsent drafts and offline data.</li>
<li>Do not enter your password on a page you reached from a message claiming the service is &ldquo;down&rdquo;. Scammers use outages as bait.</li>
<li>Do not keep refreshing. That adds load and can trigger limits.</li>
</ul>
'''
},
{
'slug': 'streaming-keeps-buffering', 'cat': 'fix',
'title': 'Why Netflix, YouTube or other streaming keeps buffering',
'desc': 'How to tell whether buffering comes from the streaming service, your Wi-Fi, your internet plan or your device, with speeds needed for HD and 4K.',
'related': ['why-is-my-internet-slow', 'is-it-my-wifi-router-or-isp', 'latency-packet-loss-and-jitter-explained'],
'body': '''
<p class="lead">Buffering happens when video arrives more slowly than it plays. The cause can be the service, your home network, your internet connection or the device itself. Working out which saves a lot of time.</p>
<h2>How much speed streaming needs</h2>
<ul>
<li><b>Standard definition:</b> about 3 Mbps.</li>
<li><b>HD (1080p):</b> about 5 to 8 Mbps.</li>
<li><b>4K:</b> about 15 to 25 Mbps.</li>
</ul>
<p>These are per stream. A household watching on two TVs while someone downloads a game needs much more. Speed is only part of the story: a stable connection with low packet loss matters as much as a high number. See <a href="/help/latency-packet-loss-and-jitter-explained">latency, packet loss and jitter</a>.</p>
<h2>Work out where the problem is</h2>
<ol>
<li><b>Is it one service or all of them?</b> If only one app buffers while others stream fine, the problem is probably that service or its delivery network. Use the <a href="/">checker</a>.</li>
<li><b>Is it one device or all of them?</b> If a phone streams fine but the TV buffers, look at the TV: its Wi-Fi signal, its app version or its memory.</li>
<li><b>Is it a certain time of day?</b> Buffering every evening at peak hours points to congestion on your provider&rsquo;s network, which they can fix or explain.</li>
<li><b>Run a speed test</b> on the same Wi-Fi, ideally close to the router. Our <a href="/internet-speed-test">internet speed test</a> also shows latency. Compare the result with your plan.</li>
</ol>
<h2>Common causes and fixes</h2>
<ul>
<li><b>Weak Wi-Fi signal:</b> walls and distance cut speed sharply. Move the router, use a wired cable to the TV, or add a mesh unit.</li>
<li><b>Busy 2.4 GHz band:</b> the 5 GHz band is faster at close range. Use it for TVs near the router.</li>
<li><b>Too many devices:</b> pause big downloads and cloud backups while streaming.</li>
<li><b>An old router:</b> routers that are many years old can struggle with several HD streams.</li>
<li><b>VPN on:</b> a VPN adds distance and overhead. Turn it off to test.</li>
<li><b>Service-side problems:</b> a delivery network issue can hit one service in one region while the rest of the internet is fine.</li>
</ul>
<h2>A worked example</h2>
<p>A family pays for a 100 Mbps plan but the living-room TV buffers at 8 pm. A speed test beside the router shows 95 Mbps, but the same test in the living room shows 9 Mbps. The plan is fine; the Wi-Fi signal does not reach the TV. Running a cable or adding a mesh unit fixes it, and no call to the provider is needed.</p>
<h2>If the service is the problem</h2>
<p>Most platforms let you lower the quality manually. Dropping from 4K to HD cuts the speed needed to a third and is a useful workaround during a partial outage. Remember that large outages show up at once for many people; check the <a href="/outage-map">outage map</a> to see whether others are affected.</p>
<h2>When to call your provider</h2>
<p>Call if speed is far below your plan when wired directly to the router, if it drops at the same time every day, or if the connection keeps disconnecting. Give them speed test results with times, which makes the conversation far shorter. See <a href="/help/is-it-my-wifi-router-or-isp">is it my Wi-Fi, router or ISP</a>.</p>
'''
},
{
'slug': 'what-is-an-ip-address', 'cat': 'checks',
'title': 'What is an IP address, and what does it tell people about you?',
'desc': 'A plain explanation of IP addresses: public and private, IPv4 and IPv6, how websites see yours, what it reveals, and what it does not.',
'related': ['what-is-dns-and-why-it-fails', 'vpns-and-websites-that-stop-working', 'website-and-network-terms-glossary'],
'body': '''
<p class="lead">An IP address is a number that identifies a device or network on the internet, the way a postal address identifies a building. Every request you make carries one, so that the reply knows where to go.</p>
<h2>Public and private addresses</h2>
<p>Your home has one <b>public</b> address, given by your internet provider. It is the one websites see. Inside your home, your router hands out <b>private</b> addresses, usually starting with 192.168 or 10, to your phone, laptop and TV. Those private numbers mean nothing outside your house, which is why many homes can use the same ones. When you ask <a href="/what-is-my-ip">what is my IP</a>, the answer is the public address.</p>
<h2>IPv4 and IPv6</h2>
<ul>
<li><b>IPv4</b> looks like 203.0.113.25. There are only about 4.3 billion of them, and they ran short years ago.</li>
<li><b>IPv6</b> looks like 2001:db8::1 and has an almost unlimited supply.</li>
</ul>
<p>Most networks now use both. Sometimes a site works on one but not the other, which is one reason a site can load on mobile data and not on Wi-Fi.</p>
<h2>Static and dynamic</h2>
<p>Most homes get a <b>dynamic</b> address that can change when the router restarts or after some time. Businesses and servers often pay for a <b>static</b> address that never changes, which matters when something must be reachable at a fixed place.</p>
<h2>What an IP address reveals</h2>
<ul>
<li>Your internet provider and roughly where it is based.</li>
<li>An approximate location, usually the city or region, and often inaccurate.</li>
<li>Whether you are on a VPN or a business network.</li>
</ul>
<h2>What it does not reveal</h2>
<ul>
<li>Your name, your home address or your phone number. Only your provider can link an address to an account, and they do so only under legal process.</li>
<li>What you do on a site, if the connection is encrypted with HTTPS.</li>
<li>Your exact position. Location from an IP is a rough guess, not GPS.</li>
</ul>
<h2>Why IP addresses cause problems for sites</h2>
<p>Sites use addresses to rate limit and block abuse, so sharing one with many people can cause trouble. Office networks, mobile networks and VPNs put thousands of people behind one address. If one of them misbehaves, everyone may see <a href="/help/error-429-too-many-requests">error 429</a> or <a href="/help/error-403-forbidden">error 403</a>. See also <a href="/help/vpns-and-websites-that-stop-working">VPNs and websites that stop working</a>.</p>
<h2>A worked example</h2>
<p>You check your address at home and see 86.x.x.x, then again on mobile data and see a different address from another provider. The website sees you as two different visitors in two different networks. If a site works on one and is blocked on the other, the block is tied to the address range, not to you.</p>
<h2>Staying private</h2>
<p>A VPN replaces the address websites see with the VPN&rsquo;s. It hides your address from sites, but your VPN provider can see your traffic, so choose one you trust. HTTPS protects content; an address cannot be hidden from the sites you contact without a VPN or similar tool.</p>
'''
},
{
'slug': 'how-to-test-your-internet-speed-properly', 'cat': 'checks',
'title': 'How to test your internet speed properly (and read the results)',
'desc': 'Why speed test results vary, how to get a fair reading, and what download, upload, latency and jitter mean for everyday use.',
'related': ['why-is-my-internet-slow', 'latency-packet-loss-and-jitter-explained', 'streaming-keeps-buffering'],
'body': '''
<p class="lead">A speed test gives you a number, but the number only means something if the test was fair. A few simple habits make the difference between a useful result and a misleading one.</p>
<h2>What the numbers mean</h2>
<ul>
<li><b>Download:</b> how fast data reaches you. Matters for streaming, browsing and downloads.</li>
<li><b>Upload:</b> how fast you send data. Matters for video calls, cloud backups and posting videos.</li>
<li><b>Latency (ping):</b> the delay for a message to travel and come back, in milliseconds. Matters for gaming and calls. Under 30 ms is excellent, and under 100 ms is fine for most things.</li>
<li><b>Jitter:</b> how much latency varies. High jitter makes calls choppy even when speed is high.</li>
</ul>
<h2>How to get a fair test</h2>
<ol>
<li>Use a cable if you can. Wi-Fi adds variation that hides what your line can really do.</li>
<li>If testing Wi-Fi, stand near the router first, then repeat in the room where you have problems.</li>
<li>Pause downloads, updates, backups and streaming on all devices.</li>
<li>Turn off any VPN for the test, then optionally test with it on.</li>
<li>Run it three times and note the range, not just one result.</li>
<li>Test at different times, including your busy evening hours.</li>
</ol>
<h2>Why results differ between test sites</h2>
<p>Each test measures against a particular server. A nearby server gives higher numbers than a far one. Browsers and older devices can also limit the speed they can measure. Use one tool consistently and compare like with like. Our <a href="/internet-speed-test">internet speed test</a> measures from your own browser, so it shows what you can really get.</p>
<h2>What speed do you actually need?</h2>
<ul>
<li>Browsing and email: 5 to 10 Mbps.</li>
<li>HD streaming per screen: 5 to 8 Mbps.</li>
<li>Video calls: 3 to 8 Mbps both ways.</li>
<li>Online gaming: speed matters less than low latency, under 50 ms is ideal.</li>
<li>A busy household: add the needs of everyone using the network at once.</li>
</ul>
<h2>A worked example</h2>
<p>A plan promises 300 Mbps. A Wi-Fi test in the bedroom shows 40 Mbps, but a wired test next to the router shows 285 Mbps. The line delivers; the Wi-Fi does not. Moving the router, switching to the 5 GHz band, or adding a mesh unit will help more than a faster plan.</p>
<h2>When the result is poor</h2>
<p>If a wired test is well below the plan at several times of day, note the results and contact your provider. If speed is fine but things still feel slow, the problem may be the site you are using, not your line. Check it with the <a href="/">checker</a>, and see <a href="/help/why-is-my-internet-slow">why is my internet slow</a>.</p>
'''
},
{
'slug': 'online-banking-or-payment-site-not-working', 'cat': 'fix',
'title': 'Online banking or a payment site not working? What to do safely',
'desc': 'How to handle a bank, card or checkout page that will not load or errors mid-payment, without double paying or falling for scams.',
'related': ['what-to-do-when-an-app-or-service-is-down', 'ssl-certificate-errors', 'is-it-down-or-just-me'],
'body': '''
<p class="lead">Money makes outages stressful. The risks are paying twice and falling for scams that appear during problems. The safe approach is to slow down, confirm the problem, and check before trying again.</p>
<h2>If a payment fails or freezes halfway</h2>
<ol>
<li><b>Do not press pay again straight away.</b> The first attempt may have succeeded and only the confirmation failed.</li>
<li>Check your bank app or statement for a pending charge, and your email for an order confirmation.</li>
<li>Wait 10 to 15 minutes before trying again. Pending charges that never turn into an order are usually released automatically within a few days.</li>
<li>If you were charged but have no order, contact the shop with the time, amount and any reference number.</li>
</ol>
<h2>If the bank site or app will not load</h2>
<ul>
<li>Use the <a href="/">checker</a> to see whether the bank&rsquo;s site is up for everyone. Banks also have separate systems for the app, card payments and cash machines, which can fail independently.</li>
<li>Try the other route: if the website fails, try the app, and the reverse.</li>
<li>Check the bank&rsquo;s official status page or its verified social accounts.</li>
<li>Do not use a link from a text or email to get there. Type the address or use the official app.</li>
</ul>
<h2>Common causes on your side</h2>
<ul>
<li>An out-of-date app or browser.</li>
<li>A VPN, which many banks block for security (see <a href="/help/vpns-and-websites-that-stop-working">VPNs and websites that stop working</a>).</li>
<li>A wrong date or time on your device, which breaks the secure connection.</li>
<li>A security warning on the page. Treat it seriously and read <a href="/help/ssl-certificate-errors">SSL certificate errors</a>. Never enter card details on a page showing one.</li>
</ul>
<h2>Staying safe during an outage</h2>
<p>Outages attract scammers. Be wary of any message saying a service is down and asking you to &ldquo;verify your account&rdquo;, call a number, or move money to a &ldquo;safe account&rdquo;. A real bank will not ask for your full PIN or password, and will not ask you to transfer money to protect it. If in doubt, end the contact and call the number on the back of your card.</p>
<h2>A worked example</h2>
<p>You pay for tickets and the page shows an error after you click Pay. The checker shows the ticket site is up, and your banking app shows a pending charge. You wait 15 minutes and your email brings the confirmation. If you had paid again, you would have been charged twice. If no confirmation arrived, you would contact the seller with the reference from the pending charge.</p>
<h2>Prevention</h2>
<ul>
<li>Keep a second payment method available for important purchases.</li>
<li>For urgent payments, avoid the last minute, so an outage does not matter.</li>
<li>Keep your banking apps updated and enable alerts for transactions.</li>
</ul>
<p>This guide is general information, not financial advice. For problems with money already taken, your bank or card provider is the right place to start.</p>
'''
},
]
