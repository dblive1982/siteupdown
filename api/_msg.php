<?php
// Paid alert channels: SMS and WhatsApp through Twilio, plus the Pro plan checks and monthly usage caps.
// All keys live in sud-config.php (above public_html). Nothing here runs unless they are filled in.
declare(strict_types=1);

function msg_cfg(): array {
    $c = config() ?: [];
    return [
        'sid' => (string)($c['tw_sid'] ?? ''), 'token' => (string)($c['tw_token'] ?? ''),
        'sms_from' => (string)($c['tw_sms_from'] ?? ''), 'wa_from' => (string)($c['tw_wa_from'] ?? ''), 'wa_tpl' => (string)($c['tw_wa_tpl'] ?? ''),
        'api' => rtrim((string)($c['tw_api'] ?? 'https://api.twilio.com'), '/'),
        'cc' => array_filter(array_map('trim', explode(',', (string)($c['msg_countries'] ?? '44,353')))),
        'sms_cap' => (int)($c['pro_sms_cap'] ?? 30), 'wa_cap' => (int)($c['pro_wa_cap'] ?? 200),
        'price' => (string)($c['pro_price'] ?? '£4.99/month'),
        'pro_emails' => array_map('strtolower', (array)($c['pro_emails'] ?? [])),
        'stripe_sk' => (string)($c['stripe_sk'] ?? ''), 'stripe_price' => (string)($c['stripe_price'] ?? ''), 'stripe_whsec' => (string)($c['stripe_whsec'] ?? ''),
        'stripe_api' => rtrim((string)($c['stripe_api'] ?? 'https://api.stripe.com'), '/'),
    ];
}
function msg_can(): array {
    $m = msg_cfg();
    $tw = $m['sid'] !== '' && $m['token'] !== '';
    return ['sms' => $tw && $m['sms_from'] !== '', 'whatsapp' => $tw && $m['wa_from'] !== '', 'billing' => $m['stripe_sk'] !== '' && $m['stripe_price'] !== ''];
}

/** '07700 900123' / '+44 7700 900123' -> '+447700900123', or null. UK numbers may start with 0. */
function phone_norm(string $raw): ?string {
    $s = preg_replace('~[\s().-]+~', '', trim($raw));
    if (preg_match('~^00(\d+)$~', $s, $m)) $s = '+' . $m[1];
    if (preg_match('~^0(7\d{9})$~', $s, $m)) $s = '+44' . $m[1];
    return preg_match('~^\+[1-9]\d{7,14}$~', $s) ? $s : null;
}
function phone_allowed(string $e164): bool {
    foreach (msg_cfg()['cc'] as $cc) if (str_starts_with($e164, '+' . $cc)) return true;
    return false;
}
function phone_mask(string $e164): string { return substr($e164, 0, 3) . str_repeat("\u{2022}", max(3, strlen($e164) - 6)) . substr($e164, -3); }

/** Active Pro plan (paid through Stripe), or listed in pro_emails for free. */
function is_pro(PDO $pdo, int $uid): bool {
    $m = msg_cfg();
    if ($m['pro_emails']) {
        $q = $pdo->prepare('SELECT email FROM users WHERE id=?'); $q->execute([$uid]);
        if (in_array(strtolower((string)$q->fetchColumn()), $m['pro_emails'], true)) return true;
    }
    $q = $pdo->prepare('SELECT status, period_end FROM subscriptions WHERE user_id=?'); $q->execute([$uid]);
    $r = $q->fetch();
    if (!$r) return false;
    if (in_array($r['status'], ['active', 'trialing'], true)) return true;
    return $r['status'] === 'canceled' && !empty($r['period_end']) && $r['period_end'] > sql_now(); // cancelled but paid until period end
}

function usage_used(PDO $pdo, int $uid, string $kind): int {
    $q = $pdo->prepare('SELECT n FROM msg_usage WHERE user_id=? AND ym=? AND kind=?'); $q->execute([$uid, gmdate('Y-m'), $kind]);
    return (int)$q->fetchColumn();
}
function usage_add(PDO $pdo, int $uid, string $kind): void {
    $sql = is_sqlite($pdo) ? 'INSERT INTO msg_usage (user_id, ym, kind, n) VALUES (?,?,?,1) ON CONFLICT(user_id, ym, kind) DO UPDATE SET n = n + 1'
                           : 'INSERT INTO msg_usage (user_id, ym, kind, n) VALUES (?,?,?,1) ON DUPLICATE KEY UPDATE n = n + 1';
    $pdo->prepare($sql)->execute([$uid, gmdate('Y-m'), $kind]);
}
function usage_cap(string $kind): int { $m = msg_cfg(); return $kind === 'sms' ? $m['sms_cap'] : $m['wa_cap']; }

/** One Twilio message. Returns [ok, twilioCode, gone]. "gone" = number can no longer receive messages (opted out, invalid). */
function tw_send(string $kind, string $to, string $body, ?string $tplVar = null, string $link = ''): array {
    $m = msg_cfg();
    $f = ['To' => ($kind === 'whatsapp' ? 'whatsapp:' : '') . $to];
    if ($kind === 'whatsapp') {
        $f['From'] = str_starts_with($m['wa_from'], 'whatsapp:') ? $m['wa_from'] : 'whatsapp:' . $m['wa_from'];
        if ($m['wa_tpl'] !== '' && $tplVar !== null) { $f['ContentSid'] = $m['wa_tpl']; $f['ContentVariables'] = json_encode(['1' => $tplVar, '2' => $link !== '' ? $link : 'https://siteupdown.com']); }
        else $f['Body'] = $body;
    } else { $f['From'] = $m['sms_from']; $f['Body'] = $body; }
    $ch = curl_init($m['api'] . '/2010-04-01/Accounts/' . rawurlencode($m['sid']) . '/Messages.json');
    $https = str_starts_with($m['api'], 'https://');
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query($f), CURLOPT_USERPWD => $m['sid'] . ':' . $m['token'], CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8, CURLOPT_CONNECTTIMEOUT => 4, CURLOPT_FOLLOWLOCATION => false, CURLOPT_USERAGENT => 'siteupdown.com alerts',
        CURLOPT_PROTOCOLS => $https ? CURLPROTO_HTTPS : (CURLPROTO_HTTP | CURLPROTO_HTTPS)]);
    $raw = curl_exec($ch);
    $http = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    $j = is_string($raw) ? json_decode($raw, true) : null;
    $code = is_array($j) ? (int)($j['code'] ?? 0) : 0;
    return [$http >= 200 && $http < 300, $code, in_array($code, [21610, 21211, 21614, 63024], true)];
}

/** Pro alert to one phone channel, respecting the plan and monthly cap. Returns false only when the number is gone. */
function push_phone(array $ch, string $text, string $link = '', bool $isTest = false): bool {
    $pdo = db(); $uid = (int)$ch['user_id']; $kind = $ch['kind'];
    if (!is_pro($pdo, $uid)) return true;                       // plan lapsed: keep the number, send nothing
    if (usage_used($pdo, $uid, $kind) >= usage_cap($kind)) return true; // monthly cap reached
    $plain = trim(preg_replace('~\s+~', ' ', preg_replace('~[^\x20-\x7E\x{00A3}]+~u', '', $text)));
    $body = $kind === 'sms' ? mb_substr('siteupdown.com: ' . $plain . ($link !== '' ? ' ' . $link : ''), 0, 300) : 'siteupdown.com alert: ' . $plain . ($link !== '' ? "\n" . $link : '');
    [$ok, , $gone] = tw_send($kind, $ch['target'], $body, $plain, $link);
    if ($ok) usage_add($pdo, $uid, $kind);
    return !$gone;
}
