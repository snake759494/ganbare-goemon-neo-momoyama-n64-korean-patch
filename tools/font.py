from PIL import Image
ROM='D:/n64/힘내라고에몽-네오모모야마막부의춤/Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64'
FONT=0x637C0
def glyph(d,code,base=FONT):
    b=d[base+(code>>1)*128:base+(code>>1)*128+128]
    k=code&1
    px=[[0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            byte=b[y*8+x//2]; nib=(byte>>4) if x%2==0 else byte&15
            px[15-y][x]=(nib>>(2*k))&3
    return px
if __name__=='__main__':
    import sys
    d=open(ROM,'rb').read();N=int(sys.argv[1],0)
    im=Image.new('L',(32*17,(N//32+1)*17),40)
    for c in range(N):
        g=glyph(d,c)
        for y in range(16):
            for x in range(16): im.putpixel(((c%32)*17+x,(c//32)*17+y),g[y][x]*85)
    im.resize((im.width*2,im.height*2)).save(sys.argv[2])
