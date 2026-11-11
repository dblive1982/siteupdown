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
    require_once __DIR__ . '/_plan.php'; ensure_billing($pdo);
    out(200, [
        'tiles' => [
            'pro' => $one('SELECT COUNT(*) FROM users u WHERE ' . pro_users_sql('u')),
            'pro_canceling' => $one("SELECT COUNT(*) FROM users u WHERE plan_state='canceling' AND " . pro_users_sql('u')),
            'phones' => $one('SELECT COUNT(*) FROM phones WHERE verified=1'),
            'status_pages' => $one('SELECT COUNT(*) FROM status_pages'),
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
if ($a === 'traffic') {                                         // who is visiting: page views and visitors, by day, country, page, source, device and hour (counts only)
    $days = in_array((int)($_GET['days'] ?? 30), [7, 30, 90], true) ? (int)$_GET['days'] : 30;
    $from = $day($days - 1); $y = $day(1); $today = $day(0);
    $rows = function (string $sql, array $args = []) use ($pdo) { $q = $pdo->prepare($sql); $q->execute($args); return $q->fetchAll(); };
    $sum = fn(string $tbl, string $col, string $since) => (int)$one("SELECT COALESCE(SUM($col),0) FROM $tbl WHERE day >= ?", [$since]);
    $views = $rows('SELECT day AS d, SUM(views) AS n FROM pv_daily WHERE day >= ? GROUP BY day', [$from]);
    $vis = $rows('SELECT day AS d, SUM(visitors) AS n FROM pv_visitors WHERE day >= ? GROUP BY day', [$from]);
    $mk = function (array $r) use ($days) { $m = []; foreach ($r as $x) $m[$x['d']] = (int)$x['n']; $o = []; for ($i = $days - 1; $i >= 0; $i--) { $d = gmdate('Y-m-d', time() - $i * 86400); $o[] = ['d' => $d, 'n' => $m[$d] ?? 0]; } return $o; };
    $cv = []; foreach ($rows('SELECT country, SUM(visitors) AS n FROM pv_visitors WHERE day >= ? GROUP BY country', [$from]) as $r) $cv[$r['country']] = (int)$r['n'];
    $countries = [];
    foreach ($rows('SELECT country, SUM(views) AS n FROM pv_daily WHERE day >= ? GROUP BY country ORDER BY n DESC LIMIT 20', [$from]) as $r) $countries[] = ['code' => $r['country'], 'views' => (int)$r['n'], 'visitors' => $cv[$r['country']] ?? 0];
    $hours = array_fill(0, 24, 0); foreach ($rows('SELECT hr, SUM(views) AS n FROM pv_hour WHERE day >= ? GROUP BY hr', [$from]) as $r) $hours[(int)$r['hr']] = (int)$r['n'];
    $dev = ['d' => 0, 'm' => 0, 't' => 0]; foreach ($rows('SELECT device, SUM(views) AS n FROM pv_daily WHERE day >= ? GROUP BY device', [$from]) as $r) $dev[$r['device']] = (int)$r['n'];
    out(200, [
        'days' => $days,
        'tiles' => ['views_today' => $sum('pv_daily', 'views', $today), 'visitors_today' => $sum('pv_visitors', 'visitors', $today), 'views_yesterday' => (int)$one('SELECT COALESCE(SUM(views),0) FROM pv_daily WHERE day = ?', [$y]), 'visitors_yesterday' => (int)$one('SELECT COALESCE(SUM(visitors),0) FROM pv_visitors WHERE day = ?', [$y]),
            'views_range' => $sum('pv_daily', 'views', $from), 'visitors_range' => $sum('pv_visitors', 'visitors', $from), 'countries' => count(array_filter(array_column($countries, 'code')))],
        'views' => $mk($views), 'visitors' => $mk($vis), 'countries' => $countries,
        'pages' => array_map(fn($r) => ['path' => $r['path'], 'views' => (int)$r['n']], $rows('SELECT path, SUM(views) AS n FROM pv_daily WHERE day >= ? GROUP BY path ORDER BY n DESC LIMIT 25', [$from])),
        'refs' => array_map(fn($r) => ['ref' => $r['ref'] ?: 'Direct or unknown', 'views' => (int)$r['n']], $rows('SELECT ref, SUM(views) AS n FROM pv_daily WHERE day >= ? GROUP BY ref ORDER BY n DESC LIMIT 12', [$from])),
        'devices' => $dev, 'hours' => $hours,
        'since' => $pdo->query('SELECT MIN(day) FROM pv_daily')->fetchColumn() ?: null,
    ]);
}
if ($a === 'health') {                                          // everything that is happening right now: monitoring, incidents, security, usage, storage
    $t24 = gmdate('Y-m-d H:i:s', time() - 86400); $t7 = gmdate('Y-m-d H:i:s', time() - 7 * 86400); $t1h = gmdate('Y-m-d H:i:s', time() - 3600);
    $rows = function (string $sql, array $args = []) use ($pdo) { $q = $pdo->prepare($sql); $q->execute($args); return $q->fetchAll(); };
    $verdicts = []; foreach ($rows('SELECT verdict, COUNT(*) AS n FROM site_status GROUP BY verdict') as $r) $verdicts[$r['verdict']] = (int)$r['n'];
    $tracked = array_sum($verdicts);
    $stale = $one('SELECT COUNT(*) FROM site_status WHERE checked_at < ?', [gmdate('Y-m-d H:i:s', time() - 3 * 3600)]);
    $downNow = array_map(fn($r) => ['host' => $r['host'], 'verdict' => $r['verdict'], 'code' => $r['http_code'] === null ? null : (int)$r['http_code'], 'at' => iso($r['checked_at'])],
        $rows("SELECT host, verdict, http_code, checked_at FROM site_status WHERE verdict IN ('down','timeout') ORDER BY checked_at DESC LIMIT 25"));
    $open = array_map(fn($r) => ['host' => $r['host'], 'since' => iso($r['started_at'])], $rows('SELECT host, started_at FROM incidents WHERE ended_at IS NULL ORDER BY started_at DESC LIMIT 25'));
    $dur = $rows('SELECT started_at, ended_at FROM incidents WHERE ended_at IS NOT NULL AND started_at > ?', [$t7]); $secs = 0;
    foreach ($dur as $r) $secs += max(0, strtotime($r['ended_at'] . ' UTC') - strtotime($r['started_at'] . ' UTC'));
    $kinds = []; foreach ($rows('SELECT kind, COUNT(*) AS n FROM attempts GROUP BY kind ORDER BY n DESC') as $r) $kinds[$r['kind']] = (int)$r['n'];
    $tbl = []; foreach (['users', 'checks', 'site_log', 'site_daily', 'incidents', 'reports', 'pv_daily', 'watchlist', 'history_days', 'world_checks'] as $t) { try { $tbl[] = ['t' => $t, 'n' => $one("SELECT COUNT(*) FROM $t")]; } catch (Throwable $e) {} }
    $dbsize = null;
    try { if (!is_sqlite($pdo)) $dbsize = (int)$one('SELECT COALESCE(SUM(data_length + index_length),0) FROM information_schema.tables WHERE table_schema = DATABASE()'); } catch (Throwable $e) {}
    $users = (int)$one('SELECT COUNT(*) FROM users'); $tf = 0; try { $tf = (int)$one('SELECT COUNT(*) FROM users WHERE twofa = 1'); } catch (Throwable $e) {}
    $cfg = config() ?: [];
    $lastCron = $pdo->query('SELECT MAX(checked_at) FROM site_status')->fetchColumn() ?: null;
    $ago = $lastCron ? time() - strtotime($lastCron . ' UTC') : null;
    $root = dirname(__DIR__);
    out(200, [
        'now' => gmdate('Y-m-d\TH:i:s\Z'),
        'monitor' => ['tracked' => $tracked, 'verdicts' => $verdicts, 'stale' => $stale, 'last' => iso($lastCron), 'last_age_s' => $ago,
            'checks_1h' => $one('SELECT COUNT(*) FROM checks WHERE checked_at > ?', [$t1h]), 'checks_24h' => $one('SELECT COUNT(*) FROM checks WHERE checked_at > ?', [$t24])],
        'down_now' => $downNow, 'open_incidents' => $open,
        'incidents' => ['h24' => $one('SELECT COUNT(*) FROM incidents WHERE started_at > ?', [$t24]), 'd7' => count($dur) + count($open), 'avg_s' => $dur ? (int)round($secs / count($dur)) : 0],
        'security' => ['non_admin_tries' => $kinds['adm'] ?? 0, 'admin_codes' => $kinds['admcode'] ?? 0, 'admin_verifies' => $kinds['admver'] ?? 0, 'logins' => $kinds['login'] ?? 0, 'registers' => $kinds['register'] ?? 0, 'resets' => ($kinds['forgot'] ?? 0) + ($kinds['reset'] ?? 0),
            'twofa_users' => $tf, 'users' => $users, 'turnstile' => turnstile_on(), 'security_txt' => is_file($root . '/.well-known/security.txt')],
        'usage' => $kinds,
        'storage' => ['tables' => $tbl, 'db_bytes' => $dbsize],
        'site' => ['ads_txt' => is_file($root . '/ads.txt'), 'sitemap' => is_file($root . '/sitemap.xml'), 'robots' => is_file($root . '/robots.txt'), 'config' => !empty($cfg), 'php' => PHP_VERSION],
    ]);
}
if ($a === 'seo') {                                             // the page-by-page search audit written by the site build
    $f = __DIR__ . '/_seo.json';
    out(200, is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: ['pages' => []]) : ['pages' => [], 'missing' => true]);
}
if ($a === 'usage') {                                           // daily totals of actions (long-term), for the health trend chart
    $days = in_array((int)($_GET['days'] ?? 30), [7, 30, 90], true) ? (int)$_GET['days'] : 30; $from = $day($days - 1);
    $kind = preg_replace('/[^a-z_]/', '', (string)($_GET['kind'] ?? ''));
    $rows = function (string $sql, array $args = []) use ($pdo) { try { $q = $pdo->prepare($sql); $q->execute($args); return $q->fetchAll(); } catch (Throwable $e) { return []; } };
    $m = []; foreach ($rows('SELECT day AS d, SUM(n) AS n FROM usage_daily WHERE day >= ?' . ($kind !== '' ? ' AND kind = ?' : '') . ' GROUP BY day', $kind !== '' ? [$from, $kind] : [$from]) as $r) $m[$r['d']] = (int)$r['n'];
    $ser = []; for ($i = $days - 1; $i >= 0; $i--) { $d = gmdate('Y-m-d', time() - $i * 86400); $ser[] = ['d' => $d, 'n' => $m[$d] ?? 0]; }
    $tot = []; foreach ($rows('SELECT kind, SUM(n) AS n FROM usage_daily WHERE day >= ? GROUP BY kind ORDER BY n DESC', [$from]) as $r) $tot[] = ['kind' => $r['kind'], 'n' => (int)$r['n']];
    $since = ''; foreach ($rows('SELECT MIN(day) AS d FROM usage_daily') as $r) $since = $r['d'] ?: '';
    out(200, ['days' => $days, 'kind' => $kind, 'series' => $ser, 'totals' => $tot, 'since' => $since]);
}
if ($a === 'userstats') {                                       // the whole picture of the user base
    $d = fn(int $ago) => gmdate('Y-m-d H:i:s', time() - $ago * 86400);
    $rows = function (string $sql, array $args = []) use ($pdo) { $q = $pdo->prepare($sql); $q->execute($args); return $q->fetchAll(); };
    $total = $one('SELECT COUNT(*) FROM users');
    $tf = 0; try { $tf = $one('SELECT COUNT(*) FROM users WHERE twofa = 1'); } catch (Throwable $e) {}
    $cohort = $one('SELECT COUNT(*) FROM users WHERE created_at BETWEEN ? AND ?', [$d(37), $d(7)]);
    $cohortBack = $one('SELECT COUNT(*) FROM users WHERE created_at BETWEEN ? AND ? AND last_login > ?', [$d(37), $d(7), $d(7)]);
    $signups = series($pdo, 'SELECT substr(created_at,1,10) AS d, COUNT(*) AS n FROM users WHERE created_at > ? GROUP BY substr(created_at,1,10)', [$d(90)], 90);
    $before = $one('SELECT COUNT(*) FROM users WHERE created_at <= ?', [$d(90)]); $run = $before; $growth = [];
    foreach ($signups as $x) { $run += $x['n']; $growth[] = ['d' => $x['d'], 'n' => $run]; }
    $recent = array_map(fn($r) => ['name' => $r['name'], 'email' => $r['email'], 'created' => iso($r['created_at']), 'last' => iso($r['last_login']), 'google' => (bool)$r['g']],
        $rows('SELECT name, email, created_at, last_login, (google_sub IS NOT NULL) AS g FROM users ORDER BY id DESC LIMIT 10'));
    $top = array_map(fn($r) => ['name' => $r['name'], 'email' => $r['email'], 'n' => (int)$r['n']],
        $rows('SELECT u.name, u.email, COUNT(*) AS n FROM watchlist w JOIN users u ON u.id = w.user_id GROUP BY u.id, u.name, u.email ORDER BY n DESC LIMIT 10'));
    out(200, [
        'total' => $total,
        'new' => ['d1' => $one('SELECT COUNT(*) FROM users WHERE created_at > ?', [$d(1)]), 'd7' => $one('SELECT COUNT(*) FROM users WHERE created_at > ?', [$d(7)]), 'd30' => $one('SELECT COUNT(*) FROM users WHERE created_at > ?', [$d(30)])],
        'active' => ['d1' => $one('SELECT COUNT(*) FROM users WHERE last_login > ?', [$d(1)]), 'd7' => $one('SELECT COUNT(*) FROM users WHERE last_login > ?', [$d(7)]), 'd30' => $one('SELECT COUNT(*) FROM users WHERE last_login > ?', [$d(30)])],
        'dormant30' => $one('SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL AND last_login <= ?', [$d(30)]),
        'never' => $one('SELECT COUNT(*) FROM users WHERE last_login IS NULL'),
        'method' => ['google' => $one('SELECT COUNT(*) FROM users WHERE google_sub IS NOT NULL AND pass_hash IS NULL'), 'password' => $one('SELECT COUNT(*) FROM users WHERE google_sub IS NULL AND pass_hash IS NOT NULL'), 'both' => $one('SELECT COUNT(*) FROM users WHERE google_sub IS NOT NULL AND pass_hash IS NOT NULL')],
        'adoption' => ['watching' => $one('SELECT COUNT(DISTINCT user_id) FROM watchlist'), 'channels' => $one('SELECT COUNT(DISTINCT user_id) FROM alert_channels'), 'saved' => $one('SELECT COUNT(DISTINCT user_id) FROM saved_checks'), 'twofa' => $tf],
        'retention' => ['cohort' => $cohort, 'back' => $cohortBack],
        'signups' => $signups, 'growth' => $growth, 'recent' => $recent, 'top_watchers' => $top,
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

// ---------------- stage 2: email a user, reset data, exports, activity log (all need the unlocked admin session) ----------------
if ($a === 'email') {
    $in2 = $in; throttle('admmail', 30, 60);
    $q = $pdo->prepare('SELECT id, name, email FROM users WHERE id=?'); $q->execute([(int)($in2['id'] ?? 0)]); $u = $q->fetch();
    if (!$u) out(404, ['error' => 'User not found.']);
    $subj = trim(preg_replace('/\s+/', ' ', (string)($in2['subject'] ?? ''))); $msg = trim(str_replace("\r", '', (string)($in2['message'] ?? '')));
    if ($subj === '' || mb_strlen($subj) > 120) out(422, ['error' => 'Please add a subject (up to 120 characters).']);
    if (mb_strlen($msg) < 3 || mb_strlen($msg) > 5000) out(422, ['error' => 'Please write a message (up to 5000 characters).']);
    note_attempt('admmail');
    $e = fn($v) => htmlspecialchars($v, ENT_QUOTES, 'UTF-8');
    $html = '<p style="margin:0 0 12px">Hi ' . $e($u['name']) . ',</p><p style="margin:0;white-space:pre-wrap">' . $e($msg) . '</p>';
    sud_email($u['email'], $subj, $subj, $html, "Hi {$u['name']},\n\n$msg\n", '', '', $me['email']);
    admin_log('email', 'to user #' . $u['id'] . ': ' . $subj);
    out(200, ['ok' => true, 'message' => 'Email sent to ' . $u['email'] . '.']);
}
if ($a === 'user_clear') {                                     // empty one part of a user's data
    $id = (int)($in['id'] ?? 0); $what = (string)($in['what'] ?? '');
    $tables = ['watchlist' => 'watchlist', 'saved' => 'saved_checks', 'channels' => 'alert_channels'];
    if (!isset($tables[$what]) || $id <= 0) out(422, ['error' => 'Nothing to clear.']);
    if (($in['confirm'] ?? '') !== 'RESET') out(422, ['error' => 'Type RESET to confirm.']);
    $d = $pdo->prepare('DELETE FROM ' . $tables[$what] . ' WHERE user_id=?'); $d->execute([$id]);
    admin_log('user_clear', $what . ' of user #' . $id . ' (' . $d->rowCount() . ' rows)');
    out(200, ['ok' => true, 'message' => 'Cleared ' . $d->rowCount() . ' items.']);
}
if ($a === 'user_delete') {
    $id = (int)($in['id'] ?? 0);
    $q = $pdo->prepare('SELECT id, email FROM users WHERE id=?'); $q->execute([$id]); $u = $q->fetch();
    if (!$u) out(404, ['error' => 'User not found.']);
    if ((int)$u['id'] === (int)$me['id'] || in_array(clean_email($u['email']), $admins, true)) out(422, ['error' => 'The admin account cannot be deleted here.']);
    if (clean_email((string)($in['confirm'] ?? '')) !== clean_email($u['email'])) out(422, ['error' => 'Type the user\'s email address to confirm.']);
    foreach (['watchlist', 'saved_checks', 'alert_channels', 'extra_checks', 'tg_links', 'resets'] as $t) { try { $pdo->prepare("DELETE FROM $t WHERE user_id=?")->execute([$id]); } catch (Throwable $x) {} }
    $pdo->prepare('DELETE FROM users WHERE id=?')->execute([$id]);
    admin_log('user_delete', 'user #' . $id . ' ' . $u['email']);
    out(200, ['ok' => true, 'message' => 'Account deleted.']);
}
if ($a === 'reset') {                                          // site data: reports / history of one host or everything
    $what = (string)($in['what'] ?? ''); $host = strtolower(trim((string)($in['host'] ?? '')));
    if (($in['confirm'] ?? '') !== 'RESET') out(422, ['error' => 'Type RESET to confirm.']);
    $n = 0;
    $del = function (string $t, string $col) use ($pdo, $host, &$n) { $d = $host !== '' ? $pdo->prepare("DELETE FROM $t WHERE $col=?") : $pdo->prepare("DELETE FROM $t"); $d->execute($host !== '' ? [$host] : []); $n += $d->rowCount(); };
    if ($what === 'reports') $del('reports', 'host');
    elseif ($what === 'history') { $del('site_log', 'host'); $del('incidents', 'host'); }
    elseif ($what === 'checks') $del('checks', 'host');
    else out(422, ['error' => 'Choose what to reset.']);
    admin_log('reset', $what . ' for ' . ($host !== '' ? $host : 'ALL sites') . ' (' . $n . ' rows)');
    out(200, ['ok' => true, 'message' => 'Removed ' . $n . ' rows' . ($host !== '' ? ' for ' . $host : ' for all sites') . '.']);
}
if ($a === 'export') {
    $what = (string)($_GET['what'] ?? '');
    $cell = fn($v) => '"' . str_replace('"', '""', preg_match('/^[=+\-@\t\r]/', (string)$v) ? "'" . $v : (string)$v) . '"';
    if ($what === 'users') {
        $hdr = ['id', 'name', 'email', 'created', 'last_login', 'watching', 'channels'];
        $rows = $pdo->query('SELECT u.id, u.name, u.email, u.created_at, u.last_login, (SELECT COUNT(*) FROM watchlist w WHERE w.user_id=u.id), (SELECT COUNT(*) FROM alert_channels c WHERE c.user_id=u.id) FROM users u ORDER BY u.id')->fetchAll(PDO::FETCH_NUM);
    } elseif ($what === 'reports') {
        $hdr = ['host', 'kind', 'time_utc']; $rows = $pdo->query('SELECT host, kind, ts FROM reports ORDER BY ts DESC LIMIT 100000')->fetchAll(PDO::FETCH_NUM);
    } else out(404, ['error' => 'Not found.']);
    admin_log('export', $what . ' (' . count($rows) . ' rows)');
    header('Content-Type: text/csv; charset=utf-8'); header('Content-Disposition: attachment; filename="siteupdown-' . $what . '-' . gmdate('Y-m-d') . '.csv"');
    echo implode(',', array_map($cell, $hdr)) . "\r\n";
    foreach ($rows as $r) echo implode(',', array_map($cell, $r)) . "\r\n";
    exit;
}
if ($a === 'log') {
    $r = $pdo->query('SELECT ts, action, detail FROM admin_log ORDER BY id DESC LIMIT 100')->fetchAll();
    out(200, ['log' => array_map(fn($x) => ['ts' => iso($x['ts']), 'action' => $x['action'], 'detail' => $x['detail']], $r)]);
}
out(404, ['error' => 'Not found.']);
