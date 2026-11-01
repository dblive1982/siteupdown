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
    // 'globalping_token' => '',       // optional free token from globalping.io for higher limits
    // 'cron_batch' => 40,             // sites re-probed per cron run
];
