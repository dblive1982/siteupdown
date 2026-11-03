<?php
// Stripe webhook. In the Stripe dashboard add an endpoint https://siteupdown.com/api/stripe.php for the events
// checkout.session.completed, customer.subscription.created, customer.subscription.updated, customer.subscription.deleted,
// and put its signing secret in sud-config.php as 'stripe_whsec'.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_msg.php';
require __DIR__ . '/_stripe.php';
$m = msg_cfg();
if ($m['stripe_whsec'] === '') out(404, ['error' => 'Not configured.']);
$raw = (string)file_get_contents('php://input');
$hdr = (string)($_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '');
$t = 0; $sigs = [];
foreach (explode(',', $hdr) as $part) { $kv = explode('=', trim($part), 2); if (count($kv) === 2) { if ($kv[0] === 't') $t = (int)$kv[1]; elseif ($kv[0] === 'v1') $sigs[] = $kv[1]; } }
$good = false;
$calc = hash_hmac('sha256', $t . '.' . $raw, $m['stripe_whsec']);
foreach ($sigs as $sg) if (hash_equals($calc, $sg)) $good = true;
if (!$good || abs(time() - $t) > 600) out(400, ['error' => 'Bad signature.']);
$ev = json_decode($raw, true);
$obj = $ev['data']['object'] ?? null;
if (!is_array($obj)) out(200, ['ok' => true]);
$pdo = db();
$type = (string)($ev['type'] ?? '');

if ($type === 'checkout.session.completed' && ($obj['mode'] ?? '') === 'subscription') {
    $uid = (int)($obj['client_reference_id'] ?? 0);
    if ($uid > 0 && !empty($obj['subscription'])) {
        [$http, $sub] = stripe_call('GET', '/v1/subscriptions/' . rawurlencode((string)$obj['subscription']));
        if ($http === 200) stripe_save_sub($pdo, $uid, $sub);
    }
} elseif (in_array($type, ['customer.subscription.created', 'customer.subscription.updated', 'customer.subscription.deleted'], true)) {
    $uid = (int)($obj['metadata']['uid'] ?? 0);
    if ($uid <= 0) { $q = $pdo->prepare('SELECT user_id FROM subscriptions WHERE sub=?'); $q->execute([(string)($obj['id'] ?? '')]); $uid = (int)$q->fetchColumn(); }
    if ($uid > 0) { if ($type === 'customer.subscription.deleted') { $obj['status'] = 'canceled'; $obj['current_period_end'] = time(); } stripe_save_sub($pdo, $uid, $obj); }
}
out(200, ['ok' => true]);
