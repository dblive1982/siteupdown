# More help-centre guides (batch D). Merged into ARTICLES by help_content.py.
ARTICLES_D = [
{
'slug': 'what-is-a-ddos-attack', 'cat': 'checks',
'title': 'What is a DDoS attack, and how does it take a website down?',
'desc': 'A plain-English explanation of distributed denial-of-service attacks: how they work, why they cause outages, how sites defend themselves and what you can do as a visitor.',
'related': ['why-big-websites-go-down', 'what-is-a-cdn-and-why-outages-spread', 'how-websites-stay-up'],
'body': '''
<p class="lead">Most outages are accidents: a bad update, a failed server, an expired certificate. A smaller number are deliberate. A distributed denial-of-service attack, usually shortened to DDoS, tries to make a website or service unusable by flooding it with more traffic than it can handle. This guide explains what that means and what it looks like from the outside.</p>
<h2>The idea in one picture</h2>
<p>Imagine a shop with one door. On a normal day customers come in a few at a time. Now imagine thousands of people crowd the doorway at once, none of whom want to buy anything. Real customers cannot get in, and the staff cannot serve anyone. The shop has not been broken into and nothing has been stolen, but it is effectively closed. A denial-of-service attack does the same to a server.</p>
<p>The &ldquo;distributed&rdquo; part means the traffic comes from a very large number of machines at once, often hundreds of thousands, which makes it hard to block by simply banning one address. The machines are usually ordinary devices such as poorly secured home routers, cameras or computers that have been taken over without their owners knowing.</p>
<h2>The main kinds of attack</h2>
<ul>
<li><b>Volume attacks.</b> These try to fill the network link in front of a site with junk, so real requests cannot get through. Think of a motorway blocked by sheer numbers of cars.</li>
<li><b>Protocol attacks.</b> These abuse the way connections are set up, for example by starting huge numbers of connections and never finishing them, so a server or firewall runs out of room to track them.</li>
<li><b>Application attacks.</b> These look like normal visitors but ask for the most expensive things a site can do, such as a search or a login, again and again. They need much less traffic to cause trouble because each request costs the server real work.</li>
</ul>
<h2>Why it causes an outage</h2>
<p>Every server, network link and database has a limit. A DDoS tries to push one of those limits past breaking point. When it works, the symptoms people see are the same as any overload: pages that load very slowly, time out, or return errors such as <a href="/help/server-errors-500-502-503-504">503 Service Unavailable</a>. The site&rsquo;s own data is normally untouched. A denial of service is about availability, not theft, although attackers sometimes use one as a distraction while they try something else.</p>
<h2>How websites defend themselves</h2>
<ul>
<li><b>Absorbing the traffic.</b> Large providers run networks with far more capacity than any single attack. A <a href="/help/what-is-a-cdn-and-why-outages-spread">content delivery network</a> spreads requests across many locations, so the flood is diluted rather than aimed at one machine.</li>
<li><b>Filtering.</b> Systems look at traffic patterns and drop requests that look like part of an attack, while letting real visitors through. This is why you may occasionally be asked to prove you are human.</li>
<li><b>Rate limiting.</b> Capping how many requests one address or one account can make in a short time stops a single source from using up the whole site.</li>
<li><b>Scaling and redundancy.</b> Running several servers behind a <a href="/help/what-is-a-load-balancer">load balancer</a> means one overloaded machine does not take everything with it. See also <a href="/help/how-websites-stay-up">how websites stay up</a>.</li>
</ul>
<h2>How to tell whether an outage might be an attack</h2>
<p>From outside, you usually cannot. A flood and a failed server look alike: slow pages, timeouts, error messages. A few clues help. An attack tends to start abruptly, may hit one site rather than a whole provider, and is often described by the company as &ldquo;unusually high traffic&rdquo; or &ldquo;a denial of service incident&rdquo;. Companies sometimes avoid saying so at first, because the cause takes time to confirm. Treat a cause as unknown until the site itself reports it. Our <a href="/state-of-the-internet">State of the internet</a> page shows whether many sites are affected at once, which points to a shared provider rather than a targeted attack.</p>
<h2>What you can do as a visitor</h2>
<p>There is little you can do to help a site under attack, and nothing you need to fix on your side. Check that it is down for others with the <a href="/">website checker</a>, wait, and follow the company&rsquo;s status page or social account for updates (see <a href="/help/what-to-do-when-an-app-or-service-is-down">what to do when a service is down</a>). Do not repeatedly refresh, since that adds a little to the load, and be wary of messages claiming to be from the company that ask you to log in or pay to &ldquo;restore access&rdquo;. Those are scams that tend to appear during any well-publicised outage.</p>
<h2>What it means for site owners</h2>
<p>If you run a site, the best protection is boring and done in advance: put it behind a content delivery network or protection service, keep your own server address private, make expensive pages cheap with caching, and set up <a href="/help/how-to-monitor-your-own-website">monitoring</a> so you know the moment it slows. Decide beforehand who to contact at your host, and how you will tell your users, using a plain update such as the ones described in <a href="/help/how-to-write-an-outage-update">how to write an outage update</a>.</p>
<p class="note">We describe general concepts here. We cannot tell from our own checks whether any particular outage was an attack, and we never claim to.</p>
'''
},
{
'slug': 'err-too-many-redirects', 'cat': 'fix',
'title': 'ERR_TOO_MANY_REDIRECTS: how to fix a redirect loop',
'desc': 'What a redirect loop is, why browsers show "too many redirects" or "redirected you too many times", and how visitors and site owners can fix it.',
'related': ['clear-browser-cache-and-cookies', 'website-works-in-one-browser-not-another', 'http-status-codes-explained'],
'body': '''
<p class="lead">You open a page and the browser says &ldquo;This page isn&rsquo;t working: example.com redirected you too many times&rdquo;, or shows the code ERR_TOO_MANY_REDIRECTS. The site is sending your browser in circles, and the browser gives up after about twenty hops. This guide explains why and how to fix it, whether you are the visitor or the owner.</p>
<h2>What a redirect is</h2>
<p>A redirect is an instruction from a server saying &ldquo;the page you want is somewhere else, go there&rdquo;. They are everywhere and usually invisible: from <code>http</code> to <code>https</code>, from <code>example.com</code> to <code>www.example.com</code>, from an old page to a new one. They use status codes in the 300 range, mainly 301 (moved permanently) and 302 (moved temporarily). See <a href="/help/http-status-codes-explained">HTTP status codes explained</a>.</p>
<p>A loop happens when the destination sends you back to where you started. Page A says go to B, and B says go to A. Browsers stop after a limit and show the error rather than spinning forever.</p>
<h2>If you are a visitor</h2>
<p>Most cases that affect only you come from a stale or conflicting cookie, because many sites use a cookie to decide where to send you after sign-in.</p>
<ol>
<li><b>Check it is not everyone.</b> Paste the address into the <a href="/">website checker</a>. If it also fails for us, the problem is on the site and only the owner can fix it. Wait and try later.</li>
<li><b>Clear cookies for that site only.</b> You do not need to wipe everything. In the address bar, open the site information, choose cookies or site settings, and delete the data for that one site. Our guide to <a href="/help/clear-browser-cache-and-cookies">clearing cache and cookies</a> shows each browser.</li>
<li><b>Try a private window.</b> It starts with no cookies and no extensions. If the page loads there, the cause is a cookie or an extension in your normal window.</li>
<li><b>Turn off extensions.</b> Privacy and security extensions can interfere with redirects. Disable them one at a time to find the culprit.</li>
<li><b>Check your device clock.</b> A badly wrong date can break sign-in and security flows that rely on timing.</li>
</ol>
<h2>If you own the site</h2>
<p>When everyone sees the loop, it is nearly always a configuration problem. The common causes are:</p>
<ul>
<li><b>HTTPS rules fighting each other.</b> Your server forces HTTPS, while a proxy or CDN in front of it connects to the server over plain HTTP. The server redirects to HTTPS, the proxy fetches it again over HTTP, and the loop never ends. The fix is to set the proxy&rsquo;s encryption mode to connect securely to the origin, not to remove the redirect.</li>
<li><b>www and non-www rules in conflict.</b> One rule sends <code>www</code> to the bare domain while another sends the bare domain to <code>www</code>. Pick one canonical form and make sure only one rule exists.</li>
<li><b>A CMS address mismatch.</b> In WordPress and similar systems the &ldquo;site address&rdquo; and &ldquo;home address&rdquo; settings must match what is actually served. A wrong value can redirect forever.</li>
<li><b>Plugins or caching.</b> Two plugins that both enforce a redirect, or a cached redirect that no longer matches your rules, can cause a loop. Disable redirect and security plugins one at a time and purge the cache.</li>
<li><b>Redirects on the login page.</b> A rule that sends visitors who are not signed in to the login page, combined with a login page that is also protected, creates a circle.</li>
</ul>
<h2>How to see the loop</h2>
<p>The clearest way is to follow the chain. Our <a href="/tools/redirect-checker">redirect checker</a> shows each hop with its status code and destination, so you can spot the address that repeats. The same can be done with a command line tool by asking it to show headers and not follow redirects. Once you see the repeating pair of addresses, the rule responsible is usually obvious.</p>
<h2>Prevent it coming back</h2>
<p>Keep a single place where redirects are defined, rather than rules in the server, the CMS and the CDN all at once. After any change to HTTPS, domains or a proxy, test the home page, a deep page and the login page in a fresh private window. A <a href="/help/how-to-monitor-your-own-website">monitor</a> that follows redirects will alert you if a loop appears after a deploy.</p>
'''
},
{
'slug': 'what-is-bgp-and-why-it-matters', 'cat': 'checks',
'title': 'What is BGP, and why can one mistake take a whole company offline?',
'desc': 'How the internet decides where to send traffic, what the Border Gateway Protocol does, and why a routing error can make big services unreachable for hours.',
'related': ['major-internet-outages-explained', 'what-is-dns-and-why-it-fails', 'how-to-read-a-traceroute'],
'body': '''
<p class="lead">The internet is not one network. It is tens of thousands of separate networks, run by internet providers, companies, universities and cloud platforms, all agreeing to pass traffic for one another. The way they tell each other where things are is called the Border Gateway Protocol, or BGP. It mostly works silently, which is why the rare times it fails make headlines.</p>
<h2>A map made of announcements</h2>
<p>Each network has a number, called an autonomous system number, and owns blocks of addresses. A network announces to its neighbours, &ldquo;you can reach these addresses through me&rdquo;. Neighbours pass those announcements on, adding their own details, and over time every large network builds a picture of the best path to every address.</p>
<p>It is a little like roads with no central map. Each town only knows which neighbouring towns lead toward a destination and relies on them to know the next step. That design is why the internet has no single point of control and can grow so large. It is also why it relies on a lot of trust.</p>
<h2>How a routing error causes an outage</h2>
<p>If a network stops announcing its addresses, or announces them wrongly, the rest of the internet no longer knows how to reach them. Two broad things can go wrong:</p>
<ul>
<li><b>Withdrawal.</b> Routes to a company&rsquo;s addresses are withdrawn, often by an internal change that went wrong. The servers are running perfectly, but nobody can find the way to them. Because DNS servers also live on those addresses, names stop resolving too, which makes the problem look like the whole company has vanished.</li>
<li><b>Leaks and hijacks.</b> A network announces addresses it does not own, or passes on routes it should not. Traffic then flows through the wrong place, where it may be slowed, dropped or, in the worst cases, intercepted. Most are honest configuration mistakes rather than attacks.</li>
</ul>
<h2>Why recovery can be slow</h2>
<p>Fixing the mistake is usually quick once found. What takes time is everything around it. Engineers may be unable to reach the systems they need because those depend on the same network. Announcements take minutes to spread, and cached information in other networks lingers. When a company&rsquo;s own tools, door badges and internal chat run on the failed network, even getting into the building to fix it can become a problem. This is why a routing outage can last hours even when the cause is a single wrong line.</p>
<h2>What it looks like from the outside</h2>
<ul>
<li>A large service is unreachable from everywhere at once, not just for some people.</li>
<li>Names fail to resolve, and addresses time out instead of returning an error page.</li>
<li>Connected services fail too: apps, sign-in buttons and embedded content that depend on the company&rsquo;s servers.</li>
<li>Our <a href="/outage-map">outage map</a> shows reachability problems in every region, not a local pattern.</li>
</ul>
<p>The tools in our <a href="/tools/">tools section</a>, such as the DNS lookup and ping test, show whether a name resolves and an address responds, which helps tell a routing problem from an application fault. A <a href="/help/how-to-read-a-traceroute">traceroute</a> can show where packets stop.</p>
<h2>How the industry is making it safer</h2>
<p>Several improvements are slowly being adopted. Route filtering lets providers refuse announcements that make no sense. A system called RPKI lets network owners publish signed statements about which networks may announce their addresses, so wrong announcements can be rejected automatically. Providers also monitor for unexpected changes to their routes. None of this is universal yet, which is why incidents continue to happen, though most are now caught and corrected within minutes.</p>
<h2>What you can do</h2>
<p>As a user, nothing needs fixing on your side, and restarting your router or changing DNS will not help. Check that the service is down for others, wait, and look for updates from the company on a channel that does not depend on its own network. For the bigger picture of outages that spread, read <a href="/help/major-internet-outages-explained">major internet outages explained</a> and <a href="/help/why-big-websites-go-down">why big websites go down</a>.</p>
<p class="note">This is a simplified explanation. Real routing involves policies, agreements between networks and many technical details we have left out on purpose.</p>
'''
},
{
'slug': 'what-is-a-load-balancer', 'cat': 'owners',
'title': 'What is a load balancer, and why does it matter for uptime?',
'desc': 'How load balancers share traffic between servers, how health checks keep broken servers out of rotation, and what to know when setting one up.',
'related': ['how-websites-stay-up', 'uptime-percentages-explained', 'what-is-a-cdn-and-why-outages-spread'],
'body': '''
<p class="lead">A busy website is rarely one computer. It is several servers working together, and something has to decide which server answers each visitor. That something is a load balancer. It is one of the main reasons large sites can stay up when individual machines fail, and understanding it helps you plan for your own site.</p>
<h2>What a load balancer does</h2>
<p>A load balancer sits in front of a group of servers and receives every incoming request. It then forwards each request to one of the servers behind it. To the visitor it looks like a single site with a single address. Behind the scenes the work is spread out, so no one server is overloaded.</p>
<p>It gives you two benefits at once. First, <b>capacity</b>: you can handle more visitors by adding servers rather than buying a bigger one. Second, <b>resilience</b>: if one server breaks, the others carry on.</p>
<h2>How it chooses a server</h2>
<ul>
<li><b>Round robin.</b> Requests go to each server in turn. Simple and fair when servers are similar.</li>
<li><b>Least connections.</b> The next request goes to whichever server is handling the fewest right now. Better when some requests take much longer than others.</li>
<li><b>Weighted.</b> Stronger servers get a larger share than weaker ones.</li>
<li><b>Sticky sessions.</b> A visitor keeps being sent to the same server, often needed when a server remembers state such as a shopping basket. It is simple but makes a server failure more disruptive for the people on it.</li>
</ul>
<h2>Health checks: the part that protects uptime</h2>
<p>A load balancer is only useful if it knows which servers are healthy. It regularly sends small test requests to each one, usually to a simple page or a dedicated health address. If a server stops answering correctly several times in a row, the balancer takes it out of rotation and sends traffic elsewhere. When the server recovers and passes checks again, it is added back.</p>
<p>The quality of the health check matters more than people expect. A check that only tests whether the server is switched on will keep sending traffic to a server whose application has crashed. A better check confirms the application can reach its database and return a real answer. Be careful not to make it too heavy or too strict, or a short database hiccup can mark every server unhealthy at once and turn a small problem into a full outage.</p>
<h2>Where load balancers sit</h2>
<p>You will meet them at several layers. A <b>network</b> balancer passes connections along quickly without looking at their content. An <b>application</b> balancer reads each web request and can route by address, for example sending <code>/api</code> to one group of servers and everything else to another. A <a href="/help/what-is-a-cdn-and-why-outages-spread">content delivery network</a> does a similar job across the world, sending visitors to the nearest location. Large sites often use all three.</p>
<h2>Common mistakes</h2>
<ul>
<li><b>A single balancer.</b> If the load balancer itself is one machine, it becomes the one thing that can take the whole site down. Managed services run balancers redundantly for this reason. If you run your own, run at least two.</li>
<li><b>No spare capacity.</b> If three servers share the load and one fails, the remaining two take on 50% more each. If they were already near their limit, the failure cascades. Plan so the site survives losing one server.</li>
<li><b>Everything in one place.</b> Spreading servers across several machines helps little if they all sit in the same data centre or on the same power feed. Many outages in <a href="/help/major-internet-outages-explained">well-known incidents</a> came from a shared dependency, not a lone server.</li>
<li><b>Forgetting the database.</b> Balancing web servers does nothing if every server depends on one database that fails.</li>
</ul>
<h2>Checking it is working</h2>
<p>Watch for uneven load, repeated server removals and slow responses from only some requests. External monitoring from outside your network, such as a <a href="/help/how-to-monitor-your-own-website">monitor on your site</a>, shows what visitors experience, which can differ from what the balancer reports. If you see errors only some of the time, a single bad server in the pool is a likely cause: see <a href="/help/server-errors-500-502-503-504">server errors 500, 502, 503 and 504</a> for what each response means. For how uptime figures translate into real downtime, read <a href="/help/uptime-percentages-explained">uptime percentages explained</a>.</p>
'''
},
{
'slug': 'how-to-use-a-status-page', 'cat': 'fix',
'title': 'How to use a status page during an outage',
'desc': 'What company status pages show, how to read the wording, what they leave out, and how to combine them with independent checks.',
'related': ['what-to-do-when-an-app-or-service-is-down', 'how-to-write-an-outage-update', 'is-it-down-or-just-me'],
'body': '''
<p class="lead">When a service stops working, the first instinct is to check whether it is down for everyone. Many companies publish a status page for this purpose. Used well, it tells you what the company knows. Used alone, it can mislead, because a status page reports what the company has confirmed, not always what you are experiencing. This guide shows how to read one and how to combine it with other sources.</p>
<h2>What a status page is</h2>
<p>A status page is a public page where a company lists the health of its services and any current or past incidents. Typical entries include components such as &ldquo;website&rdquo;, &ldquo;login&rdquo;, &ldquo;API&rdquo; and &ldquo;payments&rdquo;, each marked with a status, plus written updates as the company investigates. Most keep a history, so you can see how often problems have happened.</p>
<h2>How to read the wording</h2>
<p>Companies use a fairly consistent set of terms, though each has its own style.</p>
<ul>
<li><b>Operational.</b> The company believes the component is working normally.</li>
<li><b>Degraded performance.</b> It works, but slowly or for some people.</li>
<li><b>Partial outage.</b> Some features or regions are failing.</li>
<li><b>Major outage.</b> The component is largely unavailable.</li>
<li><b>Investigating.</b> The company knows there is a problem and does not yet know why.</li>
<li><b>Identified.</b> The cause has been found and a fix is being prepared.</li>
<li><b>Monitoring.</b> A fix has been applied and the team is watching to be sure it holds.</li>
<li><b>Resolved.</b> The company considers the incident over.</li>
</ul>
<h2>Why the page can say &ldquo;all good&rdquo; when things are broken</h2>
<ul>
<li><b>Updates take time.</b> Many pages are updated by people, after an incident has been confirmed. There is often a gap of ten or more minutes.</li>
<li><b>Some pages are automatic and some are cautious.</b> Companies decide when a problem is serious enough to post. A fault that affects a minority of users may never appear.</li>
<li><b>It can fail with the service.</b> If the status page is hosted on the same infrastructure as the product, it can go down at the same time. Well-run companies host it separately for exactly this reason.</li>
<li><b>It reports the service, not your connection.</b> A fault on your side, your network or your account will not appear.</li>
</ul>
<h2>A quick routine that works</h2>
<ol>
<li><b>Test it independently.</b> Run the address through the <a href="/">website checker</a>. If we cannot reach it either, and our <a href="/outage-map">worldwide map</a> shows trouble in several regions, that is a strong sign of a real outage, whatever the status page says.</li>
<li><b>Open the company&rsquo;s status page.</b> Look at the component you use, not just the headline. Read the latest update and its timestamp.</li>
<li><b>Look for the pattern.</b> Check our <a href="/outage-history">outage history</a> and the site&rsquo;s page for recent reports from other visitors. A spike in reports at the same time as your problem points to a shared fault.</li>
<li><b>Check the company&rsquo;s other channels.</b> A social media account or support page may be updated before the status page.</li>
<li><b>If everything says it is fine,</b> the problem is probably yours. Work through the <a href="/help/website-not-loading-checklist">website not loading checklist</a>, or <a href="/help/is-it-down-or-just-me">is it down or just me</a>.</li>
</ol>
<h2>Subscribing so you do not have to refresh</h2>
<p>Most status pages let you subscribe by email, text message or a feed. If you rely on a service for work, this is worth doing once: you hear about incidents and fixes as they are posted, and you can stop checking by hand. You can also add the service to a <a href="/monitor">watchlist here</a> to be told when our own checks see it fail.</p>
<h2>If you run a service</h2>
<p>A status page is a promise to be honest in public, and it earns trust when it is quick, specific and written plainly. The best ones say what is affected, what users should do, and when the next update will come, even if it is only &ldquo;no new information yet&rdquo;. Our guide on <a href="/help/how-to-write-an-outage-update">how to write an outage update</a> has examples and a simple template. Host the page away from your main systems so that it stays up when they do not.</p>
'''
},
]
