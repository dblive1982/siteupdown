<?php
// The sites that have an "Is X down?" page. The list is written by _tools/build.py into _sitepages.json.
declare(strict_types=1);

function site_pages(): array {
    static $list = null;
    if ($list !== null) return $list;
    $j = @file_get_contents(__DIR__ . '/_sitepages.json');
    $d = $j ? json_decode($j, true) : null;
    return $list = (is_array($d) ? $d : []);   // host => ['name' => ..., 'page' => '/is-x-down', 'cat' => ...]
}
