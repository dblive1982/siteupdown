<?php
// Command line only: php api/testmail.php you@example.com  (sends one test email, prints the result)
declare(strict_types=1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
$to = $argv[1] ?? '';
$c = config() ?: [];
echo 'smtp configured: ' . (!empty($c['smtp_user']) && !empty($c['smtp_pass']) ? 'yes' : 'no') . "\n";
if (!filter_var($to, FILTER_VALIDATE_EMAIL)) { echo "give an email address\n"; exit(1); }
$t = 'sud' . bin2hex(random_bytes(4));
$ok = !empty($c['smtp_user']) && sud_smtp($c, $c['smtp_user'], $to,
  "From: \"siteupdown.com\" <{$c['smtp_user']}>\r\nTo: <$to>\r\nSubject: siteupdown.com test email\r\nDate: " . date('r') . "\r\nMessage-ID: <$t@siteupdown.com>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nThis is a test email from siteupdown.com. If you can read this, alert emails work.\r\n");
echo 'smtp send: ' . ($ok ? 'OK' : 'FAILED') . "\n";
