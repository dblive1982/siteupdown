<?php
// Pro only. GET -> my phone alert settings. POST {action: add|verify|prefs|remove|test}.
// A number is only used after the owner types back a 6-digit code we text to it.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_plan.php';
require __DIR__ . '/_sms.php';
$pdo = db();
ensure_billing($pdo);
$uid = require_user();

function mine(PDO $pdo, int $uid): array {
    $s = $pdo->prepare('SELECT number, verified, sms_on, call_on FROM phones WHERE user_id=?'); $s->execute([$uid]); $p = $s->fetch();
    $u = phone_usage($pdo, $uid);
    $mask = fn($n) => substr($n, 0, 3) . str_repeat('*', max(0, strlen($n) - 6)) . substr($n, -3);
    return ['pro' => is_pro($pdo, $uid), 'ready' => twilio_on(),
        'phone' => $p ? ['number' => $mask($p['number']), 'verified' => (int)$p['verified'] === 1, 'sms' => (int)$p['sms_on'] === 1, 'call' => (int)$p['call_on'] === 1] : null,
        'used' => $u, 'caps' => ['sms' => PRO_SMS_MONTH, 'calls' => PRO_CALL_MONTH]];
}
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') out(200, mine($pdo, $uid));

$in = read_post();
$a = (string)($in['action'] ?? '');
if ($a !== 'remove') pro_required($pdo, $uid, 'Text and phone alerts');
if (!twilio_on() && $a !== 'remove') out(503, ['error' => 'Text and phone alerts are not switched on yet. Please check back soon.', 'soon' => true]);

if ($a === 'add') {
    $n = phone_e164((string)($in['number'] ?? ''));
    if (!$n) out(422, ['error' => 'Please enter your mobile number with its country code, for example +44 7700 900123.']);
    throttle('phone', 6, 60); note_attempt('phone');
    $s = $pdo->prepare('SELECT sent_at FROM phones WHERE user_id=?'); $s->execute([$uid]); $old = $s->fetch();
    if ($old && time() - (int)$old['sent_at'] < 60) out(429, ['error' => 'Please wait a minute before asking for another code.']);
    $code = (string)random_int(100000, 999999);
    $pdo->prepare('DELETE FROM phones WHERE user_id=?')->execute([$uid]);
    $pdo->prepare('INSERT INTO phones (user_id, number, verified, code_hash, code_exp, tries, sent_at) VALUES (?,?,0,?,?,0,?)')->execute([$uid, $n, hash('sha256', $code . '|' . $uid), time() + 600, time()]);
    if (!sms_send($n, "siteupdown.com code: $code. It expires in 10 minutes. If you did not ask for this, ignore it.")) {
        $pdo->prepare('DELETE FROM phones WHERE user_id=?')->execute([$uid]);      // nothing was sent, so let them try again straight away
        out(502, ['error' => 'We could not send the text. Check the number and try again.']);
    }
    out(200, mine($pdo, $uid) + ['sent' => true]);
}
if ($a === 'verify') {
    $s = $pdo->prepare('SELECT code_hash, code_exp, tries FROM phones WHERE user_id=? AND verified=0'); $s->execute([$uid]); $p = $s->fetch();
    if (!$p) out(404, ['error' => 'Add your number first.']);
    if ((int)$p['tries'] >= 5 || (int)$p['code_exp'] < time()) out(410, ['error' => 'That code has expired. Please ask for a new one.']);
    $pdo->prepare('UPDATE phones SET tries = tries + 1 WHERE user_id=?')->execute([$uid]);
    if (!hash_equals((string)$p['code_hash'], hash('sha256', preg_replace('/\D/', '', (string)($in['code'] ?? '')) . '|' . $uid))) out(422, ['error' => 'That code is not right. Please check it and try again.']);
    $pdo->prepare('UPDATE phones SET verified=1, code_hash=NULL, tries=0 WHERE user_id=?')->execute([$uid]);
    out(200, mine($pdo, $uid));
}
if ($a === 'prefs') {
    $pdo->prepare('UPDATE phones SET sms_on=?, call_on=? WHERE user_id=? AND verified=1')->execute([!empty($in['sms']) ? 1 : 0, !empty($in['call']) ? 1 : 0, $uid]);
    out(200, mine($pdo, $uid));
}
if ($a === 'remove') {
    $pdo->prepare('DELETE FROM phones WHERE user_id=?')->execute([$uid]);
    out(200, mine($pdo, $uid));
}
if ($a === 'test') {
    throttle('phonetest', 3, 60); note_attempt('phonetest');
    $s = $pdo->prepare('SELECT number FROM phones WHERE user_id=? AND verified=1'); $s->execute([$uid]); $p = $s->fetch();
    if (!$p) out(404, ['error' => 'Add and verify your number first.']);
    if (phone_usage($pdo, $uid)['sms'] >= PRO_SMS_MONTH) out(429, ['error' => 'You have used this month\'s texts.']);
    if (!sms_send($p['number'], 'siteupdown.com test: your text alerts are working.')) out(502, ['error' => 'We could not send the test text.']);
    phone_usage_add($pdo, $uid, 'sms');
    out(200, mine($pdo, $uid) + ['sent' => true]);
}
out(400, ['error' => 'Bad request.']);
