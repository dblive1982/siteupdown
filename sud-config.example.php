<?php
// Copy this file to ONE FOLDER ABOVE public_html and name it sud-config.php, e.g.
//   /home/u175986232/domains/siteupdown.com/sud-config.php
// Fill in the database details from hPanel > Databases. Never put the real file in Git.
return [
    'db_host' => '127.0.0.1',
    'db_name' => 'u175986232_siteupdown',
    'db_user' => 'u175986232_sud',
    'db_pass' => 'PUT-THE-DATABASE-PASSWORD-HERE',
    'site' => 'https://siteupdown.com',
    'mail_from' => 'noreply@siteupdown.com',
    // Optional but recommended: send email through a real mailbox for better delivery
    // 'smtp_user' => 'hello@siteupdown.com', 'smtp_pass' => 'THE-MAILBOX-PASSWORD',
    'google_client_id' => '',          // Google sign-in: Client ID only, no secret needed
    'cron_key' => 'PUT-A-LONG-RANDOM-STRING-HERE', // lets a web pinger call /api/cron.php?key=... if hPanel cron is unavailable
    // Telegram alerts (optional): create a bot with @BotFather, then open /api/telegram.php?setup=1&key=YOUR_CRON_KEY once.
    // 'tg_token' => '123456:ABC...', 'tg_bot' => 'YourBotUsername', 'tg_secret' => 'A-LONG-RANDOM-STRING',
    // Pro plan: SMS + WhatsApp alerts through Twilio, paid by users through Stripe (all optional, off until filled in).
    // 'tw_sid' => 'ACxxxxxxxx', 'tw_token' => '...', 'tw_sms_from' => 'SiteUpDown',   // sender ID name or a +44 number
    // 'tw_wa_from' => 'whatsapp:+14155238886',   // sandbox number at first, your approved WhatsApp sender later
    // 'tw_wa_tpl' => 'HXxxxxxxxx',               // approved WhatsApp template (variables {{1}} text, {{2}} link); leave out in the sandbox
    // 'stripe_sk' => 'sk_live_...', 'stripe_price' => 'price_...', 'stripe_whsec' => 'whsec_...',
    // 'pro_price' => '£4.99/month', 'pro_sms_cap' => 30, 'pro_wa_cap' => 200, 'msg_countries' => '44,353',
    // 'pro_emails' => ['you@example.com'],   // accounts that get Pro for free (testing, friends)
    // 'globalping_token' => '',       // optional free token from globalping.io for higher limits
    // 'cron_batch' => 40,             // sites re-probed per cron run
];
