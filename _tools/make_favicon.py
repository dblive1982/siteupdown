# Tab icon: white question mark on a black rounded square (matches the header).
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def make(n, full=False):
    S=n*4
    im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    if full: d.rectangle([0,0,S,S],fill=(0,0,0,255))
    else: d.rounded_rectangle([0,0,S-1,S-1],radius=int(S*.22),fill=(0,0,0,255))
    f=ImageFont.truetype(F,int(S*.82)); bb=d.textbbox((0,0),'?',font=f)
    d.text(((S-(bb[2]-bb[0]))/2-bb[0],(S-(bb[3]-bb[1]))/2-bb[1]),'?',font=f,fill=(255,255,255,255))
    return im.resize((n,n),Image.LANCZOS)
for n in (16,32,64,192,512): make(n).save({192:'favicon-192.png',512:'android-chrome-512.png'}.get(n,'favicon-%d.png'%n))
make(180,True).convert('RGB').save('apple-touch-icon.png')
make(48).save('favicon.ico',sizes=[(16,16),(32,32),(48,48)])
