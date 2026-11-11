from PIL import Image,ImageDraw,ImageFont
import numpy as np
DIR='D:/n64/힘내라고에몽-네오모모야마막부의춤/'
def render(ch,fontfile,size,box=14,yoff=0,thr=110):
    f=ImageFont.truetype(DIR+fontfile,size)
    im=Image.new('L',(64,64),0);dr=ImageDraw.Draw(im)
    dr.text((32,32),ch,font=f,fill=255,anchor='mm')
    a=np.array(im)
    # fixed placement: center glyph from em box rather than bbox to keep baseline consistent
    ys,xs=np.nonzero(a>thr)
    out=np.zeros((16,16),np.uint8)
    if len(xs)==0: return out
    # crop around center 32,32
    cx,cy=32,32+yoff
    sub=a[cy-7:cy+7,cx-7:cx+7]
    fill=(sub>thr)
    out[1:15,1:15][fill]=1
    m=out==1
    dil=np.zeros_like(m)
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            dil|=np.roll(np.roll(m,dy,0),dx,1)
    out[(dil)&(~m)]=2
    return out
def show(glyphs,path,scale=4):
    im=Image.new('RGB',(len(glyphs)*17,16),(40,40,40))
    pal={0:(0,0,0),1:(255,255,255),2:(90,60,30)}
    for i,g in enumerate(glyphs):
        for y in range(16):
            for x in range(16): im.putpixel((i*17+x,y),pal[int(g[y][x])])
    im.resize((im.width*scale,im.height*scale),Image.NEAREST).save(path)

def render_small(ch, fontfile='Galmuri9.ttf', size=10, W=10, H=12):
    """작은 글자: 갈무리9 원래 크기(10px) 그대로 1:1, 오른쪽·아래 그림자. 16x16 타일의 좌상단 10x12 사용"""
    f = ImageFont.truetype(DIR + fontfile, size)
    im = Image.new('L', (32, 32), 0)
    ImageDraw.Draw(im).text((4, 4), ch, font=f, fill=255)
    a = np.array(im) > 127
    ys, xs = np.nonzero(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape
    m = np.zeros((H, W), bool)
    ox = max(0, (W - 1 - w) // 2); oy = max(0, (H - 1 - h) // 2)
    m[oy:oy + h, ox:ox + w] = a[:H - oy, :W - ox]
    sh = np.zeros_like(m)
    sh[1:, 1:] |= m[:-1, :-1]; sh[:, 1:] |= m[:, :-1]; sh[1:, :] |= m[:-1, :]
    out = np.zeros((16, 16), np.uint8)
    out[:H, :W][sh & ~m] = 2
    out[:H, :W][m] = 1
    return out


def render_tiny(ch, bank):
    """bank2: 8x10 칸(갈무리7 8px + 그림자, y=1), bank3: 7x8 칸(갈무리7 8px, 그림자 없음, y=1)"""
    f = ImageFont.truetype(DIR + 'Galmuri7.ttf', 8)
    im = Image.new('L', (32, 32), 0)
    ImageDraw.Draw(im).text((4, 4), ch, font=f, fill=255)
    a = np.array(im) > 127
    ys, xs = np.nonzero(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape
    W, H = (8, 10) if bank == 2 else (7, 8)
    m = np.zeros((16, 16), bool)
    ox = max(0, (W - (1 if bank == 2 else 0) - w) // 2)
    m[1:1 + h, ox:ox + w] = a[:15, :16 - ox]
    out = np.zeros((16, 16), np.uint8)
    if bank == 2:
        sh = np.zeros_like(m)
        sh[1:, 1:] |= m[:-1, :-1]; sh[:, 1:] |= m[:, :-1]; sh[1:, :] |= m[:-1, :]
        out[sh & ~m] = 2
    out[m] = 1
    out[H:, :] = 0; out[:, W:] = 0
    return out


def render_label(s):
    """두 글자를 16x8로 그린 뒤 세로 2배(16x16) — 게임이 14x8로 줄여 그림"""
    f = ImageFont.truetype(DIR + 'Galmuri7.ttf', 8)
    m = np.zeros((8, 16), bool)
    for i, ch in enumerate(s):
        im = Image.new('L', (16, 16), 0)
        ImageDraw.Draw(im).text((2, 2), ch, font=f, fill=255)
        a = np.array(im) > 127
        ys, xs = np.nonzero(a)
        a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1][:8, :8]
        h, w = a.shape
        m[(8 - h) // 2:(8 - h) // 2 + h, i * 8 + (8 - w) // 2:i * 8 + (8 - w) // 2 + w] = a
    m = np.repeat(m, 2, axis=0)
    out = np.zeros((16, 16), np.uint8)
    sh = np.zeros_like(m); sh[1:, 1:] = m[:-1, :-1]
    out[sh & ~m] = 2
    out[m] = 1
    return out
