<?php
// TEST SITE ONLY: accepts a report but stores nothing.
header('Content-Type: application/json');
echo json_encode(['ok' => true, 'added' => 1, 'message' => 'Thanks. This is the test site, so nothing was saved.']);
