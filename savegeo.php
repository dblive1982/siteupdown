<?php
// TEMPORARY: receives the country map data once from the owner's browser, then this file is deleted.
header('Content-Type: text/plain');
if ($_SERVER['REQUEST_METHOD']!=='POST' || ($_GET['t']??'')!=='c0bc51f2ea03e15d') { http_response_code(403); exit('no'); }
$d=file_get_contents('php://input');
if (strlen($d)<1000 || strlen($d)>400000 || json_decode($d)===null) { http_response_code(400); exit('bad'); }
file_put_contents(__DIR__.'/assets/countries.json',$d);
echo 'saved '.strlen($d);
