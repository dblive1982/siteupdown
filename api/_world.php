<?php
// Shared helper: what the latest worldwide (fifteen-place) check says about a listed site.
declare(strict_types=1);

/** Did the latest worldwide check (fifteen places, under 12 hours old) reach this site from at least 80% of them? Then our own server being blocked or unanswered does not mean the site is down. */
function world_says_up(PDO $pdo, string $host): bool {
    $q = $pdo->prepare('SELECT data, ts FROM world_checks WHERE host=?'); $q->execute([$host]);
    $r = $q->fetch();
    if (!$r || $r['data'] === '' || (int)$r['ts'] < time() - 43200) return false;
    $d = json_decode($r['data'], true);
    if (!is_array($d) || empty($d['probes']) || count($d['probes']) < 10) return false;
    $ok = 0; foreach ($d['probes'] as $p) if (($p['state'] ?? '') === 'ok') $ok++;
    return $ok / count($d['probes']) >= 0.8;
}
