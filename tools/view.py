import sys
from PIL import Image
def render(data,bpp,W,H,cols=16,scale=2):
    gsz=W*H*bpp//8;n=len(data)//gsz;rows=(n+cols-1)//cols
    im=Image.new('L',(cols*(W+1),rows*(H+1)),40)
    for g in range(n):
        b=data[g*gsz:(g+1)*gsz];bits=''.join(f'{x:08b}' for x in b)
        for y in range(H):
            for x in range(W):
                v=int(bits[(y*W+x)*bpp:(y*W+x+1)*bpp],2)*255//((1<<bpp)-1)
                im.putpixel(((g%cols)*(W+1)+x,(g//cols)*(H+1)+y),v)
    return im.resize((im.width*scale,im.height*scale),Image.NEAREST)
if __name__=='__main__':
    f,off,ln,bpp,W,H,out=sys.argv[1:8]
    d=open(f,'rb').read()[int(off,0):int(off,0)+int(ln,0)]
    render(d,int(bpp),int(W),int(H)).save(out)
