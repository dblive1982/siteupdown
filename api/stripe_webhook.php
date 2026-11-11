<?php
// Stripe calls this when a subscription starts, renews, is cancelled or a payment fails. Every call is checked against the signing secret first.
// In the Stripe dashboard add the endpoint https://siteupdown.com/api/stripe_webhook.php with these events:
//   checkout.session.completed, customer.subscription.created, customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed
require __DIR__ . '/_boot.php';
require __DIR__ . '/_plan.php';
$pdo = db();
ensure_billing($pdo);
$sec = stripe_cfg()['hook'];
if ($sec === '') out(503, ['error' => 'Not configured.']);

/** Stripe-Signature: t=timestamp,v1=hmac. Valid when the HMAC of "t.body" matches and the timestamp is recent. */
function stripe_sig_ok(string $payload, string $header, string $secret, int $tolerance = 300, ?int $now = null): bool {
    $t = 0; $sigs = [];
    foreach (explode(',', $header) as $part) { $kv = explode('=', trim($part), 2); if (count($kv) !== 2) continue; if ($kv[0] === 't') $t = (int)$kv[1]; elseif ($kv[0] === 'v1') $sigs[] = $kv[1]; }
    if ($t <= 0 || !$sigs || abs(($now ?? time()) - $t) > $tolerance) return false;
    $calc = hash_hmac('sha256', $t . '.' . $payload, $secret);
    foreach ($sigs as $s) if (hash_equals($calc, $s)) return true;
    return false;
}

function set_plan(PDO $pdo, string $where, string $val, string $plan, ?string $until, ?string $state, ?string $cus = null, ?string $sub = null): void {
    $col = $where === 'sub' ? 'stripe_sub' : ($where === 'uid' ? 'id' : 'stripe_cus');
    $sets = 'plan=?, plan_until=?, plan_state=?'; $args = [$plan, $until, $state];
    if ($cus) { $sets .= ', stripe_cus=?'; $args[] = $cus; }
    if ($sub) { $sets .= ', stripe_sub=?'; $args[] = $sub; }
    $args[] = $val;
    $pdo->prepare("UPDATE users SET $sets WHERE $col=?")->execute($args);
}
function period_end(array $sub): ?int {
    if (isset($sub['current_period_end'])) return (int)$sub['current_period_end'];
    return isset($sub['items']['data'][0]['current_period_end']) ? (int)$sub['items']['data'][0]['current_period_end'] : null;
}

if (PHP_SAPI !== 'cli' || !defined('SUD_WEBHOOK_TEST')) {
    $body = file_get_contents('php://input') ?: '';
    if (!stripe_sig_ok($body, (string)($_SERVER['HTTP_STRIPE_SIGNATURE'] ?? ''), $sec)) out(400, ['error' => 'Bad signature.']);
    $ev = json_decode($body, true);
    if (!is_array($ev) || empty($ev['id']) || empty($ev['type'])) out(400, ['error' => 'Bad event.']);
    try { $pdo->prepare('INSERT INTO billing_events (id, ts) VALUES (?,?)')->execute([substr((string)$ev['id'], 0, 80), sql_now()]); }
    catch (Throwable $e) { out(200, ['ok' => true, 'duplicate' => true]); }     // already handled: Stripe retries, so repeat events are normal
    $pdo->prepare('DELETE FROM billing_events WHERE ts < ?')->execute([gmdate('Y-m-d H:i:s', time() - 60 * 86400)]);
    $o = $ev['data']['object'] ?? [];
    switch ($ev['type']) {
        case 'checkout.session.completed':
            $uid = (int)($o['client_reference_id'] ?? 0);
            if ($uid > 0 && ($o['mode'] ?? '') === 'subscription')   // a first period end arrives with the subscription event; until then allow a month
                set_plan($pdo, 'uid', (string)$uid, 'pro', gmdate('Y-m-d H:i:s', time() + 33 * 86400), 'active', (string)($o['customer'] ?? ''), (string)($o['subscription'] ?? ''));
            break;
        case 'customer.subscription.created':
        case 'customer.subscription.updated':
            $st = (string)($o['status'] ?? ''); $end = period_end($o);
            $uid = (int)($o['metadata']['uid'] ?? 0);
            $key = $uid > 0 ? ['uid', (string)$uid] : ['sub', (string)($o['id'] ?? '')];
            if (in_array($st, ['active', 'trialing', 'past_due'], true)) {
                $state = !empty($o['cancel_at_period_end']) ? 'canceling' : ($st === 'past_due' ? 'past_due' : 'active');
                set_plan($pdo, $key[0], $key[1], 'pro', gmdate('Y-m-d H:i:s', ($end ?? time() + 33 * 86400) + 86400), $state, (string)($o['customer'] ?? ''), (string)($o['id'] ?? ''));
            } elseif (in_array($st, ['canceled', 'unpaid', 'incomplete_expired'], true)) {
                set_plan($pdo, $key[0], $key[1], 'free', null, null);
            }
            break;
        case 'customer.subscription.deleted':
            set_plan($pdo, 'sub', (string)($o['id'] ?? ''), 'free', null, null);
            break;
        case 'invoice.payment_failed':
            if (!empty($o['customer'])) $pdo->prepare("UPDATE users SET plan_state='past_due' WHERE stripe_cus=? AND plan='pro'")->execute([(string)$o['customer']]);
            break;
    }
    out(200, ['ok' => true]);
}
