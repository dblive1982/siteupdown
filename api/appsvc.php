<?php
// GET ?host=whatsapp.com -> latest status of the app servers listed for that site's "Is X down?" page.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$host = strtolower(trim((string)($_GET['host'] ?? '')));
$sp = site_pages()[$host] ?? null;
if (!$sp || empty($sp['app'])) out(404, ['error' => 'No app servers listed.']);
$pdo = db();
$q = $pdo->prepare('SELECT verdict, ms, checked_at FROM site_status WHERE host=?');
$items = [];
foreach ($sp['app'] as [$label, $h]) {
    $q->execute([$h]);
    $r = $q->fetch();
    $items[] = ['label' => $label, 'host' => $h, 'v' => $r['verdict'] ?? null, 'ms' => isset($r['ms']) ? (int)$r['ms'] : null, 'at' => $r ? iso($r['checked_at']) : null];
}
header('Cache-Control: public, max-age=30');
out(200, ['items' => $items]);
