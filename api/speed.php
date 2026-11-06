<?php
// POST {address} -> website speed test: 3 timed loads from our server, with a breakdown, page weight, grade and tips.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_probe.php';
$in = read_post();
$t = parse_target((string)($in['address'] ?? ''));
if (!$t || filter_var($t[0], FILTER_VALIDATE_IP)) out(422, ['error' => 'Please enter a website address like example.com.']);
[$host, $path] = $t;
$pdo = db();
throttle('speed', 8, 10);
note_attempt('speed');
@set_time_limit(60);

/** One full page load (follows up to 5 redirects). Every hop is resolved, checked and pinned like the normal check. */
function speed_load(string $host, string $path, bool $https = true): array {
    $r = ['ok' => false, 'err' => null, 'code' => null, 'dns' => 0, 'connect' => 0, 'tls' => 0, 'wait' => 0, 'download' => 0, 'total' => 0, 'redirects' => 0,
        'size' => 0, 'wire' => null, 'enc' => null, 'ver' => null, 'final' => null, 'https' => true, 'headers' => [], 'html' => '', 'server' => null];
    $t0 = microtime(true);
    $curHost = $host; $curPath = $path; $curHttps = $https; $dnsTotal = 0.0;
    for ($hop = 0; $hop <= 5; $hop++) {
        $d0 = microtime(true);
        $rp = resolve_public($curHost);
        $dnsTotal += (microtime(true) - $d0) * 1000;
        if ($rp['error']) { $r['err'] = $rp['error']; return $r; }
        $port = $curHttps ? 443 : 80; $urlPort = '';
        if (!empty(config()['test_port'])) { $port = (int)config()['test_port']; $urlPort = ':' . $port; }
        $url = ($curHttps ? 'https://' : 'http://') . $curHost . $urlPort . $curPath;
        $headers = []; $bytes = 0; $html = '';
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => false, CURLOPT_FOLLOWLOCATION => false, CURLOPT_NOPROXY => '*',
            CURLOPT_CONNECTTIMEOUT => 6, CURLOPT_TIMEOUT => 12, CURLOPT_USERAGENT => SUD_UA,
            CURLOPT_HTTPHEADER => ['Accept: text/html,*/*;q=0.8', 'Accept-Language: en', 'Accept-Encoding: gzip, deflate, br'],
            CURLOPT_RESOLVE => [$curHost . ':' . $port . ':' . $rp['ips'][0]], CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
            CURLOPT_FRESH_CONNECT => true, CURLOPT_FORBID_REUSE => true, CURLOPT_HTTP_VERSION => defined('CURL_HTTP_VERSION_2TLS') ? CURL_HTTP_VERSION_2TLS : 0,
            CURLOPT_HEADERFUNCTION => function ($c, $line) use (&$headers) {
                $x = trim($line);
                if (stripos($x, 'HTTP/') === 0) $headers = [];
                elseif (str_contains($x, ':')) { [$k, $v] = explode(':', $x, 2); $headers[strtolower(trim($k))] = trim($v); }
                return strlen($line);
            },
            CURLOPT_WRITEFUNCTION => function ($c, $data) use (&$bytes, &$html) {
                $bytes += strlen($data);
                if (strlen($html) < 262144) $html .= $data;
                return $bytes > 3000000 ? -1 : strlen($data);
            },
        ]);
        // No CURLOPT_ENCODING: we ask for compression ourselves so we can see (and count) the compressed size too.
        curl_exec($ch);
        $errno = curl_errno($ch);
        $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        $ci = curl_getinfo($ch);
        curl_close($ch);
        if ($code === 0) { $r['err'] = $errno === 28 ? 'timeout' : ($errno === 6 ? 'dns' : 'connect'); return $r; }
        $r['code'] = $code; $r['server'] = $headers['server'] ?? $r['server'];
        $r['redirects'] = $hop;
        if ($code >= 300 && $code < 400 && !empty($headers['location'])) {
            $loc = $headers['location'];
            if (str_starts_with($loc, '//')) $loc = ($curHttps ? 'https:' : 'http:') . $loc;
            if (!preg_match('~^[a-z][a-z0-9+.-]*://~i', $loc)) $loc = ($curHttps ? 'https://' : 'http://') . $curHost . ($loc !== '' && $loc[0] === '/' ? '' : '/') . $loc;
            $tt = parse_target($loc);
            if (!$tt) { $r['err'] = 'blocked'; return $r; }
            [$curHost, $curPath, $sch] = $tt; $curHttps = $sch === 'https';
            continue;
        }
        // The last hop gives the breakdown.
        $conn = max(0.0, ($ci['connect_time'] ?? 0) - ($ci['namelookup_time'] ?? 0));
        $app = (float)($ci['appconnect_time'] ?? 0);
        $r['dns'] = (int)round($dnsTotal);
        $r['connect'] = (int)round($conn * 1000);
        $r['tls'] = $curHttps && $app > 0 ? (int)round(max(0.0, $app - ($ci['connect_time'] ?? 0)) * 1000) : 0;
        $ready = $app > 0 ? $app : (float)($ci['connect_time'] ?? 0);
        $r['wait'] = (int)round(max(0.0, ($ci['starttransfer_time'] ?? 0) - $ready) * 1000);
        $r['download'] = (int)round(max(0.0, ($ci['total_time'] ?? 0) - ($ci['starttransfer_time'] ?? 0)) * 1000);
        $r['total'] = (int)round((microtime(true) - $t0) * 1000);
        $r['size'] = $bytes; $r['enc'] = isset($headers['content-encoding']) ? strtolower($headers['content-encoding']) : null;
        $r['wire'] = isset($headers['content-length']) && $r['enc'] ? (int)$headers['content-length'] : (int)($ci['size_download'] ?? $bytes);
        $v = (int)($ci['http_version'] ?? 0);
        $r['ver'] = $v === 3 ? 'HTTP/2' : ($v === 2 ? 'HTTP/1.1' : ($v === 1 ? 'HTTP/1.0' : ($v >= 30 ? 'HTTP/3' : null)));
        $r['final'] = ($curHttps ? 'https://' : 'http://') . $curHost; $r['https'] = $curHttps;
        $r['headers'] = $headers;
        $r["html"] = $html;
        $r['ok'] = true;
        return $r;
    }
    $r['err'] = 'redirects';
    return $r;
}

$runs = []; $useHttps = true;
for ($i = 0; $i < 3; $i++) {
    $x = speed_load($host, $path, $useHttps);
    if (!$x['ok'] && $i === 0 && $useHttps && $x['err'] === 'connect') { $useHttps = false; $x = speed_load($host, $path, false); } // HTTPS refused: try plain HTTP
    if (!$x['ok']) { if ($i === 0) $first = $x; break; }
    $runs[] = $x;
    if ($x['total'] > 6000) break; // do not hammer a slow site
    if ($i < 2) usleep(250000);
}
if (!$runs) {
    $e = $first['err'] ?? 'connect';
    $msg = ['dns' => 'We could not find this address. Check the spelling.', 'blocked' => 'That address is not one we can test.', 'timeout' => 'The site did not answer in time, so there is nothing to time.', 'redirects' => 'The site redirected too many times.'][$e] ?? 'We could not connect to this site from our server.';
    out(200, ['host' => $host, 'ok' => false, 'error' => $msg]);
}
usort($runs, fn($a, $b) => $a['total'] <=> $b['total']);
$m = $runs[intdiv(count($runs), 2)]; // median run
$h = $m['headers'];
$body = $m['html'];
$res = ['scripts' => preg_match_all('~<script[^>]+src=~i', $body), 'styles' => preg_match_all('~<link[^>]+rel=["\']?stylesheet~i', $body), 'images' => preg_match_all('~<img\b~i', $body)];
$res['total'] = $res['scripts'] + $res['styles'] + $res['images'];
$cache = ['cache_control' => $h['cache-control'] ?? null, 'etag' => isset($h['etag']), 'last_modified' => isset($h['last-modified']), 'expires' => isset($h['expires'])];
$ttfb = $m['dns'] + $m['connect'] + $m['tls'] + $m['wait'];

// Score and plain-language tips.
$score = 100; $tips = [];
if ($ttfb > 200) $score -= min(35, (int)round(($ttfb - 200) / 25));
if ($m['wait'] > 600) $tips[] = 'The server took ' . $m['wait'] . ' ms to start answering. Caching, a faster host or a CDN usually fixes this.';
if ($m['total'] > 1000) $score -= min(25, (int)round(($m['total'] - 1000) / 120));
if (!$m['enc'] && $m['size'] > 10240) { $score -= 12; $tips[] = 'The page is not compressed. Turning on gzip or Brotli typically cuts HTML size by 70% or more.'; }
if ($m['ver'] === 'HTTP/1.1' && $m['https']) { $score -= 4; $tips[] = 'The site uses HTTP/1.1. HTTP/2 or HTTP/3 loads many files faster.'; }
if ($m['redirects'] > 0) { $score -= min(10, 5 * $m['redirects']); $tips[] = 'Visitors are redirected ' . $m['redirects'] . ' time' . ($m['redirects'] > 1 ? 's' : '') . ' before the page loads. Link straight to the final address to save a round trip.'; }
if ($m['size'] > 1000000) { $score -= 10; $tips[] = 'The page itself is over 1 MB. Large HTML slows every visit.'; }
if (!$m['https']) { $score -= 8; $tips[] = 'The page loads over plain HTTP. HTTPS is safer and enables HTTP/2.'; }
if ($cache['cache_control'] === null && !$cache['etag'] && !$cache['last_modified'] && !$cache['expires']) { $score -= 5; $tips[] = 'No caching headers were sent, so browsers cannot reuse the page.'; }
if ($res['scripts'] > 20) { $score -= 4; $tips[] = 'The page links ' . $res['scripts'] . ' script files. Fewer or combined scripts load faster.'; }
$score = max(0, min(100, $score));
$grade = $score >= 90 ? 'A' : ($score >= 75 ? 'B' : ($score >= 60 ? 'C' : ($score >= 40 ? 'D' : 'E')));
if (!$tips) $tips[] = 'Nothing obvious to fix. This site loads quickly from our server.';

out(200, ['host' => $host, 'ok' => true, 'final' => $m['final'], 'code' => $m['code'], 'server' => $m['server'], 'https' => $m['https'], 'version' => $m['ver'],
    'runs' => array_map(fn($x) => $x['total'], $runs), 'median' => ['dns' => $m['dns'], 'connect' => $m['connect'], 'tls' => $m['tls'], 'wait' => $m['wait'], 'download' => $m['download'], 'total' => $m['total'], 'ttfb' => $ttfb],
    'redirects' => $m['redirects'], 'size' => $m['size'], 'wire' => $m['wire'], 'encoding' => $m['enc'], 'resources' => $res, 'cache' => $cache,
    'score' => $score, 'grade' => $grade, 'tips' => $tips, 'at' => iso(sql_now())]);
