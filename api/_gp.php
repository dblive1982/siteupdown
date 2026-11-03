<?php
// Globalping (https://globalping.io) client: runs the same request from probes around the world.
declare(strict_types=1);

const GP_BASE = 'https://api.globalping.io/v1';

function gp_request(string $method, string $path, ?array $body = null): array {
    $c = config() ?: [];
    $base = $c['globalping_base'] ?? GP_BASE; // overridable for tests
    $ch = curl_init($base . $path);
    $h = ['Accept: application/json', 'Content-Type: application/json', 'User-Agent: siteupdown.com'];
    if (!empty($c['globalping_token'])) $h[] = 'Authorization: Bearer ' . $c['globalping_token'];
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 12, CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_CUSTOMREQUEST => $method, CURLOPT_HTTPHEADER => $h,
    ]);
    if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
    $raw = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    $d = is_string($raw) ? json_decode($raw, true) : null;
    return ['code' => $code, 'data' => is_array($d) ? $d : []];
}

/** The twelve places we ask. If a country has no probe free, we fall back to continents. */
function gp_locations(): array {
    $countries = ['US', 'CA', 'BR', 'GB', 'DE', 'FR', 'ZA', 'AE', 'IN', 'JP', 'SG', 'AU'];
    return array_map(fn($c) => ['country' => $c, 'limit' => 1], $countries);
}
function gp_fallback_locations(): array {
    return [['continent' => 'NA', 'limit' => 2], ['continent' => 'SA', 'limit' => 1], ['continent' => 'EU', 'limit' => 3],
            ['continent' => 'AF', 'limit' => 1], ['continent' => 'AS', 'limit' => 3], ['continent' => 'OC', 'limit' => 2]];
}

function gp_start(string $host): ?string {
    if (function_exists('probe_alias_get') && ($al = probe_alias_get($host))) $host = $al;     // ask for the address that really answers
    $opts = ['request' => ['method' => 'GET', 'path' => '/'], 'protocol' => 'HTTPS', 'port' => 443];
    foreach ([gp_locations(), gp_fallback_locations()] as $locs) {
        $r = gp_request('POST', '/measurements', ['type' => 'http', 'target' => $host, 'locations' => $locs, 'measurementOptions' => $opts]);
        if (in_array($r['code'], [200, 202], true) && !empty($r['data']['id'])) return (string)$r['data']['id'];
        if ($r['code'] === 429) return null; // rate limited: do not hammer
    }
    return null;
}

/** Turn a Globalping measurement into our map data. Returns null while it is still running. */
function gp_summarise(array $m): ?array {
    if (($m['status'] ?? '') === 'in-progress' && empty($m['results'])) return null;
    $probes = []; $ms = [];
    foreach (($m['results'] ?? []) as $r) {
        $p = $r['probe'] ?? []; $res = $r['result'] ?? [];
        $code = (int)($res['statusCode'] ?? 0);
        $state = 'none';
        if (($res['status'] ?? '') === 'finished' && $code > 0) {
            if (in_array($code, [401, 403, 429], true)) $state = 'blocked';
            elseif ($code >= 500) $state = 'error';
            else $state = 'ok';
        }
        $t = $res['timings']['total'] ?? null;
        if ($state !== 'none' && is_numeric($t)) $ms[] = (int)round((float)$t);
        $probes[] = [
            'country' => (string)($p['country'] ?? ''), 'city' => (string)($p['city'] ?? ''), 'continent' => (string)($p['continent'] ?? ''),
            'lat' => isset($p['latitude']) ? round((float)$p['latitude'], 2) : null, 'lon' => isset($p['longitude']) ? round((float)$p['longitude'], 2) : null,
            'state' => $state, 'code' => $code ?: null, 'ms' => is_numeric($t) ? (int)round((float)$t) : null,
        ];
    }
    sort($ms);
    $n = count($ms);
    $median = $n ? ($n % 2 ? $ms[intdiv($n, 2)] : (int)round(($ms[$n / 2 - 1] + $ms[$n / 2]) / 2)) : null;
    $reach = count(array_filter($probes, fn($x) => $x['state'] === 'ok'));
    return ['done' => ($m['status'] ?? '') === 'finished', 'probes' => $probes, 'total' => count($probes), 'reachable' => $reach, 'median_ms' => $median];
}

/** Cautious plain-English verdict from the server check plus the regional picture. */
function combined_verdict(array $server, ?array $reg): array {
    $v = $server['verdict'];
    if (!$reg || !$reg['done'] || $reg['total'] === 0) return ['key' => $v, 'text' => ''];
    $ok = $reg['reachable']; $tot = $reg['total'];
    $blocked = count(array_filter($reg['probes'], fn($x) => $x['state'] === 'blocked'));
    $responded = $ok + $blocked + count(array_filter($reg['probes'], fn($x) => $x['state'] === 'error'));
    if ($ok === $tot) return ['key' => 'up', 'text' => 'Up for everyone we asked. If it fails for you, the problem is likely on your side (network, DNS, browser or device).'];
    if ($ok === 0 && $responded === 0 && $v !== 'up') return ['key' => 'down-everywhere', 'text' => 'No probe could reach it, and neither could our server. It looks down for everyone, but this is a snapshot, not proof.'];
    if ($ok === 0 && $blocked > 0) return ['key' => 'blocked', 'text' => 'It answered, but it is blocking automated checks, so we cannot tell what a real visitor sees.'];
    return ['key' => 'partial', 'text' => "Reachable from $ok of $tot places. It may be down only in some regions. Check the map to see where it stops."];
}

/** Before calling a site down: can independent probes in three countries reach it? Cached for 30 minutes per site. True means at least one can, so it is blocking us rather than being down. */
function corroborate_alive(string $host): bool {
    $pdo = db(); $orig = $host;
    $c = $pdo->prepare('SELECT alive, ts FROM corroboration WHERE host=?'); $c->execute([$orig]); $c = $c->fetch();
    if ($c && (int)$c['ts'] > time() - 1800) return (bool)$c['alive'];
    if (function_exists('probe_alias_get') && ($al = probe_alias_get($host))) $host = $al;
    $opts = ['request' => ['method' => 'GET', 'path' => '/'], 'protocol' => 'HTTPS', 'port' => 443];
    $r = gp_request('POST', '/measurements', ['type' => 'http', 'target' => $host, 'locations' => [['country' => 'US', 'limit' => 1], ['country' => 'GB', 'limit' => 1], ['country' => 'DE', 'limit' => 1]], 'measurementOptions' => $opts]);
    if (!in_array($r['code'], [200, 202], true) || empty($r['data']['id'])) return false;   // cannot ask: rely on our own evidence
    $alive = null;
    for ($i = 0; $i < 6; $i++) {
        usleep(1200000);
        $m = gp_request('GET', '/measurements/' . rawurlencode((string)$r['data']['id']));
        if (($m['data']['status'] ?? '') === 'in-progress') continue;
        $alive = false;
        foreach (($m['data']['results'] ?? []) as $x) { $code = (int)($x['result']['statusCode'] ?? 0); if ($code > 0 && $code < 500) $alive = true; }
        break;
    }
    if ($alive === null) return false;
    $pdo->prepare('DELETE FROM corroboration WHERE host=?')->execute([$orig]);
    $pdo->prepare('INSERT INTO corroboration (host, alive, ts) VALUES (?,?,?)')->execute([$orig, $alive ? 1 : 0, time()]);
    return $alive;
}
