<?php
// POST {share} starts the Globalping run for a share row made by check.php.
// GET ?share=ID polls it; when finished the summary is saved on the share row so the share link shows it.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_gp.php';
require __DIR__ . '/_sitepages.php';
$pdo = db();

function load_share(PDO $pdo, string $id): array {
    if (!preg_match('/^[a-f0-9]{10}$/', $id)) out(404, ['error' => 'Not found.']);
    $s = $pdo->prepare('SELECT host, data, created_at FROM shares WHERE id=?');
    $s->execute([$id]);
    $r = $s->fetch();
    if (!$r) out(404, ['error' => 'Not found.']);
    return [$r['host'], json_decode($r['data'], true) ?: [], $r['created_at']];
}
function save_share(PDO $pdo, string $id, array $d): void {
    $pdo->prepare('UPDATE shares SET data=? WHERE id=?')->execute([json_encode($d), $id]);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    $in = read_post();
    [$host, $d] = load_share($pdo, (string)($in['share'] ?? ''));
    if (!empty($d['gp'])) out(200, ['started' => true]);
    throttle('regional', 15, 10);
    note_attempt('regional');
    $gp = gp_start($host);
    if (!$gp) out(503, ['error' => 'The worldwide probes are busy right now. Please try again in a minute.']);
    $d['gp'] = $gp;
    save_share($pdo, (string)$in['share'], $d);
    out(200, ['started' => true]);
}

$id = (string)($_GET['share'] ?? '');
[$host, $d, $created] = load_share($pdo, $id);
if (!empty($d['regional']['done'])) out(200, ['regional' => $d['regional'], 'verdict' => combined_verdict($d['server'], $d['regional'])]);
if (empty($d['gp'])) out(200, ['regional' => null]);
$r = gp_request('GET', '/measurements/' . rawurlencode($d['gp']));
if ($r['code'] !== 200) out(200, ['regional' => null]);
$sum = gp_summarise($r['data']);
if (!$sum) out(200, ['regional' => null]);
if ($sum['done']) {
    $sum['measured_at'] = iso(gmdate('Y-m-d H:i:s'));
    $d['regional'] = $sum;
    save_share($pdo, $id, $d);
    // A fresh live check of a site we list becomes that site's worldwide snapshot, so its status page shows the same 15 results.
    $h = strtolower($host);
    if ($sum['total'] > 0 && isset(site_pages()[$h])) {
        try { $pdo->prepare('REPLACE INTO world_checks (host, data, ts) VALUES (?,?,?)')->execute([$h, json_encode($sum), time()]); } catch (Throwable $e) {}
    }
}
out(200, ['regional' => $sum, 'verdict' => combined_verdict($d['server'], $sum)]);
