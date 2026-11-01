# siteupdown.com — deploy notes

Plain PHP 8 + MySQL on a regular Hostinger website (same setup as gounscramble.com). No build step on the server.

## Files
- `index.html, login.html, account.html, monitor.html, privacy.html, legal.html, contact.html, 404.html` — built by `python3 _tools/build.py`
- `assets/` — CSS, JS, `worldmap.js` (built by `python3 _tools/mkmap.py`), `og.png`
- `api/` — PHP endpoints. Files starting with `_` are helpers and are blocked by `.htaccess`.
- `sud-config.example.php` — copy to ONE FOLDER ABOVE `public_html` as `sud-config.php` (never in Git).

## One-time setup
1. hPanel > Databases: create a MySQL database + user. Tables are created automatically on first request.
2. Create `sud-config.php` (see the example) with the DB details, `site`, and `cron_key`.
3. hPanel > Advanced > Cron Jobs: every 5 minutes
   `/usr/bin/php /home/USER/domains/siteupdown.com/public_html/api/cron.php`
   (If cron is not available, use a free uptime pinger to call `https://siteupdown.com/api/cron.php?key=YOUR_CRON_KEY` every 5 minutes.)
4. Google sign-in: Google Cloud Console > APIs & Services > Credentials > OAuth client ID (Web application).
   Authorised JavaScript origin: `https://siteupdown.com`. Put the Client ID in `google_client_id`. No secret needed.
5. Email: create `hello@siteupdown.com` and `noreply@siteupdown.com` in hPanel and (optionally) add the SMTP login to the config.

## Editing
- Change the top-sites / gaming lists in `api/_sites.php`.
- After editing text in `_tools/build.py`, run `python3 _tools/build.py` and commit the generated pages.

## Notes
- Regional probes use Globalping (free). If you see "probes are busy", add a free `globalping_token` to the config.
- Rate limits: 30 checks / 10 min and 15 regional runs / 10 min per visitor (see `api/check.php`, `api/regional.php`).
