<?php
// Signed-in users only. GET -> last 100 checks. POST {action: add|delete|clear}.
require __DIR__ . '/_boot.php';
$pdo = db();
$uid = require_user();
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') {
    $s = $pdo->prepare('SELECT id, host, verdict, http_code, ms, reachable, probes, median_ms, checked_at FROM saved_checks WHERE user_id=? ORDER BY checked_at DESC, id DESC LIMIT 100');
    $s->execute([$uid]);
    $items = array_map(fn($r) => [
        'id' => (int)$r['id'], 'host' => $r['host'], 'verdict' => $r['verdict'], 'code' => $r['http_code'] !== null ? (int)$r['http_code'] : null,
        'ms' => $r['ms'] !== null ? (int)$r['ms'] : null, 'reachable' => $r['reachable'] !== null ? (int)$r['reachable'] : null,
        'probes' => $r['probes'] !== null ? (int)$r['probes'] : null, 'median_ms' => $r['median_ms'] !== null ? (int)$r['median_ms'] : null, 'at' => iso($r['checked_at']),
    ], $s->fetchAll());
    out(200, ['items' => $items]);
}
$in = read_post();
$a = (string)($in['action'] ?? '');
if ($a === 'add') {
    // Saved from the server's own copy of the check (the share row), never from numbers sent by the browser.
    $sid = (string)($in['share'] ?? '');
    if (!preg_match('/^[a-f0-9]{10}$/', $sid)) out(422, ['error' => 'Bad request.']);
    $s = $pdo->prepare('SELECT host, data, created_at FROM shares WHERE id=?');
    $s->execute([$sid]);
    $r = $s->fetch();
    if (!$r) out(404, ['error' => 'That check was not found.']);
    $d = json_decode($r['data'], true) ?: [];
    $srv = $d['server'] ?? [];
    $reg = $d['regional'] ?? null;
    $e = $pdo->prepare('SELECT id FROM saved_checks WHERE user_id=? AND share_id=?');
    $e->execute([$uid, $sid]);
    $vals = [$srv['verdict'] ?? 'inconclusive', $srv['http_code'] ?? null, $srv['ms'] ?? null, $reg['reachable'] ?? null, $reg['total'] ?? null, $reg['median_ms'] ?? null];
    if ($row = $e->fetch()) {
        $pdo->prepare('UPDATE saved_checks SET verdict=?, http_code=?, ms=?, reachable=?, probes=?, median_ms=? WHERE id=?')->execute([...$vals, $row['id']]);
    } else {
        $n = $pdo->prepare('SELECT COUNT(*) FROM saved_checks WHERE user_id=?');
        $n->execute([$uid]);
        if ((int)$n->fetchColumn() >= 500) $pdo->prepare('DELETE FROM saved_checks WHERE user_id=? AND id IN (SELECT id FROM (SELECT id FROM saved_checks WHERE user_id=? ORDER BY checked_at ASC LIMIT 50) x)')->execute([$uid, $uid]);
        $pdo->prepare('INSERT INTO saved_checks (user_id, share_id, host, verdict, http_code, ms, reachable, probes, median_ms, checked_at) VALUES (?,?,?,?,?,?,?,?,?,?)')
            ->execute([$uid, $sid, $r['host'], ...$vals, $r['created_at']]);
    }
    out(200, ['ok' => true]);
}
if ($a === 'delete') {
    $pdo->prepare('DELETE FROM saved_checks WHERE id=? AND user_id=?')->execute([(int)($in['id'] ?? 0), $uid]);
    out(200, ['ok' => true]);
}
if ($a === 'clear') {
    $pdo->prepare('DELETE FROM saved_checks WHERE user_id=?')->execute([$uid]);
    out(200, ['ok' => true]);
}
out(400, ['error' => 'Bad request.']);
