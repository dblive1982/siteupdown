<?php
// Telegram bot webhook: a user taps our link, Telegram sends "/start <token>" here, and we connect that chat to their account.
// One-time setup (after the bot token is in the config): open /api/telegram.php?setup=1&key=<cron_key> once.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_notify.php';
$tg = tg_config();
$cfg = config() ?: [];
if ($tg['token'] === '') out(404, ['error' => 'Not configured.']);

$cliSetup = PHP_SAPI === 'cli' && (($argv[1] ?? '') === 'setup');
if ($cliSetup || isset($_GET['setup'])) {
    if (!$cliSetup && (empty($cfg['cron_key']) || !hash_equals((string)$cfg['cron_key'], (string)($_GET['key'] ?? '')))) out(403, ['error' => 'Forbidden.']);
    $site = rtrim((string)($cfg['site'] ?? 'https://siteupdown.com'), '/');
    $code = notify_post('https://api.telegram.org/bot' . $tg['token'] . '/setWebhook', ['url' => $site . '/api/telegram.php', 'secret_token' => $tg['secret'], 'allowed_updates' => ['message']]);
    out(200, ['webhook_set' => $code === 200, 'http' => $code]);
}

// Only Telegram knows the secret it was given when the webhook was set.
if ($tg['secret'] === '' || !hash_equals($tg['secret'], (string)($_SERVER['HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN'] ?? ''))) out(403, ['error' => 'Forbidden.']);
$u = json_decode((string)file_get_contents('php://input'), true);
$m = is_array($u) ? ($u['message'] ?? null) : null;
if (!is_array($m) || empty($m['chat']['id']) || ($m['chat']['type'] ?? '') !== 'private') out(200, ['ok' => true]);
$chat = (string)$m['chat']['id'];
$text = trim((string)($m['text'] ?? ''));
$say = fn(string $t) => notify_post('https://api.telegram.org/bot' . $tg['token'] . '/sendMessage', ['chat_id' => $chat, 'text' => $t, 'disable_web_page_preview' => true]);
$pdo = db();

if (preg_match('~^/start(?:@\w+)?\s+([a-f0-9]{32})$~i', $text, $mm)) {
    $pdo->prepare('DELETE FROM tg_links WHERE expires_at < ?')->execute([sql_now()]);
    $q = $pdo->prepare('SELECT user_id FROM tg_links WHERE token_hash=? AND expires_at >= ?');
    $q->execute([hash('sha256', strtolower($mm[1])), sql_now()]);
    $row = $q->fetch();
    if (!$row) { $say('That link has expired. Please go back to siteupdown.com/monitor and tap Connect Telegram again.'); out(200, ['ok' => true]); }
    $uid = (int)$row['user_id'];
    $pdo->prepare('DELETE FROM tg_links WHERE token_hash=?')->execute([hash('sha256', strtolower($mm[1]))]);
    $n = $pdo->prepare('SELECT COUNT(*) FROM alert_channels WHERE user_id=?'); $n->execute([$uid]);
    $e = $pdo->prepare('SELECT 1 FROM alert_channels WHERE user_id=? AND kind=? AND target=?'); $e->execute([$uid, 'telegram', $chat]);
    if (!$e->fetch() && (int)$n->fetchColumn() < 5) {
        $label = 'Telegram' . (!empty($m['from']['first_name']) ? ' (' . mb_substr((string)$m['from']['first_name'], 0, 30) . ')' : '');
        $pdo->prepare('INSERT INTO alert_channels (user_id, kind, target, label, created_at) VALUES (?,?,?,?,?)')->execute([$uid, 'telegram', $chat, $label, sql_now()]);
    }
    $say("\u{2705} Connected. You will get a message here when a site on your siteupdown.com watchlist goes down or comes back up. Send /stop at any time to disconnect.");
} elseif (preg_match('~^/stop(?:@\w+)?$~i', $text)) {
    $pdo->prepare('DELETE FROM alert_channels WHERE kind=? AND target=?')->execute(['telegram', $chat]);
    $say('Disconnected. You will no longer get siteupdown.com alerts here.');
} else {
    $say('This bot sends siteupdown.com alerts. To connect it, open siteupdown.com/monitor, sign in and tap Connect Telegram. Send /stop to disconnect.');
}
out(200, ['ok' => true]);
