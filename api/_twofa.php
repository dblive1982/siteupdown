<?php
// Email-code second step. The code is kept only as a keyed hash in the visitor's own session; it lasts 10 minutes and allows 5 tries.
require_once __DIR__ . '/_mail.php';
function twofa_send(int $uid, string $email, string $name, string $mode): void {
    throttle('tfsend', 6, 30);
    note_attempt('tfsend');
    $code = str_pad((string)random_int(0, 999999), 6, '0', STR_PAD_LEFT);
    $_SESSION['tf'] = ['uid' => $uid, 'mode' => $mode, 'h' => hash_hmac('sha256', $code, session_id()), 'exp' => time() + 600, 'tries' => 0];
    $why = $mode === 'login' ? 'Use this code to finish signing in.' : 'Use this code to confirm the change to your two-step sign-in.';
    sud_email($email, 'Your siteupdown.com code: ' . $code, 'Your sign-in code',
        '<p style="margin:0 0 12px">Hi ' . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . ', ' . $why . '</p><p style="margin:0 0 12px;font-size:28px;font-weight:800;letter-spacing:6px">' . $code . '</p><p style="margin:0">It works for 10 minutes. If this was not you, someone knows your password: please change it.</p>',
        "Hi $name, $why\n\nYour code: $code\n\nIt works for 10 minutes. If this was not you, someone knows your password: please change it.");
}
// Returns the stored record when the code is right, otherwise ends the request with an error.
function twofa_check(string $code, string $mode): array {
    $t = $_SESSION['tf'] ?? null;
    if (!$t || $t['mode'] !== $mode || $t['exp'] < time()) out(401, ['error' => 'That code has expired. Please start again.']);
    if ($t['tries'] >= 5) { unset($_SESSION['tf']); out(429, ['error' => 'Too many wrong codes. Please start again.']); }
    $_SESSION['tf']['tries']++;
    if (!hash_equals($t['h'], hash_hmac('sha256', preg_replace('/\D/', '', $code), session_id()))) { note_attempt('tfbad'); out(401, ['error' => 'That code is not right. Check the email and try again.']); }
    unset($_SESSION['tf']);
    return $t;
}
