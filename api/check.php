<?php
// POST {address, thorough} -> server check result + a share id used for the regional run.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
$in = read_post();
$t = parse_target((string)($in['address'] ?? ''));
if (!$t) out(422, ['error' => 'Please enter a website address like example.com.']);
[$host, $path] = $t;
$pdo = db();
throttle('check', 30, 10);
note_attempt('check');
$thorough = !empty($in['thorough']);
$r = check_site($host, $path, $thorough);
$now = sql_now();
if (!filter_var($host, FILTER_VALIDATE_IP)) {
    $pdo->prepare('INSERT INTO checks (host, verdict, http_code, ms, checked_at) VALUES (?,?,?,?,?)')->execute([$host, $r['verdict'], $r['http_code'], $r['ms'], $now]);
    $pdo->prepare('DELETE FROM checks WHERE checked_at < ?')->execute([gmdate('Y-m-d H:i:s', time() - 3 * 86400)]);
}
$share = bin2hex(random_bytes(5));
$pdo->prepare('INSERT INTO shares (id, host, data, created_at) VALUES (?,?,?,?)')
    ->execute([$share, $host, json_encode(['server' => $r, 'gp' => null, 'regional' => null, 'at' => $now]), $now]);
out(200, ['result' => $r, 'share' => $share, 'checked_at' => iso($now)]);
