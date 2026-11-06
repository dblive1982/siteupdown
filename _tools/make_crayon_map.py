"""Builds assets/nl-crayon-world.png: the crayon folded-paper picture with a crayon-drawn world map on it.
Source paper: _tools/crayon-paper.png (cropped from the Canva map). Needs numpy, scipy, Pillow.  Run from the repo root."""
import re, json, numpy as np
from scipy import ndimage as nd
from PIL import Image
ROOT = '.'
a = np.array(Image.open(ROOT + '/_tools/crayon-paper.png').convert('RGB')).astype(float)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
bg = (abs(R - 241) < 7) & (abs(G - 241) < 7) & (abs(B - 245) < 7)
H, W = bg.shape
rng = np.random.default_rng(11)
# 1. wipe the doodles off the paper, keeping its folds
paperlike = (R >= 228) & (G >= 208) & (B >= 115) & ((R - B) < 135) & ~bg
bad = nd.binary_dilation(~paperlike & ~bg, iterations=7) & ~bg
idx = nd.distance_transform_edt(~(~bad & ~bg), return_distances=False, return_indices=True)
f = a[idx[0], idx[1]]
for c in range(3): f[..., c] = nd.gaussian_filter(np.where(bad, f[..., c], a[..., c]), 4)
paper = np.where(bad[..., None], f, a); paper = np.where(bg[..., None], a, paper)
paper[~bg] += (nd.gaussian_filter(rng.normal(0, 1, (H, W)), 1.2) * 5)[~bg][:, None]
# 2. world land
L = re.search(r'SUD_LAND="([^"]*)"', open(ROOT + '/assets/landmask.js').read()).group(1)
AL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
M = np.zeros((180, 360))
for r, row in enumerate(L.split(';')):
    x = 0; cur = 0
    for i in range(0, len(row) - 1, 2):
        run = (AL.index(row[i]) << 6) | AL.index(row[i + 1])
        if cur: M[r, x:x + run] = 1
        x += run; cur ^= 1
TOP, BOT = 16, 146
M = np.pad(M[TOP:BOT], ((3, 3), (0, 0)))
X0, Y0, Wd, Hd = 52, 110, 856, 560
U = nd.zoom(M, (Hd / M.shape[0], Wd / M.shape[1]), order=1); U = nd.gaussian_filter(U, (4, 2.4))
land = np.zeros((H, W), float); land[Y0:Y0 + U.shape[0], X0:X0 + U.shape[1]] = U[:Hd, :Wd]
# hand-drawn wobble: shift the edge with smooth noise
dx = nd.gaussian_filter(rng.normal(0, 1, (H, W)), 9) * 30; dy = nd.gaussian_filter(rng.normal(0, 1, (H, W)), 9) * 30
yy, xx = np.mgrid[0:H, 0:W]
land = nd.map_coordinates(land, [yy + dy, xx + dx], order=1, mode='nearest')
land = nd.gaussian_filter(land + nd.gaussian_filter(rng.normal(0, 1, (H, W)), 1.4) * 0.07, 1.0)
mask = (land > 0.5) & ~bg
# 3. crayon colour: three greens from the original map, stroke texture
lab, n = nd.label(mask); sizes = nd.sum(mask, lab, range(1, n + 1)); order = np.argsort(-sizes)
greens = [(128, 170, 62), (98, 156, 68), (84, 146, 72)]
col = np.zeros((H, W, 3))
for rank, i in enumerate(order): col[lab == i + 1] = greens[rank % 3] if rank < 6 else greens[0]
def streaks(sig_along, sig_across, ang):
    z = nd.gaussian_filter(rng.normal(0, 1, (H, W)), 1.0)
    z = nd.rotate(z, ang, reshape=False, order=1, mode='reflect')
    z = nd.gaussian_filter(z, (sig_across, sig_along)); z = nd.rotate(z, -ang, reshape=False, order=1, mode='reflect')
    return z / (z.std() + 1e-6)
s1 = streaks(9, 0.9, -35); s2 = streaks(6, 0.8, 50)
light = 1 + 0.035 * s1 + 0.02 * s2
cover = np.clip(0.95 + 0.05 * s1 - 0.03 * np.abs(s2), 0.78, 1.0)
rim = nd.gaussian_filter(mask.astype(float), 2.2); darker = 1 - 0.14 * np.clip((0.75 - rim) * 3, 0, 1)
paper_shade = nd.gaussian_filter(paper.mean(-1), 6) / 232.0
fill = col * (light * darker * np.clip(paper_shade, 0.86, 1.05))[..., None]
m = nd.gaussian_filter(mask.astype(float), 0.7)
a_ = (m * cover)[..., None]
out = paper * (1 - a_) + fill * a_
out = np.clip(out, 0, 255).astype(np.uint8)
alpha = nd.gaussian_filter(nd.binary_closing(~bg, iterations=3).astype(float), 1.2)
Image.fromarray(np.dstack([out, (alpha * 255).astype(np.uint8)])).save(ROOT + '/assets/nl-crayon-world.png', optimize=True)
json.dump(dict(x0=X0, y0=Y0, w=Wd, h=Hd, W=W, H=H, rows=M.shape[0], top=90 - TOP + 3), open(ROOT + '/_tools/crayon_geo.json', 'w'))
print('ok', X0, Y0, Wd, Hd, M.shape[0])
