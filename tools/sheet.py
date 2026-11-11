import sys,os
from PIL import Image,ImageDraw
d=sys.argv[1];fs=[f for f in sorted(os.listdir(d)) if f.endswith('.png') and not f.startswith('06') or len(sys.argv)>3]
ims=[(f,Image.open(os.path.join(d,f))) for f in fs]
W=1100;x=y=0;rowh=0;pos=[]
for f,im in ims:
    if x+im.width>W: x=0;y+=rowh+14;rowh=0
    pos.append((f,im,x,y));x+=im.width+6;rowh=max(rowh,im.height)
S=Image.new('RGB',(W,y+rowh+14),(60,0,60));dr=ImageDraw.Draw(S)
for f,im,x,y in pos:
    S.paste(im,(x,y+12),im);dr.text((x,y),f[:6],fill=(255,255,0))
S.save(sys.argv[2])
