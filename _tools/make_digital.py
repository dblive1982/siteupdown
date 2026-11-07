"""Dot-matrix (digital) version of the continents map -> assets/nl-continents-digital.png (needs assets/nl-continents.png)."""
from PIL import Image, ImageDraw
import numpy as np
a=np.array(Image.open('assets/nl-continents.png').convert('RGB')).astype(np.float32)
OC=np.array((200,225,238),np.float32); GR=np.array((176,208,226),np.float32)
t=np.clip(np.minimum(np.linalg.norm(a-OC,axis=2),np.linalg.norm(a-GR,axis=2))/50,0,1)
H,W=t.shape;S=3;P=15
img=Image.new('RGB',(W*S,H*S),(241,241,245));d=ImageDraw.Draw(img)
for y in range(P//2,H,P):
    for x in range(P//2,W,P):
        v=t[max(0,y-P//2):y+P//2,max(0,x-P//2):x+P//2].mean()
        if v>.5: r,c=5.2,(70,82,104)
        else: r,c=1.5,(223,224,232)
        d.ellipse([(x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S],fill=c)
img.resize((W,H),Image.LANCZOS).save('assets/nl-continents-digital.png',optimize=True)
