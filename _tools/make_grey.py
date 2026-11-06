"""Greyscale version of assets/nl-continents.png (run after make_continents.py)."""
from PIL import Image
import numpy as np
a=np.array(Image.open('assets/nl-continents.png').convert('RGB')).astype(np.float32)
OC=np.array((200,225,238),np.float32); GR=np.array((176,208,226),np.float32)
dO=np.linalg.norm(a-OC,axis=2); dG=np.linalg.norm(a-GR,axis=2)
t=np.clip(np.minimum(dO,dG)/50,0,1)
L=a@np.array([.299,.587,.114],np.float32)
land=np.clip(110+(L-60)*0.5,95,185)
ocean=np.where(dG<dO,214,232).astype(np.float32)
g=ocean*(1-t)+land*t
Image.fromarray(np.dstack([g,g,g]).clip(0,255).astype(np.uint8)).save('assets/nl-continents-grey.png',optimize=True)
