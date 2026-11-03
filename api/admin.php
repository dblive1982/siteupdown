<?php
// Admin area API. Needs (1) a signed-in account whose email is in config 'admin_emails' and (2) a code emailed to that address.
// Everyone else gets a plain 404, so the area does not announce itself.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
$pdo = db();
$uid = current_uid();
$admins = array_map('clean_email', (array)(config()['admin_emails'] ?? ['dblive1982@gmail.com']));
$me = null;
if ($uid > 0) { $q = $pdo->prepare('SELECT id, name, email FROM users WHERE id=?'); $q->execute([$uid]); $me = $q->fetch() ?: null; }
$a = (string)($_GET['a'] ?? '');
$in = $_SERVER['REQUEST_METHOD'] === 'POST' ? read_post() : [];
if ($in && isset($in['a'])) $a = (string)$in['a'];

if (!$me) out(401, ['error' => 'Please sign in first.', 'signin' => true]);
if (!in_array(clean_email($me['email']), $admins, true)) { note_attempt('adm'); out(404, ['error' => 'Not found.']); }
throttle('admreq', 120, 10);

function admin_log(string $action, string $detail = ''): void {
    db()->prepare('INSERT INTO admin_log (ts, action, detail) VALUES (?,?,?)')->execute([sql_now(), $action, mb_substr($detail, 0, 255)]);
}
$unlocked = !empty($_SESSION['admin_until']) && $_SESSION['admin_until'] > time();

if ($a === 'status') out(200, ['admin' => true, 'unlocked' => $unlocked, 'name' => $me['name'], 'email' => $me['email']]);

if ($a === 'code') {                              // email a six-digit code to the admin address
    throttle('admcode', 5, 60);
    $code = (string)random_int(100000, 999999);
    $_SESSION['admin_code'] = ['h' => hash_hmac('sha256', $code, session_id()), 'exp' => time() + 600, 'tries' => 0];
    note_attempt('admcode');
    sud_email($me['email'], 'Your siteupdown.com admin code', 'Admin sign-in code',
        '<p style="margin:0 0 12px">Use this code to open the admin area. It works for 10 minutes.</p><p style="margin:0;font-size:34px;letter-spacing:8px;font-weight:700">' . $code . '</p><p style="margin:14px 0 0">If you did not ask for this, ignore this email and consider changing your password.</p>',
        "Use this code to open the admin area (valid for 10 minutes): $code\n\nIf you did not ask for this, ignore this email.", '', '', '', 'warn');
    out(200, ['ok' => true, 'message' => 'A code has been sent to ' . $me['email'] . '.']);
}
if ($a === 'verify') {
    throttle('admver', 8, 15);
    $c = $_SESSION['admin_code'] ?? null;
    note_attempt('admver');
    if (!$c || $c['exp'] < time() || $c['tries'] >= 5) { unset($_SESSION['admin_code']); out(422, ['error' => 'That code has expired. Please request a new one.']); }
    $_SESSION['admin_code']['tries']++;
    if (!hash_equals($c['h'], hash_hmac('sha256', trim((string)($in['code'] ?? '')), session_id()))) out(422, ['error' => 'That code is not right.']);
    unset($_SESSION['admin_code']);
    session_regenerate_id(true);
    $_SESSION['admin_until'] = time() + 7200;
    admin_log('unlock', 'admin area opened');
    out(200, ['ok' => true]);
}
if ($a === 'lock') { unset($_SESSION['admin_until']); out(200, ['ok' => true]); }
if (!$unlocked) out(403, ['error' => 'Please enter your code first.', 'locked' => true]);

$day = fn(int $ago) => gmdate('Y-m-d', time() - $ago * 86400);
function series(PDO $pdo, string $sql, array $args, int $days): array {      // [{d:'2026-11-03', n:5}, ...] oldest first, zero-filled
    $q = $pdo->prepare($sql); $q->execute($args);
    $m = []; foreach ($q->fetchAll() as $r) $m[$r['d']] = (int)$r['n'];
    $o = []; for ($i = $days - 1; $i >= 0; $i--) { $d = gmdate('Y-m-d', time() - $i * 86400); $o[] = ['d' => $d, 'n' => $m[$d] ?? 0]; }
    return $o;
}
$one = function (string $sql, array $args = []) use ($pdo) { $q = $pdo->prepare($sql); $q->execute($args); return (int)$q->fetchColumn(); };

if ($a === 'overview') {
    $t7 = gmdate('Y-m-d H:i:s', time() - 7 * 86400); $t30 = gmdate('Y-m-d H:i:s', time() - 30 * 86400); $t24 = gmdate('Y-m-d H:i:s', time() - 86400);
    $top = $pdo->prepare('SELECT host, COUNT(*) AS n FROM reports WHERE ts > ? GROUP BY host ORDER BY n DESC LIMIT 8'); $top->execute([$t7]);
    $ch = $pdo->query('SELECT kind, COUNT(*) AS n FROM alert_channels GROUP BY kind')->fetchAll();
    $topw = $pdo->query('SELECT host, COUNT(*) AS n FROM watchlist GROUP BY host ORDER BY n DESC LIMIT 8')->fetchAll();
    out(200, [
        'tiles' => [
            'users' => $one('SELECT COUNT(*) FROM users'),
            'new7' => $one('SELECT COUNT(*) FROM users WHERE created_at > ?', [$t7]),
            'active7' => $one('SELECT COUNT(*) FROM users WHERE last_login > ?', [$t7]),
            'watching' => $one('SELECT COUNT(*) FROM watchlist'),
            'hosts' => $one('SELECT COUNT(DISTINCT host) FROM watchlist'),
            'checks24' => $one('SELECT COUNT(*) FROM checks WHERE checked_at > ?', [$t24]),
            'reports24' => $one('SELECT COUNT(*) FROM reports WHERE ts > ?', [$t24]),
            'incidents7' => $one('SELECT COUNT(*) FROM incidents WHERE started_at > ?', [$t7]),
        ],
        'signups' => series($pdo, 'SELECT substr(created_at,1,10) AS d, COUNT(*) AS n FROM users WHERE created_at > ? GROUP BY substr(created_at,1,10)', [$t30], 30),
        'logins' => series($pdo, 'SELECT substr(last_login,1,10) AS d, COUNT(*) AS n FROM users WHERE last_login > ? GROUP BY substr(last_login,1,10)', [$t30], 30),
        'checks' => series($pdo, 'SELECT substr(checked_at,1,10) AS d, COUNT(*) AS n FROM checks WHERE checked_at > ? GROUP BY substr(checked_at,1,10)', [$t30], 30),
        'reports' => series($pdo, 'SELECT substr(ts,1,10) AS d, COUNT(*) AS n FROM reports WHERE ts > ? GROUP BY substr(ts,1,10)', [$t30], 30),
        'top_reported' => $top->fetchAll(), 'top_watched' => $topw,
        'channels' => $ch,
        'last_probe' => iso($pdo->query('SELECT MAX(checked_at) FROM site_status')->fetchColumn() ?: null),
        'db' => is_sqlite($pdo) ? 'sqlite' : 'mysql',
    ]);
}
if ($a === 'users') {
    $qs = trim((string)($_GET['q'] ?? '')); $page = max(1, (int)($_GET['page'] ?? 1)); $per = 25;
    $where = $qs !== '' ? 'WHERE u.email LIKE ? OR u.name LIKE ?' : ''; $args = $qs !== '' ? ['%' . $qs . '%', '%' . $qs . '%'] : [];
    $total = $one("SELECT COUNT(*) FROM users u $where", $args);
    $q = $pdo->prepare("SELECT u.id, u.name, u.email, u.created_at, u.last_login, (u.google_sub IS NOT NULL) AS google, (u.pass_hash IS NOT NULL) AS pw,
        (SELECT COUNT(*) FROM watchlist w WHERE w.user_id=u.id) AS watching, (SELECT COUNT(*) FROM alert_channels c WHERE c.user_id=u.id) AS channels,
        (SELECT COUNT(*) FROM saved_checks s WHERE s.user_id=u.id) AS saved FROM users u $where ORDER BY u.id DESC LIMIT $per OFFSET " . (($page - 1) * $per));
    $q->execute($args);
    $rows = array_map(fn($r) => ['id' => (int)$r['id'], 'name' => $r['name'], 'email' => $r['email'], 'created' => iso($r['created_at']), 'last' => iso($r['last_login']),
        'google' => (bool)$r['google'], 'pw' => (bool)$r['pw'], 'watching' => (int)$r['watching'], 'channels' => (int)$r['channels'], 'saved' => (int)$r['saved']], $q->fetchAll());
    out(200, ['total' => $total, 'page' => $page, 'per' => $per, 'users' => $rows]);
}
if ($a === 'user') {
    $id = (int)($_GET['id'] ?? 0);
    $w = $pdo->prepare('SELECT host, added_at FROM watchlist WHERE user_id=? ORDER BY added_at DESC'); $w->execute([$id]);
    $c = $pdo->prepare('SELECT kind, label, created_at FROM alert_channels WHERE user_id=?'); $c->execute([$id]);
    out(200, ['watchlist' => $w->fetchAll(), 'channels' => $c->fetchAll()]);
}
out(404, ['error' => 'Not found.']);
