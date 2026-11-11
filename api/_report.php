<?php
// Uptime reports for the sites on a user's watchlist, built from the daily record (site_daily, kept for over a year).
declare(strict_types=1);

/** Rows for every site the user watches between two dates (inclusive, 'YYYY-MM-DD'). Our own checks only. */
function report_rows(PDO $pdo, int $uid, string $from, string $to): array {
    $w = $pdo->prepare('SELECT host FROM watchlist WHERE user_id=? ORDER BY host'); $w->execute([$uid]);
    $hosts = $w->fetchAll(PDO::FETCH_COLUMN);
    if (!$hosts) return [];
    $in = implode(',', array_fill(0, count($hosts), '?'));
    $q = $pdo->prepare("SELECT host, SUM(up_n) AS up_n, SUM(bad_n) AS bad_n, SUM(ms_sum) AS ms_sum, SUM(ms_n) AS ms_n, SUM(outages) AS outages, SUM(down_s) AS down_s, COUNT(*) AS days
        FROM site_daily WHERE host IN ($in) AND day >= ? AND day <= ? GROUP BY host");
    $q->execute(array_merge($hosts, [$from, $to]));
    $by = [];
    foreach ($q->fetchAll() as $r) $by[$r['host']] = $r;
    $out = [];
    foreach ($hosts as $h) {
        $r = $by[$h] ?? null; $n = $r ? (int)$r['up_n'] + (int)$r['bad_n'] : 0;
        $out[] = ['host' => $h, 'checks' => $n, 'uptime' => $n ? round(100 * (int)$r['up_n'] / $n, 3) : null,
            'avg_ms' => $r && (int)$r['ms_n'] ? (int)round((int)$r['ms_sum'] / (int)$r['ms_n']) : null, 'outages' => $r ? (int)$r['outages'] : 0, 'down_min' => $r ? (int)round((int)$r['down_s'] / 60) : 0, 'days' => $r ? (int)$r['days'] : 0];
    }
    return $out;
}

function month_bounds(string $ym): ?array {
    if (!preg_match('/^(\d{4})-(0[1-9]|1[0-2])$/', $ym, $m)) return null;
    $first = sprintf('%04d-%02d-01', (int)$m[1], (int)$m[2]);
    return [$first, gmdate('Y-m-t', strtotime($first . ' UTC'))];
}
function fmt_down(int $min): string {
    if ($min < 1) return 'none';
    if ($min < 90) return $min . ' min';
    $h = intdiv($min, 60); return $h . ' h ' . ($min % 60) . ' min';
}

/** Email the previous month's report to every Pro member who watches at least one site. Each member gets it once per month. */
function send_monthly_reports(PDO $pdo): int {
    require_once __DIR__ . '/_plan.php'; require_once __DIR__ . '/_mail.php';
    $ym = gmdate('Y-m', strtotime('first day of last month 00:00 UTC'));
    [$from, $to] = month_bounds($ym);
    $label = gmdate('F Y', strtotime($from . ' UTC'));
    $site = rtrim((config()['site'] ?? 'https://siteupdown.com'), '/');
    $n = 0;
    $users = $pdo->query('SELECT u.id, u.email, u.name FROM users u WHERE ' . pro_users_sql('u') . ' AND EXISTS (SELECT 1 FROM watchlist w WHERE w.user_id=u.id)')->fetchAll();
    foreach ($users as $u) {
        $key = 'rep:' . $ym . ':' . $u['id'];
        try { $pdo->prepare('INSERT INTO billing_events (id, ts) VALUES (?,?)')->execute([$key, sql_now()]); } catch (Throwable $e) { continue; }   // already sent
        $rows = report_rows($pdo, (int)$u['id'], $from, $to);
        $html = '<table role="presentation" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:14px"><tr style="text-align:left;border-bottom:2px solid #111"><th>Site</th><th>Uptime</th><th>Outages</th><th>Time down</th><th>Avg response</th></tr>';
        $txt = '';
        foreach ($rows as $r) {
            $h = htmlspecialchars($r['host'], ENT_QUOTES, 'UTF-8');
            $up = $r['uptime'] === null ? 'no data' : $r['uptime'] . '%';
            $html .= "<tr style=\"border-bottom:1px solid #ddd\"><td><b>$h</b></td><td>$up</td><td>{$r['outages']}</td><td>" . fmt_down($r['down_min']) . '</td><td>' . ($r['avg_ms'] !== null ? $r['avg_ms'] . ' ms' : '-') . '</td></tr>';
            $txt .= "{$r['host']}: uptime $up, {$r['outages']} outages, down " . fmt_down($r['down_min']) . "\n";
        }
        $html .= '</table><p style="font-size:13px;color:#555">Measured by siteupdown.com from our own server, times in UTC. This is a guide from our own checks, not a service-level guarantee.</p>';
        $name = htmlspecialchars($u['name'], ENT_QUOTES, 'UTF-8');
        try {
            sud_email($u['email'], "Your $label uptime report", "Your $label uptime report", "<p>Hi $name,</p><p>Here is how the sites on your watchlist did last month.</p>$html",
                "Hi {$u['name']},\n\nHere is how the sites on your watchlist did in $label.\n\n$txt\nFull report and CSV: $site/account", 'Open your reports', $site . '/account');
            $n++;
        } catch (Throwable $e) {}
    }
    return $n;
}
