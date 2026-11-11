"""RDRAM 덤프의 디스플레이 리스트에서 텍스처를 추출"""
import sys,os,struct
from PIL import Image
def conv(ram,addr,fmt,siz,w,h,pal=None):
    bpp=[4,8,16,32][siz];n=w*h*bpp//8
    d=ram[addr:addr+n]
    if len(d)<n: return None
    im=Image.new('RGBA',(w,h))
    px=[]
    for i in range(w*h):
        if bpp==4:
            b=d[i//2];v=(b>>4) if i%2==0 else b&15
        elif bpp==8: v=d[i]
        elif bpp==16: v=int.from_bytes(d[i*2:i*2+2],'big')
        else: v=int.from_bytes(d[i*4:i*4+4],'big')
        if fmt==0 and bpp==16: px.append((((v>>11)&31)*8,((v>>6)&31)*8,((v>>1)&31)*8,255*(v&1)))
        elif fmt==0 and bpp==32: px.append((v>>24,(v>>16)&255,(v>>8)&255,v&255))
        elif fmt==4: g=v*255//((1<<bpp)-1);px.append((g,g,g,255))
        elif fmt==3:
            if bpp==4: g=(v>>1)*36;a=255*(v&1)
            elif bpp==8: g=(v>>4)*17;a=(v&15)*17
            else: g=v>>8;a=v&255
            px.append((g,g,g,a))
        elif fmt==2 and pal is not None:
            c=int.from_bytes(ram[pal+v*2:pal+v*2+2],'big')
            px.append((((c>>11)&31)*8,((c>>6)&31)*8,((c>>1)&31)*8,255*(c&1)))
        else: g=v*255//((1<<bpp)-1) if bpp<16 else 128;px.append((g,g,g,255))
    im.putdata(px);return im
def scan(ram):
    res={}
    tlut=None;seg=[0]*16
    for i in range(0,len(ram)-64,8):
        w0=int.from_bytes(ram[i:i+4],'big')
        if (w0&0xff0000ff)==0xbc000006:
            seg[((w0>>8)&0xffff)//4 & 15]=int.from_bytes(ram[i+4:i+8],'big')&0xffffff
        if w0>>24==0xfd:
            fmt=(w0>>21)&7;siz=(w0>>19)&3;addr=int.from_bytes(ram[i+4:i+8],'big')
            sg=addr>>24
            if sg in (0x80,0xa0): a=addr&0xffffff
            elif sg<16: a=(seg[sg]+(addr&0xffffff))&0xffffff
            else: continue
            if a>=len(ram): continue
            # 다음 명령들에서 F0(loadtlut)/F3(loadblock)/F2(settilesize)/F5(settile)
            info={'fmt':fmt,'siz':siz,'addr':a}
            for j in range(i+8,i+8*12,8):
                c=int.from_bytes(ram[j:j+4],'big');c1=int.from_bytes(ram[j+4:j+8],'big')
                if c>>24==0xf0: info['tlut']=True
                if c>>24==0xf5 and (c1>>24)&7==0:
                    info['tfmt']=(c>>21)&7;info['tsiz']=(c>>19)&3;info['line']=(c>>9)&0x1ff
                if c>>24==0xf2 and (c1>>24)&7==0:
                    info['w']=((c1>>12)&0xfff)//4+1;info['h']=(c1&0xfff)//4+1
                if c>>24==0xfd and j>i: break
            if info.get('tlut'): tlut=a;continue
            info['pal']=tlut
            if 'w' in info: res.setdefault(a,info)
    return res
if __name__=='__main__':
    ram=open(sys.argv[1],'rb').read();out=sys.argv[2];os.makedirs(out,exist_ok=True)
    r=scan(ram)
    for a,inf in sorted(r.items()):
        fmt=inf.get('tfmt',inf['fmt']);siz=inf.get('tsiz',inf['siz'])
        w,h=inf['w'],inf['h']
        if w*h>256*256 or w<4 or h<4: continue
        im=conv(ram,a,fmt,siz,w,h,inf.get('pal'))
        if im: im.resize((w*2,h*2),Image.NEAREST).save(out+'/%06x_f%d_s%d_%dx%d.png'%(a,fmt,siz,w,h))
    print(len(r))
