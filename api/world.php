<?php
// GET ?host=example.com -> the latest worldwide (15-place) snapshot for one of our listed pages, if the background sweep has one.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
$host = strtolower(trim((string)($_GET['host'] ?? '')));
if (!isset(site_pages()[$host])) out(404, ['error' => 'Not found.']);
$q = db()->prepare('SELECT data, ts FROM world_checks WHERE host=?'); $q->execute([$host]);
$r = $q->fetch();
header('Cache-Control: public, max-age=120');
if (!$r) out(200, ['world' => null]);
$d = json_decode($r['data'], true);
out(200, ['world' => is_array($d) ? $d : null]);
