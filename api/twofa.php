<?php
// Two-step sign-in: finish a sign-in (verify), or turn it on/off for the signed-in account (send, then confirm).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_twofa.php';
$in = read_post();
start_session();
ensure_twofa();
$pdo = db();
$act = (string)($in['action'] ?? '');
$code = (string)($in['code'] ?? '');
if ($act === 'verify') {
    throttle('tfver', 20, 30);
    $t = twofa_check($code, 'login');
    $s = $pdo->prepare('SELECT id, name, email FROM users WHERE id=?'); $s->execute([$t['uid']]); $u = $s->fetch();
    if (!$u) out(401, ['error' => 'Please sign in again.']);
    $pdo->prepare('UPDATE users SET last_login=? WHERE id=?')->execute([sql_now(), $u['id']]);
    session_regenerate_id(true);
    $_SESSION['uid'] = (int)$u['id'];
    out(200, ['user' => public_user($u)]);
}
$uid = require_user();
$s = $pdo->prepare('SELECT name, email, twofa FROM users WHERE id=?'); $s->execute([$uid]); $u = $s->fetch();
if (!$u) out(401, ['error' => 'Please sign in again.']);
if ($act === 'send') {
    $mode = !empty($u['twofa']) ? 'off' : 'on';
    twofa_send($uid, $u['email'], $u['name'], $mode);
    out(200, ['sent' => true, 'mode' => $mode]);
}
if ($act === 'confirm') {
    throttle('tfver', 20, 30);
    $mode = !empty($u['twofa']) ? 'off' : 'on';
    twofa_check($code, $mode);
    $pdo->prepare('UPDATE users SET twofa=? WHERE id=?')->execute([$mode === 'on' ? 1 : 0, $uid]);
    out(200, ['twofa' => $mode === 'on']);
}
out(422, ['error' => 'Unknown action.']);
