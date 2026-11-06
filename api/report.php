<?php
// POST {host, kind} -> records one visitor problem report for a site that has an "Is X down?" page.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_probe.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['error' => 'POST only.']);
$in = json_decode((string)file_get_contents('php://input'), true);
$host = strtolower(trim((string)($in['host'] ?? '')));
$kinds = isset($in['kinds']) && is_array($in['kinds']) ? $in['kinds'] : [(string)($in['kind'] ?? '')];
$kinds = array_values(array_unique(array_map('strval', $kinds)));
$sites = site_pages();
if (!$kinds || count($kinds) > 4 || array_diff($kinds, ['site', 'login', 'app', 'slow'])) out(422, ['error' => 'Please pick at least one option.']);
$pdo = db();
if (!isset($sites[$host])) {
    // Any website, as long as it is a real public address that has been checked here recently.
    $t = parse_target($host);
    if (!$t || filter_var($t[0], FILTER_VALIDATE_IP) || $t[0] !== $host) out(422, ['error' => 'That is not a website address we can take a report for.']);
    $seen = $pdo->prepare('SELECT 1 FROM checks WHERE host=? AND checked_at > ? LIMIT 1');
    $seen->execute([$host, gmdate('Y-m-d H:i:s', time() - 3 * 86400)]);
    if (!$seen->fetch()) {
        $seen = $pdo->prepare('SELECT 1 FROM site_status WHERE host=? LIMIT 1');
        $seen->execute([$host]);
        if (!$seen->fetch()) out(422, ['error' => 'Please run a check on that website first, then report the problem.']);
    }
}
throttle('report', 12, 60);                       // at most 12 reports an hour from one address
$h = client_hash();
// Country only (never a city or address): the network's country header when the host provides one, otherwise the country of the visitor's own time zone.
$cc = strtoupper((string)($_SERVER['HTTP_CF_IPCOUNTRY'] ?? $_SERVER['HTTP_X_COUNTRY_CODE'] ?? ''));
if (!preg_match('/^[A-Z]{2}$/', $cc) || $cc === 'XX' || $cc === 'T1') {
    $cc = '';
    $tz = (string)($in['tz'] ?? '');
    if ($tz !== '' && strlen($tz) < 64 && in_array($tz, DateTimeZone::listIdentifiers(), true)) {
        $loc = (new DateTimeZone($tz))->getLocation();
        $c2 = strtoupper((string)($loc['country_code'] ?? ''));
        if (preg_match('/^[A-Z]{2}$/', $c2)) $cc = $c2;
    }
}
$dup = $pdo->prepare('SELECT 1 FROM reports WHERE host=? AND ip_hash=? AND kind=? AND ts > ? LIMIT 1');
$ins = $pdo->prepare('INSERT INTO reports (host, kind, ip_hash, ts, country) VALUES (?,?,?,?,?)');
$added = 0;
foreach ($kinds as $kind) {
    $dup->execute([$host, $h, $kind, gmdate('Y-m-d H:i:s', time() - 1800)]);
    if ($dup->fetch()) continue;
    $ins->execute([$host, $kind, $h, sql_now(), $cc !== '' ? $cc : null]);
    $added++;
}
if (!$added) out(200, ['ok' => true, 'duplicate' => true, 'message' => 'Thanks, we already have ' . (count($kinds) > 1 ? 'those reports' : 'that report') . ' from you in the last 30 minutes.']);
note_attempt('report');
out(200, ['ok' => true, 'added' => $added, 'message' => $added > 1 ? 'Thanks, your ' . $added . ' reports have been added.' : 'Thanks, your report has been added.']);
