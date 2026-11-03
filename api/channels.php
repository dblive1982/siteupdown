<?php
// Signed-in users only. GET -> my alert channels + what is available. POST {action: tg_link|add_webhook|test|remove}.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_notify.php';
$uid = require_user();
$pdo = db();
const MAX_CHANNELS = 5;
$tg = tg_config();
$can = ['telegram' => $tg['token'] !== '' && $tg['bot'] !== ''];

function my_channels(PDO $pdo, int $uid): array {
    $q = $pdo->prepare('SELECT id, kind, label FROM alert_channels WHERE user_id=? ORDER BY id');
    $q->execute([$uid]);
    return array_map(fn($r) => ['id' => (int)$r['id'], 'kind' => $r['kind'], 'label' => $r['label']], $q->fetchAll());
}
function reply(PDO $pdo, int $uid, array $can, array $extra = []): void { out(200, array_merge(['items' => my_channels($pdo, $uid), 'can' => $can, 'max' => MAX_CHANNELS], $extra)); }

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') reply($pdo, $uid, $can);
$in = read_post();
$a = (string)($in['action'] ?? '');

if ($a === 'tg_link') {
    if (!$can['telegram']) out(422, ['error' => 'Telegram alerts are not switched on yet.']);
    if (count(my_channels($pdo, $uid)) >= MAX_CHANNELS) out(422, ['error' => 'You have reached the limit of ' . MAX_CHANNELS . ' alert channels.']);
    throttle('chan', 20, 60); note_attempt('chan');
    $pdo->prepare('DELETE FROM tg_links WHERE expires_at < ?')->execute([sql_now()]);
    $tok = bin2hex(random_bytes(16));
    $pdo->prepare('INSERT INTO tg_links (token_hash, user_id, expires_at) VALUES (?,?,?)')->execute([hash('sha256', $tok), $uid, gmdate('Y-m-d H:i:s', time() + 900)]);
    reply($pdo, $uid, $can, ['link' => 'https://t.me/' . $tg['bot'] . '?start=' . $tok]);
}
if ($a === 'add_webhook') {
    throttle('chan', 20, 60); note_attempt('chan');
    $url = trim((string)($in['url'] ?? ''));
    $kind = webhook_kind($url);
    if ($kind === null) out(422, ['error' => 'That does not look like a Slack or Discord webhook address. Slack addresses start with https://hooks.slack.com/services/ and Discord ones with https://discord.com/api/webhooks/.']);
    if (count(my_channels($pdo, $uid)) >= MAX_CHANNELS) out(422, ['error' => 'You have reached the limit of ' . MAX_CHANNELS . ' alert channels.']);
    $dup = $pdo->prepare('SELECT 1 FROM alert_channels WHERE user_id=? AND target=?');
    $dup->execute([$uid, $url]);
    if ($dup->fetch()) out(422, ['error' => 'That webhook is already connected.']);
    $ch = ['kind' => $kind, 'target' => $url];
    if (!push_channel($ch, "\u{2705} siteupdown.com alerts are connected. You will get a message here when a site on your watchlist goes down or comes back up.")) out(422, ['error' => 'We could not send a test message to that webhook. Check the address and try again.']);
    $pdo->prepare('INSERT INTO alert_channels (user_id, kind, target, label, created_at) VALUES (?,?,?,?,?)')->execute([$uid, $kind, $url, $kind === 'slack' ? 'Slack' : 'Discord', sql_now()]);
    reply($pdo, $uid, $can);
}
if ($a === 'test' || $a === 'remove') {
    $id = (int)($in['id'] ?? 0);
    $q = $pdo->prepare('SELECT id, kind, target FROM alert_channels WHERE id=? AND user_id=?');
    $q->execute([$id, $uid]);
    $ch = $q->fetch();
    if (!$ch) out(404, ['error' => 'That channel was not found.']);
    if ($a === 'remove') { $pdo->prepare('DELETE FROM alert_channels WHERE id=?')->execute([$id]); reply($pdo, $uid, $can); }
    throttle('chan', 20, 60); note_attempt('chan');
    if (!push_channel($ch, "\u{1F514} Test message from siteupdown.com. Alerts to this channel are working.")) { $pdo->prepare('DELETE FROM alert_channels WHERE id=?')->execute([$id]); out(422, ['error' => 'That channel no longer works, so we removed it. Please connect it again.']); }
    reply($pdo, $uid, $can, ['sent' => true]);
}
out(400, ['error' => 'Bad request.']);
