"""일본어 UI 텍스처 -> 한글 텍스처 생성 (work/tex/XXXX.png 원본, work/tex_ko/XXXX.png 결과)"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
R = 'D:/n64/힘내라고에몽-네오모모야마막부의춤/'
T = R + 'work/tex/'; O = R + 'work/tex_ko/'
HV = R + 'NanumSquareNeo-eHv.ttf'; EB = R + 'NanumSquareNeo-dEb.ttf'; BD = R + 'NanumSquareNeo-cBd.ttf'
G11 = R + 'Galmuri11.ttf'; G9 = R + 'Galmuri9.ttf'

def load(k): return Image.open(T + k + '.png').convert('RGBA')
def save(k, im): im.save(O + k + '.png')

def mask(text, font, size, w, h, x=None, y=None, aa=True, spacing=0, sx=1.0):
    """텍스트 알파 마스크 (w x h), 가운데 정렬 기본"""
    f = ImageFont.truetype(font, size)
    big = Image.new('L', (w * 4 + 200, h * 4 + 200), 0)
    d = ImageDraw.Draw(big)
    if not aa: d.fontmode = '1'
    cx = 100
    for ch in text:
        d.text((cx, 100), ch, font=f, fill=255)
        cx += int(d.textlength(ch, font=f)) + spacing
    a = np.array(big)
    ys, xs = np.nonzero(a > 40)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(a)
    if sx != 1.0: im = im.resize((max(1, int(im.width * sx)), im.height), Image.LANCZOS)
    out = Image.new('L', (w, h), 0)
    px = (w - im.width) // 2 if x is None else x
    py = (h - im.height) // 2 if y is None else y
    out.paste(im, (px, py))
    return out

def fitmask(text, font, w, h, box, aa=True, spacing=0, maxsize=40, sx=1.0):
    """box=(x,y,bw,bh) 안에 들어가는 최대 크기로"""
    bx, by, bw, bh = box
    for s in range(maxsize, 5, -1):
        m = mask(text, font, s, bw, bh, aa=aa, spacing=spacing, sx=sx)
        a = np.array(mask_raw(text, font, s, spacing, sx, aa))
        if a.shape[1] <= bw and a.shape[0] <= bh:
            out = Image.new('L', (w, h), 0); out.paste(m, (bx, by)); return out
    raise ValueError(text)

def mask_raw(text, font, size, spacing=0, sx=1.0, aa=True):
    f = ImageFont.truetype(font, size)
    big = Image.new('L', (len(text) * size * 2 + 200, size * 3 + 200), 0)
    d = ImageDraw.Draw(big)
    if not aa: d.fontmode = '1'
    cx = 100
    for ch in text:
        d.text((cx, 100), ch, font=f, fill=255); cx += int(d.textlength(ch, font=f)) + spacing
    a = np.array(big); ys, xs = np.nonzero(a > 40)
    im = Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    if sx != 1.0: im = im.resize((max(1, int(im.width * sx)), im.height), Image.LANCZOS)
    return im

def dilate(m, r):
    return m.filter(ImageFilter.MaxFilter(2 * r + 1)) if r > 0 else m

def grad(w, h, cols, y0=0, y1=None):
    """세로 그라데이션 RGBA (cols: [(pos0..1, (r,g,b))])"""
    y1 = h if y1 is None else y1
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        t = min(1, max(0, (y - y0) / max(1, (y1 - y0 - 1))))
        for i in range(len(cols) - 1):
            if cols[i][0] <= t <= cols[i + 1][0]:
                u = (t - cols[i][0]) / max(1e-6, cols[i + 1][0] - cols[i][0])
                c = [int(cols[i][1][k] * (1 - u) + cols[i + 1][1][k] * u) for k in range(3)]
                break
        a[y, :, :3] = c; a[y, :, 3] = 255
    return Image.fromarray(a, 'RGBA')

def layer(base, m, color):
    """마스크 m 위치에 color(RGB 튜플 또는 RGBA 이미지) 합성"""
    src = Image.new('RGBA', base.size, color + (255,)) if isinstance(color, tuple) else color
    base.paste(src, (0, 0), m)
    return base

def clear(im, box, color=(0, 0, 0, 0)):
    d = ImageDraw.Draw(im); d.rectangle(box, fill=color); return im
