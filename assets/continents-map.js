(function(){
var A={ax:3.41904622,bx:-24.79309414,ay:-213.39670053,by:670.34834736,mix:0.5,S:2.5,y0:690,k:2400/3125};
function mil(p){return 1.25*Math.log(Math.tan(Math.PI/4+0.4*p*Math.PI/180))}
function PR(lon,lat){var f=A.mix*mil(lat)+(1-A.mix)*lat*Math.PI/180;return [(A.ax*(lon+180)+A.bx)*A.S*A.k,((A.ay*f+A.by)*A.S-A.y0)*A.k]}
var NS='http://www.w3.org/2000/svg',COL={g:'#2fbf4a',a:'#ffb020',r:'#e84a4a'};
var CN=[['NORTH AMERICA',-103,50,52],['SOUTH AMERICA',-60,-14,46],['AFRICA',19,6,56],['EUROPE',17,52.5,38],['ASIA',92,50,64],['MIDDLE EAST',46,26.5,30],['AUSTRALIA &amp; OCEANIA',134,-25,36]];
var OC=[['ATLANTIC',-35,30,30],['OCEAN',-35,24,30],['PACIFIC',-150,10,30],['OCEAN',-150,4,30],['INDIAN',78,-20,30],['OCEAN',78,-26,30],['ARCTIC OCEAN',-60,80,26],['PACIFIC',160,-45,26],['OCEAN',160,-51,26]];
var P=[['London',51.5,-0.1,'g',99,120],['New York',40.7,-74,'g',94,210],['Sao Paulo',-23.5,-46.6,'a',78,640],['Johannesburg',-26.2,28,'r',56,980],['Mumbai',19,72.8,'a',78,420],['Tokyo',35.7,139.7,'g',97,180],['Sydney',-33.9,151.2,'g',95,300],['Los Angeles',34,-118,'g',96,230],['Singapore',1.3,103.8,'g',98,160],['Dubai',25.2,55.3,'g',92,260]];
var h='';
CN.forEach(function(c){var p=PR(c[1],c[2]);h+='<text class="cn" x="'+p[0].toFixed(0)+'" y="'+p[1].toFixed(0)+'" style="font-size:'+c[3]+'px">'+c[0]+'</text>'});
OC.forEach(function(c){var p=PR(c[1],c[2]);h+='<text class="oc" x="'+p[0].toFixed(0)+'" y="'+p[1].toFixed(0)+'" style="font-size:'+c[3]+'px">'+c[0]+'</text>'});
P.forEach(function(p,i){var q=PR(p[2],p[1]);
 h+='<g class="pole '+p[3]+(i==4?' on':'')+'" data-i="'+i+'" transform="translate('+q[0].toFixed(1)+' '+q[1].toFixed(1)+')">'
  +(p[3]!='g'?'<circle class="ring" r="14" fill="none" stroke="'+COL[p[3]]+'" stroke-width="5"/>':'')
  +'<ellipse cx="0" cy="2" rx="20" ry="7" fill="rgba(0,0,0,.28)"/><line x1="0" y1="0" x2="0" y2="-100" stroke="#3a2412" stroke-width="7" stroke-linecap="round"/>'
  +'<path class="flag" d="M3 -100 L66 -84 L3 -64 Z" fill="'+COL[p[3]]+'" stroke="#111" stroke-width="5.5" stroke-linejoin="round"/><circle cx="0" cy="-104" r="9" fill="#111"/>'
  +'<text class="pl" x="0" y="-124" text-anchor="middle">'+p[0].toUpperCase()+'</text></g>'});
document.getElementById('lay').innerHTML=h;
document.getElementById('lay').addEventListener('click',function(e){var g=e.target.closest('.pole');if(!g)return;document.querySelectorAll('.pole').forEach(function(n){n.classList.remove('on')});g.classList.add('on');var p=P[+g.getAttribute('data-i')];document.getElementById('pn').textContent=p[0];var c=document.getElementById('pc');c.textContent=p[4]+'%';c.style.background=COL[p[3]];document.getElementById('pt').textContent='Typical time '+p[5]+' ms'});
})();
