<?php
// GET ?id=... -> the saved check (server result + regional summary) for a share link.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_gp.php';
$id = (string)($_GET['id'] ?? '');
if (!preg_match('/^[a-f0-9]{10}$/', $id)) out(404, ['error' => 'That link is not valid.']);
$s = db()->prepare('SELECT host, data, created_at FROM shares WHERE id=?');
$s->execute([$id]);
$r = $s->fetch();
if (!$r) out(404, ['error' => 'That shared check has expired or does not exist.']);
$d = json_decode($r['data'], true) ?: [];
out(200, ['host' => $r['host'], 'result' => $d['server'] ?? null, 'regional' => $d['regional'] ?? null,
    'verdict' => combined_verdict($d['server'] ?? ['verdict' => 'inconclusive'], $d['regional'] ?? null), 'checked_at' => iso($r['created_at'])]);
