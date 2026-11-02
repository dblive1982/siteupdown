<?php
// POST {host, kind} -> records one visitor problem report for a site that has an "Is X down?" page.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_probe.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['error' => 'POST only.']);
$in = json_decode((string)file_get_contents('php://input'), true);
$host = strtolower(trim((string)($in['host'] ?? '')));
$kind = (string)($in['kind'] ?? '');
$sites = site_pages();
if (!in_array($kind, ['site', 'login', 'app', 'slow'], true)) out(422, ['error' => 'Please pick one of the options.']);
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
$dup = $pdo->prepare('SELECT 1 FROM reports WHERE host=? AND ip_hash=? AND ts > ? LIMIT 1');
$dup->execute([$host, $h, gmdate('Y-m-d H:i:s', time() - 1800)]);
if ($dup->fetch()) out(200, ['ok' => true, 'duplicate' => true, 'message' => 'Thanks, we already have a report from you in the last 30 minutes.']);
$pdo->prepare('INSERT INTO reports (host, kind, ip_hash, ts) VALUES (?,?,?,?)')->execute([$host, $kind, $h, sql_now()]);
note_attempt('report');
out(200, ['ok' => true, 'message' => 'Thanks, your report has been added.']);
