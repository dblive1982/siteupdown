<?php
// Extra checks (a word that must be on the page, a port that must answer) and expiry warnings for SSL certificates and domains.
declare(strict_types=1);
require_once __DIR__ . '/_fetch.php';
require_once __DIR__ . '/_dns.php';
require_once __DIR__ . '/_track.php';

const XCHECK_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 5432, 8080, 8443];
const XCHECK_MAX = 5;

/** Run one extra check. Returns ['verdict' => up|down, 'ms' => int|null, 'detail' => string]. */
function xcheck_run(array $row): array {
    $host = $row['host'];
    if ($row['kind'] === 'port') {
        $rp = resolve_public($host);
        if ($rp['error'] || !$rp['ips']) return ['verdict' => 'down', 'ms' => null, 'detail' => $rp['error'] === 'blocked' ? 'address not allowed' : 'name not found'];
        $ip = $rp['ips'][0]; $port = (int)$row['param'];
        $t0 = microtime(true);
        $fp = @stream_socket_client('tcp://' . (str_contains($ip, ':') ? "[$ip]" : $ip) . ':' . $port, $en, $es, 5);
        $ms = (int)round((microtime(true) - $t0) * 1000);
        if ($fp) { fclose($fp); return ['verdict' => 'up', 'ms' => $ms, 'detail' => 'open']; }
        return ['verdict' => 'down', 'ms' => null, 'detail' => 'port closed or not answering'];
    }
    // keyword: the page must load and contain the text (first 600 KB, not case sensitive)
    $f = sud_follow($host, '/', true, 5, 600000);
    if (in_array($f['err'] ?? null, ['connect', 'ssl'], true)) $f = sud_follow($host, '/', false, 5, 600000);
    $last = $f['last'];
    if ($f['err'] || !$last || $last['code'] === null) return ['verdict' => 'down', 'ms' => null, 'detail' => 'page did not load'];
    if ($last['code'] >= 400) return ['verdict' => 'down', 'ms' => $last['ms'], 'detail' => 'HTTP ' . $last['code']];
    if (stripos((string)$last['body'], $row['param']) === false) return ['verdict' => 'down', 'ms' => $last['ms'], 'detail' => 'text not found'];
    return ['verdict' => 'up', 'ms' => $last['ms'], 'detail' => 'text found'];
}

function xcheck_title(array $r): string {
    return $r['kind'] === 'port' ? $r['host'] . ' port ' . $r['param'] : $r['host'] . ' page text "' . mb_substr($r['param'], 0, 40) . '"';
}

/** Store the result and, after two failures in a row (or on recovery), tell the owner. */
function xcheck_track(PDO $pdo, array $row, array $res): void {
    $now = sql_now(); $bad = $res['verdict'] === 'down';
    $state = $row['state']; $fails = (int)$row['fails']; $since = $row['since'];
    $alert = null;
    if ($bad) {
        $fails++;
        if ($state !== 'down' && $fails >= 2) { $state = 'down'; $since = $now; $alert = 'down'; }
    } else {
        if ($state === 'down') $alert = 'up';
        $state = 'up'; $fails = 0;
    }
    $pdo->prepare('UPDATE extra_checks SET state=?, fails=?, since=?, verdict=?, ms=?, detail=?, checked_at=? WHERE id=?')
        ->execute([$state, $fails, $since, $res['verdict'], $res['ms'], mb_substr($res['detail'], 0, 120), $now, $row['id']]);
    if ($alert) xcheck_notify($pdo, $row, $alert === 'down', $res['detail'], $alert === 'up' ? $row['since'] : null);
}

function xcheck_notify(PDO $pdo, array $row, bool $down, string $detail, ?string $since): void {
    $u = $pdo->prepare('SELECT id, email, name FROM users WHERE id=?'); $u->execute([$row['user_id']]);
    $u = $u->fetch();
    if (!$u) return;
    $site = rtrim((config()['site'] ?? 'https://siteupdown.com'), '/');
    $page = $site . '/monitor';
    $t = xcheck_title($row);
    $th = htmlspecialchars($t, ENT_QUOTES, 'UTF-8'); $nm = htmlspecialchars($u['name'], ENT_QUOTES, 'UTF-8');
    if ($down) {
        $why = $row['kind'] === 'port' ? 'is not answering' : 'check is failing (' . $detail . ')';
        sud_email($u['email'], $t . ' ' . $why, $t . ' ' . $why, "<p>Hi $nm,</p><p>Your extra check on <b>$th</b> has failed twice in a row ($detail). We will email you again when it passes.</p>",
            "Hi {$u['name']},\n\nYour extra check on $t has failed twice in a row ($detail). We will email you again when it passes.", 'Open Monitor', $page, '', 'down');
        push_user($pdo, (int)$u['id'], "\u{1F534} $t: $detail. Failed on two checks in a row.", $page);
    } else {
        $for = $since ? ' It was failing for ' . human_span(max(0, time() - strtotime($since . ' UTC'))) . '.' : '';
        sud_email($u['email'], $t . ' is passing again', $t . ' is passing again', "<p>Hi $nm,</p><p>Your extra check on <b>$th</b> is passing again.$for</p>",
            "Hi {$u['name']},\n\nYour extra check on $t is passing again.$for", 'Open Monitor', $page, '', 'up');
        push_user($pdo, (int)$u['id'], "\u{1F7E2} $t is passing again." . $for, $page);
    }
}

/** Warn watchers as an SSL certificate or domain gets close to its end date. Each warning level is sent once per renewal cycle. */
function expiry_check(PDO $pdo, string $name, string $kind, int $days, string $date): void {
    $levels = $kind === 'ssl' ? [1, 3, 7, 14, 30] : [1, 7, 14, 30, 60];
    $cur = $days < 0 ? 0 : null;
    if ($cur === null) foreach ($levels as $l) if ($days <= $l) { $cur = $l; break; }
    if ($cur === null) { $pdo->prepare('DELETE FROM expiry_state WHERE host=? AND kind=?')->execute([$name, $kind]); return; } // renewed
    $q = $pdo->prepare('SELECT level FROM expiry_state WHERE host=? AND kind=?'); $q->execute([$name, $kind]);
    $prev = $q->fetchColumn();
    if ($prev !== false && (int)$prev <= $cur) return; // already warned at this level (or a tighter one)
    $pdo->prepare('DELETE FROM expiry_state WHERE host=? AND kind=?')->execute([$name, $kind]);
    $pdo->prepare('INSERT INTO expiry_state (host, kind, level, ts) VALUES (?,?,?,?)')->execute([$name, $kind, $cur, sql_now()]);
    expiry_notify($pdo, $name, $kind, $days, $date);
}

function expiry_notify(PDO $pdo, string $name, string $kind, int $days, string $date): void {
    $q = $pdo->prepare('SELECT DISTINCT u.id, u.email, u.name FROM watchlist w JOIN users u ON u.id = w.user_id WHERE w.alerts=1 AND (w.host=? OR w.host LIKE ?)');
    $q->execute([$name, '%.' . $name]);
    $site = rtrim((config()['site'] ?? 'https://siteupdown.com'), '/');
    $page = $site . '/status/' . rawurlencode($name);
    $when = $days < 0 ? 'has expired' : ($days === 0 ? 'expires today' : 'expires in ' . $days . ' day' . ($days === 1 ? '' : 's'));
    $what = $kind === 'ssl' ? "The SSL certificate for $name" : "The domain name $name";
    $msg = "$what $when ($date).";
    $advice = $kind === 'ssl' ? 'Renew or reissue the certificate before then, or visitors will see a security warning instead of your site.'
        : 'Renew it with your domain registrar before then, or the site (and its email) will stop working.';
    $h = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
    foreach ($q->fetchAll() as $u) {
        $nm = htmlspecialchars($u['name'], ENT_QUOTES, 'UTF-8');
        sud_email($u['email'], ($kind === 'ssl' ? 'SSL certificate' : 'Domain') . " for $name $when", ($kind === 'ssl' ? 'SSL certificate' : 'Domain') . " $when",
            "<p>Hi $nm,</p><p>" . htmlspecialchars($msg, ENT_QUOTES, 'UTF-8') . "</p><p>$advice</p>", "Hi {$u['name']},\n\n$msg\n\n$advice", 'See live status', $page, '', 'warn');
        push_user($pdo, (int)$u['id'], "\u{26A0}\u{FE0F} $msg $advice", $page);
    }
}
