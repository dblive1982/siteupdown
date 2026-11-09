<?php
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
$in = read_post();
$email = clean_email((string)($in['email'] ?? ''));
if (!valid_email($email)) out(422, ['error' => 'Please enter a valid email address.']);
turnstile_check($in);
throttle('forgot', 5, 60);
note_attempt('forgot');
$pdo = db();
$s = $pdo->prepare('SELECT id, name FROM users WHERE email=?');
$s->execute([$email]);
$u = $s->fetch();
if ($u) {
    $token = bin2hex(random_bytes(32));
    $pdo->prepare('INSERT INTO resets (user_id, token_hash, expires_at) VALUES (?,?,?)')
        ->execute([$u['id'], hash('sha256', $token), gmdate('Y-m-d H:i:s', time() + 3600)]);
    $site = rtrim(config()['site'] ?? 'https://siteupdown.com', '/');
    $link = $site . '/login?reset=' . $token;
    sud_email($email, 'Reset your siteupdown.com password', 'Choose a new password',
        '<p style="margin:0 0 12px">Hi ' . htmlspecialchars($u['name'], ENT_QUOTES, 'UTF-8') . ', tap the button to choose a new password. The link works for one hour.</p>'
        . '<p style="margin:0">If you did not ask for this, you can ignore this email and your password will stay the same.</p>',
        'Hi ' . $u['name'] . ", use this link to choose a new password. It works for one hour.\n\nIf you did not ask for this, you can ignore this email.",
        'Choose a new password', $link);
}
// Same answer whether or not the email has an account.
out(200, ['ok' => true]);
