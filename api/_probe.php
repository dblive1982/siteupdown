<?php
// Server-side website check. Built to be safe to point at any address a visitor types:
//  - only http/https on the standard ports
//  - the address is resolved first and refused if ANY result is private/internal (SSRF protection)
//  - the connection is pinned to the checked IP, and every redirect is checked again
declare(strict_types=1);

const SUD_UA = 'Mozilla/5.0 (compatible; siteupdown.com status checker; +https://siteupdown.com)';

/** Turn what the visitor typed into [host, path] or null. Only the host and path are kept. */
function parse_target(string $in): ?array {
    $in = trim($in);
    if ($in === '' || strlen($in) > 300 || preg_match('/[\x00-\x20\x7f]/', $in)) return null;
    if (!preg_match('~^[a-z][a-z0-9+.-]*://~i', $in)) $in = 'https://' . $in;
    $p = parse_url($in);
    if (!$p || empty($p['host'])) return null;
    $scheme = strtolower($p['scheme'] ?? '');
    if (!in_array($scheme, ['http', 'https'], true)) return null;
    if (isset($p['user']) || isset($p['pass'])) return null;
    if (isset($p['port']) && !in_array((int)$p['port'], [80, 443], true)) return null;
    $host = strtolower(rtrim($p['host'], '.'));
    if (function_exists('idn_to_ascii') && preg_match('/[^\x00-\x7f]/', $host)) {
        $a = idn_to_ascii($host, IDNA_DEFAULT, INTL_IDNA_VARIANT_UTS46);
        if ($a === false) return null;
        $host = $a;
    }
    if (strlen($host) > 253 || !preg_match('/^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$/', $host)) {
        // allow bare public IPv4 addresses too
        if (!filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) return null;
    }
    if (in_array($host, ['localhost'], true) || str_ends_with($host, '.local') || str_ends_with($host, '.internal') || str_ends_with($host, '.localhost')) return null;
    $path = ($p['path'] ?? '/');
    if ($path === '') $path = '/';
    $q = isset($p['query']) ? '?' . $p['query'] : '';
    $path = substr($path . $q, 0, 200);
    return [$host, $path, $scheme];
}

function ip_is_public(string $ip): bool {
    if (!empty(config()['allow_private'])) return true; // local testing only
    if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) return false;
    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
        $n = ip2long($ip);
        // 100.64.0.0/10 (carrier-grade NAT) and 198.18.0.0/15 are not covered by the PHP flags.
        if ($n >= ip2long('100.64.0.0') && $n <= ip2long('100.127.255.255')) return false;
        if ($n >= ip2long('198.18.0.0') && $n <= ip2long('198.19.255.255')) return false;
        return true;
    }
    $b = inet_pton($ip);
    if ($b === false) return false;
    $h = bin2hex($b);
    if (str_starts_with($h, '00000000000000000000ffff')) { // IPv4-mapped
        return ip_is_public(long2ip((int)hexdec(substr($h, 24, 8))));
    }
    if (preg_match('/^(fc|fd|fe[89ab])/', $h)) return false; // unique local, link local
    return true;
}

/** @return array{ips:string[], error:?string} */
function resolve_public(string $host): array {
    if (!empty(config()['test_port'])) return ['ips' => ['127.0.0.1'], 'error' => null]; // local tests only
    if (filter_var($host, FILTER_VALIDATE_IP)) {
        return ip_is_public($host) ? ['ips' => [$host], 'error' => null] : ['ips' => [], 'error' => 'blocked'];
    }
    $ips = [];
    $a = @dns_get_record($host, DNS_A);
    if (is_array($a)) foreach ($a as $r) if (!empty($r['ip'])) $ips[] = $r['ip'];
    if (!$ips) {
        $aaaa = @dns_get_record($host, DNS_AAAA);
        if (is_array($aaaa)) foreach ($aaaa as $r) if (!empty($r['ipv6'])) $ips[] = $r['ipv6'];
    }
    if (!$ips) {
        $l = @gethostbynamel($host);
        if (is_array($l)) $ips = $l;
    }
    if (!$ips) return ['ips' => [], 'error' => 'dns'];
    foreach ($ips as $ip) if (!ip_is_public($ip)) return ['ips' => [], 'error' => 'blocked'];
    return ['ips' => array_values(array_unique($ips)), 'error' => null];
}

/** Best guess at who runs the infrastructure in front of a site, from its response headers only. Null when nothing is recognisable. */
function sud_provider(array $h): ?string {
    $sv = strtolower($h['server'] ?? ''); $via = strtolower(($h['via'] ?? '') . ' ' . ($h['x-served-by'] ?? ''));
    if (isset($h['cf-ray']) || str_contains($sv, 'cloudflare')) return 'Cloudflare';
    if (isset($h['x-amz-cf-id']) || str_contains($via, 'cloudfront')) return 'Amazon CloudFront';
    if (isset($h['x-amz-request-id']) || isset($h['x-amzn-requestid']) || str_contains($sv, 'amazons3') || str_contains($sv, 'awselb')) return 'Amazon Web Services';
    if (isset($h['x-azure-ref']) || str_contains($sv, 'microsoft-iis') && isset($h['x-msedge-ref'])) return 'Microsoft Azure';
    if (isset($h['x-goog-generation']) || str_contains($sv, 'gws') || str_contains($sv, 'gse') || str_contains($sv, 'esf') || isset($h['x-cloud-trace-context'])) return 'Google';
    if (isset($h['x-fastly-request-id']) || str_contains($via, 'fastly') || str_contains($sv, 'fastly')) return 'Fastly';
    if (isset($h['x-akamai-transformed']) || str_contains($sv, 'akamai')) return 'Akamai';
    if (isset($h['x-vercel-id']) || str_contains($sv, 'vercel')) return 'Vercel';
    if (isset($h['x-nf-request-id']) || str_contains($sv, 'netlify')) return 'Netlify';
    if (isset($h['x-github-request-id'])) return 'GitHub Pages';
    if (isset($h['x-sucuri-id'])) return 'Sucuri';
    if (str_contains($sv, 'envoy') && str_contains($via, 'google')) return 'Google';
    return null;
}

/**
 * One request (following up to 5 redirects). Returns:
 * code, ms, err (dns|blocked|timeout|ssl|connect|redirects|null), final, title, headings[], server, https
 */
function http_probe(string $host, string $path, bool $https, bool $thorough, int $timeout = 8): array {
    $res = ['code' => null, 'ms' => null, 'err' => null, 'final' => null, 'title' => null, 'headings' => [], 'server' => null, 'https' => $https, 'hops' => 0, 'ctype' => null, 'bytes' => null, 'desc' => null, 'lang' => null, 'tls_expires' => null, 'tls_issuer' => null, 'sec' => [], 'ip' => null, 'chain' => []];
    $start = microtime(true);
    $curHost = $host; $curPath = $path; $curHttps = $https;
    for ($hop = 0; $hop <= 5; $hop++) {
        $dns0 = microtime(true);
        $r = resolve_public($curHost);
        $dnsMs = (int)round((microtime(true) - $dns0) * 1000);
        if ($r['error']) { $res['err'] = $r['error']; break; }
        $port = $curHttps ? 443 : 80;
        $urlPort = '';
        if (!empty(config()['test_port'])) { $port = (int)config()['test_port']; $urlPort = ':' . $port; } // local tests only
        $url = ($curHttps ? 'https://' : 'http://') . $curHost . $urlPort . $curPath;
        $ip = $r['ips'][0];
        $body = ''; $headers = [];
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => false,
            CURLOPT_FOLLOWLOCATION => false,
            CURLOPT_NOPROXY => '*', // never via a proxy: the connection must go to the IP we checked
            CURLOPT_CONNECTTIMEOUT => 5,
            CURLOPT_TIMEOUT => $timeout,
            CURLOPT_USERAGENT => SUD_UA,
            CURLOPT_HTTPHEADER => ['Accept: text/html,*/*;q=0.8', 'Accept-Language: en'],
            CURLOPT_RESOLVE => [$curHost . ':' . $port . ':' . $ip],
            CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
            CURLOPT_ENCODING => '',
            CURLOPT_CERTINFO => $thorough && $curHttps,
            CURLOPT_HEADERFUNCTION => function ($c, $line) use (&$headers) {
                $t = trim($line);
                if (stripos($t, 'HTTP/') === 0) $headers = [];
                elseif (str_contains($t, ':')) { [$k, $v] = explode(':', $t, 2); $headers[strtolower(trim($k))] = trim($v); }
                return strlen($line);
            },
            CURLOPT_WRITEFUNCTION => function ($c, $data) use (&$body, $thorough) {
                if (!$thorough) return -1; // we only need the status line and headers
                $body .= $data;
                return strlen($body) > 131072 ? -1 : strlen($data);
            },
        ]);
        curl_exec($ch);
        $errno = curl_errno($ch);
        $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        $ci = ($thorough && $curHttps) ? curl_getinfo($ch, CURLINFO_CERTINFO) : [];
        $inf = curl_getinfo($ch);
        curl_close($ch);
        if ($code > 0) {   // where the time went on this request: DNS lookup, connecting, secure handshake, waiting for the first byte
            $cn = (int)round(($inf['connect_time'] ?? 0) * 1000); $ap = (int)round(($inf['appconnect_time'] ?? 0) * 1000);
            $res['t'] = ['dns' => $dnsMs, 'conn' => $cn, 'tls' => $curHttps && $ap > $cn ? $ap - $cn : 0, 'ttfb' => max(0, (int)round((($inf['starttransfer_time'] ?? 0) - ($inf['pretransfer_time'] ?? 0)) * 1000))];
            $res['prov'] = sud_provider($headers);
        }
        $res['ms'] = (int)round((microtime(true) - $start) * 1000);
        if ($code === 0) {
            if ($errno === 28) $res['err'] = 'timeout';
            elseif (in_array($errno, [35, 51, 53, 54, 58, 59, 60, 64, 66, 77, 80, 82, 83, 90, 91], true)) $res['err'] = 'ssl';
            elseif ($errno === 6) $res['err'] = 'dns';
            else $res['err'] = 'connect';
            break;
        }
        // A deliberate abort after the headers (errno 23) is fine.
        $res['code'] = $code;
        if (count($res['chain']) < 7) $res['chain'][] = ['url' => mb_substr(($curHttps ? 'https://' : 'http://') . $curHost . $curPath, 0, 200), 'code' => $code];
        $res['server'] = $headers['server'] ?? $res['server'];
        $res['hops'] = $hop;
        if ($code >= 300 && $code < 400 && !empty($headers['location'])) {
            $loc = $headers['location'];
            if (strlen($loc) > 2000) { $res['err'] = 'redirects'; break; }
            if (str_starts_with($loc, '//')) $loc = ($curHttps ? 'https:' : 'http:') . $loc;
            if (!preg_match('~^[a-z][a-z0-9+.-]*://~i', $loc)) {
                if ($loc === '' || $loc[0] !== '/') $loc = rtrim(substr($curPath, 0, (int)strrpos($curPath, '/') + 1), '/') . '/' . $loc;
                $loc = ($curHttps ? 'https://' : 'http://') . $curHost . $loc;
            }
            $t = parse_target($loc);
            if (!$t) { $res['err'] = 'blocked'; break; }
            [$curHost, $curPath, $sch] = $t;
            $curHttps = $sch === 'https';
            if ($hop === 5) { $res['err'] = 'redirects'; break; }
            continue;
        }
        $res['final'] = ($curHttps ? 'https://' : 'http://') . $curHost;
        $res['https'] = $curHttps;
        if ($thorough) {
            $res['ip'] = $ip;
            $res['ctype'] = isset($headers['content-type']) ? mb_substr(trim(explode(';', $headers['content-type'])[0]), 0, 60) : null;
            foreach (['strict-transport-security' => 'HSTS', 'content-security-policy' => 'CSP', 'x-frame-options' => 'X-Frame-Options', 'x-content-type-options' => 'X-Content-Type-Options', 'referrer-policy' => 'Referrer-Policy'] as $hk => $hn) {
                if (isset($headers[$hk])) $res['sec'][] = $hn;
            }
            $res['bytes'] = strlen($body);
            if (!empty($ci[0]['Expire date'])) { $t = strtotime($ci[0]['Expire date']); if ($t) $res['tls_expires'] = gmdate('Y-m-d', $t); }
            if (!empty($ci[0]['Issuer']) && preg_match('~(?:^|[,/ ])O ?= ?([^,/]+)~', $ci[0]['Issuer'], $mm)) $res['tls_issuer'] = mb_substr(trim($mm[1]), 0, 60);
        }
        if ($thorough && $body !== '' && preg_match('~text/html|application/xhtml~i', $headers['content-type'] ?? 'text/html')) {
            if (preg_match('~<title[^>]*>(.*?)</title>~is', $body, $m)) $res['title'] = mb_substr(trim(html_entity_decode(strip_tags($m[1]), ENT_QUOTES | ENT_HTML5, 'UTF-8')), 0, 160);
            if (preg_match('~<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)~i', $body, $m) || preg_match('~<meta[^>]+content=["\']([^"\']*)["\'][^>]*name=["\']description~i', $body, $m)) $res['desc'] = mb_substr(trim(html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5, 'UTF-8')), 0, 200);
            if (preg_match('~<html[^>]*\slang=["\']?([A-Za-z-]{2,10})~i', $body, $m)) $res['lang'] = $m[1];
            if (preg_match_all('~<h([12])[^>]*>(.*?)</h\1>~is', $body, $m, PREG_SET_ORDER)) {
                foreach ($m as $h) {
                    $t = mb_substr(trim(preg_replace('/\s+/', ' ', html_entity_decode(strip_tags($h[2]), ENT_QUOTES | ENT_HTML5, 'UTF-8'))), 0, 120);
                    if ($t !== '') $res['headings'][] = 'h' . $h[1] . ': ' . $t;
                    if (count($res['headings']) >= 6) break;
                }
            }
        }
        break;
    }
    return $res;
}

/**
 * Full check with the rules we publish on the site:
 *  Up | Confirmed down (server errors on two attempts) | Timeout | Inconclusive (blocked / could not verify)
 */
/** The address that really answers for $host (for example www.example.com when example.com never replies), or null. */
function probe_alias_get(string $host): ?string {
    try {
        $q = db()->prepare('SELECT alias FROM probe_alias WHERE host=? AND ts > ?'); $q->execute([$host, time() - 7 * 86400]);
        $a = $q->fetchColumn(); return $a ? (string)$a : null;
    } catch (Throwable $e) { return null; }
}
function probe_alias_set(string $host, string $alias): void {
    try { $pdo = db(); $pdo->prepare('DELETE FROM probe_alias WHERE host=?')->execute([$host]); $pdo->prepare('INSERT INTO probe_alias (host, alias, ts) VALUES (?,?,?)')->execute([$host, $alias, time()]); } catch (Throwable $e) {}
}

function check_site(string $host, string $path = '/', bool $thorough = false, bool $quick = false): array {
    $orig = $host;
    $alias = probe_alias_get($host);
    if ($alias) $host = $alias;
    $r = check_site_once($host, $path, $thorough, $quick);
    // Some sites only answer on "www." (and some block bare addresses from hosting networks): if the address we were given gets no reply, try the other form once.
    if ($r['http_code'] === null && in_array($r['err'], ['timeout', 'ssl', null, 'connect'], true) && !filter_var($host, FILTER_VALIDATE_IP)) {
        $other = str_starts_with($host, 'www.') ? substr($host, 4) : 'www.' . $host;
        if (substr_count($other, '.') >= 1 && ($alias === null || $other !== $orig)) {
            $r2 = check_site_once($other, $path, $thorough, $quick);
            if ($r2['http_code'] !== null) { probe_alias_set($orig, $other); $r = $r2; }
        }
    }
    $r['host'] = $orig;
    return $r;
}

function check_site_once(string $host, string $path = '/', bool $thorough = false, bool $quick = false): array {
    $r = http_probe($host, $path, true, $thorough, $quick ? 6 : 8);
    // If HTTPS cannot connect at all, see whether plain HTTP answers.
    if ($r['code'] === null && in_array($r['err'], ['ssl', 'connect'], true)) {
        $r2 = http_probe($host, $path, false, $thorough, $quick ? 6 : 8);
        if ($r2['code'] !== null || $r2['err'] === 'timeout') $r = $r2;
    }
    $attempts = 1;
    if ($r['code'] !== null && $r['code'] >= 500 && $r['code'] <= 599) {
        usleep(900000);
        $again = http_probe($host, $path, $r['https'], false, $quick ? 6 : 8);
        $attempts = 2;
        if ($again['code'] !== null && $again['code'] >= 500) { $r['confirmed'] = true; }
        else { $r = $again['code'] !== null ? array_merge($r, ['code' => $again['code'], 'ms' => $again['ms']]) : $r; }
    }
    $verdict = 'inconclusive'; $note = '';
    $code = $r['code'];
    if ($r['err'] === 'timeout') { $verdict = 'timeout'; $note = 'The site was slow or did not answer in time. A timeout is not proof it is down.'; }
    elseif ($r['err'] === 'dns') { $note = 'We could not find this address. Check the spelling.'; }
    elseif ($r['err'] === 'blocked') { $note = 'That address is not one we can check.'; }
    elseif ($r['err'] === 'ssl') { $note = 'We could not verify a secure connection to this site.'; }
    elseif ($r['err'] === 'redirects') { $note = 'The site redirected too many times.'; }
    elseif ($code === null) { $note = 'We could not connect from our server. That alone does not mean it is down.'; }
    elseif ($code >= 500) {
        if (!empty($r['confirmed'])) { $verdict = 'down'; $note = 'The server returned errors on two attempts.'; }
        else { $note = 'The server returned an error once, but not on the second try.'; }
    }
    elseif (in_array($code, [401, 403, 429, 451, 999], true)) { $note = 'The site answered but blocked automated checks, so we cannot be sure.'; }
    else { $verdict = 'up'; $note = $r['https'] ? 'The site responded to our server.' : 'The site responded, but not over a secure (HTTPS) connection.'; }
    return [
        'host' => $host, 'verdict' => $verdict, 'http_code' => $code, 'ms' => $r['ms'], 'note' => $note, 'err' => $r['err'],
        'title' => $r['title'], 'headings' => $r['headings'], 'server' => $r['server'], 'https' => $r['https'],
        'redirected' => ($r['hops'] ?? 0) > 0, 'attempts' => $attempts,
        'chain' => count($r['chain']) > 1 ? $r['chain'] : [],
        'timing' => $r['t'] ?? null, 'prov' => $r['prov'] ?? null,
        'extra' => ['final' => $r['final'], 'ip' => $r['ip'], 'ctype' => $r['ctype'], 'bytes' => $r['bytes'], 'desc' => $r['desc'], 'lang' => $r['lang'], 'sec' => $r['sec'], 'tls_expires' => $r['tls_expires'], 'tls_issuer' => $r['tls_issuer']],
    ];
}
