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

/**
 * One request (following up to 5 redirects). Returns:
 * code, ms, err (dns|blocked|timeout|ssl|connect|redirects|null), final, title, headings[], server, https
 */
function http_probe(string $host, string $path, bool $https, bool $thorough, int $timeout = 8): array {
    $res = ['code' => null, 'ms' => null, 'err' => null, 'final' => null, 'title' => null, 'headings' => [], 'server' => null, 'https' => $https, 'hops' => 0];
    $start = microtime(true);
    $curHost = $host; $curPath = $path; $curHttps = $https;
    for ($hop = 0; $hop <= 5; $hop++) {
        $r = resolve_public($curHost);
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
        curl_close($ch);
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
        if ($thorough && $body !== '' && preg_match('~text/html|application/xhtml~i', $headers['content-type'] ?? 'text/html')) {
            if (preg_match('~<title[^>]*>(.*?)</title>~is', $body, $m)) $res['title'] = mb_substr(trim(html_entity_decode(strip_tags($m[1]), ENT_QUOTES | ENT_HTML5, 'UTF-8')), 0, 160);
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
function check_site(string $host, string $path = '/', bool $thorough = false, bool $quick = false): array {
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
    ];
}
