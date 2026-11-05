<?php
// POST {tool, address} -> result for one of the tools pages (dns, headers, ssl, redirects, whois, mx, robots, secheaders).
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
require __DIR__ . '/_tls.php';
require __DIR__ . '/_dns.php';
require __DIR__ . '/_fetch.php';
$in = read_post();
$tool = (string)($in['tool'] ?? '');
if (!in_array($tool, ['dns', 'headers', 'ssl', 'redirects', 'whois', 'mx', 'robots', 'secheaders', 'ports'], true)) out(422, ['error' => 'Unknown tool.']);
$t = parse_target((string)($in['address'] ?? ''));
if (!$t) out(422, ['error' => 'Please enter a website address like example.com.']);
[$host, $path, $scheme] = $t;
$isIp = (bool)filter_var($host, FILTER_VALIDATE_IP);
throttle('tool', 40, 10);
note_attempt('tool');
$errText = ['dns' => 'That address does not exist (no DNS record was found).', 'blocked' => 'We can only test public websites.', 'timeout' => 'The site did not answer in time.', 'ssl' => 'The secure (HTTPS) connection failed.', 'connect' => 'We could not connect to that site.', 'redirects' => 'The site redirects too many times.', 'loop' => 'The site redirects in a circle.'];
$fail = fn(?string $e) => out(200, ['tool' => $tool, 'host' => $host, 'error' => $errText[$e ?? ''] ?? 'We could not reach that site.', 'code' => $e]);

if ($tool === 'dns') {
    if ($isIp) out(422, ['error' => 'Please enter a domain name, not an IP address.']);
    $types = ['A' => DNS_A, 'AAAA' => DNS_AAAA, 'CNAME' => DNS_CNAME, 'MX' => DNS_MX, 'NS' => DNS_NS, 'TXT' => DNS_TXT, 'SOA' => DNS_SOA];
    if (defined('DNS_CAA')) $types['CAA'] = constant('DNS_CAA');
    $recs = [];
    foreach ($types as $name => $const) {
        $rows = @dns_get_record($host, $const);
        if (!is_array($rows)) continue;
        foreach ($rows as $r) {
            $val = match ($name) {
                'A' => $r['ip'] ?? '', 'AAAA' => $r['ipv6'] ?? '', 'CNAME', 'NS' => $r['target'] ?? '',
                'MX' => ($r['pri'] ?? 0) . ' ' . ($r['target'] ?? ''), 'TXT' => $r['txt'] ?? '',
                'SOA' => trim(($r['mname'] ?? '') . ' ' . ($r['rname'] ?? '') . ' serial ' . ($r['serial'] ?? '')),
                'CAA' => trim(($r['flags'] ?? 0) . ' ' . ($r['tag'] ?? '') . ' ' . ($r['value'] ?? '')), default => ''};
            if ($val === '' || $val === ' ') continue;
            $recs[] = ['type' => $name, 'value' => mb_substr((string)$val, 0, 600), 'ttl' => isset($r['ttl']) ? (int)$r['ttl'] : null];
            if (count($recs) >= 80) break 2;
        }
    }
    out(200, ['tool' => $tool, 'host' => $host, 'records' => $recs]);
}

if ($tool === 'mx') {
    if ($isIp) out(422, ['error' => 'Please enter a domain name, not an IP address.']);
    $dom = $host; $mx = @dns_get_record($dom, DNS_MX);
    if ((!is_array($mx) || !$mx) && registrable_domain($host) !== $host) { $dom = registrable_domain($host); $mx = @dns_get_record($dom, DNS_MX); }
    $rows = [];
    foreach (is_array($mx) ? $mx : [] as $r) {
        if (empty($r['target'])) continue;
        $ips = [];
        foreach ((array)@dns_get_record($r['target'], DNS_A) as $a) if (!empty($a['ip'])) $ips[] = $a['ip'];
        $rows[] = ['pri' => (int)($r['pri'] ?? 0), 'host' => $r['target'], 'ips' => array_slice($ips, 0, 4), 'ttl' => (int)($r['ttl'] ?? 0)];
    }
    usort($rows, fn($a, $b) => $a['pri'] <=> $b['pri']);
    $spf = []; foreach ((array)@dns_get_record($dom, DNS_TXT) as $r) if (isset($r['txt']) && stripos($r['txt'], 'v=spf1') === 0) $spf[] = mb_substr($r['txt'], 0, 500);
    $dmarc = []; foreach ((array)@dns_get_record('_dmarc.' . $dom, DNS_TXT) as $r) if (isset($r['txt']) && stripos($r['txt'], 'v=DMARC1') === 0) $dmarc[] = mb_substr($r['txt'], 0, 500);
    out(200, ['tool' => $tool, 'host' => $host, 'domain' => $dom, 'mx' => array_slice($rows, 0, 10), 'spf' => $spf, 'dmarc' => $dmarc]);
}

if ($tool === 'whois') {
    if ($isIp) out(422, ['error' => 'Please enter a domain name, not an IP address.']);
    $dom = registrable_domain($host);
    $w = domain_whois($dom);
    $ns = []; foreach ((array)@dns_get_record($dom, DNS_NS) as $r) if (!empty($r['target'])) $ns[] = $r['target'];
    out(200, ['tool' => $tool, 'host' => $host, 'domain' => $dom, 'whois' => $w, 'ns' => array_slice(array_values(array_unique($ns)), 0, 8)]);
}

if ($tool === 'ports') {
    $allowed = [21 => 'FTP', 22 => 'SSH', 25 => 'SMTP', 53 => 'DNS (TCP)', 80 => 'HTTP', 110 => 'POP3', 143 => 'IMAP', 443 => 'HTTPS', 465 => 'SMTP over SSL', 587 => 'SMTP submission', 993 => 'IMAP over SSL', 995 => 'POP3 over SSL',
                3306 => 'MySQL', 3389 => 'Remote Desktop', 5432 => 'PostgreSQL', 8080 => 'Alternate web', 8443 => 'Alternate HTTPS', 25565 => 'Minecraft (Java)'];
    $port = (int)($in['port'] ?? 443);
    if (!isset($allowed[$port])) out(422, ['error' => 'Please pick one of the listed ports.']);
    $rp = resolve_public($host);
    if ($rp['error']) $fail($rp['error']);
    $ip = $rp['ips'][0];
    $addr = filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6) ? '[' . $ip . ']' : $ip;
    $t0 = microtime(true); $en = 0; $es = '';
    $fp = @stream_socket_client('tcp://' . $addr . ':' . $port, $en, $es, 4.0, STREAM_CLIENT_CONNECT);
    $ms = (int)round((microtime(true) - $t0) * 1000);
    if ($fp) { fclose($fp); $state = 'open'; }
    elseif ($en === 111 || $en === 10061 || stripos($es, 'refused') !== false) $state = 'closed';
    else $state = 'filtered';
    out(200, ['tool' => $tool, 'host' => $host, 'ip' => $ip, 'port' => $port, 'service' => $allowed[$port], 'state' => $state, 'ms' => $ms]);
}

if ($tool === 'ssl') {
    $rp = resolve_public($host);
    if ($rp['error']) $fail($rp['error']);
    $c = tls_inspect($host, $rp['ips'][0]);
    out(200, ['tool' => $tool, 'host' => $host, 'cert' => $c]);
}

if ($tool === 'redirects') {
    $f = sud_follow($host, $path, $scheme === 'https', 8);
    $total = 0; foreach ($f['hops'] as $h) $total += (int)($h['ms'] ?? 0);
    $f['hops'][0]['ip'] = $f['last']['ip'] ?? null;
    out(200, ['tool' => $tool, 'host' => $host, 'start' => ($scheme === 'https' ? 'https://' : 'http://') . $host . $path, 'hops' => $f['hops'], 'error' => $f['err'] ? ($errText[$f['err']] ?? null) : null, 'code' => $f['err'], 'total_ms' => $total]);
}

if ($tool === 'headers' || $tool === 'secheaders') {
    $f = sud_follow($host, $path, $scheme === 'https', 8);
    $r = $f['last'];
    if (!$r || $r['code'] === null) $fail($f['err'] ?? 'connect');
    $fin = ($f['final']['https'] ? 'https://' : 'http://') . $f['final']['host'] . $f['final']['path'];
    if ($tool === 'headers') {
        out(200, ['tool' => $tool, 'host' => $host, 'url' => mb_substr($fin, 0, 300), 'code' => $r['code'], 'version' => $r['version'], 'ms' => $r['ms'], 'ip' => $r['ip'], 'redirects' => count($f['hops']) - 1, 'headers' => $r['headers'], 'note' => $f['err'] ? ($errText[$f['err']] ?? null) : null]);
    }
    $h = fn(string $n) => sud_header($r, $n);
    $items = []; $score = 0;
    $add = function (string $name, int $pts, ?string $val, string $status, string $good, string $bad) use (&$items, &$score) {
        $score += $status === 'ok' ? $pts : ($status === 'warn' ? (int)round($pts / 2) : 0);
        $items[] = ['name' => $name, 'value' => $val !== null ? mb_substr($val, 0, 300) : null, 'status' => $status, 'text' => $status === 'missing' ? $bad : $good, 'points' => $pts];
    };
    $hsts = $h('strict-transport-security');
    if (!$f['final']['https']) $add('Strict-Transport-Security', 20, null, 'missing', '', 'The site was not served over HTTPS, so HSTS cannot apply. Serve the site over HTTPS first.');
    elseif ($hsts === null) $add('Strict-Transport-Security', 20, null, 'missing', '', 'Not set. HSTS tells browsers to always use HTTPS for this site.');
    else { preg_match('/max-age=(\d+)/i', $hsts, $m); $age = (int)($m[1] ?? 0);
        $add('Strict-Transport-Security', 20, $hsts, $age >= 15552000 ? 'ok' : 'warn', 'Browsers are told to use HTTPS only.', ''); if ($age < 15552000) $items[count($items) - 1]['text'] = 'Set, but max-age is short. Six months (15552000) or more is recommended.'; }
    $csp = $h('content-security-policy');
    $add('Content-Security-Policy', 25, $csp, $csp === null ? 'missing' : ((stripos($csp, "'unsafe-inline'") !== false && stripos($csp, 'script-src') !== false) ? 'warn' : 'ok'), $csp !== null && stripos($csp, "'unsafe-inline'") !== false && stripos($csp, 'script-src') !== false ? "Set, but it allows 'unsafe-inline' scripts, which weakens it." : 'A policy limits where scripts and other content can load from.', 'Not set. A Content-Security-Policy is the strongest protection against injected scripts.');
    $xfo = $h('x-frame-options');
    $fa = $csp !== null && stripos($csp, 'frame-ancestors') !== false;
    $add('X-Frame-Options', 10, $xfo ?? ($fa ? 'frame-ancestors (in CSP)' : null), ($xfo !== null || $fa) ? 'ok' : 'missing', 'The page cannot be embedded in other sites, which blocks clickjacking.', 'Not set. Without it, other sites can embed this page in a frame.');
    $xc = $h('x-content-type-options');
    $add('X-Content-Type-Options', 15, $xc, ($xc !== null && stripos($xc, 'nosniff') !== false) ? 'ok' : 'missing', 'Browsers will not guess file types.', 'Not set to nosniff. Browsers may guess file types, which can be abused.');
    $rp = $h('referrer-policy');
    $add('Referrer-Policy', 10, $rp, $rp !== null ? 'ok' : 'missing', 'Controls how much address information is shared when visitors follow links.', 'Not set. Browsers choose how much of the address to share with other sites.');
    $pp = $h('permissions-policy');
    $add('Permissions-Policy', 10, $pp, $pp !== null ? 'ok' : 'missing', 'Limits which browser features (camera, location and so on) the page may use.', 'Not set. Optional, but useful to switch off features the site does not need.');
    $co = $h('cross-origin-opener-policy');
    $add('Cross-Origin-Opener-Policy', 10, $co, $co !== null ? 'ok' : 'missing', 'Isolates the page from windows opened by other sites.', 'Not set. Optional extra isolation between windows.');
    $leaks = []; foreach (['server', 'x-powered-by'] as $n) { $v = $h($n); if ($v !== null && preg_match('/\d/', $v)) $leaks[] = $n . ': ' . mb_substr($v, 0, 80); }
    $grade = $score >= 90 ? 'A' : ($score >= 75 ? 'B' : ($score >= 55 ? 'C' : ($score >= 35 ? 'D' : 'F')));
    out(200, ['tool' => $tool, 'host' => $host, 'url' => mb_substr($fin, 0, 300), 'code' => $r['code'], 'score' => $score, 'grade' => $grade, 'items' => $items, 'leaks' => $leaks]);
}

if ($tool === 'robots') {
    $f = sud_follow($host, '/robots.txt', true, 4, 200000);
    $r = $f['last'];
    if (!$r || $r['code'] === null) {
        $f = sud_follow($host, '/robots.txt', false, 4, 200000); $r = $f['last'];
        if (!$r || $r['code'] === null) $fail($f['err'] ?? 'connect');
    }
    $fin = ($f['final']['https'] ? 'https://' : 'http://') . $f['final']['host'] . '/robots.txt';
    $res = ['tool' => $tool, 'host' => $host, 'url' => $fin, 'code' => $r['code'], 'found' => false, 'groups' => [], 'sitemaps' => [], 'text' => '', 'issues' => []];
    $ct = (string)sud_header($r, 'content-type');
    if ($r['code'] === 200 && $r['body'] !== '' && !preg_match('~text/html~i', $ct)) {
        $res['found'] = true;
        $res['text'] = mb_substr(mb_convert_encoding($r['body'], 'UTF-8', 'UTF-8'), 0, 8000);
        $cur = null; $groups = [];
        foreach (preg_split('/\r\n|\r|\n/', $r['body']) as $line) {
            $line = trim(preg_replace('/#.*$/', '', $line));
            if ($line === '' || !str_contains($line, ':')) continue;
            [$k, $v] = array_map('trim', explode(':', $line, 2)); $k = strtolower($k);
            if ($k === 'sitemap') { if (count($res['sitemaps']) < 10) $res['sitemaps'][] = mb_substr($v, 0, 300); continue; }
            if ($k === 'user-agent') { if ($cur === null || $cur['has_rules']) { $groups[] = ['agents' => [], 'disallow' => [], 'allow' => [], 'has_rules' => false]; $cur = &$groups[count($groups) - 1]; } $cur['agents'][] = mb_substr($v, 0, 80); continue; }
            if ($cur === null) continue;
            if ($k === 'disallow') { $cur['has_rules'] = true; if ($v !== '' && count($cur['disallow']) < 40) $cur['disallow'][] = mb_substr($v, 0, 200); }
            if ($k === 'allow') { $cur['has_rules'] = true; if ($v !== '' && count($cur['allow']) < 40) $cur['allow'][] = mb_substr($v, 0, 200); }
        }
        unset($cur);
        foreach ($groups as $g) $res['groups'][] = ['agents' => $g['agents'], 'disallow' => $g['disallow'], 'allow' => $g['allow']];
        foreach ($res['groups'] as $g) if (in_array('*', $g['agents'], true) && in_array('/', $g['disallow'], true) && !$g['allow']) $res['issues'][] = ['level' => 'bad', 'text' => 'Disallow: / for all crawlers. This blocks search engines from the whole site.'];
        if (!$res['sitemaps']) $res['issues'][] = ['level' => 'warn', 'text' => 'No Sitemap line. Adding one helps search engines find your pages.'];
        if (!$res['groups']) $res['issues'][] = ['level' => 'warn', 'text' => 'No User-agent rules were found in this file.'];
    } elseif ($r['code'] === 404 || $r['code'] === 410) {
        $res['issues'][] = ['level' => 'info', 'text' => 'There is no robots.txt, which means crawlers may visit everything. That is fine, but a robots.txt lets you point to your sitemap.'];
    } else {
        $res['issues'][] = ['level' => 'warn', 'text' => 'robots.txt answered with HTTP ' . $r['code'] . ($r['code'] === 200 ? ' but did not look like a text file.' : '.')];
    }
    out(200, $res);
}
