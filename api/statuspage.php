<?php
// Pro status pages. GET ?slug=my-page (public) -> what the page at /p/my-page shows.
// Signed in: GET (no slug) -> my page settings; POST {action: save|delete, slug, title, hosts[]}.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_plan.php';
$pdo = db();
ensure_billing($pdo);
const RESERVED = ['admin', 'api', 'status', 'help', 'tools', 'account', 'login', 'pricing', 'about', 'contact', 'monitor', 'www', 'siteupdown', 'test', 'demo'];

function page_view(PDO $pdo, array $pg): array {
    $hosts = json_decode((string)$pg['hosts'], true) ?: [];
    $in = implode(',', array_fill(0, max(1, count($hosts)), '?'));
    $st = $pdo->prepare("SELECT host, verdict, ms, checked_at FROM site_status WHERE host IN ($in)"); $st->execute($hosts ?: ['-']);
    $cur = []; foreach ($st->fetchAll() as $r) $cur[$r['host']] = $r;
    $from = gmdate('Y-m-d', time() - 89 * 86400);
    $dq = $pdo->prepare("SELECT host, day, up_n, bad_n FROM site_daily WHERE host IN ($in) AND day >= ? ORDER BY day"); $dq->execute(array_merge($hosts ?: ['-'], [$from]));
    $days = []; foreach ($dq->fetchAll() as $r) $days[$r['host']][$r['day']] = $r;
    $sites = []; $bad = 0; $warn = 0;
    foreach ($hosts as $h) {
        $c = $cur[$h] ?? null; $v = $c['verdict'] ?? null;
        $state = $v === 'up' ? 'up' : (in_array($v, ['down', 'timeout'], true) ? 'down' : ($v ? 'unclear' : 'unknown'));
        if ($state === 'down') $bad++; elseif ($state !== 'up') $warn++;
        $bars = []; $ok = 0; $all = 0;
        for ($i = 89; $i >= 0; $i--) {
            $d = gmdate('Y-m-d', time() - $i * 86400); $r = $days[$h][$d] ?? null; $n = $r ? (int)$r['up_n'] + (int)$r['bad_n'] : 0;
            if ($n) { $ok += (int)$r['up_n']; $all += $n; }
            $bars[] = $n ? round(100 * (int)$r['up_n'] / $n, 2) : null;
        }
        $sites[] = ['host' => $h, 'state' => $state, 'ms' => isset($c['ms']) ? (int)$c['ms'] : null, 'at' => !empty($c['checked_at']) ? iso($c['checked_at']) : null, 'uptime90' => $all ? round(100 * $ok / $all, 3) : null, 'bars' => $bars];
    }
    $inc = []; 
    if ($hosts) {
        $iq = $pdo->prepare("SELECT host, started_at, ended_at FROM incidents WHERE host IN ($in) AND started_at > ? ORDER BY started_at DESC LIMIT 15"); $iq->execute(array_merge($hosts, [gmdate('Y-m-d H:i:s', time() - 30 * 86400)]));
        foreach ($iq->fetchAll() as $r) $inc[] = ['host' => $r['host'], 'started' => iso($r['started_at']), 'ended' => $r['ended_at'] ? iso($r['ended_at']) : null];
    }
    return ['title' => $pg['title'], 'slug' => $pg['slug'], 'overall' => $bad ? 'down' : ($warn ? 'unclear' : 'up'), 'down' => $bad, 'sites' => $sites, 'incidents' => $inc, 'now' => gmdate('Y-m-d\TH:i:s\Z')];
}

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET' && isset($_GET['slug'])) {
    $slug = strtolower((string)$_GET['slug']);
    $s = $pdo->prepare('SELECT slug, user_id, title, hosts FROM status_pages WHERE slug=?'); $s->execute([$slug]); $pg = $s->fetch();
    if (!$pg || !is_pro($pdo, (int)$pg['user_id'])) out(404, ['error' => 'This status page does not exist, or has been paused.']);
    header('Cache-Control: public, max-age=30');
    out(200, page_view($pdo, $pg));
}

$uid = require_user();
$pro = is_pro($pdo, $uid);
$q = $pdo->prepare('SELECT slug, title, hosts FROM status_pages WHERE user_id=?'); $q->execute([$uid]); $mine = $q->fetch();
$w = $pdo->prepare('SELECT host FROM watchlist WHERE user_id=? ORDER BY host'); $w->execute([$uid]); $watch = $w->fetchAll(PDO::FETCH_COLUMN);
$state = function () use (&$pro, &$mine, &$watch) { return ['pro' => $pro, 'page' => $mine ? ['slug' => $mine['slug'], 'title' => $mine['title'], 'hosts' => json_decode($mine['hosts'], true) ?: []] : null, 'watch' => $watch, 'max' => PRO_STATUS_SITES]; };
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') out(200, $state());

$in = read_post();
$a = (string)($in['action'] ?? '');
if ($a === 'delete') { $pdo->prepare('DELETE FROM status_pages WHERE user_id=?')->execute([$uid]); $mine = null; out(200, $state()); }
if ($a === 'save') {
    pro_required($pdo, $uid, 'A public status page');
    $slug = strtolower(trim((string)($in['slug'] ?? '')));
    if (!preg_match('/^[a-z0-9](?:[a-z0-9-]{1,38})[a-z0-9]$/', $slug) || in_array($slug, RESERVED, true)) out(422, ['error' => 'Choose a web address of 3 to 40 letters, numbers or hyphens, such as my-shop.']);
    $title = trim(preg_replace('/\s+/', ' ', strip_tags((string)($in['title'] ?? ''))) ?? '');
    if ($title === '' || mb_strlen($title) > 80) out(422, ['error' => 'Give your page a name of up to 80 characters.']);
    $hosts = array_values(array_unique(array_map('strtolower', array_filter((array)($in['hosts'] ?? []), 'is_string'))));
    $hosts = array_values(array_intersect($hosts, $watch));
    if (!$hosts) out(422, ['error' => 'Pick at least one site from your watchlist.']);
    if (count($hosts) > PRO_STATUS_SITES) out(422, ['error' => 'A status page can show up to ' . PRO_STATUS_SITES . ' sites.']);
    $e = $pdo->prepare('SELECT user_id FROM status_pages WHERE slug=?'); $e->execute([$slug]); $o = $e->fetch();
    if ($o && (int)$o['user_id'] !== $uid) out(409, ['error' => 'That web address is taken. Please choose another.']);
    $pdo->prepare('DELETE FROM status_pages WHERE user_id=?')->execute([$uid]);
    $pdo->prepare('INSERT INTO status_pages (slug, user_id, title, hosts, created_at) VALUES (?,?,?,?,?)')->execute([$slug, $uid, $title, json_encode($hosts), sql_now()]);
    $q->execute([$uid]); $mine = $q->fetch();
    out(200, $state());
}
out(400, ['error' => 'Bad request.']);
