<?php
// GET -> my plan and what it includes. POST {action: checkout|portal}: returns a Stripe-hosted page to go to.
// Card details are only ever typed on Stripe's own pages. We store a customer id and a plan flag, never a card.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_plan.php';
$pdo = db();
ensure_billing($pdo);

$info = fn(int $uid) => ['on' => billing_on(), 'plan' => user_plan($pdo, $uid), 'price_month' => '5.00', 'price_year' => stripe_cfg()['year'] !== '' ? '48.00' : null, 'currency' => 'GBP',
    'limits' => ['watch' => PRO_WATCH, 'free_watch' => FREE_WATCH, 'sms' => PRO_SMS_MONTH, 'calls' => PRO_CALL_MONTH, 'status_sites' => PRO_STATUS_SITES, 'history_days' => PRO_HISTORY_DAYS],
    'sms_ready' => (function () { require_once __DIR__ . '/_sms.php'; return twilio_on(); })()];

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') {
    // The price list is public (the pricing page shows it); the plan only appears for a signed-in user.
    $uid = current_uid();
    $base = ['on' => billing_on(), 'price_month' => '5.00', 'price_year' => stripe_cfg()['year'] !== '' ? '48.00' : null, 'currency' => 'GBP'];
    out(200, $uid > 0 ? $info($uid) : $base + ['plan' => ['pro' => false, 'until' => null, 'state' => null]]);
}

$uid = require_user();
$in = read_post();
$a = (string)($in['action'] ?? '');
if (!billing_on()) out(503, ['error' => 'Subscriptions are not switched on yet. Please check back soon.', 'soon' => true]);
throttle('billing', 12, 10); note_attempt('billing');
$site = rtrim((config()['site'] ?? 'https://siteupdown.com'), '/');
$u = $pdo->prepare('SELECT email, stripe_cus FROM users WHERE id=?'); $u->execute([$uid]); $row = $u->fetch();
if (!$row) out(401, ['error' => 'Please sign in first.']);

if ($a === 'checkout') {
    if (user_plan($pdo, $uid)['pro']) out(409, ['error' => 'You already have Pro. Use Manage billing to change it.']);
    $cfg = stripe_cfg();
    $price = (($in['interval'] ?? 'month') === 'year' && $cfg['year'] !== '') ? $cfg['year'] : $cfg['month'];
    $f = ['mode' => 'subscription', 'line_items[0][price]' => $price, 'line_items[0][quantity]' => 1, 'client_reference_id' => (string)$uid,
        'success_url' => $site . '/account?plan=ok', 'cancel_url' => $site . '/pricing?canceled=1', 'allow_promotion_codes' => 'true',
        'subscription_data[metadata][uid]' => (string)$uid, 'billing_address_collection' => 'auto'];
    if (!empty($row['stripe_cus'])) $f['customer'] = $row['stripe_cus']; else $f['customer_email'] = $row['email'];
    $s = stripe_call('POST', 'checkout/sessions', $f);
    if (!$s || empty($s['url'])) out(502, ['error' => 'We could not start the payment page. Please try again in a moment.']);
    out(200, ['url' => $s['url']]);
}
if ($a === 'portal') {
    if (empty($row['stripe_cus'])) out(404, ['error' => 'There is no subscription to manage yet.']);
    $s = stripe_call('POST', 'billing_portal/sessions', ['customer' => $row['stripe_cus'], 'return_url' => $site . '/account']);
    if (!$s || empty($s['url'])) out(502, ['error' => 'We could not open the billing page. Please try again in a moment.']);
    out(200, ['url' => $s['url']]);
}
out(400, ['error' => 'Bad request.']);
