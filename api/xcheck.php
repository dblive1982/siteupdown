<?php
// Signed-in users only. GET -> my extra checks. POST {action: add|remove|run}.
// Extra checks: "kw" = this text must be on the page, "port" = this port must answer. Checked every minute by cron.php.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_xcheck.php';
$uid = require_user();
$pdo = db();

function xc_list(PDO $pdo, int $uid): array {
    $q = $pdo->prepare('SELECT id, host, kind, param, state, verdict, ms, detail, checked_at FROM extra_checks WHERE user_id=? ORDER BY id');
    $q->execute([$uid]);
    return array_map(fn($r) => ['id' => (int)$r['id'], 'host' => $r['host'], 'kind' => $r['kind'], 'param' => $r['param'], 'state' => $r['state'], 'verdict' => $r['verdict'],
        'ms' => $r['ms'] !== null ? (int)$r['ms'] : null, 'detail' => $r['detail'], 'at' => $r['checked_at'] ? iso($r['checked_at']) : null], $q->fetchAll());
}
function xc_out(PDO $pdo, int $uid): void { out(200, ['items' => xc_list($pdo, $uid), 'max' => XCHECK_MAX, 'ports' => XCHECK_PORTS]); }

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') xc_out($pdo, $uid);
$in = read_post();
$a = (string)($in['action'] ?? '');
if ($a === 'add') {
    throttle('xcheck', 30, 60); note_attempt('xcheck');
    $t = parse_target((string)($in['address'] ?? ''));
    if (!$t || filter_var($t[0], FILTER_VALIDATE_IP)) out(422, ['error' => 'Please enter a website address like example.com.']);
    $kind = (string)($in['kind'] ?? '');
    if (!in_array($kind, ['kw', 'port'], true)) out(422, ['error' => 'Pick a check type.']);
    $param = trim((string)($in['param'] ?? ''));
    if ($kind === 'port') {
        if (!in_array((int)$param, XCHECK_PORTS, true)) out(422, ['error' => 'We can check these ports: ' . implode(', ', XCHECK_PORTS) . '.']);
        $param = (string)(int)$param;
    } else {
        $kind = 'keyword';
        if (mb_strlen($param) < 2 || mb_strlen($param) > 100 || preg_match('~[\x00-\x1F]~', $param)) out(422, ['error' => 'Enter the word or phrase that should appear on the page (2 to 100 characters).']);
    }
    $n = $pdo->prepare('SELECT COUNT(*) FROM extra_checks WHERE user_id=?'); $n->execute([$uid]);
    if ((int)$n->fetchColumn() >= XCHECK_MAX) out(422, ['error' => 'You can have up to ' . XCHECK_MAX . ' extra checks. Remove one to add another.']);
    $d = $pdo->prepare('SELECT 1 FROM extra_checks WHERE user_id=? AND host=? AND kind=? AND param=?'); $d->execute([$uid, $t[0], $kind, $param]);
    if ($d->fetch()) out(422, ['error' => 'You already have that check.']);
    $pdo->prepare('INSERT INTO extra_checks (user_id, host, kind, param, created_at) VALUES (?,?,?,?,?)')->execute([$uid, $t[0], $kind, $param, sql_now()]);
    $id = (int)$pdo->lastInsertId();
    // First result straight away so the person can see it work.
    $row = ['id' => $id, 'user_id' => $uid, 'host' => $t[0], 'kind' => $kind, 'param' => $param, 'state' => 'up', 'fails' => 0, 'since' => null];
    $res = xcheck_run($row);
    $pdo->prepare('UPDATE extra_checks SET verdict=?, ms=?, detail=?, checked_at=?, fails=? WHERE id=?')->execute([$res['verdict'], $res['ms'], mb_substr($res['detail'], 0, 120), sql_now(), $res['verdict'] === 'down' ? 1 : 0, $id]);
    xc_out($pdo, $uid);
}
if ($a === 'remove') {
    $pdo->prepare('DELETE FROM extra_checks WHERE id=? AND user_id=?')->execute([(int)($in['id'] ?? 0), $uid]);
    xc_out($pdo, $uid);
}
if ($a === 'run') {
    throttle('xcheck', 30, 60); note_attempt('xcheck');
    $q = $pdo->prepare('SELECT * FROM extra_checks WHERE id=? AND user_id=?'); $q->execute([(int)($in['id'] ?? 0), $uid]);
    $row = $q->fetch();
    if (!$row) out(404, ['error' => 'That check was not found.']);
    xcheck_track($pdo, $row, xcheck_run($row));
    xc_out($pdo, $uid);
}
out(400, ['error' => 'Bad request.']);
