<?php
// GET ?host=x  -> what visitors said in the last hour about whether a site opens.
// POST {host, vote: "opened"|"noload"} -> add one answer (one per visitor per site per 30 minutes).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_probe.php';
$pdo = db();
$in = $_SERVER['REQUEST_METHOD'] === 'POST' ? json_decode((string)file_get_contents('php://input'), true) : $_GET;
$host = strtolower(trim((string)($in['host'] ?? '')));
if (!isset(site_pages()[$host])) {
    $t = parse_target($host);
    if (!$t || filter_var($t[0], FILTER_VALIDATE_IP) || $t[0] !== $host) out(422, ['error' => 'That is not a website address we can take an answer for.']);
}
$since = gmdate('Y-m-d H:i:s', time() - 3600);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (($_SERVER['HTTP_X_SUD'] ?? '') !== '1') out(403, ['error' => 'Forbidden.']);
    $vote = (string)($in['vote'] ?? '');
    if (!in_array($vote, ['opened', 'noload'], true)) out(422, ['error' => 'Please choose an answer.']);
    $known = $pdo->prepare('SELECT 1 FROM site_status WHERE host=? LIMIT 1'); $known->execute([$host]);
    if (!$known->fetch()) out(422, ['error' => 'Please run a check on that website first.']);
    throttle('vote', 20, 60);
    $h = client_hash();
    $dup = $pdo->prepare('SELECT 1 FROM site_votes WHERE host=? AND ip_hash=? AND ts > ? LIMIT 1');
    $dup->execute([$host, $h, gmdate('Y-m-d H:i:s', time() - 1800)]);
    if (!$dup->fetch()) { $pdo->prepare('INSERT INTO site_votes (host, vote, ip_hash, ts) VALUES (?,?,?,?)')->execute([$host, $vote, $h, sql_now()]); note_attempt('vote'); }
}
$q = $pdo->prepare('SELECT vote, COUNT(*) AS n FROM site_votes WHERE host=? AND ts > ? GROUP BY vote');
$q->execute([$host, $since]);
$c = ['opened' => 0, 'noload' => 0];
foreach ($q->fetchAll() as $r) if (isset($c[$r['vote']])) $c[$r['vote']] = (int)$r['n'];
$call = null;     // needs at least three answers and a clear majority
if ($c['noload'] >= 3 && $c['noload'] >= 2 * $c['opened']) $call = 'down';
elseif ($c['opened'] >= 3 && $c['opened'] >= 2 * $c['noload']) $call = 'working';
header('Cache-Control: no-store');
out(200, ['host' => $host, 'opened' => $c['opened'], 'noload' => $c['noload'], 'call' => $call]);
