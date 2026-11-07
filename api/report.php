<?php
// TEST SITE ONLY: accepts a report but stores nothing.
header('Content-Type: application/json');
$b = json_decode(file_get_contents('php://input'), true); $fx = !empty($b['kinds']) && $b['kinds'] === ['fixed'];
echo json_encode(['ok' => true, 'added' => 1, 'message' => $fx ? 'Thanks. This is the test site, so nothing was saved.' : 'Thanks. This is the test site, so nothing was saved.']);
