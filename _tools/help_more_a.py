# More help-centre guides (batch A). Merged into ARTICLES by help_content.py.
ARTICLES_A = [
{
'slug': 'what-happens-when-you-open-a-website', 'cat': 'checks',
'title': 'What happens when you open a website, step by step',
'desc': 'From typing an address to seeing a page: how DNS, connections, encryption and servers fit together, and where each step can fail.',
'related': ['what-is-dns-and-why-it-fails', 'website-not-loading-checklist', 'how-our-checks-work'],
'body': '''
<p class="lead">You type an address, press enter, and a page appears a moment later. In that moment your device and several other computers have a short, very fast conversation. Knowing the steps makes error messages much easier to understand, because each one points at a different step.</p>
<h2>Step 1: finding the address (DNS)</h2>
<p>Computers do not use names like <code>example.com</code>. They use numeric addresses, such as <code>203.0.113.10</code>. The first job is to translate the name into a number, and that is what the Domain Name System, or DNS, does. Your device asks a DNS resolver, usually run by your internet provider or a public service, and the resolver either answers from memory or asks other servers until it finds the answer.</p>
<p>If this step fails you see messages such as <code>DNS_PROBE_FINISHED_NXDOMAIN</code> or &ldquo;server not found&rdquo;. The website itself may be perfectly healthy. Our guide to <a href="/help/what-is-dns-and-why-it-fails">DNS and why it fails</a> covers this step in detail.</p>
<h2>Step 2: opening a connection</h2>
<p>With the address in hand, your device contacts the server and they agree how to talk. This is called a TCP connection. It needs a small exchange of messages in both directions, so the time it takes depends on distance. A server on the other side of the world will take longer to answer than one in the same city, simply because signals take time to travel.</p>
<p>If this step fails you usually see &ldquo;connection timed out&rdquo; or &ldquo;connection refused&rdquo;. A timeout means nothing answered. Refused means a machine answered and said no, which usually means the software that should be listening is not running. See <a href="/help/err-connection-timed-out">what a connection timeout means</a>.</p>
<h2>Step 3: making it private (TLS)</h2>
<p>Almost every site now uses HTTPS. Before any page content is sent, your browser and the server agree on encryption keys, and the server shows a certificate that proves it really is the site you asked for. The browser checks that the certificate matches the name, has not expired and was issued by an authority it trusts.</p>
<p>When this fails you get a full-page warning about your connection not being private. The cause is nearly always the certificate: it has expired, it is for a different name, or your device clock is wrong. Read more in <a href="/help/ssl-certificate-errors">SSL certificate errors explained</a>, or test any site with our <a href="/tools/ssl-certificate-checker">SSL certificate checker</a>.</p>
<h2>Step 4: asking for the page (HTTP)</h2>
<p>Now your browser sends the actual request: &ldquo;please give me this page&rdquo;. The server answers with a status code and, usually, the page. The status code is the three-digit number that tells you how it went. <code>200</code> means success. <code>404</code> means nothing lives at that address. The <code>5xx</code> family means the server had a problem. Our <a href="/help/http-status-codes-explained">status code guide</a> explains each family.</p>
<p>For a large site this step is rarely handled by one machine. The request may go through a content delivery network, a load balancer, a web server and a database before an answer comes back. A fault in any layer can produce a 5xx error even though the front door is open.</p>
<h2>Step 5: building the page</h2>
<p>The first response is usually just the outline of a page. Your browser reads it and discovers it also needs style sheets, scripts, fonts and images, often from several different servers. It requests those too, in parallel, and then draws the page. A page can therefore &ldquo;load&rdquo; but look broken if one of those extra resources fails, for example when a font or script host is having its own outage.</p>
<h2>Where each step can go wrong</h2>
<ul>
<li><b>Name not found.</b> DNS problem. Often fixed by <a href="/help/flush-dns-cache">flushing your DNS cache</a> or trying another resolver.</li>
<li><b>Timed out.</b> The server is unreachable, overloaded, or something between you and it is dropping traffic.</li>
<li><b>Certificate warning.</b> The encryption step failed. Do not click through on a site that handles passwords or payments.</li>
<li><b>5xx error.</b> The server was reached but could not do its job.</li>
<li><b>Blank or half-drawn page.</b> A supporting file failed, or something in your browser blocked it.</li>
</ul>
<h2>Why this matters when checking a site</h2>
<p>When you use siteupdown.com we repeat these steps ourselves, from our server and from probes in other countries. Each run reports which step failed, not just whether the page opened, so you can tell &ldquo;the site is down&rdquo; from &ldquo;the name does not resolve&rdquo; from &ldquo;the certificate has expired&rdquo;. If every location can complete every step and you still cannot, the problem is almost certainly on your side. Our <a href="/help/website-not-loading-checklist">website not loading checklist</a> walks through it.</p>
<h2>A note on speed</h2>
<p>Every step adds a little time, and a few of them depend on distance. This is why a site feels instant on a second visit: your browser and your DNS resolver remember answers, so steps 1 to 3 can be skipped or shortened. It is also why large sites place copies of their content in many cities, which is the idea behind a <a href="/help/what-is-a-cdn-and-why-outages-spread">content delivery network</a>.</p>
'''
},
{
'slug': 'what-is-dns-and-why-it-fails', 'cat': 'owners',
'title': 'What is DNS, and why does it fail?',
'desc': 'A plain-English explanation of the Domain Name System, how lookups are cached, the common ways DNS breaks, and how to tell a DNS fault from a down website.',
'related': ['dns-probe-finished-nxdomain', 'flush-dns-cache', 'dns-propagation'],
'body': '''
<p class="lead">DNS is the internet&rsquo;s phone book. It turns the names people type into the numeric addresses that computers use. It is invisible when it works and baffling when it does not, and a surprising share of &ldquo;the internet is down&rdquo; moments are really DNS problems.</p>
<h2>How a lookup works</h2>
<p>When you visit a site, your device asks a <b>recursive resolver</b>, normally run by your internet provider or a public service, for the address. If the resolver does not already know, it works down a chain. It asks one of the root servers who handles the last part of the name, such as <code>.com</code>. It then asks that registry who is responsible for the domain, and finally asks the domain&rsquo;s own <b>authoritative name servers</b> for the answer. The resolver passes the answer back to you and remembers it for a while.</p>
<h2>Caching and TTL</h2>
<p>Every DNS answer carries a time to live, or TTL, measured in seconds. It tells resolvers how long they may reuse the answer before asking again. A short TTL means changes spread quickly and a long TTL means fewer lookups but slower changes. Caching exists at several levels: your browser, your operating system, your router and your provider&rsquo;s resolver. That is why two people can see different results for the same name at the same moment, and why a fix sometimes seems to work for some people before others. See <a href="/help/dns-propagation">what DNS propagation really means</a>.</p>
<h2>The common record types</h2>
<ul>
<li><b>A and AAAA</b> point a name at an IPv4 or IPv6 address.</li>
<li><b>CNAME</b> says one name is an alias for another. Many services you use are reached this way.</li>
<li><b>MX</b> says which servers handle email for the domain. Our <a href="/tools/mx-record-lookup">MX record lookup</a> shows them.</li>
<li><b>TXT</b> holds free text, used for things like email authentication and ownership checks.</li>
<li><b>NS</b> says which name servers are responsible for the domain.</li>
</ul>
<p>You can inspect any of these with our <a href="/tools/dns-lookup">DNS lookup tool</a>.</p>
<h2>Ways DNS fails</h2>
<ul>
<li><b>The domain does not exist, or has expired.</b> The resolver answers &ldquo;no such name&rdquo;, which browsers show as NXDOMAIN. Expired domains are more common than people expect. See <a href="/help/domain-name-expiry">what happens when a domain expires</a>.</li>
<li><b>The name servers are unreachable.</b> The records may be perfect, but if every authoritative server is down or unreachable, nobody can look them up. This is the classic cause of big, sudden outages that affect everything a company runs at once.</li>
<li><b>A bad change.</b> A wrong or missing record is published, such as a typo in an address or a deleted record. Everything looks healthy on the servers, but the name now leads to the wrong place or nowhere.</li>
<li><b>Your resolver is the problem.</b> Your provider&rsquo;s resolver may be slow, overloaded or misbehaving, so some names fail while others work.</li>
<li><b>Stale cache.</b> Your device or router remembers an old answer after a site has moved. A <a href="/help/flush-dns-cache">DNS flush</a> clears it.</li>
<li><b>Blocking and filtering.</b> Some networks, parental controls and security tools refuse to resolve certain names on purpose.</li>
</ul>
<h2>Telling DNS from a down site</h2>
<p>The quickest test is to try the site&rsquo;s numeric address, if you know it, or to check the same name from somewhere else. If a site is reachable from other places but not for you, switch your device to a public resolver and try again. If the name now loads, your original resolver or a stale cache was the problem. If it still fails everywhere, the site&rsquo;s own DNS is broken, and only its owner can fix that.</p>
<p>Our checker does this automatically. Each run reports whether the name resolved, how long the lookup took, and what answer came back. A name that resolves but then times out is a different story from a name that does not resolve at all.</p>
<h2>For site owners</h2>
<ul>
<li>Use at least two name servers, ideally with different providers or networks.</li>
<li>Lower the TTL a day or two before a planned change, then raise it afterwards.</li>
<li>Turn on auto-renew for the domain, and keep contact details current so renewal warnings reach you.</li>
<li>Keep a copy of your records somewhere outside your DNS provider so you can rebuild quickly.</li>
<li>After a change, check it from several places with our <a href="/tools/dns-propagation-checker">DNS propagation checker</a> rather than only from your own computer.</li>
</ul>
<h2>The short version</h2>
<p>DNS is a chain of helpers, each remembering answers for a limited time. Most problems are one of three things: a name that has genuinely stopped existing, name servers that cannot be reached, or an old answer stuck in a cache. Working out which one it is takes a couple of minutes and saves a lot of guessing.</p>
'''
},
{
'slug': 'what-is-a-cdn-and-why-outages-spread', 'cat': 'owners',
'title': 'What is a CDN, and why do outages spread so widely?',
'desc': 'How content delivery networks work, why so many sites depend on a few providers, and what that means when one of them has a bad day.',
'related': ['why-big-websites-go-down', 'major-internet-outages-explained', 'how-websites-stay-up'],
'body': '''
<p class="lead">A content delivery network, or CDN, is a group of servers spread around the world that sit between visitors and a website. CDNs make sites faster and tougher against attacks. They also explain why one company&rsquo;s fault can suddenly take down thousands of unrelated sites.</p>
<h2>The problem a CDN solves</h2>
<p>Distance matters on the internet. If a site&rsquo;s only server is in one country, a visitor on the other side of the world waits for every message to cross that distance. A CDN keeps copies of the site&rsquo;s files in many cities. A visitor is sent to a nearby copy, so images, scripts and often whole pages arrive far sooner.</p>
<h2>What a CDN does besides speed</h2>
<ul>
<li><b>Absorbs traffic spikes.</b> Millions of requests are spread across many servers instead of landing on one.</li>
<li><b>Filters attacks.</b> Flood attacks are soaked up at the edge, and many CDNs also block known bad traffic and automated abuse.</li>
<li><b>Handles encryption.</b> The CDN can hold the site&rsquo;s certificate and manage HTTPS on its behalf.</li>
<li><b>Keeps a site up when the origin struggles.</b> If the real server is slow or briefly unavailable, the CDN can sometimes keep serving saved copies.</li>
</ul>
<h2>The cost: concentration</h2>
<p>A handful of providers carry a very large share of the web&rsquo;s traffic. That is efficient, but it means many unrelated sites share the same front door. When that front door has a problem, they all show errors at once, even though their own servers are fine. From a visitor&rsquo;s point of view it looks as though half the internet has broken.</p>
<p>This is a recurring pattern in major outages. The fault is often in a shared service, such as a content delivery network, a cloud region, a DNS provider or an identity service, rather than in any one website. Our guide to <a href="/help/major-internet-outages-explained">major internet outages</a> gives real examples.</p>
<h2>What a CDN error looks like</h2>
<p>When a CDN cannot reach a site&rsquo;s own server, or has an internal fault, visitors see an error page that often carries the provider&rsquo;s name. Typical signs:</p>
<ul>
<li>A <code>5xx</code> error such as <code>502</code>, <code>503</code> or <code>504</code>, sometimes with a branded message. See <a href="/help/server-errors-500-502-503-504">what the 5xx errors mean</a>.</li>
<li>A page saying the site cannot be reached because of an error with the network in front of it.</li>
<li>A &ldquo;checking your browser&rdquo; or challenge page that never finishes, which is a security filter not a server failure.</li>
</ul>
<h2>Why we sometimes say &ldquo;blocked&rdquo;</h2>
<p>CDN security filters can also refuse automated checks. When a site answers our probes with a challenge instead of the page, we cannot see what a real visitor sees. We show that as <b>Blocked</b> and explain that it does not mean the site is down. <a href="/help/sites-that-block-automated-checks">Why some sites block automated checks</a> explains this in more detail.</p>
<h2>Working out what is affected</h2>
<ol>
<li><b>Check more than one site.</b> If several unrelated sites fail in the same way at the same time, suspect a shared provider.</li>
<li><b>Look at the provider&rsquo;s status page.</b> Large providers publish incident updates, and these are usually the fastest reliable source.</li>
<li><b>Check our <a href="/outage-map">outage map</a>.</b> Clusters of reports across different services are a strong sign of a shared cause.</li>
<li><b>Wait, then retry.</b> Most large provider incidents are fixed within hours, and recovery can be uneven while caches and connections settle.</li>
</ol>
<h2>For site owners: reducing the risk</h2>
<ul>
<li>Know exactly which providers your site depends on: DNS, CDN, hosting, certificates, email, payments and login.</li>
<li>Make sure your status page and alerts do not depend on the same provider as your main site, or they will fail together.</li>
<li>Consider whether a second provider for DNS is worth the extra complexity for your site. It protects against one specific kind of failure.</li>
<li>Prepare a simple message you can post in minutes saying you are aware and working on it.</li>
<li>Monitor from outside your own network. Our <a href="/help/how-to-monitor-your-own-website">monitoring guide</a> shows how.</li>
</ul>
<h2>The takeaway</h2>
<p>CDNs are a big reason the web feels fast and survives attacks. The trade-off is that a few shared services sit under a huge number of sites. When many unrelated sites fail together, the cause is usually one of those shared layers, and the practical advice is to confirm it, check the provider&rsquo;s status page and wait for them to fix it.</p>
'''
},
{
'slug': 'major-internet-outages-explained', 'cat': 'checks',
'title': 'Major internet outages and what caused them',
'desc': 'Real examples of large outages, including Facebook in 2021, AWS in 2025 and Cloudflare in 2025, and the lessons that repeat from one to the next.',
'related': ['why-big-websites-go-down', 'what-is-a-cdn-and-why-outages-spread', 'how-websites-stay-up'],
'body': '''
<p class="lead">Big outages make headlines because so many people notice at once, but the causes are usually ordinary: a configuration change, a software bug, a certificate or a dependency nobody realised was shared. This guide summarises a few well-documented incidents and the lessons they share. The details come from the companies&rsquo; own published explanations and news reports, and exact times differ between sources, so treat durations as approximate.</p>
<h2>Facebook, Instagram and WhatsApp, October 2021</h2>
<p>On 4 October 2021 Facebook and its other services became unreachable for roughly six hours. The company explained that a routine maintenance command accidentally disconnected its data centres from each other and from the internet. Its DNS servers, which are designed to withdraw themselves when they cannot reach the data centres, then also stopped announcing themselves. The names of its sites effectively disappeared from the internet.</p>
<p>The recovery was slow because the same outage cut off many of the internal tools staff used to fix problems. <b>Lesson:</b> keep a way in to your systems that does not depend on the systems being repaired.</p>
<h2>Fastly, June 2021</h2>
<p>In June 2021 a large number of well-known websites returned errors for under an hour. A content delivery network called Fastly later said a valid customer configuration change triggered a bug in software that had been deployed earlier, causing a large part of its network to return errors. Fastly identified the cause quickly and most of the network recovered within the hour. <b>Lesson:</b> a latent bug can sit unnoticed until a particular input finds it, and when the provider is shared, the impact is wide. See <a href="/help/what-is-a-cdn-and-why-outages-spread">what a CDN is and why outages spread</a>.</p>
<h2>The CrowdStrike update, July 2024</h2>
<p>On 19 July 2024 a faulty content update for a widely used security product caused Windows computers running it to crash and fail to restart. Airlines, hospitals, banks and shops were affected. This was not a website outage at all, but it is worth including because it shows how one update delivered to millions of machines at the same time can cause a global problem. <b>Lesson:</b> staged roll-outs, where an update reaches a small share of machines first, limit the damage from a mistake.</p>
<h2>Amazon Web Services, October 2025</h2>
<p>On 20 October 2025 a problem in AWS&rsquo;s US-EAST-1 region disrupted a very large number of services, including apps and websites that had nothing obviously to do with Amazon. Amazon&rsquo;s explanation pointed to a fault involving DNS resolution of the endpoints for one of its database services, which then spread to other internal services that depended on it. Recovery took many hours, and the surge of retries from systems trying to reconnect made it harder. <b>Lesson:</b> a fault in one internal service can cascade, and a rush of automatic retries can prolong an outage.</p>
<h2>Cloudflare, November 2025</h2>
<p>On 18 November 2025 Cloudflare had a global outage that returned errors for many of the sites it protects. The company&rsquo;s published account said a change to database permissions caused a configuration file used by its bot-management system to roughly double in size. The software that read the file had a size limit, and it failed when the file grew past it. The incident was caused by an internal change, not by an attack. <b>Lesson:</b> a harmless-looking internal change can break software that makes assumptions about its inputs, and shared infrastructure turns that into a worldwide event.</p>
<h2>The patterns that repeat</h2>
<ul>
<li><b>It is rarely a hack.</b> Most large outages come from a configuration change, a software bug or an expired certificate rather than an attack.</li>
<li><b>Shared layers amplify it.</b> DNS, CDNs, cloud regions and identity services sit under many sites, so one fault looks like many.</li>
<li><b>Fixing it can be harder than breaking it.</b> If the tools used to repair a system depend on that system, recovery slows down.</li>
<li><b>Retries make things worse.</b> When a service comes back, a flood of automatic reconnection attempts can knock it over again.</li>
<li><b>Recovery is uneven.</b> Caches, connections and queues clear at different speeds, so some people see the site return before others.</li>
</ul>
<h2>What this means for you</h2>
<p>If many unrelated sites and apps are failing together, it is almost certainly a shared provider and nothing is wrong with your device. Check the provider&rsquo;s status page, look at our <a href="/outage-map">outage map</a> for clusters of reports, and wait. If it is only one site, work through our <a href="/help/website-not-loading-checklist">checklist</a>.</p>
<p>You can also browse the <a href="/outage-history">outage history</a> on this site to see which services have had problems on which days, based on our own checks and visitor reports.</p>
<h2>What owners can learn</h2>
<ul>
<li>Roll changes out gradually and have a fast way to undo them.</li>
<li>Test what happens when a dependency fails, not only when everything works.</li>
<li>Back off and add randomness to automatic retries so recovery does not become a second outage.</li>
<li>Keep emergency access and communication tools independent of the systems they are meant to repair.</li>
<li>Tell customers early, plainly and often. Silence feels worse than bad news.</li>
</ul>
<p class="note">These summaries are simplified. For full technical detail, read each company&rsquo;s own post-incident write-up.</p>
'''
},
]
