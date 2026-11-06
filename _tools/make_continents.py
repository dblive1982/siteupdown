# Builds assets/nl-continents.png (flat WorldAtlas-style continents map) from _tools/continents-src.png
import numpy as np, json
from PIL import Image, ImageDraw
AX,BX,AY,BY,MIX=3.41904622,-24.79309414,-213.39670053,670.34834736,0.5   # fitted at 1250px, x5 for 6250
S=2.5
def miller(p):return 1.25*np.log(np.tan(np.pi/4+0.4*np.radians(p)))
def fl(p):return MIX*miller(p)+(1-MIX)*np.radians(p)
def fwd(lon,lat):return (AX*(lon+180)+BX)*S,(AY*fl(lat)+BY)*S
im=np.array(Image.open('_tools/continents-src.png').convert('RGB').resize((3125,3125),Image.LANCZOS)).astype(np.int16)
H,W,_=im.shape
bg=im[0,0]
dist=np.abs(im-bg).sum(2)
alpha=np.clip(dist/150.0,0,1)
land=dist>40
# inverse projection tables
latt=np.linspace(-70,90,3201);ft=fl(latt)
lon=((np.arange(W,dtype=np.float32)/S-BX)/AX-180)[None,:].repeat(H,0)
f=((np.arange(H,dtype=np.float32)/S-BY)/AY)[:,None].repeat(W,1)
lat=np.interp(f,ft,latt).astype(np.float32)
# original colour classes
def near(c,t=60):return np.abs(im-np.array(c)).sum(2)<t
cls=np.zeros((H,W),np.uint8)  # 0 none
teal=near((0,172,140),80);ltb=near((64,185,206),80);grn=near((130,208,40),80);org=near((255,164,26),80);pur=near((146,16,105),80);red=near((255,64,42),80)
# fallback by nearest of the six
cols=np.array([(0,172,140),(64,185,206),(130,208,40),(255,164,26),(146,16,105),(255,64,42)])
d=np.stack([np.abs(im-c).sum(2) for c in cols],2);k=d.argmin(2)
PAL={'NA':(255,198,92),'SA':(255,97,97),'AF':(106,103,255),'EU':(0,176,80),'AS':(203,200,144),'ME':(255,140,0),'OC':(224,64,251),'CA':(42,26,160)}
out=np.zeros((H,W,3),np.uint8);name=np.empty((H,W),'<U2');name[:]=''
name[k==0]='NA';name[k==1]='NA';name[k==3]='AF';name[k==4]='SA';name[k==5]='OC'
g=(k==2)
def poly(pts):
    im2=Image.new('L',(W,H),0);d2=ImageDraw.Draw(im2)
    dense=[]
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]+pts[:1]):
        for t in np.linspace(0,1,30,endpoint=False):dense.append(fwd(x1+(x2-x1)*t,y1+(y2-y1)*t))
    d2.polygon(dense,fill=255);return np.array(im2)>0
ME_P=[(24,43),(41.5,43),(46,41),(49,39.5),(54,38),(55,37.5),(60.8,36.6),(62,38),(65,37.8),(70,38),(74,37.5),(71.5,34),(70,31.5),(66.5,30),(62.5,29.5),(61.5,25.5),(63,24),(60,10),(26,10)]
EU_P=[(-35,34),(-35,85),(70,85),(68,76),(66,70),(62,66),(60,60),(59,55),(55,51),(51,50.5),(49,47),(48,44),(46,43),(42,43),(37,41),(28,40),(26,36)]
ME=poly(ME_P);EU=poly(EU_P)&~ME
me=g&ME;eu=g&EU
name[g]='AS';name[eu]='EU';name[me]='ME'
# Turkey north coast / Caucasus belong to ME polygon only below 43
ca=(k==0)&poly([(-92.2,14.3),(-90.9,17.9),(-88,18.6),(-82,17),(-77.2,9.5),(-77.2,6),(-93,6)])
name[ca]='CA'
# Egypt/Sinai: orange (Africa) east of Suez stays Africa
for n,c in PAL.items():out[name==n]=c
# ocean + grid
OC=np.array((127,208,255),np.uint8)
canvas=np.zeros((H,W,3),np.uint8);canvas[:]=OC
img=Image.fromarray(canvas);dr=ImageDraw.Draw(img)
GR=(98,184,242)
for lo in range(-180,181,30):
    pts=[fwd(lo,la) for la in np.linspace(-62,85,60)];dr.line(pts,fill=GR,width=4)
for la in range(-60,90,15):
    pts=[fwd(lo,la) for lo in np.linspace(-180,180,120)];dr.line(pts,fill=GR,width=4)
canvas=np.array(img).astype(np.float32)
a=(alpha*land)[...,None]
# soften AA edges: land where classified
res=canvas*(1-a)+out.astype(np.float32)*a
res=np.clip(res,0,255).astype(np.uint8)
# crop
x0,x1=0,W;y0,y1=690,2280
res=res[y0:y1,x0:x1]
final=Image.fromarray(res).resize((2400,int(2400*(y1-y0)/(x1-x0))),Image.LANCZOS)
final.save('assets/nl-continents.png',optimize=True)
json.dump({'ax':AX,'bx':BX,'ay':AY,'by':BY,'mix':MIX,'S':S,'x0':x0,'y0':y0,'w':x1-x0,'h':y1-y0,'outW':2400,'outH':final.size[1]},open('_tools/continents_geo.json','w'))
print(final.size)
