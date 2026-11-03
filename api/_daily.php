<?php
// Daily roll-up of site_log + incidents into site_daily, which is kept for the 12-month record.
declare(strict_types=1);
function rollup_daily(PDO $pdo, int $days): void {
    $now = time();
    $from = gmdate('Y-m-d 00:00:00', $now - ($days - 1) * 86400);
    $q = $pdo->prepare("SELECT host, substr(ts,1,10) AS d, SUM(CASE WHEN verdict='up' THEN 1 ELSE 0 END) AS u,
        SUM(CASE WHEN verdict IN ('down','timeout') THEN 1 ELSE 0 END) AS b,
        SUM(CASE WHEN verdict='up' AND ms IS NOT NULL THEN ms ELSE 0 END) AS s,
        SUM(CASE WHEN verdict='up' AND ms IS NOT NULL THEN 1 ELSE 0 END) AS n
        FROM site_log WHERE ts >= ? GROUP BY host, substr(ts,1,10)");
    $q->execute([$from]);
    $rows = [];
    foreach ($q->fetchAll() as $r) $rows[$r['host'] . '|' . $r['d']] = ['host' => $r['host'], 'day' => $r['d'], 'u' => (int)$r['u'], 'b' => (int)$r['b'], 's' => (int)$r['s'], 'n' => (int)$r['n'], 'o' => 0, 'down' => 0];
    $i = $pdo->prepare('SELECT host, started_at, ended_at FROM incidents WHERE started_at < ? AND (ended_at IS NULL OR ended_at >= ?)');
    $i->execute([gmdate('Y-m-d H:i:s', $now + 1), $from]);
    foreach ($i->fetchAll() as $inc) {
        $st = strtotime($inc['started_at'] . ' UTC'); $en = $inc['ended_at'] ? strtotime($inc['ended_at'] . ' UTC') : $now;
        for ($t = max($st, strtotime($from . ' UTC')); $t < $en; $t = (int)(floor($t / 86400) * 86400 + 86400)) {
            $dayStart = (int)(floor($t / 86400) * 86400); $d = gmdate('Y-m-d', $dayStart);
            $k = $inc['host'] . '|' . $d;
            if (!isset($rows[$k])) continue;
            $rows[$k]['down'] += min($en, $dayStart + 86400) - $t;
        }
        $sd = gmdate('Y-m-d', $st);
        if (isset($rows[$inc['host'] . '|' . $sd])) $rows[$inc['host'] . '|' . $sd]['o']++;
    }
    $w = $pdo->prepare('REPLACE INTO site_daily (host, day, up_n, bad_n, ms_sum, ms_n, outages, down_s) VALUES (?,?,?,?,?,?,?,?)');
    $pdo->beginTransaction();
    try { foreach ($rows as $r) $w->execute([$r['host'], $r['day'], $r['u'], $r['b'], $r['s'], $r['n'], $r['o'], $r['down']]); $pdo->commit(); }
    catch (Throwable $e) { if ($pdo->inTransaction()) $pdo->rollBack(); throw $e; }
}
