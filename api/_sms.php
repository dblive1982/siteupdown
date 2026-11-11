<?php
// Text messages and phone calls through Twilio. Switched on only when twilio_sid, twilio_token and twilio_from are in sud-config.php.
declare(strict_types=1);

function twilio_cfg(): array {
    $c = config() ?: [];
    $from = (string)($c['twilio_from'] ?? '');
    return ['sid' => (string)($c['twilio_sid'] ?? ''), 'token' => (string)($c['twilio_token'] ?? ''), 'from' => $from, 'sms_from' => (string)($c['twilio_sms_from'] ?? $from)];
}
function twilio_on(): bool { $t = twilio_cfg(); return $t['sid'] !== '' && $t['token'] !== '' && $t['from'] !== ''; }

/** Normalise to E.164. Accepts +44 7700 900123, 0044..., and UK mobiles written 07700 900123. Returns null if it does not look like a real number. */
function phone_e164(string $raw): ?string {
    $s = preg_replace('/[\s().-]+/', '', trim($raw));
    if ($s === null || $s === '') return null;
    if (strncmp($s, '00', 2) === 0) $s = '+' . substr($s, 2);
    if (preg_match('/^07\d{9}$/', $s)) $s = '+44' . substr($s, 1);
    return preg_match('/^\+[1-9]\d{7,14}$/', $s) ? $s : null;
}

function twilio_post(string $path, array $fields): int {
    $t = twilio_cfg();
    $ch = curl_init('https://api.twilio.com/2010-04-01/Accounts/' . rawurlencode($t['sid']) . '/' . $path);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query($fields), CURLOPT_RETURNTRANSFER => true, CURLOPT_USERPWD => $t['sid'] . ':' . $t['token'],
        CURLOPT_TIMEOUT => 8, CURLOPT_CONNECTTIMEOUT => 4, CURLOPT_FOLLOWLOCATION => false, CURLOPT_PROTOCOLS => CURLPROTO_HTTPS]);
    curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    return $code;
}
/** Plain text only (no emoji: they force a shorter, costlier message). True if Twilio accepted it. */
function sms_send(string $to, string $body): bool {
    if (!twilio_on()) return false;
    $body = trim(preg_replace('/[^\x20-\x7E\n]/u', '', $body) ?? '');
    return twilio_post('Messages.json', ['To' => $to, 'From' => twilio_cfg()['sms_from'], 'Body' => mb_substr($body, 0, 300)]) === 201;
}
/** A short spoken call. */
function call_send(string $to, string $say): bool {
    if (!twilio_on()) return false;
    $say = htmlspecialchars(trim(preg_replace('/[^\x20-\x7E]/u', '', $say) ?? ''), ENT_XML1 | ENT_QUOTES, 'UTF-8');
    $twiml = '<Response><Pause length="1"/><Say voice="alice" language="en-GB">' . $say . '</Say><Pause length="1"/><Say voice="alice" language="en-GB">' . $say . '</Say></Response>';
    return twilio_post('Calls.json', ['To' => $to, 'From' => twilio_cfg()['from'], 'Twiml' => $twiml]) === 201;
}

/** Alert a Pro user's verified phone. $event is 'down' or 'up'. Calls ring only for outages. Respects the monthly caps. */
function phone_alert(PDO $pdo, int $uid, string $event, string $host): void {
    if (!twilio_on() || !in_array($event, ['down', 'up'], true)) return;
    require_once __DIR__ . '/_plan.php';
    if (!is_pro($pdo, $uid)) return;
    $s = $pdo->prepare('SELECT number, sms_on, call_on FROM phones WHERE user_id=? AND verified=1');
    $s->execute([$uid]);
    $p = $s->fetch();
    if (!$p) return;
    $u = phone_usage($pdo, $uid);
    $safe = preg_replace('/[^a-z0-9.-]/i', '', $host);
    if ((int)$p['sms_on'] === 1 && $u['sms'] < PRO_SMS_MONTH) {
        $msg = $event === 'down' ? "siteupdown: $safe looks down. We could not reach it on two checks in a row." : "siteupdown: $safe is back up.";
        if (sms_send($p['number'], $msg)) phone_usage_add($pdo, $uid, 'sms');
    }
    if ($event === 'down' && (int)$p['call_on'] === 1 && $u['calls'] < PRO_CALL_MONTH) {
        if (call_send($p['number'], "This is siteupdown dot com. $safe looks down. We could not reach it on two checks in a row.")) phone_usage_add($pdo, $uid, 'calls');
    }
}
