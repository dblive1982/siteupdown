<?php
// Safe single-request fetcher used by the tools pages. Same safety rules as the checker:
// public addresses only, standard ports only, connection pinned to the checked IP, every redirect re-checked.
declare(strict_types=1);

/** One request, no redirect following. Returns code, ms, err, ip, headers (list of [name, value]), body. */
function sud_get(string $host, string $path, bool $https, int $maxBody = 0, int $timeout = 8): array {
    $res = ['code' => null, 'ms' => null, 'err' => null, 'ip' => null, 'headers' => [], 'body' => '', 'version' => null];
    $r = resolve_public($host);
    if ($r['error']) { $res['err'] = $r['error']; return $res; }
    $port = $https ? 443 : 80; $urlPort = '';
    if (!empty(config()['test_port'])) { $port = (int)config()['test_port']; $urlPort = ':' . $port; } // local tests only
    $ip = $r['ips'][0]; $res['ip'] = $ip;
    $headers = []; $body = '';
    $ch = curl_init(($https ? 'https://' : 'http://') . $host . $urlPort . $path);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => false, CURLOPT_FOLLOWLOCATION => false, CURLOPT_NOPROXY => '*',
        CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => $timeout, CURLOPT_USERAGENT => SUD_UA,
        CURLOPT_HTTPHEADER => ['Accept: text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.7', 'Accept-Language: en-GB,en;q=0.9', 'Cache-Control: no-cache', 'Pragma: no-cache'],
        CURLOPT_RESOLVE => [$host . ':' . $port . ':' . $ip],
        CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS, CURLOPT_ENCODING => '',
        CURLOPT_HEADERFUNCTION => function ($c, $line) use (&$headers, &$res) {
            $t = trim($line);
            if (stripos($t, 'HTTP/') === 0) { $headers = []; $res['version'] = strtok($t, ' '); }
            elseif (str_contains($t, ':') && count($headers) < 60) { [$k, $v] = explode(':', $t, 2); $headers[] = [mb_substr(trim($k), 0, 80), mb_substr(trim($v), 0, 600)]; }
            return strlen($line);
        },
        CURLOPT_WRITEFUNCTION => function ($c, $data) use (&$body, $maxBody) {
            if ($maxBody <= 0) return -1;
            $body .= $data;
            return strlen($body) > $maxBody ? -1 : strlen($data);
        },
    ]);
    $t0 = microtime(true);
    curl_exec($ch);
    $errno = curl_errno($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    $res['ms'] = (int)round((microtime(true) - $t0) * 1000);
    if ($code === 0) {
        if ($errno === 28) $res['err'] = 'timeout';
        elseif (in_array($errno, [35, 51, 53, 54, 58, 59, 60, 64, 66, 77, 80, 82, 83, 90, 91], true)) $res['err'] = 'ssl';
        elseif ($errno === 6) $res['err'] = 'dns';
        else $res['err'] = 'connect';
        return $res;
    }
    $res['code'] = $code; $res['headers'] = $headers; $res['body'] = $body;
    return $res;
}

function sud_header(array $r, string $name): ?string {
    foreach ($r['headers'] as [$k, $v]) if (strcasecmp($k, $name) === 0) return $v;
    return null;
}

/** Follow redirects (max $max hops). Returns hops[] (url, code, ms, location), last response, and an overall error. */
function sud_follow(string $host, string $path, bool $https, int $max = 8, int $maxBody = 0): array {
    $hops = []; $seen = []; $last = null; $err = null;
    $curHost = $host; $curPath = $path; $curHttps = $https;
    for ($i = 0; $i <= $max; $i++) {
        $url = ($curHttps ? 'https://' : 'http://') . $curHost . $curPath;
        if (isset($seen[$url])) { $err = 'loop'; break; }
        $seen[$url] = 1;
        $r = sud_get($curHost, $curPath, $curHttps, $maxBody);
        $last = $r;
        $loc = $r['code'] !== null ? sud_header($r, 'location') : null;
        $hops[] = ['url' => mb_substr($url, 0, 300), 'code' => $r['code'], 'ms' => $r['ms'], 'err' => $r['err'], 'location' => $loc !== null ? mb_substr($loc, 0, 300) : null];
        if ($r['code'] === null) { $err = $r['err']; break; }
        if ($r['code'] >= 300 && $r['code'] < 400 && $loc) {
            if (strlen($loc) > 2000) { $err = 'redirects'; break; }
            if (str_starts_with($loc, '//')) $loc = ($curHttps ? 'https:' : 'http:') . $loc;
            if (!preg_match('~^[a-z][a-z0-9+.-]*://~i', $loc)) {
                if ($loc[0] !== '/') $loc = rtrim(substr($curPath, 0, (int)strrpos($curPath, '/') + 1), '/') . '/' . $loc;
                $loc = ($curHttps ? 'https://' : 'http://') . $curHost . $loc;
            }
            $t = parse_target($loc);
            if (!$t) { $err = 'blocked'; break; }
            [$curHost, $curPath, $sch] = $t; $curHttps = $sch === 'https';
            if ($i === $max) { $err = 'redirects'; break; }
            continue;
        }
        break;
    }
    return ['hops' => $hops, 'last' => $last, 'err' => $err, 'final' => ['host' => $curHost, 'path' => $curPath, 'https' => $curHttps]];
}
