import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
from texko import *

def binmask(text, font, size, spacing=0, sx=1.0, thr=110, aa=False):
    m = mask_raw(text, font, size, spacing, sx, aa=aa)
    return np.array(m) > thr

def fit(text, font, bw, bh, spacing=0, sx=1.0, aa=False, thr=110):
    for s in range(60, 5, -1):
        m = binmask(text, font, s, spacing, sx, thr, aa)
        if m.shape[1] <= bw and m.shape[0] <= bh: return m
    raise ValueError(text)

def dil(m, r=1, diag=True):
    p = np.pad(m, r); o = np.zeros_like(m)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if not diag and abs(dx) + abs(dy) > r: continue
            o |= p[r + dy:r + dy + m.shape[0], r + dx:r + dx + m.shape[1]]
    return o

def gradcol(cols, t):
    for i in range(len(cols) - 1):
        if cols[i][0] <= t <= cols[i + 1][0]:
            u = (t - cols[i][0]) / max(1e-6, cols[i + 1][0] - cols[i][0])
            return tuple(int(cols[i][1][k] * (1 - u) + cols[i + 1][1][k] * u) for k in range(3))
    return cols[-1][1]

def stamp(A, m, x, y, cols, outline=None, shadow=None, orad=1, diag=True):
    """A: HxWx4 uint8 배열에 마스크 m을 (x,y)에 그림. cols 세로 그라데이션"""
    h, w = m.shape
    pad = 3
    M = np.zeros((h + 2 * pad, w + 2 * pad), bool); M[pad:pad + h, pad:pad + w] = m
    layers = []
    if shadow:
        dx, dy, c = shadow
        S = np.zeros_like(M); S[pad + dy:pad + dy + h, pad + dx:pad + dx + w] = m
        if outline: S = dil(S, orad, diag)
        layers.append((S, lambda yy: c))
    if outline: layers.append((dil(M, orad, diag), lambda yy: outline))
    layers.append((M, lambda yy: gradcol(cols, (yy - pad) / max(1, h - 1)) if isinstance(cols, list) else cols))
    H, W = A.shape[:2]
    for L, cf in layers:
        ys, xs = np.nonzero(L)
        for yy, xx in zip(ys, xs):
            X, Y = x + xx - pad, y + yy - pad
            if 0 <= X < W and 0 <= Y < H:
                A[Y, X, :3] = cf(yy); A[Y, X, 3] = 255
    return A

def stamp_aa(A, alpha, x, y, color, under=None):
    """안티앨리어스 마스크(0..255)를 불투명 합성: under 색 위에 color 블렌드"""
    h, w = alpha.shape
    for yy in range(h):
        for xx in range(w):
            a = alpha[yy, xx] / 255
            if a <= 0: continue
            X, Y = x + xx, y + yy
            if not (0 <= X < A.shape[1] and 0 <= Y < A.shape[0]): continue
            base = A[Y, X, :3].astype(float) if A[Y, X, 3] else np.array(under if under else color, float)
            A[Y, X, :3] = (base * (1 - a) + np.array(color) * a).astype(np.uint8); A[Y, X, 3] = 255
    return A

YEL = [(0, (255, 255, 200)), (0.35, (255, 255, 74)), (0.75, (255, 205, 49)), (1, (213, 148, 24))]

def m8764():
    U = ImageOps.flip(load('8764')); A = np.zeros((32, 64, 4), np.uint8)
    for txt, y0 in (('옵션', 0), ('스타트', 16)):
        f = ImageFont.truetype(HV, 13)
        m = mask_raw(txt, HV, 13, spacing=1)
        al = np.array(m)
        h, w = al.shape
        x = (64 - w) // 2; y = y0 + (16 - h) // 2
        hard = al > 60
        o = dil(np.pad(hard, 2), 1)
        ys, xs = np.nonzero(o)
        for yy, xx in zip(ys, xs):
            X, Y = x + xx - 2, y + yy - 2
            if 0 <= X < 64 and 0 <= Y < 32: A[Y, X] = (49, 49, 49, 255)
        stamp_aa(A, al, x, y, (255, 255, 255), (49, 49, 49))
    save('8764', ImageOps.flip(Image.fromarray(A, 'RGBA')))

def label_aitemu():
    """8017 상단 띠 + 8015/8016 박스 라벨"""
    B = np.array(load('8017'))
    band = B[13, 45].copy()
    B[3:6, 4:43] = 0
    B[6:13, 4:43] = band
    m = fit('아이템', G11, 37, 9)
    h, w = m.shape
    x = 4 + (39 - w) // 2; y = 3 + (10 - h) // 2
    stamp(B, m, x, y, [(0, (255, 255, 120)), (0.5, (255, 255, 60)), (1, (240, 190, 40))], outline=(57, 24, 0), diag=False)
    # 골드 라인 끝부분 복원 (라벨 좌우)
    save('8017', Image.fromarray(B, 'RGBA'))
    a = load('8015'); b = load('8016'); T = Image.new('RGBA', (128, 32)); T.paste(a, (0, 0)); T.paste(b, (64, 0))
    C = np.array(T); C[0:7, 32:71] = B[6:13, 4:43]
    T = Image.fromarray(C, 'RGBA'); save('8015', T.crop((0, 0, 64, 32))); save('8016', T.crop((64, 0, 128, 32)))

def m8696():
    A = np.array(load('8696')); A[:] = 0
    m = fit('아이템', HV, 44, 12, spacing=1)
    h, w = m.shape
    stamp(A, m, 1 + (44 - w) // 2, 2 + (12 - h) // 2, YEL, outline=(8, 8, 8), shadow=(1, 1, (8, 8, 8)))
    save('8696', Image.fromarray(A, 'RGBA'))

def nyang_icon():
    """8009 의 両 아이콘(16x16 정도) -> 냥"""
    A = np.array(load('8009'))
    sub = A[0:16, 44:64]
    ys, xs = np.nonzero(sub[:, :, 3])
    # 両 아이콘 범위: 검은 테두리 사각형
    blk = (sub[:, :, 0] < 20) & (sub[:, :, 3] > 0)
    yy, xx = np.nonzero(blk)
    x0, x1, y0, y1 = xx.min(), xx.max(), yy.min(), yy.max()
    reg = A[y0:y1 + 1, 44 + x0:44 + x1 + 1]
    reg[:, :] = (8, 8, 8, 255)
    m = binmask('냥', G9, 10)
    h, w = m.shape
    stamp(A, m, 44 + x0 + (x1 - x0 + 1 - w) // 2, y0 + (y1 - y0 + 1 - h) // 2, [(0, (255, 255, 115)), (1, (205, 164, 0))])
    save('8009', Image.fromarray(A, 'RGBA'))
    return (x0, x1, y0, y1)

def m8677():
    A = np.array(load('8677'))
    # 90両 흰 글자: 0..~23 x, 0..12 y  -> 両 자리만 지우고 냥
    al = (A[:, :, 3] > 0) & (A[:, :, 0] > 200) & (A[:, :, 1] > 200)
    ys, xs = np.nonzero(al[0:14, :])
    return xs.min(), xs.max(), ys.min(), ys.max()

if __name__ == '__main__':
    m8764(); label_aitemu(); m8696(); print(nyang_icon()); print(m8677())

import collections
def rowcols(A, x0, x1, dark=40):
    cols = {}
    for y in range(A.shape[0]):
        c = collections.Counter(tuple(A[y, x, :3]) for x in range(x0, x1) if A[y, x, 3] and max(A[y, x, :3]) > dark)
        if c: cols[y] = c.most_common(1)[0][0]
    ys = sorted(cols)
    out = {}
    for y in range(A.shape[0]):
        if y in cols: out[y] = cols[y]
        else:
            n = min(ys, key=lambda t: abs(t - y)); out[y] = cols[n]
    return out

def stamp_rows(A, m, x, y, rc, outline=None, diag=True):
    h, w = m.shape
    if outline is not None:
        o = dil(np.pad(m, 1), 1, diag)
        ys, xs = np.nonzero(o)
        for yy, xx in zip(ys, xs):
            X, Y = x + xx - 1, y + yy - 1
            if 0 <= X < A.shape[1] and 0 <= Y < A.shape[0]: A[Y, X] = outline + (255,)
    ys, xs = np.nonzero(m)
    for yy, xx in zip(ys, xs):
        X, Y = x + xx, y + yy
        if 0 <= X < A.shape[1] and 0 <= Y < A.shape[0]: A[Y, X, :3] = rc[Y]; A[Y, X, 3] = 255

def nyang_big(k, box, digit_x, outline=None, font=HV):
    U = ImageOps.flip(load(k)); A = np.array(U)
    rc = rowcols(A, *digit_x)
    x0, y0, x1, y1 = box
    A[y0:y1 + 1, x0:x1 + 1] = 0
    pad = 1 if outline else 0
    m = fit('냥', font, x1 - x0 + 1 - 2 * pad, y1 - y0 + 1 - 2 * pad)
    h, w = m.shape
    stamp_rows(A, m, x0 + (x1 - x0 + 1 - w) // 2, y0 + (y1 - y0 + 1 - h) // 2, rc, outline)
    save(k, ImageOps.flip(Image.fromarray(A, 'RGBA')))

NY7 = ['.....W.', 'W....W.', 'W....WW', 'W....W.', 'W....WW', 'WWWW.W.', '.....W.', '..WWW..', '.W...W.', '.W...W.', '.W...W.', '..WWW..']
def m8677():
    A = np.array(load('8677'))
    A[0:14, 16:23] = 0
    for i, r in enumerate(NY7):
        for j, c in enumerate(r):
            if c == 'W': A[1 + i, 16 + j] = (255, 255, 255, 255)
    save('8677', Image.fromarray(A, 'RGBA'))

def nyang_icon2():
    A = np.array(load('8009'))
    A[6:15, 49:58] = (8, 8, 8, 255)
    m = binmask('냥', G9, 10)
    h, w = m.shape
    rc = {y: gradcol([(0, (255, 255, 115)), (0.5, (255, 230, 65)), (1, (205, 164, 0))], (y - 6) / 8) for y in range(32)}
    stamp_rows(A, m[:9, :9], 49 + (9 - min(9, w)) // 2, 6 + (9 - min(9, h)) // 2, rc)
    save('8009', Image.fromarray(A, 'RGBA'))

def run_nyang():
    nyang_icon2(); m8677()
    nyang_big('843c', (48, 16, 63, 31), (20, 47), outline=(0, 0, 8))
    nyang_big('85da', (40, 4, 62, 29), (13, 31))
    nyang_big('85db', (40, 4, 62, 29), (1, 33))

def kbox(A, x0, ch):
    A[3:29, x0 + 3:x0 + 29] = (0, 0, 148, 255)
    for s in range(30, 8, -1):
        al = np.array(mask_raw(ch, HV, s))
        if al.shape[0] <= 23 and al.shape[1] <= 23: break
    h, w = al.shape
    x = x0 + 3 + (26 - w) // 2; y = 3 + (26 - h) // 2
    halo = dil(np.pad(al > 60, 1), 1)
    ys, xs = np.nonzero(halo)
    for yy, xx in zip(ys, xs): A[y + yy - 1, x + xx - 1] = (65, 65, 172, 255)
    stamp_aa(A, al, x, y, (255, 255, 255), (0, 0, 148))

def impact():
    for k, chs in (('8595', '연돈'), ('8598', '적')):
        A = np.array(ImageOps.flip(load(k)))
        for i, ch in enumerate(chs): kbox(A, 32 * i, ch)
        save(k, ImageOps.flip(Image.fromarray(A, 'RGBA')))

import cv2
def inpaint(A, boxes, thr=140):
    rgb = A[:, :, :3].copy()
    M = np.zeros(A.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes:
        sub = A[y0:y1 + 1, x0:x1 + 1].astype(int)
        w = (sub[:, :, 0] > thr) & (sub[:, :, 1] > thr) & (sub[:, :, 2] > thr)
        M[y0:y1 + 1, x0:x1 + 1] = w * 255
    M = cv2.dilate(M, np.ones((3, 3), np.uint8))
    out = cv2.inpaint(np.ascontiguousarray(rgb[:, :, ::-1]), M, 3, cv2.INPAINT_TELEA)[:, :, ::-1]
    A[:, :, :3] = out
    return A

def vtext(A, text, x0, y0, x1, y1, font=HV, color=(255, 255, 255), sizes=None):
    n = len(text); cw = x1 - x0 + 1; ch = (y1 - y0 + 1) // n
    for i, c in enumerate(text):
        for s in range(40, 5, -1):
            al = np.array(mask_raw(c, font, s))
            lim_h = ch - 1 if c not in '·' else ch
            if al.shape[0] <= lim_h and al.shape[1] <= cw: break
        if c == '·':
            al = np.array(mask_raw('·', font, 12))
        h, w = al.shape
        stamp_aa(A, al, x0 + (cw - w) // 2, y0 + i * ch + (ch - h) // 2, color)

def boards():
    A = np.array(load('8679'))
    inpaint(A, [(56, 60, 74, 110), (37, 60, 53, 124)])
    vtext(A, 'A·결정', 57, 60, 72, 110)
    vtext(A, 'B·취소', 38, 60, 53, 110)
    save('8679', Image.fromarray(A, 'RGBA'))
    A = np.array(load('867a'))
    inpaint(A, [(110, 52, 125, 126), (86, 72, 108, 126)])
    vtext(A, '어느데이터를', 111, 52, 124, 125)
    vtext(A, '지울래?', 87, 70, 107, 126)
    save('867a', Image.fromarray(A, 'RGBA'))

def madamada():
    a = load('86ae'); b = load('86af'); T = Image.new('RGBA', (128, 32)); T.paste(a, (0, 0)); T.paste(b, (64, 0))
    A = np.array(T)
    A[0:16, 0:73] = 0
    A[16:32, 0:66] = 0
    m = fit('아직이다', HV, 70, 14, spacing=2, sx=1.25)
    h, w = m.shape
    stamp(A, m, 72 - w, 1 + (14 - h) // 2, [(0, (255, 255, 164)), (0.5, (255, 255, 0)), (1, (255, 205, 49))], outline=(246, 98, 16))
    m = fit('자, 가자', HV, 56, 14, spacing=1, sx=1.15)
    h, w = m.shape
    stamp(A, m, 64 - w, 17 + (14 - h) // 2, [(0, (197, 238, 255)), (1, (57, 156, 255))], outline=(0, 74, 131))
    T = Image.fromarray(A, 'RGBA'); save('86ae', T.crop((0, 0, 64, 32))); save('86af', T.crop((64, 0, 128, 32)))

def clear8618():
    A = np.array(load('8618'))
    I = A.astype(int); R, G, B = I[:, :, 0], I[:, :, 1], I[:, :, 2]
    yel = (R > 60) & (G > 45) & (G > B * 1.25) & (R > B * 1.4) & (G > R * 0.68)
    gray = (R > 120) & (G > 120) & (B > 100) & (abs(R - G) < 40) & (abs(G - B) < 60)
    M = np.zeros(A.shape[:2], np.uint8)
    y0, y1, x0, x1 = 22, 82, 20, 300
    M[y0:y1, x0:x1] = ((yel | gray)[y0:y1, x0:x1]) * 255
    M = cv2.morphologyEx(M, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    M = cv2.dilate(M, np.ones((3, 3), np.uint8))
    A[:, :, :3] = cv2.inpaint(np.ascontiguousarray(A[:, :, :3][:, :, ::-1]), M, 5, cv2.INPAINT_TELEA)[:, :, ::-1]
    return A

def text3d(A, text, box, font=HV, depth=5, spacing=2, sx=1.0):
    bx, by, bw, bh = box
    m = fit(text, font, bw - depth - 2, bh - depth - 2, spacing=spacing, sx=sx, aa=True, thr=100)
    h, w = m.shape
    x = bx + (bw - depth - w) // 2; y = by + (bh - depth - h) // 2
    # 돌출(뒤에서 앞으로)
    for d in range(depth, 0, -1):
        c = gradcol([(0, (40, 30, 0)), (1, (150, 110, 10))], 1 - d / depth)
        stamp(A, m, x + d, y + d, c, outline=None)
    stamp(A, m, x, y, [(0, (255, 255, 230)), (0.3, (255, 240, 90)), (0.6, (230, 180, 20)), (0.8, (255, 230, 80)), (1, (190, 130, 0))], outline=(30, 20, 0))

def m8618():
    A = clear8618()
    text3d(A, '클리어 축하해!', (22, 24, 280, 58), depth=5, spacing=3)
    save('8618', Image.fromarray(A, 'RGBA'))
