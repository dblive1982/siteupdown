
(function(){
var G={x0:30,y0:240,w:900,h:340,rows:136,top:77};
function X(lon){return G.x0+(lon+180)/360*G.w}function Y(lat){return G.y0+(G.top-lat)/G.rows*G.h}
var PAL=['#f4a259','#f6d55c','#f28ab0','#b79ced','#8fcf6f','#6fb7e8','#ef8a7a','#78d4bd','#e9b872','#c5e17a'];
var SHORT={'United States of America':'USA','Dem. Rep. Congo':'DR CONGO','Central African Rep.':'C.A.R.','Dominican Rep.':'','Bosnia and Herz.':'','S. Sudan':'S. SUDAN','Saudi Arabia':'SAUDI ARABIA','United Kingdom':'UK','United Arab Emirates':'','Papua New Guinea':'PAPUA N.G.','New Zealand':'NEW ZEALAND','South Africa':'SOUTH AFRICA','South Korea':'','North Korea':'','W. Sahara':'','Falkland Is.':'','Greenland':'GREENLAND','Eq. Guinea':'','Fiji':'','Solomon Is.':'','Vanuatu':'','New Caledonia':'','Fr. S. Antarctic Lands':''};
var SMALLOK={'United Kingdom':1,'Japan':1,'Italy':1,'Germany':1,'France':1,'Spain':1,'Poland':1,'Turkey':1,'Norway':1,'Sweden':1,'Finland':1,'Ukraine':1,'Iran':1,'Iraq':1,'Egypt':1,'Vietnam':1,'Thailand':1,'Myanmar':1,'Philippines':1,'Malaysia':1,'Cuba':1,'Nepal':0,'Ghana':0,'Nigeria':1,'Kenya':1,'Uganda':0,'Cameroon':0,'Venezuela':1,'Colombia':1,'Peru':1,'Bolivia':1,'Chile':1,'Paraguay':0,'Uruguay':0,'Ecuador':0,'Guyana':0,'Madagascar':1,'Zambia':1,'Mozambique':1,'Tanzania':1,'Somalia':1,'Ethiopia':1,'Zimbabwe':0,'Namibia':1,'Botswana':1,'Angola':1,'Libya':1,'Algeria':1,'Morocco':1,'Mali':1,'Niger':1,'Chad':1,'Sudan':1,'Mauritania':1,'Pakistan':1,'Afghanistan':1,'Kazakhstan':1,'Mongolia':1,'India':1,'China':1,'Russia':1,'Canada':1,'Brazil':1,'Argentina':1,'Mexico':1,'Indonesia':1,'Australia':1,'Greenland':1};
function hash(s){var h=0;for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))>>>0;return h}
function dec(str){var out=[],px=0,py=0;str.split(' ').forEach(function(t){var p=t.split(',');px+=parseInt(p[0],36);py+=parseInt(p[1],36);out.push([px/2,py/2])});return out}
fetch('assets/countries.json').then(function(r){return r.json()}).then(function(j){
  var land='',hat='',names='';
  j.c.forEach(function(c,ci){
    var d='',best=null,ba=0;
    c[1].split('|').forEach(function(rs){
      var pts=dec(rs),minx=1e9,maxx=-1e9,miny=1e9,maxy=-1e9;
      d+='M'+pts.map(function(p){var x=X(p[0]),y=Y(p[1]);if(x<minx)minx=x;if(x>maxx)maxx=x;if(y<miny)miny=y;if(y>maxy)maxy=y;return x.toFixed(1)+' '+y.toFixed(1)}).join('L')+'Z';
      var a=(maxx-minx)*(maxy-miny);if(a>ba){ba=a;best=[(minx+maxx)/2,(miny+maxy)/2,maxx-minx]}
    });
    var col=PAL[hash(c[0])%PAL.length];
    land+='<path d="'+d+'" fill="'+col+'" fill-opacity=".92" stroke="#7a4a2b" stroke-width="1.3" stroke-linejoin="round"/>';
    hat+='<path d="'+d+'" fill="url(#hatch)"/>';
    var nm=SHORT.hasOwnProperty(c[0])?SHORT[c[0]]:c[0].toUpperCase();
    if(nm&&best&&(best[2]>34||SMALLOK[c[0]])&&ba>700){var fs=Math.max(8,Math.min(14,best[2]/9));names+='<text class="cn" x="'+best[0].toFixed(0)+'" y="'+best[1].toFixed(0)+'" style="font-size:'+fs.toFixed(1)+'px">'+nm.replace('&','&amp;')+'</text>';}
  });
  document.getElementById('land').innerHTML=land;document.getElementById('hatchg').innerHTML=hat;document.getElementById('names').innerHTML=names;
});
var seas=[['ATLANTIC',-35,22],['OCEAN',-35,16],['PACIFIC',-150,5],['OCEAN',-150,-1],['PACIFIC',165,-12],['OCEAN',165,-18],['INDIAN',82,-24],['OCEAN',82,-30],['ARCTIC OCEAN',-110,76],['SOUTHERN OCEAN',20,-52]];
document.getElementById('seas').innerHTML=seas.map(function(s){return '<text class="oc" x="'+X(s[1]).toFixed(0)+'" y="'+Y(s[2]).toFixed(0)+'">'+s[0]+'</text>'}).join('');
var P=[['London',51.5,-0.1,'g',99,120],['New York',40.7,-74,'g',94,210],['Sao Paulo',-23.5,-46.6,'a',78,640],['Johannesburg',-26.2,28,'r',56,980],['Mumbai',19,72.8,'a',78,420],['Tokyo',35.7,139.7,'g',97,180],['Sydney',-33.9,151.2,'g',95,300],['Los Angeles',34,-118,'g',96,230],['Singapore',1.3,103.8,'g',98,160],['Dubai',25.2,55.3,'g',92,260]];
var COL={g:'#7ed957',a:'#ffb020',r:'#e84a4a'},ph='';
P.forEach(function(p,i){var x=X(p[2]).toFixed(1),y=Y(p[1]).toFixed(1);
 ph+='<g class="pole'+(i==4?' on':'')+'" data-i="'+i+'" transform="translate('+x+' '+y+')"><ellipse cx="0" cy="1" rx="9" ry="3.5" fill="rgba(0,0,0,.28)"/><line x1="0" y1="0" x2="0" y2="-46" stroke="#4a2c17" stroke-width="3.4" stroke-linecap="round"/><path d="M1.5 -46 L30 -39 L1.5 -30 Z" fill="'+COL[p[3]]+'" stroke="#111" stroke-width="2.6" stroke-linejoin="round"/><circle cx="0" cy="-48" r="4" fill="#111"/><rect x="-14" y="-72" width="1" height="1" fill="none"/><text x="0" y="-56" text-anchor="middle">'+p[0].toUpperCase()+'</text></g>';});
document.getElementById('poles').innerHTML=ph;
document.getElementById('poles').addEventListener('click',function(e){var g=e.target.closest('.pole');if(!g)return;document.querySelectorAll('.pole').forEach(function(n){n.classList.remove('on')});g.classList.add('on');var p=P[+g.getAttribute('data-i')];document.getElementById('pn').textContent=p[0];document.getElementById('pc').textContent=p[4]+'%';document.getElementById('pc').style.background=COL[p[3]];document.getElementById('pt').textContent='Typical time '+p[5]+' ms'});
})();
