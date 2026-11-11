import json,sys
from PIL import Image,ImageDraw
res=json.load(open('../work/tex/index.json'))
ims=[r for r in res if isinstance(r[3],list)]
N=40;C=8;CW=136;CH=150
for s in range(0,len(ims),N):
    S=Image.new('RGB',(C*CW,(N//C)*CH),(90,0,90));d=ImageDraw.Draw(S)
    for i,r in enumerate(ims[s:s+N]):
        im=Image.open('../work/tex/%04x.png'%r[0]); w,h=im.size
        k=max(1,min(2,128//max(w,h)) if max(w,h)<=128 else 1)
        if max(w,h)>128: im.thumbnail((128,128)) 
        else: im=im.resize((w*k,h*k),0)
        x=(i%C)*CW;y=(i//C)*CH
        S.paste(im,(x,y+12),im); d.text((x,y),'%x %dx%d'%(r[0],w,h),fill=(255,255,0))
    S.save('../work/tex/sheet_%02d.png'%(s//N))
print((len(ims)+N-1)//N)
