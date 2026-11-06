<?php
// POST {topic, name, email, site, message, website(honeypot)} -> emails the message to hello@siteupdown.com.
require __DIR__ . '/_boot.php';
require __DIR__ . '/_mail.php';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['error' => 'POST only.']);
$in = json_decode((string)file_get_contents('php://input'), true);
if (!is_array($in)) out(400, ['error' => 'Something went wrong. Please try again.']);
if (trim((string)($in['website'] ?? '')) !== '') out(200, ['ok' => true]);          // honeypot: bots fill this in, pretend success
$topics = [
    'feedback' => 'General feedback', 'issue' => 'Report a problem with the site', 'wrong' => 'A check gave the wrong result',
    'addsite' => 'Suggest a site to add', 'account' => 'Account or sign-in help', 'complaint' => 'Complaint',
    'data' => 'Data or privacy request', 'business' => 'Advertising or business enquiry', 'other' => 'Something else',
];
$topic = (string)($in['topic'] ?? '');
$name = trim(preg_replace('/\s+/', ' ', (string)($in['name'] ?? '')));
$email = trim((string)($in['email'] ?? ''));
$site = trim(preg_replace('/\s+/', ' ', (string)($in['site'] ?? '')));
$msg = trim(str_replace("\r", '', (string)($in['message'] ?? '')));
if (!isset($topics[$topic])) out(422, ['error' => 'Please choose what your message is about.']);
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 200) out(422, ['error' => 'Please enter a valid email address so we can reply.']);
if (mb_strlen($msg) < 10) out(422, ['error' => 'Please write a little more so we can help (at least 10 characters).']);
if (mb_strlen($msg) > 4000) out(422, ['error' => 'That message is too long. Please keep it under 4000 characters.']);
if (preg_match_all('~https?://~i', $msg) > 3) out(422, ['error' => 'Please include no more than three links.']);
$name = mb_substr($name, 0, 80);
$site = mb_substr($site, 0, 253);
throttle('contact', 5, 60);                      // five messages an hour from one address
$c = config() ?: [];
$to = $c['contact_to'] ?? 'hello@siteupdown.com';
$e = fn($v) => htmlspecialchars($v, ENT_QUOTES, 'UTF-8');
$label = $topics[$topic];
$html = '<p style="margin:0 0 4px"><b>Topic:</b> ' . $e($label) . '</p>'
    . '<p style="margin:0 0 4px"><b>From:</b> ' . $e($name !== '' ? $name : '(no name)') . ' &lt;' . $e($email) . '&gt;</p>'
    . ($site !== '' ? '<p style="margin:0 0 4px"><b>Website:</b> ' . $e($site) . '</p>' : '')
    . '<p style="margin:14px 0 0;white-space:pre-wrap">' . $e($msg) . '</p>';
$text = "Topic: $label\nFrom: " . ($name !== '' ? $name : '(no name)') . " <$email>\n" . ($site !== '' ? "Website: $site\n" : '') . "\n$msg\n";
note_attempt('contact');
sud_email($to, '[Contact] ' . $label . ($site !== '' ? ' - ' . $site : ''), 'New message from the contact form', $html, $text, '', '', $email);
out(200, ['ok' => true, 'message' => 'Thanks, your message has been sent. We will reply by email.']);
