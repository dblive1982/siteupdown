<?php
// TEST SITE ONLY: sample CSV.
header('Content-Type: text/csv; charset=utf-8'); header('Content-Disposition: attachment; filename="sample-uptime.csv"');
echo "site,date_utc,checks,successful_checks,uptime_percent,average_response_ms,outages,minutes_down\nSample,2026-11-01,288,288,100,250,0,0\nSample,2026-11-02,288,286,99.31,262,1,10\n";
