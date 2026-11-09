<?php
// POST {p: path, r: referrer, tz, w: screen width} -> counts one page view. Anonymous: nothing identifying is kept.
// Stored: day, page, country, device type, where the visitor came from, and a count. Unique visitors are counted from a hash of
// address + browser + a secret that changes every day; those hashes are deleted after two days and cannot be turned back into an address.
require __DIR__ . '/_boot.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['error' => 'Not allowed']);
header('Cache-Control: no-store');
// sendBeacon cannot add the usual request header, so this one endpoint reads the body itself; it only ever adds to a counter.
$o = (string)($_SERVER['HTTP_ORIGIN'] ?? ''); if ($o !== '' && !preg_match('~^https?://(www\.)?siteupdown\.com$|^https?://[a-z0-9-]+\.hostingersite\.com$|^https?://(localhost|127\.0\.0\.1)(:\d+)?$~i', $o)) { http_response_code(204); exit; }
$in = json_decode(file_get_contents('php://input') ?: '', true); if (!is_array($in)) $in = [];
$p = (string)($in['p'] ?? '');
if (!preg_match('~^/[A-Za-z0-9/_.\-]{0,150}$~', $p) || preg_match('~^/(admin|api|login|account|s/|widget|badge)~', $p)) { http_response_code(204); exit; }
$p = preg_replace('~(?<=.)/$~', '', $p); $p = preg_replace('~\.html$~', '', $p); if ($p === '' || $p === '/index') $p = '/';
$ua = strtolower((string)($_SERVER['HTTP_USER_AGENT'] ?? ''));
if ($ua === '' || preg_match('~bot|crawl|spider|slurp|headless|lighthouse|pingdom|uptime|monitor|curl|wget|python|java/|go-http|preview|facebookexternalhit|whatsapp|telegram|discord~', $ua)) { http_response_code(204); exit; }
if (($_SERVER['HTTP_DNT'] ?? '') === '1' || ($_SERVER['HTTP_SEC_GPC'] ?? '') === '1') { http_response_code(204); exit; }
// Country only: the network's header when there is one, otherwise from the visitor's own time zone (same rule as problem reports).
$cc = strtoupper((string)($_SERVER['HTTP_CF_IPCOUNTRY'] ?? $_SERVER['HTTP_X_COUNTRY_CODE'] ?? ''));
if (!preg_match('/^[A-Z]{2}$/', $cc) || $cc === 'XX' || $cc === 'T1') {
    $cc = ''; $tz = (string)($in['tz'] ?? '');
    if ($tz !== '' && strlen($tz) < 64 && in_array($tz, DateTimeZone::listIdentifiers(), true)) { $c2 = strtoupper((string)((new DateTimeZone($tz))->getLocation()['country_code'] ?? '')); if (preg_match('/^[A-Z]{2}$/', $c2) && $c2 !== '??') $cc = $c2; }
}
$w = (int)($in['w'] ?? 0); $dev = $w > 0 && $w < 600 ? 'm' : ($w > 0 && $w < 1024 ? 't' : 'd');
// Where from: the host only, grouped into a few friendly names. Our own pages are not a source.
$ref = ''; $rh = strtolower((string)parse_url((string)($in['r'] ?? ''), PHP_URL_HOST));
if ($rh !== '' && !preg_match('~(^|\.)siteupdown\.com$~', $rh)) {
    $rh = preg_replace('~^(www|m|l|lm)\.~', '', $rh);
    $map = ['google.' => 'Google', 'bing.com' => 'Bing', 'duckduckgo.com' => 'DuckDuckGo', 'yahoo.' => 'Yahoo', 'ecosia.org' => 'Ecosia', 'baidu.com' => 'Baidu', 'yandex.' => 'Yandex', 'facebook.com' => 'Facebook', 'instagram.com' => 'Instagram', 't.co' => 'X', 'twitter.com' => 'X', 'x.com' => 'X', 'reddit.com' => 'Reddit', 'youtube.com' => 'YouTube', 'linkedin.com' => 'LinkedIn', 'tiktok.com' => 'TikTok', 'chatgpt.com' => 'ChatGPT', 'perplexity.ai' => 'Perplexity'];
    $ref = mb_substr($rh, 0, 60);
    foreach ($map as $k => $v) if (str_contains($rh, $k)) { $ref = $v; break; }
}
$pdo = db(); $day = gmdate('Y-m-d'); $hr = (int)gmdate('G');
$up = $pdo->prepare('UPDATE pv_daily SET views = views + 1 WHERE day=? AND path=? AND country=? AND device=? AND ref=?');
$up->execute([$day, $p, $cc, $dev, $ref]);
if ($up->rowCount() === 0) {
    try { $pdo->prepare('INSERT INTO pv_daily (day, path, country, device, ref, views) VALUES (?,?,?,?,?,1)')->execute([$day, $p, $cc, $dev, $ref]); }
    catch (Throwable $e) { $up->execute([$day, $p, $cc, $dev, $ref]); }
}
$salt = hash_hmac('sha256', $day, (string)(config()['pv_secret'] ?? config()['db_pass'] ?? 'sud'));
$hash = substr(hash_hmac('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|' . $ua, $salt), 0, 32);
$new = false;
try { $pdo->prepare('INSERT INTO pv_seen (day, h) VALUES (?,?)')->execute([$day, $hash]); $new = true; } catch (Throwable $e) { /* already counted today */ }
$u = $pdo->prepare('UPDATE pv_hour SET views = views + 1, visitors = visitors + ? WHERE day=? AND hr=?'); $u->execute([$new ? 1 : 0, $day, $hr]);
if ($u->rowCount() === 0) { try { $pdo->prepare('INSERT INTO pv_hour (day, hr, views, visitors) VALUES (?,?,1,?)')->execute([$day, $hr, $new ? 1 : 0]); } catch (Throwable $e) { $u->execute([$new ? 1 : 0, $day, $hr]); } }
if ($new) {
    $v = $pdo->prepare('UPDATE pv_visitors SET visitors = visitors + 1 WHERE day=? AND country=? AND device=?'); $v->execute([$day, $cc, $dev]);
    if ($v->rowCount() === 0) { try { $pdo->prepare('INSERT INTO pv_visitors (day, country, device, visitors) VALUES (?,?,?,1)')->execute([$day, $cc, $dev]); } catch (Throwable $e) { $v->execute([$day, $cc, $dev]); } }
}
http_response_code(204);
