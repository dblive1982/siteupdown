<?php
// POST {action: name|password|clear|delete, ...} for the signed-in user.
require __DIR__ . '/_boot.php';
$in = read_post();
$uid = require_user();
$pdo = db();
$a = (string)($in['action'] ?? '');
$s = $pdo->prepare('SELECT id, name, email, pass_hash FROM users WHERE id=?');
$s->execute([$uid]);
$u = $s->fetch();
if (!$u) out(404, ['error' => 'Account not found.']);

function end_session(): void {
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 3600, $p['path'], $p['domain'], true, true);
    }
    session_destroy();
}
function check_pw(array $u, array $in): void {
    if (!empty($u['pass_hash']) && !password_verify((string)($in['password'] ?? ''), $u['pass_hash'])) {
        note_attempt('acct');
        out(401, ['error' => 'That password is not right.']);
    }
}

switch ($a) {
    case 'name':
        $n = trim((string)($in['name'] ?? ''));
        if ($n === '' || mb_strlen($n) > 60) out(422, ['error' => 'Please enter a display name (up to 60 characters).']);
        $pdo->prepare('UPDATE users SET name=? WHERE id=?')->execute([$n, $uid]);
        out(200, ['user' => ['name' => $n, 'email' => $u['email']]]);

    case 'password':
        throttle('acct', 8, 15);
        check_pw($u, $in);
        $new = (string)($in['new'] ?? '');
        if (strlen($new) < 8 || strlen($new) > 200) out(422, ['error' => 'Your new password needs at least 8 characters.']);
        $pdo->prepare('UPDATE users SET pass_hash=? WHERE id=?')->execute([password_hash($new, PASSWORD_DEFAULT), $uid]);
        out(200, ['ok' => true]);

    case 'clear': // reset data: history and watchlist, keeps the account
        throttle('acct', 8, 15);
        $pdo->prepare('DELETE FROM saved_checks WHERE user_id=?')->execute([$uid]);
        $pdo->prepare('DELETE FROM watchlist WHERE user_id=?')->execute([$uid]);
        $pdo->prepare('DELETE FROM alert_channels WHERE user_id=?')->execute([$uid]);
        out(200, ['ok' => true]);

    case 'delete':
        throttle('acct', 6, 15);
        if (($in['confirm'] ?? '') !== 'DELETE') out(422, ['error' => 'Type DELETE to confirm.']);
        check_pw($u, $in);
        $pdo->beginTransaction();
        foreach (['resets', 'saved_checks', 'watchlist', 'alert_channels', 'tg_links'] as $t) $pdo->prepare("DELETE FROM $t WHERE user_id=?")->execute([$uid]);
        $pdo->prepare('DELETE FROM users WHERE id=?')->execute([$uid]);
        $pdo->commit();
        end_session();
        out(200, ['ok' => true]);

    default:
        out(400, ['error' => 'Bad request.']);
}
