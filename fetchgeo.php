<?php
header('Content-Type: text/plain');
$u='https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json';
$d=@file_get_contents($u);
if(!$d && function_exists('curl_init')){$c=curl_init($u);curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>1,CURLOPT_FOLLOWLOCATION=>1,CURLOPT_TIMEOUT=>20]);$d=curl_exec($c);}
if($d){file_put_contents(__DIR__.'/geo-countries.json',$d);echo 'saved '.strlen($d);}else echo 'failed';
