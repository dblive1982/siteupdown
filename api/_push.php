<?php
// Web Push for browser notifications: VAPID signing (RFC 8292) and message encryption (RFC 8291, aes128gcm).
// The signing key is created on first use and kept in the database, never in the repository.
declare(strict_types=1);

function b64u(string $s): string { return rtrim(strtr(base64_encode($s), '+/', '-_'), '='); }
function b64u_d(string $s): string { return (string)base64_decode(strtr($s, '-_', '+/') . str_repeat('=', (4 - strlen($s) % 4) % 4)); }

/** Raw uncompressed public key (65 bytes) of an EC key resource. */
function push_raw_pub($key): string {
    $d = openssl_pkey_get_details($key);
    return "\x04" . str_pad($d['ec']['x'], 32, "\0", STR_PAD_LEFT) . str_pad($d['ec']['y'], 32, "\0", STR_PAD_LEFT);
}
/** Public key resource from a raw 65 byte P-256 point. */
function push_pub_from_raw(string $raw) {
    if (strlen($raw) !== 65 || $raw[0] !== "\x04") return false;
    $der = hex2bin('3059301306072a8648ce3d020106082a8648ce3d030107034200') . $raw;
    return openssl_pkey_get_public("-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($der), 64, "\n") . "-----END PUBLIC KEY-----\n");
}
function push_new_key() { return openssl_pkey_new(['curve_name' => 'prime256v1', 'private_key_type' => OPENSSL_KEYTYPE_EC]); }

/** The site's VAPID key pair: [private key resource, public key as base64url]. */
function push_vapid(PDO $pdo): array {
    $q = $pdo->prepare('SELECT v FROM kv WHERE k=?'); $q->execute(['vapid_pem']);
    $pem = $q->fetchColumn();
    if (!$pem) {
        $k = push_new_key(); openssl_pkey_export($k, $pem);
        try { $pdo->prepare('INSERT INTO kv (k, v) VALUES (?, ?)')->execute(['vapid_pem', $pem]); }
        catch (Throwable $e) { $q->execute(['vapid_pem']); $pem = $q->fetchColumn(); }   // another request won the race
    }
    $key = openssl_pkey_get_private((string)$pem);
    return [$key, b64u(push_raw_pub($key))];
}

/** ES256 signature in the raw r||s form that JWT wants. */
function push_es256(string $data, $key): string {
    openssl_sign($data, $der, $key, OPENSSL_ALGO_SHA256);
    $o = 2; if (ord($der[1]) & 0x80) $o += ord($der[1]) & 0x7f;
    $rl = ord($der[$o + 1]); $r = substr($der, $o + 2, $rl); $o += 2 + $rl;
    $sl = ord($der[$o + 1]); $s = substr($der, $o + 2, $sl);
    return str_pad(ltrim($r, "\0"), 32, "\0", STR_PAD_LEFT) . str_pad(ltrim($s, "\0"), 32, "\0", STR_PAD_LEFT);
}
function push_jwt(string $endpoint, $key, string $sub): string {
    $p = parse_url($endpoint);
    $h = b64u(json_encode(['typ' => 'JWT', 'alg' => 'ES256']));
    $c = b64u(json_encode(['aud' => $p['scheme'] . '://' . $p['host'], 'exp' => time() + 12 * 3600, 'sub' => $sub]));
    return $h . '.' . $c . '.' . b64u(push_es256($h . '.' . $c, $key));
}

/** Encrypt a payload for one browser. $uaPub is its 65 byte public key and $auth its 16 byte secret. The last two arguments exist only for tests. */
function push_encrypt(string $payload, string $uaPub, string $auth, ?string $salt = null, $asKey = null): ?string {
    $uaKey = push_pub_from_raw($uaPub);
    if (!$uaKey || strlen($auth) !== 16) return null;
    $asKey = $asKey ?: push_new_key();
    $asPub = push_raw_pub($asKey);
    $secret = openssl_pkey_derive($uaKey, $asKey, 32);
    if ($secret === false) return null;
    $salt = $salt ?? random_bytes(16);
    $ikm = hash_hkdf('sha256', $secret, 32, "WebPush: info\0" . $uaPub . $asPub, $auth);
    $cek = hash_hkdf('sha256', $ikm, 16, "Content-Encoding: aes128gcm\0", $salt);
    $nonce = hash_hkdf('sha256', $ikm, 12, "Content-Encoding: nonce\0", $salt);
    $ct = openssl_encrypt($payload . "\x02", 'aes-128-gcm', $cek, OPENSSL_RAW_DATA, $nonce, $tag, '', 16);
    if ($ct === false) return null;
    return $salt . pack('N', 4096) . chr(65) . $asPub . $ct . $tag;
}

/** Only real browser push services may be called, so a subscription cannot be used to make our server fetch other addresses. */
function push_endpoint_ok(string $endpoint): bool {
    $p = parse_url($endpoint);
    if (!$p || ($p['scheme'] ?? '') !== 'https' || empty($p['host']) || isset($p['port']) && (int)$p['port'] !== 443 || strlen($endpoint) > 1000) return false;
    $h = strtolower($p['host']);
    foreach (['fcm.googleapis.com', 'updates.push.services.mozilla.com', 'push.apple.com', 'notify.windows.com', 'push.services.mozilla.com'] as $ok)
        if ($h === $ok || substr($h, -strlen('.' . $ok)) === '.' . $ok) return true;
    return false;
}

/** Send one notification. Returns false when the subscription is gone and should be deleted. */
function push_send(PDO $pdo, array $sub, array $msg): bool {
    [$key, $pub] = push_vapid($pdo);
    $body = push_encrypt(json_encode($msg, JSON_UNESCAPED_UNICODE), b64u_d($sub['p256dh']), b64u_d($sub['auth']));
    if ($body === null) return false;
    $ch = curl_init($sub['endpoint']);
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => $body, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 8, CURLOPT_CONNECTTIMEOUT => 4,
        CURLOPT_PROTOCOLS => CURLPROTO_HTTPS, CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_HTTPHEADER => ['Content-Type: application/octet-stream', 'Content-Encoding: aes128gcm', 'TTL: 7200', 'Urgency: high',
            'Authorization: vapid t=' . push_jwt($sub['endpoint'], $key, 'https://siteupdown.com') . ', k=' . $pub]]);
    curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    return !($code === 404 || $code === 410);
}

/** Tell everyone who asked to hear about this site. */
function push_host(PDO $pdo, string $host, string $title, string $text, string $url): void {
    try {
        $q = $pdo->prepare('SELECT hash, endpoint, p256dh, auth FROM push_subs WHERE host=? LIMIT 500'); $q->execute([$host]);
        $stop = time() + 25;   // never hold up the status checks for long
        foreach ($q->fetchAll() as $s) {
            if (time() > $stop) break;
            if (!push_send($pdo, $s, ['title' => $title, 'body' => $text, 'url' => $url])) $pdo->prepare('DELETE FROM push_subs WHERE hash=?')->execute([$s['hash']]);
        }
    } catch (Throwable $e) { /* never let notifications break the status checks */ }
}
