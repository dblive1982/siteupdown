<?php
// GET /badge/<host>.svg -> a small status badge for a site that has an "Is X down?" page. Listed sites only.
declare(strict_types=1);
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_world.php';
$host = strtolower(preg_replace('/[^a-z0-9.\-]/i', '', (string)($_GET['host'] ?? '')));
$list = site_pages();
function svg_out(string $label, string $value, string $color, int $age = 300): void {
    $lw = (int)ceil(mb_strlen($label) * 7.4) + 16; $vw = (int)ceil(mb_strlen($value) * 8.6) + 20; $tw = $lw + $vw;
    $l = htmlspecialchars($label, ENT_QUOTES); $v = htmlspecialchars($value, ENT_QUOTES);
    header('Content-Type: image/svg+xml; charset=utf-8');
    header('Cache-Control: public, max-age=' . $age);
    header('Access-Control-Allow-Origin: *');
    header('Cross-Origin-Resource-Policy: cross-origin');
    echo '<svg xmlns="http://www.w3.org/2000/svg" width="' . $tw . '" height="22" role="img" aria-label="' . $l . ': ' . $v . '">'
       . '<title>' . $l . ': ' . $v . '</title><clipPath id="r"><rect width="' . $tw . '" height="22" rx="4"/></clipPath>'
       . '<g clip-path="url(#r)"><rect width="' . $lw . '" height="22" fill="#1b1330"/><rect x="' . $lw . '" width="' . $vw . '" height="22" fill="' . $color . '"/></g>'
       . '<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
       . '<text x="' . ($lw / 2) . '" y="15">' . $l . '</text><text x="' . ($lw + $vw / 2) . '" y="15" font-weight="bold">' . $v . '</text></g></svg>';
    exit;
}
if (!isset($list[$host])) svg_out('siteupdown', 'unknown site', '#6b6b7a', 3600);
$name = (string)$list[$host]['name'];
$pdo = db();
$q = $pdo->prepare('SELECT verdict, checked_at FROM site_status WHERE host=?'); $q->execute([$host]);
$r = $q->fetch();
if (!$r) svg_out($name, 'checking…', '#6b6b7a', 120);
$v = (string)$r['verdict'];
if (in_array($v, ['inconclusive', 'timeout'], true) && world_says_up($pdo, $host)) $v = 'up';
if ($v === 'up') {
    $q = $pdo->prepare("SELECT SUM(verdict='up') u, COUNT(*) n FROM site_log WHERE host=? AND ts > ?");
    $q->execute([$host, gmdate('Y-m-d H:i:s', time() - 86400)]);
    $u = $q->fetch(); $pct = ($u && (int)$u['n'] >= 10) ? round(100 * (int)$u['u'] / (int)$u['n'], 1) : null;
    svg_out($name, 'Up' . ($pct !== null && $pct < 100 ? ' · ' . $pct . '%' : ($pct === 100.0 ? ' · 100%' : '')), '#2e9d46');
}
if ($v === 'down') svg_out($name, 'Down', '#d6454b', 120);
svg_out($name, 'Not sure', '#d9962b', 300);
