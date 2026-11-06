<?php
// GET /badge/<host>.svg -> a small status badge for a site that has an "Is X down?" page. Listed sites only.
declare(strict_types=1);
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_world.php';
$host = strtolower(preg_replace('/[^a-z0-9.\-]/i', '', (string)($_GET['host'] ?? '')));
$list = site_pages();
function svg_out(string $label, string $value, string $color, int $age = 60, string $tip = ''): void {
    $lw = (int)ceil(mb_strlen($label) * 7.4) + 16; $vw = (int)ceil(mb_strlen($value) * 8.6) + 20; $tw = $lw + $vw;
    $l = htmlspecialchars($label, ENT_QUOTES); $v = htmlspecialchars($value, ENT_QUOTES); $tt = htmlspecialchars($tip !== '' ? $tip : $label . ': ' . $value, ENT_QUOTES);
    header('Content-Type: image/svg+xml; charset=utf-8');
    header('Cache-Control: public, max-age=' . $age);
    header('Access-Control-Allow-Origin: *');
    header('Cross-Origin-Resource-Policy: cross-origin');
    echo '<svg xmlns="http://www.w3.org/2000/svg" width="' . $tw . '" height="22" role="img" aria-label="' . $l . ': ' . $v . '">'
       . '<title>' . $tt . '</title><clipPath id="r"><rect width="' . $tw . '" height="22" rx="4"/></clipPath>'
       . '<g clip-path="url(#r)"><rect width="' . $lw . '" height="22" fill="#5b5870"/><rect x="' . $lw . '" width="' . $vw . '" height="22" fill="' . $color . '"/></g>'
       . '<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
       . '<text x="' . ($lw / 2) . '" y="15">' . $l . '</text><text x="' . ($lw + $vw / 2) . '" y="15" font-weight="bold">' . $v . '</text></g></svg>';
    exit;
}
if (!isset($list[$host])) svg_out('siteupdown', 'unknown site', '#6b6b7a', 3600);
$name = (string)$list[$host]['name'];
$pdo = db();
$q = $pdo->prepare('SELECT verdict, checked_at, ms FROM site_status WHERE host=?'); $q->execute([$host]);
$r = $q->fetch();
if (!$r) svg_out($name, 'checking…', '#6b6b7a', 60);
$v = (string)$r['verdict']; $ms = $r['ms'] !== null ? (int)$r['ms'] : null; $when = strtotime((string)$r['checked_at'] . ' UTC') ?: time();
if (in_array($v, ['inconclusive', 'timeout'], true) && world_says_up($pdo, $host)) $v = 'up';
// a quick live sample (taken while someone is watching the status page) is newer than the five-minute check: prefer it
$ls = $pdo->prepare('SELECT ts, ms, verdict FROM live_samples WHERE host=? ORDER BY ts DESC LIMIT 1'); $ls->execute([$host]); $ls = $ls->fetch();
if ($ls && (int)$ls['ts'] > time() - 90 && (int)$ls['ts'] >= $when) { $v = (string)$ls['verdict']; $ms = $ls['ms'] !== null ? (int)$ls['ms'] : $ms; $when = (int)$ls['ts']; }
$ago = max(0, time() - $when); $agoTxt = $ago < 90 ? 'just now' : (int)round($ago / 60) . ' min ago';
if ($v === 'up') {
    $q = $pdo->prepare("SELECT SUM(verdict='up') u, COUNT(*) n FROM site_log WHERE host=? AND ts > ?");
    $q->execute([$host, gmdate('Y-m-d H:i:s', time() - 86400)]);
    $u = $q->fetch(); $pct = ($u && (int)$u['n'] >= 10) ? round(100 * (int)$u['u'] / (int)$u['n'], 1) : null;
    svg_out($name, 'Up' . ($pct !== null && $pct < 100 ? ' · ' . $pct . '%' : ($pct === 100.0 ? ' · 100%' : '')), '#2e9d46', 60,
        $name . ' is up. ' . ($pct !== null ? $pct . '% of checks answered in the last 24 hours. ' : '') . ($ms !== null ? 'Last response ' . $ms . ' ms. ' : '') . 'Checked ' . $agoTxt . ' by siteupdown.com. Click for the full status page.');
}
if ($v === 'down') svg_out($name, 'Down', '#d6454b', 60, $name . ' did not answer our last check (' . $agoTxt . '). Click for the full status page.');
svg_out($name, 'Not sure', '#d9962b', 120, 'We could not tell whether ' . $name . ' is up (' . $agoTxt . '). Click for details.');
