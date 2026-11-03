<?php
// Sends a short alert message to a user's connected channels (Telegram, Slack, Discord).
// Webhook addresses are limited to the official Slack and Discord hosts, so a visitor can never make us call another server.
declare(strict_types=1);

function webhook_kind(string $url): ?string {
    $p = parse_url($url);
    if (!$p || ($p['scheme'] ?? '') !== 'https' || isset($p['user']) || isset($p['pass']) || isset($p['port']) || empty($p['host'])) return null;
    $h = strtolower($p['host']); $path = $p['path'] ?? '';
    if ($h === 'hooks.slack.com' && preg_match('~^/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+$~', $path)) return 'slack';
    if (in_array($h, ['discord.com', 'discordapp.com'], true) && preg_match('~^/api/webhooks/\d{5,25}/[A-Za-z0-9_-]{20,120}$~', $path)) return 'discord';
    return null;
}

function tg_config(): array {
    $c = config() ?: [];
    return ['token' => (string)($c['tg_token'] ?? ''), 'bot' => ltrim((string)($c['tg_bot'] ?? ''), '@'), 'secret' => (string)($c['tg_secret'] ?? '')];
}

/** POST a JSON body. Returns the HTTP status (0 if the request failed). */
function notify_post(string $url, array $body): int {
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'], CURLOPT_TIMEOUT => 5, CURLOPT_CONNECTTIMEOUT => 3, CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_PROTOCOLS => CURLPROTO_HTTPS, CURLOPT_USERAGENT => 'siteupdown.com alerts']);
    curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    return $code;
}

/** Send one message to one channel row. Returns false when the channel no longer works (blocked bot, deleted webhook). */
function push_channel(array $ch, string $text, string $link = ''): bool {
    if ($ch['kind'] === 'sms' || $ch['kind'] === 'whatsapp') { require_once __DIR__ . '/_msg.php'; return push_phone($ch, $text, $link); }
    if ($ch['kind'] === 'telegram') {
        $tg = tg_config();
        if ($tg['token'] === '') return true;
        $code = notify_post('https://api.telegram.org/bot' . $tg['token'] . '/sendMessage', ['chat_id' => $ch['target'], 'text' => $text . ($link !== '' ? "\n" . $link : ''), 'disable_web_page_preview' => true]);
        return !in_array($code, [400, 403, 404], true);
    }
    $kind = webhook_kind($ch['target']);
    if ($kind === null) return false;
    $msg = $text . ($link !== '' ? "\n" . $link : '');
    $code = notify_post($ch['target'], $kind === 'slack' ? ['text' => $msg] : ['content' => $msg]);
    return !in_array($code, [404, 410], true);
}

/** Send to every channel a user has connected; drop channels that report they are gone. */
function push_user(PDO $pdo, int $uid, string $text, string $link = ''): void {
    $q = $pdo->prepare('SELECT id, user_id, kind, target FROM alert_channels WHERE user_id=?');
    $q->execute([$uid]);
    foreach ($q->fetchAll() as $ch) {
        if (!push_channel($ch, $text, $link)) $pdo->prepare('DELETE FROM alert_channels WHERE id=?')->execute([$ch['id']]);
    }
}
