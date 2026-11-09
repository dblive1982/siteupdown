<?php
require __DIR__ . '/_boot.php';
$c = config();
if (!$c) out(200, ['user' => null, 'enabled' => false]);
start_session();
ensure_twofa();
$user = null;
if (!empty($_SESSION['uid'])) {
    $s = db()->prepare('SELECT name, email, pass_hash, created_at, twofa FROM users WHERE id=?');
    $s->execute([$_SESSION['uid']]);
    $r = $s->fetch();
    if ($r) { $user = public_user($r); $user['pw'] = !empty($r['pass_hash']); $user['twofa'] = !empty($r['twofa']); $user['since'] = substr((string)$r['created_at'], 0, 10); } else unset($_SESSION['uid']);
}
out(200, ['user' => $user, 'enabled' => true, 'google' => !empty($c['google_client_id']), 'google_id' => $c['google_client_id'] ?? '', 'turnstile' => turnstile_on() ? $c['turnstile_site'] : '']);
