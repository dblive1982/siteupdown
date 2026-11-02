<?php
// SSL / HTTPS certificate inspection. Connects to the already-checked public IP on port 443 (never a private address),
// reads the certificate chain and reports validity. Used by check.php for every check.

function tls_san_list(array $x): array {
    $out = [];
    $san = $x['extensions']['subjectAltName'] ?? '';
    foreach (explode(',', $san) as $p) {
        $p = trim($p);
        if (stripos($p, 'DNS:') === 0) $out[] = strtolower(trim(substr($p, 4)));
    }
    return array_values(array_unique($out));
}

function tls_name_matches(string $host, string $pattern): bool {
    $host = strtolower($host); $pattern = strtolower($pattern);
    if ($host === $pattern) return true;
    if (strpos($pattern, '*.') === 0) {
        $rest = substr($pattern, 2);
        $dot = strpos($host, '.');
        return $dot !== false && substr($host, $dot + 1) === $rest && $dot > 0;
    }
    return false;
}

function tls_connect(string $host, string $ip, int $port, bool $verify, int $timeout) {
    $ssl = ['capture_peer_cert' => true, 'capture_peer_cert_chain' => true, 'peer_name' => $host, 'SNI_enabled' => true,
            'verify_peer' => $verify, 'verify_peer_name' => $verify, 'allow_self_signed' => false];
    $ca = config()['tls_cafile'] ?? null;
    if ($ca) $ssl['cafile'] = $ca;
    $ctx = stream_context_create(['ssl' => $ssl]);
    $addr = 'ssl://' . (str_contains($ip, ':') ? '[' . $ip . ']' : $ip) . ':' . $port;
    $fp = @stream_socket_client($addr, $errno, $errstr, $timeout, STREAM_CLIENT_CONNECT, $ctx);
    return $fp ? [$fp, $ctx] : [null, null];
}

function tls_cn(array $dn): string {
    return (string)($dn['CN'] ?? $dn['O'] ?? $dn['OU'] ?? '');
}

function tls_inspect(string $host, string $ip, int $timeout = 6): array {
    $res = ['status' => 'none', 'trusted' => false, 'note' => 'No HTTPS certificate could be read.'];
    if (!function_exists('openssl_x509_parse')) return $res;
    $port = (int)(config()['test_tls_port'] ?? 443);
    [$fp, $ctx] = tls_connect($host, $ip, $port, true, $timeout);
    $trusted = $fp !== null;
    if (!$fp) [$fp, $ctx] = tls_connect($host, $ip, $port, false, $timeout);
    if (!$fp) return $res;
    $meta = stream_get_meta_data($fp);
    $opt = stream_context_get_params($ctx)['options']['ssl'] ?? [];
    fclose($fp);
    $cert = $opt['peer_certificate'] ?? null;
    if (!$cert) return $res;
    $x = openssl_x509_parse($cert);
    if (!$x) return $res;
    $now = time();
    $from = (int)($x['validFrom_time_t'] ?? 0); $to = (int)($x['validTo_time_t'] ?? 0);
    $sans = tls_san_list($x);
    $names = $sans ?: [strtolower(tls_cn($x['subject'] ?? []))];
    $covers = false;
    foreach ($names as $n) if ($n !== '' && tls_name_matches($host, $n)) { $covers = true; break; }
    $keyBits = null; $keyType = null;
    $pk = @openssl_pkey_get_public($cert);
    if ($pk) {
        $d = openssl_pkey_get_details($pk);
        $keyBits = $d['bits'] ?? null;
        $keyType = ['0' => 'RSA', '3' => 'EC', '2' => 'DSA', '1' => 'DSA'][(string)($d['type'] ?? '')] ?? null;
    }
    $fp256 = openssl_x509_fingerprint($cert, 'sha256') ?: '';
    $fp256 = $fp256 ? strtoupper(implode(':', str_split($fp256, 2))) : '';
    $chain = [];
    $certs = $opt['peer_certificate_chain'] ?? [$cert];
    foreach ($certs as $i => $c) {
        $p = openssl_x509_parse($c); if (!$p) continue;
        $sub = tls_cn($p['subject'] ?? []); $iss = tls_cn($p['issuer'] ?? []);
        $role = $i === 0 ? 'leaf' : ($sub === $iss ? 'root' : 'intermediate');
        $chain[] = ['subject' => $sub, 'issuer' => $iss, 'role' => $role];
    }
    $selfSigned = tls_cn($x['subject'] ?? []) === tls_cn($x['issuer'] ?? []) && ($x['subject'] ?? null) == ($x['issuer'] ?? null);
    $days = (int)floor(($to - $now) / 86400);
    if ($now > $to) { $status = 'expired'; $note = 'This certificate expired ' . abs($days) . ' day' . (abs($days) === 1 ? '' : 's') . ' ago.'; }
    elseif ($now < $from) { $status = 'notyet'; $note = 'This certificate is not valid yet.'; }
    elseif (!$covers) { $status = 'mismatch'; $note = 'The certificate does not cover this address.'; }
    elseif (!$trusted) { $status = 'untrusted'; $note = $selfSigned ? 'The certificate is self-signed, so browsers will not trust it.' : 'Browsers may not trust this certificate or its chain.'; }
    elseif ($days <= 14) { $status = 'expiring'; $note = 'Valid, but it expires in ' . max(0, $days) . ' day' . ($days === 1 ? '' : 's') . '.'; }
    else { $status = 'valid'; $note = 'Trusted and valid.'; }
    $cry = $meta['crypto'] ?? [];
    return [
        'status' => $status, 'trusted' => $trusted, 'note' => $note, 'host' => $host,
        'subject' => tls_cn($x['subject'] ?? []), 'issuer' => tls_cn($x['issuer'] ?? []), 'issuer_org' => (string)($x['issuer']['O'] ?? ''),
        'covers' => $covers, 'from' => gmdate('Y-m-d', $from), 'to' => gmdate('Y-m-d', $to), 'days_left' => $days,
        'elapsed' => ($to > $from) ? max(0, min(100, (int)round(($now - $from) / ($to - $from) * 100))) : null,
        'protocol' => $cry['protocol'] ?? null, 'cipher' => $cry['cipher_name'] ?? null,
        'key_bits' => $keyBits, 'key_type' => $keyType, 'serial' => strtoupper((string)($x['serialNumberHex'] ?? '')),
        'fingerprint' => $fp256, 'sans' => array_slice($sans, 0, 40), 'sans_total' => count($sans), 'chain' => $chain,
    ];
}
