<?php
// Pro plan: who has it, what it unlocks, and the limits. Included lazily by the files that need it.
declare(strict_types=1);

const FREE_WATCH = 10;      // sites on a free watchlist (existing accounts keep what they already have)
const PRO_WATCH = 100;
const PRO_SMS_MONTH = 100;  // fair-use caps, so a flapping site cannot run up a bill
const PRO_CALL_MONTH = 20;
const PRO_STATUS_SITES = 30;
const FREE_HISTORY_DAYS = 30;
const PRO_HISTORY_DAYS = 365;

/** Adds the columns and tables the paid plan needs. Safe to run on every request. */
function ensure_billing(PDO $pdo): void {
    static $done = false; if ($done) return; $done = true;
    // Already migrated? One cheap look is enough, so the usual page view costs two tiny queries and nothing else.
    try { $pdo->query('SELECT plan, plan_until, stripe_cus, stripe_sub, plan_state FROM users LIMIT 1'); $pdo->query('SELECT 1 FROM billing_events LIMIT 1'); return; } catch (Throwable $e) { /* first run: create what is missing */ }
    $lite = is_sqlite($pdo);
    $cs = $lite ? '' : ' CHARACTER SET utf8mb4';
    foreach (["plan VARCHAR(8) NOT NULL DEFAULT 'free'", 'plan_until DATETIME NULL', 'stripe_cus VARCHAR(48) NULL', 'stripe_sub VARCHAR(48) NULL', 'plan_state VARCHAR(16) NULL'] as $col) {
        try { $pdo->exec('ALTER TABLE users ADD COLUMN ' . $col); } catch (Throwable $e) { /* already there */ }
    }
    $pdo->exec("CREATE TABLE IF NOT EXISTS phones (
        user_id INTEGER NOT NULL PRIMARY KEY,
        number VARCHAR(20) NOT NULL,
        verified TINYINT NOT NULL DEFAULT 0,
        code_hash VARCHAR(64) NULL,
        code_exp INTEGER NOT NULL DEFAULT 0,
        tries INTEGER NOT NULL DEFAULT 0,
        sent_at INTEGER NOT NULL DEFAULT 0,
        sms_on TINYINT NOT NULL DEFAULT 1,
        call_on TINYINT NOT NULL DEFAULT 0
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS phone_usage (
        user_id INTEGER NOT NULL,
        month CHAR(7) NOT NULL,
        sms INTEGER NOT NULL DEFAULT 0,
        calls INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (user_id, month)
    )");
    $pdo->exec("CREATE TABLE IF NOT EXISTS status_pages (
        slug VARCHAR(40) NOT NULL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title VARCHAR(80) NOT NULL,
        hosts TEXT NOT NULL,
        created_at DATETIME NOT NULL
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS billing_events (
        id VARCHAR(80) NOT NULL PRIMARY KEY,
        ts DATETIME NOT NULL
    )");
}

/** The user's plan: ['pro' => bool, 'until' => ?string, 'state' => ?string ('active','canceling','past_due')]. */
function user_plan(PDO $pdo, int $uid): array {
    ensure_billing($pdo);
    $s = $pdo->prepare('SELECT plan, plan_until, plan_state FROM users WHERE id=?');
    $s->execute([$uid]);
    $r = $s->fetch();
    if (!$r) return ['pro' => false, 'until' => null, 'state' => null];
    $pro = $r['plan'] === 'pro' && (empty($r['plan_until']) || $r['plan_until'] > sql_now());
    return ['pro' => $pro, 'until' => $r['plan_until'] ? iso($r['plan_until']) : null, 'state' => $pro ? ($r['plan_state'] ?: 'active') : null];
}
function is_pro(PDO $pdo, int $uid): bool { return user_plan($pdo, $uid)['pro']; }
function pro_required(PDO $pdo, int $uid, string $what): void {
    if (!is_pro($pdo, $uid)) out(402, ['error' => $what . ' needs siteupdown Pro.', 'upgrade' => true]);
}
function watch_limit(PDO $pdo, int $uid): int { return is_pro($pdo, $uid) ? PRO_WATCH : FREE_WATCH; }

/** SQL fragment: users who currently have Pro. */
function pro_users_sql(string $alias = 'u'): string {
    return "($alias.plan = 'pro' AND ($alias.plan_until IS NULL OR $alias.plan_until > '" . sql_now() . "'))";
}

function stripe_cfg(): array {
    $c = config() ?: [];
    return ['secret' => (string)($c['stripe_secret'] ?? ''), 'hook' => (string)($c['stripe_webhook_secret'] ?? ''),
        'month' => (string)($c['stripe_price_month'] ?? ''), 'year' => (string)($c['stripe_price_year'] ?? '')];
}
function billing_on(): bool { $s = stripe_cfg(); return $s['secret'] !== '' && $s['month'] !== ''; }

/** Month used for SMS and call caps, e.g. 2026-11. */
function usage_month(): string { return gmdate('Y-m'); }
function phone_usage(PDO $pdo, int $uid): array {
    $s = $pdo->prepare('SELECT sms, calls FROM phone_usage WHERE user_id=? AND month=?');
    $s->execute([$uid, usage_month()]);
    $r = $s->fetch();
    return ['sms' => (int)($r['sms'] ?? 0), 'calls' => (int)($r['calls'] ?? 0)];
}
function phone_usage_add(PDO $pdo, int $uid, string $col): void {
    $col = $col === 'calls' ? 'calls' : 'sms';
    $up = is_sqlite($pdo) ? "ON CONFLICT(user_id, month) DO UPDATE SET $col = $col + 1" : "ON DUPLICATE KEY UPDATE $col = $col + 1";
    $pdo->prepare("INSERT INTO phone_usage (user_id, month, $col) VALUES (?,?,1) $up")->execute([$uid, usage_month()]);
}

/** One call to the Stripe API. Returns the decoded answer, or null if it failed. */
function stripe_call(string $method, string $path, array $fields = []): ?array {
    $s = stripe_cfg();
    $ch = curl_init('https://api.stripe.com/v1/' . $path);
    curl_setopt_array($ch, [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_RETURNTRANSFER => true, CURLOPT_USERPWD => $s['secret'] . ':', CURLOPT_TIMEOUT => 12, CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_FOLLOWLOCATION => false, CURLOPT_PROTOCOLS => CURLPROTO_HTTPS, CURLOPT_HTTPHEADER => ['Stripe-Version: 2024-06-20']]);
    if ($fields) curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($fields));
    $raw = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE); curl_close($ch);
    $j = $raw ? json_decode((string)$raw, true) : null;
    return ($code >= 200 && $code < 300 && is_array($j)) ? $j : null;
}

