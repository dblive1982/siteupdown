<?php
// GET /widget/<host> -> a small live status card people can put in an iframe on their own page (listed sites only).
// GET /api/widget.php?host=<host>&data=1 -> the summary numbers the card shows (JSON).
declare(strict_types=1);
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_world.php';
$host = strtolower(preg_replace('/[^a-z0-9.\-]/i', '', (string)($_GET['host'] ?? '')));
$list = site_pages();
if (!isset($list[$host])) { http_response_code(404); header('Content-Type: text/plain'); echo 'Not a site we list.'; exit; }
$name = (string)$list[$host]['name']; $page = (string)$list[$host]['page'];
if (!empty($_GET['data'])) {
    $pdo = db();
    $q = $pdo->prepare('SELECT verdict, checked_at, ms FROM site_status WHERE host=?'); $q->execute([$host]); $r = $q->fetch();
    $v = $r ? (string)$r['verdict'] : 'unknown';
    if (in_array($v, ['inconclusive', 'timeout'], true) && world_says_up($pdo, $host)) $v = 'up';
    $q = $pdo->prepare("SELECT SUM(verdict='up') u, COUNT(*) n, AVG(CASE WHEN verdict='up' THEN ms END) a FROM site_log WHERE host=? AND ts > ?");
    $q->execute([$host, gmdate('Y-m-d H:i:s', time() - 86400)]); $u = $q->fetch();
    $n = $u ? (int)$u['n'] : 0;
    header('Content-Type: application/json'); header('Cache-Control: public, max-age=30'); header('Access-Control-Allow-Origin: *');
    echo json_encode(['name' => $name, 'v' => $v, 'ms' => $r && $r['ms'] !== null ? (int)$r['ms'] : null, 'at' => $r ? iso((string)$r['checked_at']) : null,
        'up24' => $n >= 10 ? round(100 * (int)$u['u'] / $n, 1) : null, 'avg24' => $n >= 10 && $u['a'] !== null ? (int)round((float)$u['a']) : null]);
    exit;
}
$e = htmlspecialchars($name, ENT_QUOTES);
header('Content-Type: text/html; charset=utf-8'); header('Cache-Control: public, max-age=300');
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title><?= $e ?> status</title>
<style>
*{box-sizing:border-box}html,body{margin:0;background:transparent;font:13px/1.35 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1c1b29}
.w{display:block;height:100vh;min-height:92px;background:#fff;border:1px solid #d9d6e6;border-radius:12px;padding:9px 12px;text-decoration:none;color:inherit;overflow:hidden}
.t{display:flex;align-items:center;gap:8px;justify-content:space-between}.n{font-weight:700;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.p{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:2px 10px;color:#fff;font-weight:700;font-size:12px;background:#6b6b7a;white-space:nowrap}
.p i{width:7px;height:7px;border-radius:50%;background:#fff;display:inline-block}
.p.up{background:#2e9d46}.p.down{background:#d6454b}.p.maybe{background:#d9962b}.p.up i{animation:b 1.6s infinite}
@keyframes b{50%{opacity:.35}}
.s{display:flex;gap:14px;margin:4px 0 2px;color:#5b5870;font-size:12px;flex-wrap:wrap}.s b{color:#1c1b29}
.lg{flex:0 0 auto;height:24px;width:auto;margin:0 auto}
@media(max-width:230px){.lg{display:none}}
svg{display:block;width:100%;height:30px;margin-top:2px;cursor:crosshair;touch-action:none}
.r{display:flex;justify-content:space-between;color:#5b5870;font-size:11px;min-height:15px}
</style></head><body data-host="<?= htmlspecialchars($host, ENT_QUOTES) ?>">
<a class="w" id="w" href="https://siteupdown.com<?= htmlspecialchars($page, ENT_QUOTES) ?>" target="_blank" rel="noopener" title="Open the full <?= $e ?> status page">
<div class="t"><span class="n"><?= $e ?></span><img class="lg" src="/assets/nl-logo.png" alt="siteupdown.com" width="51" height="24"><span class="p" id="p"><i></i><span id="pt">Checking</span></span></div>
<div class="s"><span>Uptime 24h <b id="u">–</b></span><span>Response <b id="m">–</b></span></div>
<svg id="g" viewBox="0 0 200 30" preserveAspectRatio="none" aria-label="Recent response times"></svg>
<div class="r"><span id="rd">Live, updates every few seconds</span><span id="ra">siteupdown.com</span></div>
</a>
<script src="/assets/embed.js"></script></body></html>
