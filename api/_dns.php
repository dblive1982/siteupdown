<?php
// DNS records and domain registration details (thorough checks only).
declare(strict_types=1);

// The registrable part of a host: www.example.co.uk -> example.co.uk
function registrable_domain(string $host): string {
    $p = explode('.', strtolower($host));
    if (count($p) <= 2) return implode('.', $p);
    $two = ['co', 'com', 'org', 'net', 'gov', 'ac', 'edu', 'ltd', 'plc', 'me', 'nhs', 'sch'];
    $n = (in_array($p[count($p) - 2], $two, true) && strlen($p[count($p) - 1]) === 2) ? 3 : 2;
    return implode('.', array_slice($p, -$n));
}

function dns_info(string $host): array {
    $dom = registrable_domain($host);
    $out = ['domain' => $dom, 'a' => [], 'aaaa' => [], 'cname' => null, 'mx' => [], 'ns' => [], 'spf' => false, 'dmarc' => false];
    $g = function (string $name, int $type) { $r = @dns_get_record($name, $type); return is_array($r) ? $r : []; };
    foreach ($g($host, DNS_A) as $r) if (!empty($r['ip'])) $out['a'][] = $r['ip'];
    foreach ($g($host, DNS_AAAA) as $r) if (!empty($r['ipv6'])) $out['aaaa'][] = $r['ipv6'];
    foreach ($g($host, DNS_CNAME) as $r) if (!empty($r['target'])) { $out['cname'] = $r['target']; break; }
    foreach ($g($dom, DNS_MX) as $r) if (!empty($r['target'])) $out['mx'][] = ['pri' => (int)($r['pri'] ?? 0), 'host' => $r['target']];
    usort($out['mx'], fn($a, $b) => $a['pri'] <=> $b['pri']);
    foreach ($g($dom, DNS_NS) as $r) if (!empty($r['target'])) $out['ns'][] = $r['target'];
    foreach ($g($dom, DNS_TXT) as $r) if (isset($r['txt']) && stripos($r['txt'], 'v=spf1') === 0) $out['spf'] = true;
    foreach ($g('_dmarc.' . $dom, DNS_TXT) as $r) if (isset($r['txt']) && stripos($r['txt'], 'v=DMARC1') === 0) $out['dmarc'] = true;
    foreach (['a', 'aaaa', 'ns'] as $k) $out[$k] = array_slice(array_values(array_unique($out[$k])), 0, 8);
    $out['mx'] = array_slice($out['mx'], 0, 6);
    $out['whois'] = domain_whois($dom);
    return $out;
}

// Registration dates from RDAP, cached for a week (null when the registry gives nothing).
function domain_whois(string $dom): ?array {
    if (!preg_match('/^[a-z0-9.-]{3,253}$/', $dom) || filter_var($dom, FILTER_VALIDATE_IP)) return null;
    $pdo = db();
    $q = $pdo->prepare('SELECT data, checked_at FROM domain_info WHERE domain=?');
    $q->execute([$dom]);
    $row = $q->fetch();
    if ($row && $row['checked_at'] > gmdate('Y-m-d H:i:s', time() - 7 * 86400)) return json_decode($row['data'], true) ?: null;
    $base = rtrim((string)(config()['rdap_base'] ?? 'https://rdap.org/domain/'), '/') . '/';
    $ch = curl_init($base . $dom);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true, CURLOPT_MAXREDIRS => 3, CURLOPT_TIMEOUT => 6, CURLOPT_CONNECTTIMEOUT => 4,
        CURLOPT_PROTOCOLS => CURLPROTO_HTTPS | CURLPROTO_HTTP, CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTPS, CURLOPT_USERAGENT => 'siteupdown.com checker',
        CURLOPT_HTTPHEADER => ['Accept: application/rdap+json, application/json'], CURLOPT_MAXFILESIZE => 600000]);
    $body = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    $out = null;
    $j = ($code === 200 && is_string($body)) ? json_decode($body, true) : null;
    if (is_array($j)) {
        $out = ['expires' => null, 'created' => null, 'registrar' => null];
        foreach ($j['events'] ?? [] as $e) {
            $d = isset($e['eventDate']) ? strtotime((string)$e['eventDate']) : false;
            if (!$d) continue;
            if (($e['eventAction'] ?? '') === 'expiration') $out['expires'] = gmdate('Y-m-d', $d);
            if (($e['eventAction'] ?? '') === 'registration') $out['created'] = gmdate('Y-m-d', $d);
        }
        foreach ($j['entities'] ?? [] as $en) {
            if (in_array('registrar', $en['roles'] ?? [], true)) {
                foreach ($en['vcardArray'][1] ?? [] as $v) if (($v[0] ?? '') === 'fn') { $out['registrar'] = mb_substr((string)($v[3] ?? ''), 0, 80); break 2; }
            }
        }
        if ($out['expires']) $out['days_left'] = (int)floor((strtotime($out['expires'] . ' UTC') - time()) / 86400);
        if (!$out['expires'] && !$out['created'] && !$out['registrar']) $out = null;
    }
    if ($out !== null || $code === 404 || $code === 200) { // do not cache network failures
        $pdo->prepare('REPLACE INTO domain_info (domain, data, checked_at) VALUES (?,?,?)')->execute([$dom, json_encode($out), sql_now()]);
    }
    return $out;
}
