<?php
// Permanent daily record: rolls visitor reports (by type) and our detected outages up into history_days. Counts only.
declare(strict_types=1);

function archive_history(PDO $pdo, int $days): void {
    $from = gmdate('Y-m-d', time() - $days * 86400);
    $rows = [];
    $q = $pdo->prepare("SELECT substr(ts,1,10) AS d, host, kind, COUNT(*) AS n FROM reports WHERE ts >= ? GROUP BY substr(ts,1,10), host, kind");
    $q->execute([$from . ' 00:00:00']);
    foreach ($q->fetchAll() as $r) {
        $k = $r['d'] . '|' . $r['host'];
        $rows[$k] = $rows[$k] ?? ['d' => $r['d'], 'h' => $r['host'], 'site' => 0, 'login' => 0, 'app' => 0, 'slow' => 0, 'fixed' => 0, 'o' => 0, 's' => 0];
        if (isset($rows[$k][$r['kind']])) $rows[$k][$r['kind']] += (int)$r['n'];
    }
    $q = $pdo->prepare('SELECT day, host, outages, down_s FROM site_daily WHERE day >= ? AND outages > 0');
    $q->execute([$from]);
    foreach ($q->fetchAll() as $r) {
        $k = $r['day'] . '|' . $r['host'];
        $rows[$k] = $rows[$k] ?? ['d' => $r['day'], 'h' => $r['host'], 'site' => 0, 'login' => 0, 'app' => 0, 'slow' => 0, 'fixed' => 0, 'o' => 0, 's' => 0];
        $rows[$k]['o'] = (int)$r['outages']; $rows[$k]['s'] = (int)$r['down_s'];
    }
    $w = $pdo->prepare('REPLACE INTO history_days (day, host, rep_site, rep_login, rep_app, rep_slow, rep_fixed, outages, down_s) VALUES (?,?,?,?,?,?,?,?,?)');
    $pdo->beginTransaction();
    foreach ($rows as $r) $w->execute([$r['d'], $r['h'], $r['site'], $r['login'], $r['app'], $r['slow'], $r['fixed'], $r['o'], $r['s']]);
    $pdo->commit();
}
