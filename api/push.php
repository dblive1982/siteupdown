<?php
// Browser notifications. GET ?key -> the public key. POST {act: sub|unsub|has, host, sub} -> manage one subscription.
declare(strict_types=1);
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_push.php';
$pdo = db();
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    [, $pub] = push_vapid($pdo);
    header('Cache-Control: public, max-age=3600');
    out(200, ['key' => $pub]);
}
$in = json_decode((string)file_get_contents('php://input'), true);
if (!is_array($in)) out(422, ['error' => 'Bad request.']);
throttle('push', 30, 60); note_attempt('push');
$host = strtolower((string)($in['host'] ?? ''));
if (!isset(site_pages()[$host])) out(422, ['error' => 'Notifications are only available for the sites we list.']);
$sub = is_array($in['sub'] ?? null) ? $in['sub'] : [];
$endpoint = (string)($sub['endpoint'] ?? '');
if (!push_endpoint_ok($endpoint)) out(422, ['error' => 'That browser address is not supported.']);
$hash = hash('sha256', $endpoint . '|' . $host);
$act = (string)($in['act'] ?? 'sub');
if ($act === 'unsub') { $pdo->prepare('DELETE FROM push_subs WHERE hash=?')->execute([$hash]); out(200, ['ok' => true]); }
if ($act === 'has') { $q = $pdo->prepare('SELECT 1 FROM push_subs WHERE hash=?'); $q->execute([$hash]); out(200, ['on' => (bool)$q->fetchColumn()]); }
$p256 = (string)($sub['keys']['p256dh'] ?? ''); $auth = (string)($sub['keys']['auth'] ?? '');
if (strlen(b64u_d($auth)) !== 16 || !push_pub_from_raw(b64u_d($p256))) out(422, ['error' => 'That browser address is not valid.']);
$n = $pdo->prepare('SELECT COUNT(*) FROM push_subs WHERE host=?'); $n->execute([$host]);
if ((int)$n->fetchColumn() >= 5000) out(409, ['error' => 'This site has reached the limit for notifications.']);
$pdo->prepare('REPLACE INTO push_subs (hash, endpoint, p256dh, auth, host, created) VALUES (?,?,?,?,?,?)')->execute([$hash, $endpoint, $p256, $auth, $host, gmdate('Y-m-d H:i:s')]);
out(200, ['ok' => true]);
