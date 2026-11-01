<?php
// Branded HTML emails (with a plain-text copy): welcome and password reset.
declare(strict_types=1);

function sud_email(string $to, string $subject, string $heading, string $paraHtml, string $paraText, string $btnText = '', string $btnUrl = ''): void {
    $c = config() ?: [];
    $site = rtrim($c['site'] ?? 'https://siteupdown.com', '/');
    $from = $c['mail_from'] ?? 'noreply@siteupdown.com';
    $h = htmlspecialchars($heading, ENT_QUOTES, 'UTF-8');
    $btn = '';
    if ($btnText !== '' && $btnUrl !== '') {
        $u = htmlspecialchars($btnUrl, ENT_QUOTES, 'UTF-8');
        $t = htmlspecialchars($btnText, ENT_QUOTES, 'UTF-8');
        $btn = '<p style="margin:26px 0 6px"><a href="' . $u . '" style="display:inline-block;background:#0dc04e;color:#04120a;text-decoration:none;font-weight:700;font-size:16px;padding:13px 28px;border-radius:6px;font-family:Arial,Helvetica,sans-serif">' . $t . '</a></p>';
    }
    $html = '<!doctype html><html><head><meta charset="utf-8"><meta name="color-scheme" content="light only"></head><body style="margin:0;padding:0;background:#eef3ef">'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef3ef"><tr><td align="center" style="padding:24px 12px">'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px">'
        . '<tr><td align="center" style="background:#07120d;border-radius:14px 14px 0 0;padding:24px 12px;font-family:Courier New,monospace;font-size:22px;letter-spacing:2px;color:#0dc04e;font-weight:700">SITEUPDOWN.COM</td></tr>'
        . '<tr><td style="background:#ffffff;border:1px solid #d5e0d8;border-top:0;border-radius:0 0 14px 14px;padding:28px 26px;font-family:Arial,Helvetica,sans-serif;color:#14201a;font-size:16px;line-height:1.6">'
        . '<h1 style="margin:0 0 14px;font-size:24px;line-height:1.2;color:#14201a">' . $h . '</h1>' . $paraHtml . $btn
        . '</td></tr><tr><td align="center" style="padding:16px 8px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#5b6b61">siteupdown.com &middot; Less refreshing. More knowing.</td></tr>'
        . '</table></td></tr></table></body></html>';
    $text = $heading . "\n\n" . $paraText . ($btnUrl !== '' ? "\n\n" . $btnText . ": " . $btnUrl : '') . "\n\n-- siteupdown.com, " . $site . "\n";
    $b = 'sud' . bin2hex(random_bytes(8));
    $body = "--$b\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($text), 76, "\r\n")
        . "--$b\r\nContent-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html), 76, "\r\n") . "--$b--";
    $subj = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    if (!empty($c['smtp_user']) && !empty($c['smtp_pass'])) {
        $sfrom = $c['smtp_user'];
        $hdr = "From: \"siteupdown.com\" <$sfrom>\r\nTo: <$to>\r\nSubject: $subj\r\nDate: " . date('r')
            . "\r\nMessage-ID: <" . bin2hex(random_bytes(12)) . "@siteupdown.com>\r\nMIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=\"$b\"\r\n";
        if (sud_smtp($c, $sfrom, $to, $hdr . "\r\n" . $body)) return;
    }
    @mail($to, $subj, $body, "From: \"siteupdown.com\" <$from>\r\nMIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=\"$b\"");
}

function sud_smtp(array $c, string $from, string $to, string $data): bool {
    $host = $c['smtp_host'] ?? 'smtp.hostinger.com';
    $port = (int)($c['smtp_port'] ?? 465);
    $fp = @stream_socket_client(($port === 465 ? 'ssl://' : 'tcp://') . $host . ':' . $port, $en, $es, 10);
    if (!$fp) { error_log("sud_smtp connect failed: $es"); return false; }
    stream_set_timeout($fp, 10);
    $read = function () use ($fp): string {
        $out = '';
        while (($l = fgets($fp, 515)) !== false) { $out .= $l; if (strlen($l) < 4 || $l[3] === ' ') break; }
        return $out;
    };
    $cmd = function (string $x, string $ok) use ($fp, $read): bool { fwrite($fp, $x . "\r\n"); return strpos($read(), $ok) === 0; };
    $good = false;
    if (strpos($read(), '220') === 0 && $cmd('EHLO siteupdown.com', '250')) {
        if ($port !== 465) {
            if ($cmd('STARTTLS', '220') && @stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) $cmd('EHLO siteupdown.com', '250');
            else { fclose($fp); return false; }
        }
        if ($cmd('AUTH LOGIN', '334') && $cmd(base64_encode($c['smtp_user']), '334') && $cmd(base64_encode($c['smtp_pass']), '235')
            && $cmd("MAIL FROM:<$from>", '250') && $cmd("RCPT TO:<$to>", '250') && $cmd('DATA', '354')) {
            $data = preg_replace('/(?<!\r)\n/', "\r\n", $data);
            $data = preg_replace('/^\./m', '..', $data);
            fwrite($fp, $data . "\r\n.\r\n");
            $good = strpos($read(), '250') === 0;
        }
    }
    if (!$good) error_log('sud_smtp failed');
    @fwrite($fp, "QUIT\r\n");
    fclose($fp);
    return $good;
}

function sud_welcome_parts(string $email, string $via = ''): array {
    $e = htmlspecialchars($email, ENT_QUOTES, 'UTF-8');
    $items = [
        ['Your checks, saved', 'Every check you run while signed in is saved to your account, so you can look back or run it again in one tap.'],
        ['Your own watchlist', 'Add the sites you care about and see at a glance which are up and which are having a bad day.'],
        ['Still free, still no spam', 'The checker works for everyone without an account. We only email you for things like password resets.'],
    ];
    $html = '<p style="margin:0 0 6px">Your free siteupdown.com account is ready.</p>';
    $text = "Your free siteupdown.com account is ready.\n";
    foreach ($items as [$h, $t]) {
        $html .= '<h2 style="margin:20px 0 4px;font-size:18px;color:#14201a">' . $h . '</h2><p style="margin:0">' . $t . '</p>';
        $text .= "\n" . $h . "\n" . $t . "\n";
    }
    $html .= '<p style="margin:22px 0 0;font-size:14px">You signed up' . $via . ' using ' . $e . '. If that was not you, you can ignore this message.</p>';
    $text .= "\nYou signed up" . $via . " using $email. If that was not you, you can ignore this message.";
    return [$html, $text];
}
