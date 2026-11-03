<?php
// Signed-in users only. GET -> my alert channels + what is available. POST {action: tg_link|add_webhook|test|remove}.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_notify.php';
require __DIR__ . '/_msg.php';
$uid = require_user();
$pdo = db();
const MAX_CHANNELS = 5;
$tg = tg_config();
$can = ['telegram' => $tg['token'] !== '' && $tg['bot'] !== ''] + msg_can();

function my_channels(PDO $pdo, int $uid): array {
    $q = $pdo->prepare('SELECT id, kind, label FROM alert_channels WHERE user_id=? ORDER BY id');
    $q->execute([$uid]);
    return array_map(fn($r) => ['id' => (int)$r['id'], 'kind' => $r['kind'], 'label' => $r['label']], $q->fetchAll());
}
function plan_info(PDO $pdo, int $uid): array {
    $m = msg_cfg();
    $q = $pdo->prepare('SELECT status, period_end FROM subscriptions WHERE user_id=?'); $q->execute([$uid]);
    $r = $q->fetch() ?: [];
    $pv = $pdo->prepare('SELECT kind, number FROM phone_verify WHERE user_id=? AND expires_at >= ?'); $pv->execute([$uid, sql_now()]);
    return ['pro' => is_pro($pdo, $uid), 'price' => $m['price'], 'status' => $r['status'] ?? null, 'ends' => iso($r['period_end'] ?? null),
        'usage' => ['sms' => ['used' => usage_used($pdo, $uid, 'sms'), 'cap' => $m['sms_cap']], 'whatsapp' => ['used' => usage_used($pdo, $uid, 'whatsapp'), 'cap' => $m['wa_cap']]],
        'pending' => array_map(fn($x) => ['kind' => $x['kind'], 'number' => phone_mask($x['number'])], $pv->fetchAll())];
}
function reply(PDO $pdo, int $uid, array $can, array $extra = []): void { out(200, array_merge(['items' => my_channels($pdo, $uid), 'can' => $can, 'max' => MAX_CHANNELS, 'plan' => plan_info($pdo, $uid)], $extra)); }

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
if ($a === 'phone_start') {
    $kind = (string)($in['kind'] ?? '');
    if (!in_array($kind, ['sms', 'whatsapp'], true) || empty($can[$kind]) || empty($can['sms'])) out(422, ['error' => 'That channel is not switched on yet.']);
    if (!is_pro($pdo, $uid)) out(402, ['error' => 'SMS and WhatsApp alerts are part of the Pro plan.']);
    $num = phone_norm((string)($in['number'] ?? ''));
    if ($num === null) out(422, ['error' => 'Please enter a full mobile number, for example 07700 900123 or +44 7700 900123.']);
    if (!phone_allowed($num)) out(422, ['error' => 'We can only send to numbers in these countries for now: +' . implode(', +', msg_cfg()['cc']) . '.']);
    if (count(my_channels($pdo, $uid)) >= MAX_CHANNELS) out(422, ['error' => 'You have reached the limit of ' . MAX_CHANNELS . ' alert channels.']);
    $dup = $pdo->prepare('SELECT 1 FROM alert_channels WHERE user_id=? AND kind=? AND target=?'); $dup->execute([$uid, $kind, $num]);
    if ($dup->fetch()) out(422, ['error' => 'That number is already connected.']);
    throttle('phone', 6, 60);
    // per-account limit as well, so one account cannot burn through our message budget from many addresses
    $uh = hash('sha256', 'u' . $uid . '|sud');
    $c = $pdo->prepare('SELECT COUNT(*) FROM attempts WHERE ip_hash=? AND kind=? AND ts > ?'); $c->execute([$uh, 'phoneu', gmdate('Y-m-d H:i:s', time() - 86400)]);
    if ((int)$c->fetchColumn() >= 8) out(429, ['error' => 'You have asked for a lot of codes today. Please try again tomorrow.']);
    $last = $pdo->prepare('SELECT sent_at FROM phone_verify WHERE user_id=? AND kind=?'); $last->execute([$uid, $kind]);
    $ls = $last->fetchColumn();
    if ($ls && strtotime($ls . ' UTC') > time() - 45) out(429, ['error' => 'Please wait a moment before asking for another code.']);
    note_attempt('phone');
    $pdo->prepare('INSERT INTO attempts (ip_hash, kind, ts) VALUES (?,?,?)')->execute([$uh, 'phoneu', sql_now()]);
    $code = (string)random_int(100000, 999999);
    [$ok] = tw_send('sms', $num, "siteupdown.com code: $code. It expires in 10 minutes. If you did not ask for this, ignore it.");
    if (!$ok) out(422, ['error' => 'We could not send a code to that number. Check it and try again.']);
    $pdo->prepare('DELETE FROM phone_verify WHERE user_id=? AND kind=?')->execute([$uid, $kind]);
    $pdo->prepare('INSERT INTO phone_verify (user_id, kind, number, code_hash, expires_at, tries, sent_at) VALUES (?,?,?,?,?,0,?)')
        ->execute([$uid, $kind, $num, hash('sha256', $code . '|' . $num . '|' . $uid), gmdate('Y-m-d H:i:s', time() + 600), sql_now()]);
    reply($pdo, $uid, $can, ['sent_to' => phone_mask($num)]);
}
if ($a === 'phone_verify') {
    $kind = (string)($in['kind'] ?? '');
    if (!in_array($kind, ['sms', 'whatsapp'], true)) out(400, ['error' => 'Bad request.']);
    if (!is_pro($pdo, $uid)) out(402, ['error' => 'SMS and WhatsApp alerts are part of the Pro plan.']);
    $q = $pdo->prepare('SELECT number, code_hash, expires_at, tries FROM phone_verify WHERE user_id=? AND kind=?'); $q->execute([$uid, $kind]);
    $r = $q->fetch();
    if (!$r || $r['expires_at'] < sql_now()) out(422, ['error' => 'That code has expired. Please ask for a new one.']);
    if ((int)$r['tries'] >= 5) out(422, ['error' => 'Too many wrong codes. Please ask for a new one.']);
    $code = preg_replace('~\D+~', '', (string)($in['code'] ?? ''));
    if (!hash_equals($r['code_hash'], hash('sha256', $code . '|' . $r['number'] . '|' . $uid))) {
        $pdo->prepare('UPDATE phone_verify SET tries = tries + 1 WHERE user_id=? AND kind=?')->execute([$uid, $kind]);
        out(422, ['error' => 'That code is not right. Please check it and try again.']);
    }
    if (count(my_channels($pdo, $uid)) >= MAX_CHANNELS) out(422, ['error' => 'You have reached the limit of ' . MAX_CHANNELS . ' alert channels.']);
    $pdo->prepare('DELETE FROM phone_verify WHERE user_id=? AND kind=?')->execute([$uid, $kind]);
    $label = ($kind === 'sms' ? 'SMS ' : 'WhatsApp ') . phone_mask($r['number']);
    $pdo->prepare('INSERT INTO alert_channels (user_id, kind, target, label, created_at) VALUES (?,?,?,?,?)')->execute([$uid, $kind, $r['number'], $label, sql_now()]);
    push_channel(['user_id' => $uid, 'kind' => $kind, 'target' => $r['number']], 'Connected. You will get a message here when a site on your watchlist goes down or comes back up. Manage alerts at siteupdown.com/monitor');
    reply($pdo, $uid, $can);
}
if ($a === 'test' || $a === 'remove') {
    $id = (int)($in['id'] ?? 0);
    $q = $pdo->prepare('SELECT id, user_id, kind, target FROM alert_channels WHERE id=? AND user_id=?');
    $q->execute([$id, $uid]);
    $ch = $q->fetch();
    if (!$ch) out(404, ['error' => 'That channel was not found.']);
    if ($a === 'remove') { $pdo->prepare('DELETE FROM alert_channels WHERE id=?')->execute([$id]); reply($pdo, $uid, $can); }
    throttle('chan', 20, 60); note_attempt('chan');
    if (in_array($ch['kind'], ['sms', 'whatsapp'], true)) {
        if (!is_pro($pdo, $uid)) out(402, ['error' => 'SMS and WhatsApp alerts are part of the Pro plan.']);
        if (usage_used($pdo, $uid, $ch['kind']) >= usage_cap($ch['kind'])) out(422, ['error' => 'You have used this month\'s messages for that channel.']);
    }
    if (!push_channel($ch, "\u{1F514} Test message from siteupdown.com. Alerts to this channel are working.")) { $pdo->prepare('DELETE FROM alert_channels WHERE id=?')->execute([$id]); out(422, ['error' => 'That channel no longer works, so we removed it. Please connect it again.']); }
    reply($pdo, $uid, $can, ['sent' => true]);
}
out(400, ['error' => 'Bad request.']);
