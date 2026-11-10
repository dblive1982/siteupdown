"""Builds assets/nl-continents-comic.png (comic-style world map, same 2400x1221 frame) from assets/nl-continents.png."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src = np.array(Image.open('assets/nl-continents.png').convert('RGB')).astype(int)
H, W, _ = src.shape
KEYS = {  # source colour -> comic colour
    (203, 200, 144): (184, 161, 255),  # Asia - lavender
    (255, 198, 92): (255, 224, 102),   # North America - yellow
    (106, 103, 255): (255, 170, 80),   # Africa - orange
    (0, 176, 80): (96, 200, 255),      # Europe - sky blue
    (255, 97, 97): (255, 143, 190),    # South America - pink
    (224, 64, 251): (112, 224, 204),   # Australia - teal
    (255, 140, 0): (255, 122, 110),    # Middle East - coral
}
sea = np.array([200, 225, 238])
d_sea = np.abs(src - sea).sum(2)
land = d_sea > 90
land = ndi.binary_opening(land, iterations=1)
land = ndi.binary_fill_holes(land)
# region id by nearest key colour (Central America & stray colours join nearest)
keys = list(KEYS); K = np.array(keys)
dist = np.stack([np.abs(src - k).sum(2) for k in K], 2)
reg = dist.argmin(2)
reg[~land] = -1
ca = land & (np.abs(src - np.array([42, 26, 160])).sum(2) < 60)
reg[ca] = keys.index((255, 198, 92))
# fill unknown (e.g. dark blue Central America) with nearest known region colour; known if dist<60
known = (dist.min(2) < 60) | ca
idx = ndi.distance_transform_edt(~(known & land), return_distances=False, return_indices=True)
reg2 = reg[idx[0], idx[1]]; reg = np.where(land, reg2, -1)
out = np.zeros((H, W, 3), np.uint8)
SEA = np.array([196, 232, 255]); out[:] = SEA
yy, xx = np.mgrid[0:H, 0:W]
# sea halftone dots (light) every 22px
sd = ((xx % 22 - 11) ** 2 + (yy % 22 - 11) ** 2) < 7
out[sd & ~land] = [172, 218, 247]
# drop shadow of land (offset down-right)
sh = np.roll(np.roll(land, 11, 0), 11, 1)
out[sh & ~land] = [128, 184, 222]
# land fill
for i, k in enumerate(keys):
    out[reg == i] = KEYS[k]
# halftone shading on land: dots growing toward the bottom-right of each landmass
lab, n = ndi.label(land)
dt = ndi.distance_transform_edt(land)
tone = np.clip(1 - dt / 38.0, 0, 1)            # darker near coasts
phase = ((xx + yy) % 2400) / 2400.0
r = 5.2 * tone * (0.5 + 0.5 * ((xx + yy) / (W + H)))  # stronger lower-right
cell = 16
dx = (xx % cell) - cell / 2 + 0.5; dy = (yy % cell) - cell / 2 + 0.5
dots = (dx * dx + dy * dy) < r * r
base = out.astype(float)
dark = (base * 0.78).astype(np.uint8)
m = dots & land
out[m] = dark[m]
# region borders and thick outline
ink = np.zeros((H, W), bool)
rb = (reg != np.roll(reg, 1, 0)) | (reg != np.roll(reg, 1, 1))
rb &= land & np.roll(land, 1, 0) & np.roll(land, 1, 1)
ink |= ndi.binary_dilation(rb, iterations=1)
edge = ndi.binary_dilation(land, iterations=4) & ~ndi.binary_erosion(land, iterations=0 + 1) if False else (ndi.binary_dilation(land, iterations=4) & ~land) | (land & ~ndi.binary_erosion(land, iterations=2))
ink |= edge
out[ink] = [17, 17, 17]
Image.fromarray(out).save('assets/nl-continents-comic.png', optimize=True)
print('ok', out.shape)
