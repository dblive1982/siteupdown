<?php
// TEST SITE ONLY: fixed sample data so the heat map globe can be styled. Not real results.
header('Content-Type: application/json');
$p = [['London','GB',51.5,-0.1,128,132,60,1,2,1],['Frankfurt','DE',50.1,8.7,124,132,77,3,3,2],['Dubai','AE',25.2,55.3,123,132,462,4,3,2],['Buenos Aires','AR',-34.6,-58.4,124,132,257,3,3,2],['Sydney','AU',-33.9,151.2,123,132,247,4,3,2],['Sao Paulo','BR',-23.5,-46.6,123,132,228,4,3,2],['Montreal','CA',45.5,-73.6,121,132,107,5,4,2],['Tokyo','JP',35.7,139.7,100,132,150,20,8,4],['Johannesburg','ZA',-26.2,28.0,123,132,300,4,3,2],['Dallas','US',32.8,-96.8,126,132,90,3,2,1],['Mumbai','IN',19.1,72.9,120,132,210,6,4,2],['Singapore','SG',1.3,103.8,125,132,140,3,2,2]];
$places = [];
foreach ($p as $r) $places[] = ['city'=>$r[0],'country'=>$r[1],'lat'=>$r[2],'lon'=>$r[3],'ok'=>$r[4],'n'=>$r[5],'median_ms'=>$r[6],'error'=>$r[7],'blocked'=>$r[8],'none'=>$r[9]];
echo json_encode(['places'=>$places,'sites_count'=>132,'newest'=>time()-300,'oldest'=>time()-7200,'unreachable'=>[]]);
