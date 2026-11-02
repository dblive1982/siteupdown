# "Is X down?" pages for siteupdown.com. Imported by build.py.
# (name, host, category, blurb). The page address is /is-<slug>-down, with the slug made from the name.

CATS = {
    'social': ('Social and messaging', [
        'Open the website version if the app is failing, or the app if the website is. Outages often hit only one of them.',
        'Check whether photos, videos or messages fail while text still loads. Partial outages are common on social platforms.',
        'Log out and back in, then restart the app. Clearing the app&rsquo;s cache can fix a feed that will not refresh.',
        'Try mobile data instead of Wi-Fi, or the other way round, to rule out your network.',
        'Look at the company&rsquo;s official support or status account on another platform for an outage notice.',
    ]),
    'video': ('Video and streaming', [
        'If videos buffer or stop but the site loads, the problem is often your connection speed or the video servers rather than the whole site.',
        'Try a lower video quality, or a different device, to see whether the problem follows the account.',
        'Restart your router and pause other downloads on your network.',
        'Sign out of the app, sign back in, and update it to the latest version.',
        'Check whether other streaming sites work. If none do, the problem is your internet connection.',
    ]),
    'search': ('Search, email and AI', [
        'Try the website in a private window, which rules out extensions and old cookies.',
        'If email will not send or load, check the service&rsquo;s own status page, since mail can fail while the website still loads.',
        'Make sure your device&rsquo;s date and time are set automatically, because a wrong clock breaks secure sign-in.',
        'Disable VPNs and ad blockers for a moment and reload.',
        'If an AI tool is slow or showing errors, it is often under heavy load. Waiting a few minutes usually helps.',
    ]),
    'work': ('Work, cloud and developer tools', [
        'Check the service&rsquo;s official status page first. Most business tools publish one with a history of incidents.',
        'If only one feature fails, such as uploads or notifications, it may be a partial outage rather than the whole service.',
        'Test from a different network. Company firewalls and VPNs can block these services.',
        'Sign out and back in, and refresh your browser cache with Ctrl+F5.',
        'If your own website uses the service, check the integration&rsquo;s API keys and recent changes before blaming the provider.',
    ]),
    'shopping': ('Shopping and payments', [
        'If the shop loads but checkout fails, the payment service may be having its own problem, so try again later before paying twice.',
        'Do not refresh repeatedly on a payment page. Check your bank app or email for a confirmation first.',
        'Clear cookies for the site, or try a private window, if your basket or sign-in is acting strangely.',
        'Sales days bring heavy traffic, and busy shops can slow down or show errors briefly.',
        'Use the company&rsquo;s official app or help page to confirm the problem before contacting your bank.',
    ]),
    'news': ('News and reference', [
        'Busy news events can overload a site for a few minutes, so wait and reload.',
        'Try a different page of the same site. A single broken page is different from a site-wide outage.',
        'If the page shows old content, hard-reload it with Ctrl+F5 to skip your cached copy.',
        'A mobile data connection will show whether your home network is the problem.',
        'Public services and news sites often post updates on their official social accounts.',
    ]),
    'gaming': ('Gaming platforms and games', [
        'Check whether the problem is the store or website, or the game servers. They can fail separately.',
        'Restart the game launcher and the game, and check for a pending update.',
        'Check the publisher&rsquo;s official status page or social account for maintenance announcements, which are common on update days.',
        'Wired connections and restarting your router fix many matchmaking and login problems.',
        'Try a different network or turn off your VPN, because some game services block VPN traffic.',
    ]),
}

SITES = [
    # social
    ('Facebook', 'facebook.com', 'social', 'Facebook is a social network owned by Meta, used for personal profiles, groups, pages and messaging.'),
    ('Instagram', 'instagram.com', 'social', 'Instagram is a photo and video sharing app owned by Meta, known for stories, reels and direct messages.'),
    ('X', 'x.com', 'social', 'X, formerly Twitter, is a social platform for short public posts, news and conversations.'),
    ('WhatsApp', 'whatsapp.com', 'social', 'WhatsApp is a messaging and calling app owned by Meta. This page checks its website, so a problem sending messages may not show here.'),
    ('TikTok', 'tiktok.com', 'social', 'TikTok is a short-video platform where people watch and share clips, owned by ByteDance.'),
    ('LinkedIn', 'linkedin.com', 'social', 'LinkedIn is a professional network for jobs, recruiting and work updates, owned by Microsoft.'),
    ('Reddit', 'reddit.com', 'social', 'Reddit is a collection of topic-based communities where people post, discuss and vote on content.'),
    ('Snapchat', 'snapchat.com', 'social', 'Snapchat is a messaging and camera app from Snap Inc, known for disappearing messages and stories. This page checks its website.'),
    ('Pinterest', 'pinterest.com', 'social', 'Pinterest is a visual discovery site where people save ideas as pins on boards.'),
    ('Telegram', 'telegram.org', 'social', 'Telegram is a cloud-based messaging service. This page checks its website, so message delivery problems may not show here.'),
    ('Discord', 'discord.com', 'social', 'Discord is a voice, video and text chat service used by gaming and community groups.'),
    ('Bluesky', 'bsky.app', 'social', 'Bluesky is a social network for short public posts, built on an open protocol.'),
    # video
    ('YouTube', 'youtube.com', 'video', 'YouTube is the world&rsquo;s largest video sharing site, owned by Google.'),
    ('Netflix', 'netflix.com', 'video', 'Netflix is a subscription streaming service for films and series.'),
    ('Twitch', 'twitch.tv', 'video', 'Twitch is a live streaming platform, mostly for gaming, owned by Amazon.'),
    ('Spotify', 'spotify.com', 'video', 'Spotify is a music and podcast streaming service. This page checks its website, so playback problems in the app may not show here.'),
    ('Disney+', 'disneyplus.com', 'video', 'Disney+ is a subscription streaming service from Disney, with films, series and live content.'),
    ('Prime Video', 'primevideo.com', 'video', 'Prime Video is Amazon&rsquo;s streaming service for films and series.'),
    ('Hulu', 'hulu.com', 'video', 'Hulu is a subscription streaming service for TV and film, owned by Disney.'),
    # search / email / AI
    ('Google', 'google.com', 'search', 'Google is the world&rsquo;s most-used search engine.'),
    ('Gmail', 'mail.google.com', 'search', 'Gmail is Google&rsquo;s free email service.'),
    ('Outlook', 'outlook.live.com', 'search', 'Outlook is Microsoft&rsquo;s email and calendar service for personal accounts.'),
    ('Yahoo', 'yahoo.com', 'search', 'Yahoo is a web portal with search, news and email.'),
    ('Bing', 'bing.com', 'search', 'Bing is Microsoft&rsquo;s search engine.'),
    ('ChatGPT', 'chatgpt.com', 'search', 'ChatGPT is an AI chat assistant made by OpenAI.'),
    ('OpenAI', 'openai.com', 'search', 'OpenAI is the AI research company behind ChatGPT. This page checks its main website.'),
    ('Wikipedia', 'wikipedia.org', 'news', 'Wikipedia is the free online encyclopedia run by the Wikimedia Foundation.'),
    ('Apple', 'apple.com', 'search', 'Apple&rsquo;s website covers its products, support and store.'),
    ('iCloud', 'icloud.com', 'search', 'iCloud is Apple&rsquo;s cloud storage and sync service for photos, files and backups.'),
    ('Microsoft', 'microsoft.com', 'work', 'Microsoft&rsquo;s website covers Windows, Office, Xbox and its other products and support.'),
    # work
    ('Zoom', 'zoom.us', 'work', 'Zoom is a video meeting and webinar service.'),
    ('Slack', 'slack.com', 'work', 'Slack is a messaging platform for teams and workplaces.'),
    ('Dropbox', 'dropbox.com', 'work', 'Dropbox is a cloud storage and file sync service.'),
    ('Google Drive', 'drive.google.com', 'work', 'Google Drive is Google&rsquo;s cloud storage for files, docs and sheets.'),
    ('Microsoft Teams', 'teams.microsoft.com', 'work', 'Microsoft Teams is a chat, meeting and collaboration app that is part of Microsoft 365.'),
    ('Notion', 'notion.so', 'work', 'Notion is a workspace for notes, documents and project planning.'),
    ('Canva', 'canva.com', 'work', 'Canva is an online design tool for graphics, presentations and social posts.'),
    ('Figma', 'figma.com', 'work', 'Figma is a collaborative design and prototyping tool that runs in the browser.'),
    ('Trello', 'trello.com', 'work', 'Trello is a board-based project management tool from Atlassian.'),
    ('Atlassian', 'atlassian.com', 'work', 'Atlassian makes Jira, Confluence and Trello. This page checks its main website.'),
    ('Cloudflare', 'cloudflare.com', 'work', 'Cloudflare provides a content delivery network, security and DNS services that a large share of websites rely on.'),
    ('AWS', 'aws.amazon.com', 'work', 'Amazon Web Services (AWS) is Amazon&rsquo;s cloud platform. This page checks the AWS website, not individual cloud regions.'),
    ('GitHub', 'github.com', 'work', 'GitHub is the code hosting platform used by developers to store, review and share software, owned by Microsoft.'),
    ('Shopify', 'shopify.com', 'shopping', 'Shopify is an e-commerce platform for building and running online shops.'),
    ('WordPress.com', 'wordpress.com', 'work', 'WordPress.com is a hosted website and blogging service from Automattic.'),
    ('GoDaddy', 'godaddy.com', 'work', 'GoDaddy is a domain registrar and web hosting company.'),
    ('Hostinger', 'hostinger.com', 'work', 'Hostinger is a web hosting and domain company.'),
    # shopping and payments
    ('Amazon', 'amazon.com', 'shopping', 'Amazon is an online shop selling a huge range of products, as well as services such as Prime.'),
    ('Amazon UK', 'amazon.co.uk', 'shopping', 'Amazon.co.uk is Amazon&rsquo;s shop for customers in the United Kingdom.'),
    ('eBay', 'ebay.com', 'shopping', 'eBay is an online marketplace for new and used items, sold by auction or at a fixed price.'),
    ('Etsy', 'etsy.com', 'shopping', 'Etsy is a marketplace for handmade, vintage and digital goods.'),
    ('PayPal', 'paypal.com', 'shopping', 'PayPal is an online payments service for buying, selling and sending money.'),
    ('Stripe', 'stripe.com', 'shopping', 'Stripe is a payment processing service used by many online shops. This page checks its website, not its payment systems.'),
    ('Temu', 'temu.com', 'shopping', 'Temu is an online marketplace selling a wide range of low-priced goods.'),
    ('Shein', 'shein.com', 'shopping', 'Shein is an online fashion retailer.'),
    ('AliExpress', 'aliexpress.com', 'shopping', 'AliExpress is an online marketplace owned by Alibaba, selling goods from sellers around the world.'),
    ('Walmart', 'walmart.com', 'shopping', 'Walmart&rsquo;s website lets customers shop for groceries and other goods in the United States.'),
    ('Vinted', 'vinted.co.uk', 'shopping', 'Vinted is a marketplace for buying and selling second-hand clothes.'),
    # news
    ('BBC', 'bbc.co.uk', 'news', 'The BBC website carries UK and world news, sport, weather and iPlayer.'),
    ('CNN', 'cnn.com', 'news', 'CNN is a US news network and website.'),
    ('GOV.UK', 'gov.uk', 'news', 'GOV.UK is the UK government&rsquo;s official website for public services and information.'),
    # gaming
    ('Steam', 'steampowered.com', 'gaming', 'Steam is Valve&rsquo;s PC game store and launcher.'),
    ('Epic Games', 'epicgames.com', 'gaming', 'Epic Games runs the Epic Games Store and makes Fortnite.'),
    ('Xbox', 'xbox.com', 'gaming', 'Xbox is Microsoft&rsquo;s gaming platform, covering consoles, Game Pass and Xbox Live.'),
    ('PlayStation Network', 'playstation.com', 'gaming', 'PlayStation Network is Sony&rsquo;s online service for PlayStation consoles.'),
    ('Nintendo', 'nintendo.com', 'gaming', 'Nintendo&rsquo;s website covers its consoles, games and online services.'),
    ('Battle.net', 'battle.net', 'gaming', 'Battle.net is Blizzard&rsquo;s game launcher and online service.'),
    ('Riot Games', 'riotgames.com', 'gaming', 'Riot Games makes League of Legends and Valorant.'),
    ('League of Legends', 'leagueoflegends.com', 'gaming', 'League of Legends is a team-based online strategy game from Riot Games. This page checks its website, not the game servers.'),
    ('Valorant', 'playvalorant.com', 'gaming', 'Valorant is a team-based tactical shooter from Riot Games. This page checks its website, not the game servers.'),
    ('Roblox', 'roblox.com', 'gaming', 'Roblox is a platform where people play and create games made by other users.'),
    ('Minecraft', 'minecraft.net', 'gaming', 'Minecraft is a sandbox building game. This page checks its website, not individual servers.'),
    ('Fortnite', 'fortnite.com', 'gaming', 'Fortnite is a popular online battle royale game from Epic Games. This page checks its website, not the game servers.'),
    ('EA', 'ea.com', 'gaming', 'EA (Electronic Arts) publishes games such as EA Sports FC, Apex Legends and The Sims.'),
    ('Ubisoft', 'ubisoft.com', 'gaming', 'Ubisoft publishes games such as Assassin&rsquo;s Creed and Rainbow Six Siege.'),
    ('Rockstar Games', 'rockstargames.com', 'gaming', 'Rockstar Games makes the Grand Theft Auto and Red Dead series.'),
    ('Call of Duty', 'callofduty.com', 'gaming', 'Call of Duty is a long-running shooter series from Activision. This page checks its website, not the game servers.'),
    ('Genshin Impact', 'genshin.hoyoverse.com', 'gaming', 'Genshin Impact is an open-world action game from HoYoverse. This page checks its website, not the game servers.'),
]

# App back-end addresses that apps talk to (public web/API hosts that answer an ordinary request). Name -> [(label, host)].
APPS = {
    'WhatsApp': [('WhatsApp Web', 'web.whatsapp.com'), ('API', 'api.whatsapp.com')],
    'Instagram': [('App API', 'i.instagram.com'), ('Graph API', 'graph.instagram.com')],
    'Facebook': [('Mobile site', 'm.facebook.com'), ('Graph API', 'graph.facebook.com')],
    'TikTok': [('Mobile site', 'm.tiktok.com')],
    'Snapchat': [('App servers', 'app.snapchat.com'), ('Accounts', 'accounts.snapchat.com')],
    'Telegram': [('Web app', 'web.telegram.org'), ('Bot API', 'api.telegram.org')],
    'Discord': [('Gateway', 'gateway.discord.gg'), ('Media servers', 'cdn.discordapp.com')],
    'Spotify': [('Web API', 'api.spotify.com'), ('Accounts and login', 'accounts.spotify.com')],
    'Netflix': [('App API', 'api-global.netflix.com')],
    'YouTube': [('App API', 'youtubei.googleapis.com')],
    'Roblox': [('Game API', 'apis.roblox.com'), ('Login', 'auth.roblox.com')],
    'Fortnite': [('Epic account service', 'account-public-service-prod.ol.epicgames.com')],
    'Minecraft': [('Session servers', 'sessionserver.mojang.com'), ('Services API', 'api.minecraftservices.com')],
    'Steam': [('Steam API', 'api.steampowered.com')],
    'Twitch': [('API', 'api.twitch.tv')],
    'Reddit': [('App API', 'oauth.reddit.com')],
    'X': [('API', 'api.x.com')],
    'Pinterest': [('API', 'api.pinterest.com')],
    'ChatGPT': [('API servers', 'api.openai.com')],
    'Xbox': [('Xbox sign-in', 'login.live.com')],
}

import re as _re

def slug(name):
    s = name.lower().replace('+', ' plus').replace('&', ' and ')
    s = _re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

def page_path(name):
    return '/is-%s-down' % slug(name)

KIND_LABELS = [
    ('site', 'Website will not load'),
    ('login', 'Cannot log in'),
    ('app', 'App not working'),
    ('slow', 'Very slow'),
]
