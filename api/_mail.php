<?php
// Branded HTML emails (with a plain-text copy): welcome, password reset, alerts and contact form.
declare(strict_types=1);

/** Builds the branded HTML and plain-text bodies. $tone: '' | 'down' | 'up' | 'warn' adds a coloured status chip. */
function sud_email_render(string $heading, string $paraHtml, string $paraText, string $btnText = '', string $btnUrl = '', string $tone = ''): array {
    $c = config() ?: [];
    $site = rtrim($c['site'] ?? 'https://siteupdown.com', '/');
    $h = htmlspecialchars($heading, ENT_QUOTES, 'UTF-8');
    $F = "font-family:Poppins,'Helvetica Neue',Arial,Helvetica,sans-serif";
    $btn = '';
    if ($btnText !== '' && $btnUrl !== '') {
        $u = htmlspecialchars($btnUrl, ENT_QUOTES, 'UTF-8');
        $t = htmlspecialchars($btnText, ENT_QUOTES, 'UTF-8');
        $btn = '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:28px 0 6px"><tr><td bgcolor="#39b54a" style="border-radius:8px"><a href="' . $u . '" style="display:inline-block;background:#39b54a;color:#0b1a10;text-decoration:none;font-weight:700;font-size:16px;padding:14px 30px;border-radius:8px;' . $F . '">' . $t . '</a></td></tr></table>';
    }
    $chip = '';
    $stripe = '#39b54a';
    if ($tone === 'down') { $stripe = '#e5484d'; $chip = '<p style="margin:0 0 12px"><span style="display:inline-block;background:#4a1a24;color:#ff9ea1;font-size:12px;font-weight:700;letter-spacing:1.5px;padding:5px 12px;border-radius:99px;' . $F . '">&#9679; LOOKS DOWN</span></p>'; }
    if ($tone === 'warn') { $stripe = '#f0a020'; $chip = '<p style="margin:0 0 12px"><span style="display:inline-block;background:#4a3410;color:#ffcb6b;font-size:12px;font-weight:700;letter-spacing:1.5px;padding:5px 12px;border-radius:99px;' . $F . '">&#9679; HEADS UP</span></p>'; }
    if ($tone === 'up') { $chip = '<p style="margin:0 0 12px"><span style="display:inline-block;background:#14391f;color:#8be69c;font-size:12px;font-weight:700;letter-spacing:1.5px;padding:5px 12px;border-radius:99px;' . $F . '">&#9679; BACK UP</span></p>'; }
    $link = fn(string $t, string $href) => '<a href="' . $site . $href . '" style="color:#b9aee0;text-decoration:underline">' . $t . '</a>';
    $html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark"><title>' . $h . '</title></head>'
        . '<body style="margin:0;padding:0;background:#0d011c">'
        . '<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#0d011c">' . $h . ' &middot; siteupdown.com</div>'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="#0d011c" style="background:#0d011c"><tr><td align="center" style="padding:26px 12px">'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:580px">'
        . '<tr><td align="center" bgcolor="#130228" style="background:#130228;border-radius:16px 16px 0 0;border-bottom:4px solid ' . $stripe . ';padding:26px 12px 22px">'
        . '<a href="' . $site . '/" style="text-decoration:none"><img src="' . $site . '/assets/logo-full-dark.png" width="150" height="62" alt="siteupdown.com" style="display:block;border:0;outline:none;width:150px;height:62px;color:#f0f2f6;font-size:20px;font-weight:700;' . $F . '"></a></td></tr>'
        . '<tr><td bgcolor="#1d0a38" style="background:#1d0a38;border-left:1px solid #34205a;border-right:1px solid #34205a;padding:32px 28px 30px;' . $F . ';color:#e6e1f5;font-size:16px;line-height:1.65">'
        . $chip . '<h1 style="margin:0 0 14px;font-size:25px;line-height:1.25;color:#ffffff;' . $F . '">' . $h . '</h1>' . $paraHtml . $btn
        . '</td></tr>'
        . '<tr><td align="center" bgcolor="#130228" style="background:#130228;border-radius:0 0 16px 16px;padding:22px 18px;' . $F . ';font-size:13px;line-height:1.7;color:#a79bd0">'
        . '<span style="color:#f0f2f6;font-weight:700">Is it down &mdash; or just you?</span><br>'
        . $link('Monitor', '/monitor') . ' &nbsp;&middot;&nbsp; ' . $link('Help', '/help/') . ' &nbsp;&middot;&nbsp; ' . $link('Privacy', '/privacy') . ' &nbsp;&middot;&nbsp; ' . $link('Contact', '/contact')
        . '<br><span style="color:#8a7fb3">You are getting this because you have a siteupdown.com account or used our contact form.</span></td></tr>'
        . '</table></td></tr></table></body></html>';
    $text = $heading . "\n\n" . $paraText . ($btnUrl !== '' ? "\n\n" . $btnText . ": " . $btnUrl : '') . "\n\n--\nsiteupdown.com - Is it down, or just you?\n" . $site . "\nMonitor: $site/monitor  Help: $site/help/  Contact: $site/contact\n";
    return [$html, $text];
}

function sud_email(string $to, string $subject, string $heading, string $paraHtml, string $paraText, string $btnText = '', string $btnUrl = '', string $replyTo = '', string $tone = ''): void {
    $c = config() ?: [];
    $from = $c['mail_from'] ?? 'noreply@siteupdown.com';
    [$html, $text] = sud_email_render($heading, $paraHtml, $paraText, $btnText, $btnUrl, $tone);
    $b = 'sud' . bin2hex(random_bytes(8));
    $body = "--$b\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($text), 76, "\r\n")
        . "--$b\r\nContent-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html), 76, "\r\n") . "--$b--";
    $subj = '=?UTF-8?B?' . base64_encode($subject) . '?=';
    $rt = ($replyTo !== '' && filter_var($replyTo, FILTER_VALIDATE_EMAIL)) ? "Reply-To: <$replyTo>\r\n" : '';
    if (!empty($c['smtp_user']) && !empty($c['smtp_pass'])) {
        $sfrom = $c['smtp_user'];
        $hdr = "From: \"siteupdown.com\" <$sfrom>\r\nTo: <$to>\r\nSubject: $subj\r\n" . $rt . "Date: " . date('r')
            . "\r\nMessage-ID: <" . bin2hex(random_bytes(12)) . "@siteupdown.com>\r\nMIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=\"$b\"\r\n";
        if (sud_smtp($c, $sfrom, $to, $hdr . "\r\n" . $body)) return;
    }
    @mail($to, $subj, $body, "From: \"siteupdown.com\" <$from>\r\n" . $rt . "MIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=\"$b\"");
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
        ['Your own watchlist', 'Add the sites you care about on the Monitor page and see at a glance which are up and which are having a bad day.'],
        ['Instant alerts', 'We email you when a site goes down and when it is back. You can also connect Telegram, Slack or Discord for a message on your phone.'],
        ['Your checks, saved', 'Every check you run while signed in is saved to your account, so you can look back or run it again in one tap.'],
        ['Still free, still no spam', 'The checker works for everyone without an account. We only email you about things you asked for, like alerts and password resets.'],
    ];
    $html = '<p style="margin:0 0 6px">Your free siteupdown.com account is ready.</p>';
    $text = "Your free siteupdown.com account is ready.\n";
    foreach ($items as [$h, $t]) {
        $html .= '<h2 style="margin:20px 0 4px;font-size:18px;color:#ffffff">' . $h . '</h2><p style="margin:0">' . $t . '</p>';
        $text .= "\n" . $h . "\n" . $t . "\n";
    }
    $html .= '<p style="margin:22px 0 0;font-size:14px">You signed up' . $via . ' using ' . $e . '. If that was not you, you can ignore this message.</p>';
    $text .= "\nYou signed up" . $via . " using $email. If that was not you, you can ignore this message.";
    return [$html, $text];
}
