<?php
// Shared setup for the siteupdown.com API. Files starting with _ are blocked from the web by .htaccess.
// Database details live in sud-config.php, one folder ABOVE public_html, so they are never in Git.
declare(strict_types=1);

if (PHP_SAPI !== 'cli') {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Content-Type-Options: nosniff');
}

function out(int $code, array $data): void {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    exit;
}

function config(): ?array {
    static $c = false;
    if ($c !== false) return $c;
    $file = getenv('SUD_CONFIG') ?: dirname(__DIR__, 2) . '/sud-config.php';
    if (!is_file($file)) return $c = null;
    $r = require $file;
    return $c = (is_array($r) ? $r : null);
}

function db(): PDO {
    static $pdo = null;
    if ($pdo) return $pdo;
    $c = config();
    if (!$c) out(503, ['error' => 'The service is being set up. Please check back soon.']);
    try {
        $dsn = !empty($c['dsn']) ? $c['dsn']
            : 'mysql:host=' . ($c['db_host'] ?? '127.0.0.1') . ';dbname=' . $c['db_name'] . ';charset=utf8mb4';
        $pdo = new PDO($dsn, $c['db_user'] ?? null, $c['db_pass'] ?? null,
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC, PDO::ATTR_EMULATE_PREPARES => false]);
    } catch (Throwable $e) {
        out(503, ['error' => 'The service is not available right now. Please try again later.']);
    }
    ensure_schema($pdo);
    return $pdo;
}

function is_sqlite(PDO $pdo): bool { return $pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'sqlite'; }

// Time helpers that work on MySQL and on SQLite (SQLite is only used for local testing).
function sql_now(): string { return gmdate('Y-m-d H:i:s'); }
// 'YYYY-MM-DD HH:MM:SS' (UTC) -> '2026-11-01T21:24:49Z' for the browser.
function iso(?string $d): ?string { return $d ? str_replace(' ', 'T', $d) . 'Z' : null; }

function ensure_schema(PDO $pdo): void {
    $lite = is_sqlite($pdo);
    $id = $lite ? 'INTEGER PRIMARY KEY AUTOINCREMENT' : 'INT UNSIGNED AUTO_INCREMENT PRIMARY KEY';
    $cs = $lite ? '' : ' CHARACTER SET utf8mb4';
    $int = $lite ? 'INTEGER' : 'INT UNSIGNED';
    $pdo->exec("CREATE TABLE IF NOT EXISTS users (
        id $id,
        email VARCHAR(190) NOT NULL UNIQUE,
        name VARCHAR(60) NOT NULL,
        pass_hash VARCHAR(255) NULL,
        google_sub VARCHAR(64) NULL UNIQUE,
        created_at DATETIME NOT NULL,
        last_login DATETIME NULL
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS resets (
        id $id,
        user_id $int NOT NULL,
        token_hash CHAR(64) NOT NULL UNIQUE,
        expires_at DATETIME NOT NULL,
        used TINYINT NOT NULL DEFAULT 0
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS attempts (
        id $id,
        ip_hash CHAR(64) NOT NULL,
        kind VARCHAR(16) NOT NULL,
        ts DATETIME NOT NULL
    )$cs");
    // Public "recently checked" feed: only host + result, never the full path or who asked.
    $pdo->exec("CREATE TABLE IF NOT EXISTS checks (
        id $id,
        host VARCHAR(253) NOT NULL,
        verdict VARCHAR(16) NOT NULL,
        http_code SMALLINT NULL,
        ms INT NULL,
        checked_at DATETIME NOT NULL
    )$cs");
    // Latest result for each watched site (top sites, gaming services and users' own sites). Filled by cron.php.
    $pdo->exec("CREATE TABLE IF NOT EXISTS site_status (
        host VARCHAR(253) NOT NULL PRIMARY KEY,
        verdict VARCHAR(16) NOT NULL,
        http_code SMALLINT NULL,
        ms INT NULL,
        checked_at DATETIME NOT NULL
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS shares (
        id CHAR(10) NOT NULL PRIMARY KEY,
        host VARCHAR(253) NOT NULL,
        data MEDIUMTEXT NOT NULL,
        created_at DATETIME NOT NULL
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS saved_checks (
        id $id,
        user_id $int NOT NULL,
        share_id CHAR(10) NULL,
        host VARCHAR(253) NOT NULL,
        verdict VARCHAR(16) NOT NULL,
        http_code SMALLINT NULL,
        ms INT NULL,
        reachable TINYINT NULL,
        probes TINYINT NULL,
        median_ms INT NULL,
        checked_at DATETIME NOT NULL
    )$cs");
    $pdo->exec("CREATE TABLE IF NOT EXISTS watchlist (
        id $id,
        user_id $int NOT NULL,
        host VARCHAR(253) NOT NULL,
        added_at DATETIME NOT NULL,
        UNIQUE (user_id, host)
    )$cs");
    foreach ([
        'CREATE INDEX IF NOT EXISTS i_att ON attempts (ip_hash, kind, ts)',
        'CREATE INDEX IF NOT EXISTS i_chk ON checks (checked_at)',
        'CREATE INDEX IF NOT EXISTS i_sc ON saved_checks (user_id, checked_at)',
    ] as $q) {
        try { $pdo->exec($q); } catch (Throwable $e) { /* MySQL has no IF NOT EXISTS for indexes: created below */ }
    }
    if (!$lite) {
        foreach ([
            ['attempts', 'i_att', '(ip_hash, kind, ts)'], ['checks', 'i_chk', '(checked_at)'], ['saved_checks', 'i_sc', '(user_id, checked_at)'],
        ] as [$t, $n, $cols]) {
            try { $pdo->exec("CREATE INDEX $n ON $t $cols"); } catch (Throwable $e) { /* already exists */ }
        }
    }
}

function start_session(): void {
    if (session_status() === PHP_SESSION_ACTIVE) return;
    $https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (config()['force_secure_cookie'] ?? true);
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => (bool)$https, 'httponly' => true, 'samesite' => 'Lax']);
    session_name('sud_sess');
    session_start();
}

function current_uid(): int {
    if (!config()) return 0;
    start_session();
    return (int)($_SESSION['uid'] ?? 0);
}

function require_user(): int {
    $uid = current_uid();
    if ($uid <= 0) out(401, ['error' => 'Please sign in first.']);
    return $uid;
}

// Posts must come from our own pages: needs the custom header (browsers block it cross-site) and a JSON body.
function read_post(): array {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(405, ['error' => 'Method not allowed.']);
    if (($_SERVER['HTTP_X_SUD'] ?? '') !== '1') out(400, ['error' => 'Bad request.']);
    $d = json_decode(file_get_contents('php://input') ?: '', true);
    return is_array($d) ? $d : [];
}

function client_hash(): string {
    return hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|sud');
}

// Allow at most $max attempts of $kind from one address in $mins minutes.
function throttle(string $kind, int $max, int $mins): void {
    $pdo = db();
    $h = client_hash();
    $pdo->prepare('DELETE FROM attempts WHERE ts < ?')->execute([gmdate('Y-m-d H:i:s', time() - 86400)]);
    $s = $pdo->prepare('SELECT COUNT(*) FROM attempts WHERE ip_hash=? AND kind=? AND ts > ?');
    $s->execute([$h, $kind, gmdate('Y-m-d H:i:s', time() - $mins * 60)]);
    if ((int)$s->fetchColumn() >= $max) out(429, ['error' => 'Too many tries. Please wait a few minutes and try again.']);
}

function note_attempt(string $kind): void {
    db()->prepare('INSERT INTO attempts (ip_hash, kind, ts) VALUES (?,?,?)')->execute([client_hash(), $kind, sql_now()]);
}

function clean_email(string $e): string { return strtolower(trim($e)); }
function valid_email(string $e): bool { return strlen($e) <= 190 && filter_var($e, FILTER_VALIDATE_EMAIL) !== false; }

function public_user(array $u): array {
    return ['name' => $u['name'], 'email' => $u['email']];
}
