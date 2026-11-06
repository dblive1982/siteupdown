<?php
// The sites we probe every few minutes. Edit these lists to change what shows on the home page.
declare(strict_types=1);

function top_sites(): array {
    return [
        ['google.com', 'Google'], ['youtube.com', 'YouTube'], ['facebook.com', 'Facebook'], ['instagram.com', 'Instagram'],
        ['x.com', 'X'], ['whatsapp.com', 'WhatsApp'], ['tiktok.com', 'TikTok'], ['wikipedia.org', 'Wikipedia'],
        ['amazon.com', 'Amazon'], ['netflix.com', 'Netflix'], ['linkedin.com', 'LinkedIn'], ['reddit.com', 'Reddit'],
        ['microsoft.com', 'Microsoft'], ['apple.com', 'Apple'], ['github.com', 'GitHub'], ['openai.com', 'OpenAI'],
        ['discord.com', 'Discord'], ['spotify.com', 'Spotify'], ['twitch.tv', 'Twitch'], ['paypal.com', 'PayPal'],
        ['cloudflare.com', 'Cloudflare'], ['bbc.co.uk', 'BBC'], ['ebay.com', 'eBay'], ['zoom.us', 'Zoom'],
    ];
}

// [host, name, category]. Categories: Multiplayer, Shooters, Platforms, Casual, Services, MMO.
function gaming_sites(): array {
    return [
        ['innersloth.com', 'Among Us', 'Multiplayer'], ['ea.com', 'Apex Legends', 'Shooters'], ['battlefield.com', 'Battlefield 2042', 'Shooters'],
        ['battle.net', 'Battle.net', 'Platforms'], ['blizzard.com', 'Blizzard', 'Platforms'], ['callofduty.com', 'Call of Duty', 'Shooters'],
        ['chess.com', 'Chess.com', 'Casual'], ['supercell.com', 'Clash Royale', 'Casual'], ['counter-strike.net', 'CSGO', 'Shooters'],
        ['curseforge.com', 'CurseForge', 'Services'], ['deadbydaylight.com', 'Dead by Daylight', 'Multiplayer'], ['bungie.net', 'Destiny 2', 'Shooters'],
        ['diablo4.blizzard.com', 'Diablo', 'MMO'], ['dota2.com', 'DOTA 2', 'Multiplayer'], ['ea.com', 'EA', 'Platforms'],
        ['eldenring.bandainamcoent.com', 'Elden Ring', 'Multiplayer'], ['elderscrollsonline.com', 'Elder Scrolls Online', 'MMO'], ['epicgames.com', 'Epic Games', 'Platforms'],
        ['finalfantasyxiv.com', 'FFXIV', 'MMO'], ['fivem.net', 'FiveM', 'Multiplayer'], ['footballfusion.com', 'Football Fusion', 'Casual'],
        ['fortnite.com', 'Fortnite', 'Shooters'], ['genshin.hoyoverse.com', 'Genshin Impact', 'MMO'], ['growtopiagame.com', 'Growtopia', 'Casual'],
        ['steampowered.com', 'Steam', 'Platforms'], ['store.steampowered.com', 'Steam Store', 'Services'], ['steamcommunity.com', 'Steam Community', 'Services'],
        ['xbox.com', 'Xbox', 'Platforms'], ['playstation.com', 'PlayStation Network', 'Platforms'], ['nintendo.com', 'Nintendo', 'Platforms'],
        ['riotgames.com', 'Riot Games', 'Platforms'], ['leagueoflegends.com', 'League of Legends', 'Multiplayer'], ['playvalorant.com', 'Valorant', 'Shooters'],
        ['minecraft.net', 'Minecraft', 'Multiplayer'], ['roblox.com', 'Roblox', 'Multiplayer'], ['rockstargames.com', 'Rockstar Games', 'Platforms'],
        ['ubisoft.com', 'Ubisoft', 'Platforms'], ['rainbow6.com', 'Rainbow Six Siege', 'Shooters'], ['overwatch.blizzard.com', 'Overwatch 2', 'Shooters'],
        ['worldofwarcraft.blizzard.com', 'World of Warcraft', 'MMO'], ['guildwars2.com', 'Guild Wars 2', 'MMO'], ['runescape.com', 'RuneScape', 'MMO'],
        ['albiononline.com', 'Albion Online', 'MMO'], ['newworld.com', 'New World', 'MMO'], ['pathofexile.com', 'Path of Exile', 'MMO'],
        ['warframe.com', 'Warframe', 'Shooters'], ['pubg.com', 'PUBG', 'Shooters'], ['escapefromtarkov.com', 'Escape from Tarkov', 'Shooters'],
        ['rocketleague.com', 'Rocket League', 'Multiplayer'], ['fallguys.com', 'Fall Guys', 'Casual'], ['lichess.org', 'Lichess', 'Casual'],
        ['itch.io', 'itch.io', 'Services'], ['gog.com', 'GOG', 'Platforms'], 
        ['discord.com', 'Discord', 'Services'], ['twitch.tv', 'Twitch', 'Services'], ['faceit.com', 'FACEIT', 'Services'],
        ['mojang.com', 'Mojang', 'Services'], ['coolmathgames.com', 'Coolmath Games', 'Casual'],
        ['poki.com', 'Poki', 'Casual'], ['brawlstars.com', 'Brawl Stars', 'Casual'], ['playlostark.com', 'Lost Ark', 'MMO'],
    ];
}
