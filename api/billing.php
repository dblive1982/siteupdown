<?php
// Signed-in users: POST {action: checkout | portal}. Sends the browser to Stripe's own pages, so card details never touch our server.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_msg.php';
require __DIR__ . '/_stripe.php';
$in = read_post();
$uid = require_user();
$pdo = db();
$m = msg_cfg();
if (!msg_can()['billing']) out(503, ['error' => 'Payments are not switched on yet.']);
throttle('bill', 12, 30); note_attempt('bill');
$site = rtrim((string)((config() ?: [])['site'] ?? 'https://siteupdown.com'), '/');
$a = (string)($in['action'] ?? '');
$u = $pdo->prepare('SELECT email FROM users WHERE id=?'); $u->execute([$uid]);
$email = (string)$u->fetchColumn();
$s = $pdo->prepare('SELECT customer, status FROM subscriptions WHERE user_id=?'); $s->execute([$uid]);
$row = $s->fetch() ?: [];

if ($a === 'checkout') {
    if (is_pro($pdo, $uid)) out(422, ['error' => 'You already have the Pro plan.']);
    $p = ['mode' => 'subscription', 'line_items' => [['price' => $m['stripe_price'], 'quantity' => 1]], 'client_reference_id' => (string)$uid,
        'success_url' => $site . '/monitor?pro=1', 'cancel_url' => $site . '/monitor', 'billing_address_collection' => 'auto',
        'subscription_data' => ['metadata' => ['uid' => (string)$uid]],
        'custom_text' => ['submit' => ['message' => 'By subscribing you agree to the terms at siteupdown.com/legal. You can cancel any time from the Monitor page.']]];
    if (!empty($row['customer'])) $p['customer'] = $row['customer']; else $p['customer_email'] = $email;
    [$http, $j] = stripe_call('POST', '/v1/checkout/sessions', $p);
    if ($http !== 200 || empty($j['url'])) out(502, ['error' => 'We could not start the payment page. Please try again in a moment.']);
    out(200, ['url' => $j['url']]);
}
if ($a === 'portal') {
    if (empty($row['customer'])) out(422, ['error' => 'There is no subscription on this account.']);
    [$http, $j] = stripe_call('POST', '/v1/billing_portal/sessions', ['customer' => $row['customer'], 'return_url' => $site . '/monitor']);
    if ($http !== 200 || empty($j['url'])) out(502, ['error' => 'We could not open the billing page. Please try again in a moment.']);
    out(200, ['url' => $j['url']]);
}
out(400, ['error' => 'Bad request.']);
