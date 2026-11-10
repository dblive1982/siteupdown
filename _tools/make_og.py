"""Branded 1200x630 share image for each page (what shows when a link is pasted into Facebook, X, WhatsApp, Slack, Discord, iMessage...).
Built at site-build time; an image is only redrawn when the page title or section changes (tracked in assets/og/_manifest.json)."""
import os, json, hashlib
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'og')
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
W, H = 1200, 630
YELLOW, INK, CREAM = (255, 222, 89), (17, 17, 17), (255, 251, 234)

def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def make(slug, title, label):
    os.makedirs(OUT, exist_ok=True)
    man_p = os.path.join(OUT, '_manifest.json')
    man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    key = hashlib.md5((title + '|' + label + '|v2').encode()).hexdigest()
    path = os.path.join(OUT, slug + '.jpg')
    if man.get(slug) == key and os.path.exists(path): return '/assets/og/' + slug + '.jpg'
    im = Image.new('RGB', (W, H), YELLOW); d = ImageDraw.Draw(im)
    # halftone dots in the top-right corner for the comic feel
    for gx in range(0, 420, 28):
        for gy in range(0, 260, 28):
            r = max(0, 9 - (gx + gy) / 55.0)
            if r > 1: d.ellipse([W - 40 - gx - r, 40 + gy - r, W - 40 - gx + r, 40 + gy + r], fill=(240, 196, 40))
    # card with comic offset shadow
    d.rounded_rectangle([64, 64, W - 40, H - 40], 36, fill=INK)
    d.rounded_rectangle([52, 52, W - 52, H - 52], 36, fill=CREAM, outline=INK, width=8)
    # section label pill
    f_lab = ImageFont.truetype(FONT, 30); lw = d.textlength(label.upper(), font=f_lab)
    d.rounded_rectangle([96, 92, 96 + lw + 44, 148], 28, fill=INK); d.text((118, 99), label.upper(), font=f_lab, fill=YELLOW)
    # title, shrinking until it fits in at most 4 lines
    size = 80
    while True:
        f = ImageFont.truetype(FONT, size); lines = _wrap(d, title, f, W - 220)
        if len(lines) * int(size * 1.18) <= 250 or size <= 36: break
        size -= 4
    lh = int(size * 1.18); y = 178
    for ln in lines[:5]:
        d.text((98, y + 4), ln, font=f, fill=(222, 214, 180)); d.text((96, y), ln, font=f, fill=INK); y += lh
    # logo and tagline
    logo = os.path.join(ROOT, 'assets', 'nl-logo.png')
    if os.path.exists(logo):
        lg = Image.open(logo).convert('RGBA'); lg.thumbnail((210, 100)); im.paste(lg, (96, H - 52 - 24 - lg.size[1]), lg)
    f_s = ImageFont.truetype(FONT, 28); tag = 'Is it down, or just you?'
    d.text((W - 96 - d.textlength(tag, font=f_s), H - 52 - 24 - 36), tag, font=f_s, fill=INK)
    im.save(path, 'JPEG', quality=72, optimize=True)
    man[slug] = key; json.dump(man, open(man_p, 'w'))
    return '/assets/og/' + slug + '.jpg'
