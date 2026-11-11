import picdec,sys,numpy as np
from PIL import Image
def rgba16(v):
    return ((v>>11&31)*255//31,(v>>6&31)*255//31,(v>>1&31)*255//31,255 if v&1 else 0)
def img(w,h,b,s,d):
    if b in (15,16):
        px=[rgba16(int.from_bytes(d[i*2:i*2+2],'big')) for i in range(w*h)]
    elif b==8:
        n=w*h; extra=s-n
        pal=[rgba16(int.from_bytes(d[n+i*2:n+i*2+2],'big')) for i in range(extra//2)] if extra>=2 else []
        px=[pal[x] if x<len(pal) else (x,x,x,255) for x in d[:n]]
    elif b==4:
        n=w*h//2; extra=s-n
        pal=[rgba16(int.from_bytes(d[n+i*2:n+i*2+2],'big')) for i in range(extra//2)]
        px=[]
        for x in d[:n]:
            for v in (x>>4,x&15): px.append(pal[v] if v<len(pal) else (v*17,)*3+(255,))
    im=Image.new('RGBA',(w,h)); im.putdata(px); return im
if __name__=='__main__':
    for k in sys.argv[1:]:
        r=picdec.decode(open('../work/files/%04d.bin'%int(k),'rb').read())
        print(k,r[:4]); img(*r).save('../work/pic/%04d.png'%int(k))
