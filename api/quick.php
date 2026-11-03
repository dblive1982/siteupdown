<?php
// POST {address} -> a fast single check for the browser extension: verdict, HTTP code and response time.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
$in = read_post();
$t = parse_target((string)($in['address'] ?? ''));
if (!$t) out(422, ['error' => 'Please enter a website address like example.com.']);
[$host, $path] = $t;
$pdo = db();
throttle('check', 30, 10);
note_attempt('check');
$r = check_site($host, $path, false, true);
if (!filter_var($host, FILTER_VALIDATE_IP)) {
    $pdo->prepare('INSERT INTO checks (host, verdict, http_code, ms, checked_at) VALUES (?,?,?,?,?)')->execute([$host, $r['verdict'], $r['http_code'], $r['ms'], sql_now()]);
}
out(200, ['host' => $host, 'verdict' => $r['verdict'], 'http_code' => $r['http_code'], 'ms' => $r['ms'], 'err' => $r['err'] ?? null]);
