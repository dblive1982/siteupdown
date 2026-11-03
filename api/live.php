<?php
// GET ?host=example.com -> the last few minutes of quick samples for a site that has an "Is X down?" page.
// Whoever asks when the newest sample is older than LIVE_EVERY seconds takes a short lock and runs the next probe,
// so a hundred people watching one site cause one check, not a hundred. Needs no sign-in.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_sitepages.php';
require __DIR__ . '/_probe.php';
const LIVE_EVERY = 10;         // seconds between samples of one site (raise or lower here)
const LIVE_MAX_HOSTS = 12;     // sites sampled at the same moment, to protect the server
const LIVE_BACKOFF = 120;      // seconds to leave a site alone if it seems to be refusing our checks
const LIVE_KEEP = 900;         // seconds of samples kept
$host = strtolower(trim((string)($_GET['host'] ?? '')));
if (!isset(site_pages()[$host])) out(404, ['error' => 'Live graph is not available for that site.']);
$pdo = db();
$now = time();
$last = $pdo->prepare('SELECT MAX(ts) FROM live_samples WHERE host=?'); $last->execute([$host]); $lastTs = (int)$last->fetchColumn();
$fresh = ($now - $lastTs) < LIVE_EVERY;
$probed = false;
if (!$fresh) {
    // busy elsewhere? then just serve what we have
    $busy = $pdo->prepare('SELECT COUNT(DISTINCT host) FROM live_samples WHERE ts > ? AND host <> ?'); $busy->execute([$now - 30, $host]);
    if ((int)$busy->fetchColumn() < LIVE_MAX_HOSTS) {
        $pdo->prepare(is_sqlite($pdo) ? 'INSERT OR IGNORE INTO live_lock (host, until_ts) VALUES (?, 0)' : 'INSERT IGNORE INTO live_lock (host, until_ts) VALUES (?, 0)')->execute([$host]);
        $lk = $pdo->prepare('UPDATE live_lock SET until_ts=? WHERE host=? AND until_ts < ?');
        $lk->execute([$now + 12, $host, $now]);
        if ($lk->rowCount() === 1) {            // we hold the lock: take the sample
            $r = check_site($host, '/', false, true);
            $pdo->prepare('INSERT INTO live_samples (host, ts, ms, verdict, code) VALUES (?,?,?,?,?)')->execute([$host, time(), $r['ms'] ?? null, $r['verdict'], $r['http_code'] ?? ($r['code'] ?? null)]);
            $pdo->prepare('DELETE FROM live_samples WHERE host=? AND ts < ?')->execute([$host, time() - LIVE_KEEP]);
            $code = (int)($r['http_code'] ?? ($r['code'] ?? 0));
            $blocked = $r['verdict'] === 'inconclusive' || $code === 403 || $code === 429;     // back off so we are never a nuisance
            $pdo->prepare('UPDATE live_lock SET until_ts=? WHERE host=?')->execute([time() + ($blocked ? LIVE_BACKOFF : LIVE_EVERY - 1), $host]);
            $probed = true;
        }
    }
}
$q = $pdo->prepare('SELECT ts, ms, verdict, code FROM live_samples WHERE host=? AND ts > ? ORDER BY ts DESC LIMIT 120');
$q->execute([$host, $now - 600]);
$rows = array_reverse($q->fetchAll());
out(200, ['host' => $host, 'every' => LIVE_EVERY, 'now' => time(), 'probed' => $probed,
    'samples' => array_map(fn($r) => ['t' => (int)$r['ts'], 'ms' => $r['ms'] !== null ? (int)$r['ms'] : null, 'v' => $r['verdict'], 'c' => $r['code'] !== null ? (int)$r['code'] : null], $rows)]);
