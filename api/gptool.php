<?php
// Worldwide tools on the Globalping network. POST {tool: ping|dns|trace, address, qtype?} starts a run and returns {id};
// GET ?id=...&tool=... returns the (possibly partial) results so the page can fill in as probes answer.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_gp.php';

function gpt_clean_ms($v): ?float { return is_numeric($v) ? round((float)$v, 1) : null; }

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    $in = read_post();
    $tool = (string)($in['tool'] ?? '');
    if (!in_array($tool, ['ping', 'dns', 'trace'], true)) out(422, ['error' => 'Unknown tool.']);
    $t = parse_target((string)($in['address'] ?? ''));
    if (!$t) out(422, ['error' => 'Please enter a website address like example.com.']);
    $host = $t[0];
    if (filter_var($host, FILTER_VALIDATE_IP) && $tool === 'dns') out(422, ['error' => 'Please enter a domain name, not an IP address.']);
    $rp = resolve_public($host);
    if (!filter_var($host, FILTER_VALIDATE_IP) && $rp['error']) out(200, ['error' => $rp['error'] === 'blocked' ? 'We can only test public websites.' : 'That address does not exist (no DNS record was found).', 'host' => $host]);
    if (filter_var($host, FILTER_VALIDATE_IP) && !$rp['ips']) out(200, ['error' => 'We can only test public addresses.', 'host' => $host]);
    throttle('gptool', 8, 10);
    note_attempt('gptool');
    if ($tool === 'dns') {
        $qt = strtoupper((string)($in['qtype'] ?? 'A'));
        if (!in_array($qt, ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT'], true)) $qt = 'A';
        $opts = ['query' => ['type' => $qt]];
        $type = 'dns';
    } elseif ($tool === 'ping') { $opts = ['packets' => 3]; $type = 'ping'; }
    else { $opts = []; $type = 'traceroute'; }
    $locs = $tool === 'trace' ? array_slice(gp_locations(), 0, 15) : gp_locations();
    if ($tool === 'trace') $locs = array_map(fn($c) => ['country' => $c, 'limit' => 1], ['US', 'GB', 'DE', 'BR', 'IN', 'SG', 'JP', 'AU']);
    $body = ['type' => $type, 'target' => $host, 'locations' => $locs];
    if ($opts) $body['measurementOptions'] = $opts;
    $id = null;
    foreach ([$locs, $tool === 'trace' ? null : gp_locations_basic(), gp_fallback_locations()] as $try) {
        if (!$try) continue;
        $body['locations'] = $try;
        $r = gp_request('POST', '/measurements', $body);
        if (in_array($r['code'], [200, 202], true) && !empty($r['data']['id'])) { $id = (string)$r['data']['id']; break; }
        if ($r['code'] === 429) break;
    }
    if (!$id) out(503, ['error' => 'The worldwide probes are busy right now. Please try again in a minute.']);
    out(200, ['id' => $id, 'host' => $host, 'tool' => $tool]);
}

$id = (string)($_GET['id'] ?? ''); $tool = (string)($_GET['tool'] ?? '');
if (!preg_match('/^[A-Za-z0-9]{8,40}$/', $id) || !in_array($tool, ['ping', 'dns', 'trace'], true)) out(422, ['error' => 'Bad request.']);
$r = gp_request('GET', '/measurements/' . rawurlencode($id));
if ($r['code'] !== 200) out(200, ['pending' => true]);
$m = $r['data'];
$done = ($m['status'] ?? '') !== 'in-progress';
$rows = [];
foreach (($m['results'] ?? []) as $x) {
    $p = $x['probe'] ?? []; $res = $x['result'] ?? [];
    $row = ['country' => (string)($p['country'] ?? ''), 'city' => (string)($p['city'] ?? ''), 'network' => mb_substr((string)($p['network'] ?? ''), 0, 40),
            'lat' => isset($p['latitude']) ? round((float)$p['latitude'], 2) : null, 'lon' => isset($p['longitude']) ? round((float)$p['longitude'], 2) : null,
            'ok' => ($res['status'] ?? '') === 'finished'];
    if ($tool === 'ping') {
        $s = $res['stats'] ?? [];
        $row += ['ip' => (string)($res['resolvedAddress'] ?? ''), 'min' => gpt_clean_ms($s['min'] ?? null), 'avg' => gpt_clean_ms($s['avg'] ?? null), 'max' => gpt_clean_ms($s['max'] ?? null), 'loss' => isset($s['loss']) ? round((float)$s['loss'], 1) : null];
        if ($row['ok'] && ($row['avg'] === null)) $row['ok'] = false;
    } elseif ($tool === 'dns') {
        $ans = [];
        foreach (($res['answers'] ?? []) as $a) $ans[] = ['type' => (string)($a['type'] ?? ''), 'value' => mb_substr((string)($a['value'] ?? ''), 0, 300), 'ttl' => isset($a['ttl']) ? (int)$a['ttl'] : null];
        $row += ['answers' => array_slice($ans, 0, 12), 'resolver' => (string)($res['resolver'] ?? ''), 'ms' => gpt_clean_ms($res['timings']['total'] ?? null)];
    } else {
        $hops = [];
        foreach (($res['hops'] ?? []) as $h) {
            $rtts = array_values(array_filter(array_map(fn($t) => isset($t['rtt']) ? (float)$t['rtt'] : null, $h['timings'] ?? []), fn($v) => $v !== null));
            $hops[] = ['host' => mb_substr((string)($h['resolvedHostname'] ?? $h['resolvedAddress'] ?? ''), 0, 80), 'ip' => (string)($h['resolvedAddress'] ?? ''), 'ms' => $rtts ? round(array_sum($rtts) / count($rtts), 1) : null];
        }
        $row += ['hops' => array_slice($hops, 0, 40), 'ip' => (string)($res['resolvedAddress'] ?? '')];
    }
    $rows[] = $row;
}
out(200, ['done' => $done, 'tool' => $tool, 'results' => $rows]);
