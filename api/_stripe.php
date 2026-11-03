<?php
// Minimal Stripe client (no library): form-encoded POST/DELETE with the secret key from sud-config.php.
declare(strict_types=1);

function stripe_call(string $method, string $path, array $params = []): array {
    $m = msg_cfg();
    $ch = curl_init($m['stripe_api'] . $path);
    $https = str_starts_with($m['stripe_api'], 'https://');
    curl_setopt_array($ch, [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_POSTFIELDS => $method === 'GET' ? null : http_build_query($params), CURLOPT_USERPWD => $m['stripe_sk'] . ':',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 12, CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_FOLLOWLOCATION => false, CURLOPT_USERAGENT => 'siteupdown.com',
        CURLOPT_PROTOCOLS => $https ? CURLPROTO_HTTPS : (CURLPROTO_HTTP | CURLPROTO_HTTPS)]);
    $raw = curl_exec($ch);
    $http = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    $j = is_string($raw) ? json_decode($raw, true) : null;
    return [$http, is_array($j) ? $j : []];
}

/** Save a Stripe subscription object for the user it belongs to. */
function stripe_save_sub(PDO $pdo, int $uid, array $sub): void {
    $end = $sub['current_period_end'] ?? ($sub['items']['data'][0]['current_period_end'] ?? null);
    $row = [$uid, (string)($sub['status'] ?? 'incomplete'), (string)($sub['customer'] ?? ''), (string)($sub['id'] ?? ''), $end ? gmdate('Y-m-d H:i:s', (int)$end) : null, sql_now()];
    $pdo->prepare('DELETE FROM subscriptions WHERE user_id=?')->execute([$uid]);
    $pdo->prepare('INSERT INTO subscriptions (user_id, status, customer, sub, period_end, updated_at) VALUES (?,?,?,?,?,?)')->execute($row);
}
