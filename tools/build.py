import json, os, re, sys, glob
import numpy as np
import nisi, scen, table, font, fontgen, mips, crc, lzkn

ROOT = 'D:/n64/힘내라고에몽-네오모모야마막부의춤/'
WORK = ROOT + 'work/'
OUT = ROOT + 'Ganbare Goemon - Neo Momoyama Bakufu no Odori (Korean).z64'
CACHE = WORK + 'zcache/'
KO_START = 0x200
FONT_RAM = 0x80400000
FONTFILE = 'NanumSquareNeo-cBd.ttf'

TAGS = {v: k for k, v in scen.CTRL.items()}
# 반각/한국어 문장부호 -> 원본 폰트 코드
PUNCT = {' ': 0x0d, '　': 0x0d, '!': 0x0b, '?': 0x0c, '-': 0x0a, '.': 0xdc, ',': 0xda,
         '~': 0x12f, '「': 0x127, '」': 0x129, '、': 0x128, '…': None, '·': 0xe8,
         '(': 0x102, ')': 0x103, '[': 0x12c, ']': 0x12d, '【': 0x124, '】': 0x125,
         ':': 0xde, '/': 0xdd, '+': 0xd9, '*': 0xd8, '#': 0xd6, '"': 0xd5, "'": 0xd7,
         '♪': 0x148, '○': 0x164, '×': 0xeb, '=': 0xdf, '@': 0xe1, '%': None}
for i, c in enumerate('0123456789'):
    PUNCT[c] = 0xb0 + i
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    PUNCT[c] = 0xba + i


def is_ko(c):
    return 0xAC00 <= ord(c) <= 0xD7A3


def load_tr():
    tr = {}
    for f in glob.glob(WORK + 'tr/*.json'):
        k = int(os.path.basename(f)[:4])
        tr[k] = {e['o']: e['ko'] for e in json.load(open(f, encoding='utf-8')) if e.get('ko') is not None}
    return tr


def charset(texts):
    cs = set()
    for t in texts:
        for c in re.sub(r'\{[^}]*\}', '', t):
            if is_ko(c):
                cs.add(c)
    return sorted(cs)


class Enc:
    def __init__(self, chars):
        self.map = {c: KO_START + i for i, c in enumerate(chars)}

    def enc(self, s):
        out = []
        i = 0
        while i < len(s):
            c = s[i]
            if c == '{':
                j = s.index('}', i)
                tag = s[i:j + 1]
                if tag in TAGS:
                    out.append(TAGS[tag])
                elif re.fullmatch(r'\{[0-9A-F]{4}\}', tag):
                    out.append(int(tag[1:5], 16))
                else:
                    raise ValueError('bad tag ' + tag + ' in ' + s)
                i = j + 1
                continue
            if c in self.map:
                out.append(self.map[c])
            elif c == '…':
                out += [0xe8, 0xe8, 0xe8]
            elif c in PUNCT and PUNCT[c] is not None:
                out.append(PUNCT[c])
            elif c in table.R:
                out.append(table.R[c])
            else:
                raise ValueError('unmapped char %r in %s' % (c, s))
            i += 1
        return out


def build_font(rom, chars, small=False, bank=1):
    """한글 타일만 생성 (코드 KO_START부터, 타일 0x100부터)"""
    n = len(chars)
    ntile = (n + 1) // 2
    buf = bytearray(ntile * 128)
    for i, c in enumerate(chars):
        code = KO_START + i
        g = (fontgen.render_small(c) if bank == 1 else fontgen.render_tiny(c, bank)) if small else fontgen.render(c, FONTFILE, 14)
        t = ((code >> 1) - 0x100) * 128
        k = code & 1
        for y in range(16):
            rr = 15 - y
            for x in range(16):
                v = int(g[y][x])
                bi = t + rr * 8 + x // 2
                sh = (4 if x % 2 == 0 else 0) + 2 * k
                buf[bi] = (buf[bi] & ~(3 << sh)) | (v << sh)
    return bytes(buf)


def encw(w):
    b = b''.join(x.to_bytes(2, 'big') for x in w)
    while len(b) % 4:
        b += b'\0\0'
    return b


def rebuild_scen(k, d, trk, E, log):
    res, refs = scen.strings(d)
    d = bytearray(d)
    seg = d[0] if False else None
    # 원래 텍스트 영역(4바이트 정렬)
    spans = []
    for o, (e, w) in res.items():
        spans.append((o, (e + 3) & ~3))
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    # 새 문자열
    newb = {}
    for o, (e, w) in res.items():
        if o in trk:
            nw = E.enc(trk[o]) + [0xffff]
        else:
            nw = w if w[-1] == 0xffff else w + [0xffff]
        newb[o] = encw(nw)
    for a, b in merged:
        d[a:b] = bytes(b - a)
    free = [list(x) for x in merged]
    newoff = {}
    dedup = {}
    for o in sorted(newb, key=lambda o: -len(newb[o])):
        bb = newb[o]
        if bb in dedup:
            newoff[o] = dedup[bb]
            continue
        for fr in free:
            if fr[1] - fr[0] >= len(bb):
                newoff[o] = fr[0]
                d[fr[0]:fr[0] + len(bb)] = bb
                fr[0] += len(bb)
                break
        else:
            while len(d) % 4:
                d += b'\0'
            newoff[o] = len(d)
            d += bb
            log.append('file %d: appended %d bytes' % (k, len(bb)))
        dedup[bb] = newoff[o]
    for i, o in refs:
        hi = d[i]
        d[i:i + 4] = ((hi << 24) | newoff[o]).to_bytes(4, 'big')
    return bytes(d)


def compress(k, data):
    os.makedirs(CACHE, exist_ok=True)
    import hashlib
    h = hashlib.md5(data).hexdigest()
    p = CACHE + '%04d_%s.bin' % (k, h)
    if os.path.exists(p):
        return open(p, 'rb').read()
    for f in glob.glob(CACHE + '%04d_*.bin' % k):
        os.remove(f)
    c = bytes(lzkn.compress_buffer(np.frombuffer(data, dtype=np.uint8)))
    assert nisi.decomp(c)[:len(data)] == data
    open(p, 'wb').write(c)
    return c


def patch_overlay_strings(k, d, trk, E, log):
    """trk: {off: ko} 오버레이 내 0000 종료 문자열 제자리 교체"""
    d = bytearray(d)
    for o, ko in trk.items():
        n = 0
        while int.from_bytes(d[o + n * 2:o + n * 2 + 2], 'big') != 0:
            n += 1
        # 종료 0 뒤 정렬용 0 패딩까지 사용 가능 (다음 0 아닌 값 직전 - 종료자 1개)
        m = n + 1
        while o + m * 2 + 2 <= len(d) and int.from_bytes(d[o + m * 2:o + m * 2 + 2], 'big') == 0 and m < n + 8:
            m += 1
        n = m - 1
        w = E.enc(ko)
        if len(w) > n:
            log.append('overlay %d @%x too long %d>%d: %s' % (k, o, len(w), n, ko))
            w = w[:n]
        b = b''.join(x.to_bytes(2, 'big') for x in w) + bytes((n - len(w)) * 2)
        d[o:o + n * 2] = b
    return bytes(d)


TEXTB = 0x80069514
SMOOTH = {0x8618: 90}


def tex_px(path, smooth_rows=0):
    from PIL import Image
    im = Image.open(path).convert('RGBA'); w, h = im.size
    px = [((R >> 3) << 11) | ((G >> 3) << 6) | ((B >> 3) << 1) | (1 if A >= 128 else 0) for R, G, B, A in im.getdata()]
    ch = lambda v: ((v >> 11) & 31, (v >> 6) & 31, (v >> 1) & 31)
    for i in range(1, w * smooth_rows):
        if px[i] != px[i - 1] and (px[i] & 1) == (px[i - 1] & 1) and all(abs(a - b) <= 1 for a, b in zip(ch(px[i]), ch(px[i - 1]))):
            px[i] = px[i - 1]
    return px, w, h


def build_textures(rom, files_raw):
    """work/tex_ko/XXXX.png -> PIC 재인코딩, 컨테이너 재구성. 반환: {file: bytes}, {id: newoff}"""
    import texall, picenc
    ents = texall.entries()
    rep = {}
    for f in glob.glob(WORK + 'tex_ko/*.png'):
        k = int(os.path.basename(f)[:4], 16)
        px, w, h = tex_px(f, SMOOTH.get(k, 0))
        rep[k] = picenc.encode(px, w, h)
    byfile = {}
    for id, f, a, b in ents:
        byfile.setdefault(f, []).append((a, id))
    out = {}; newoff = {}
    for f, lst in byfile.items():
        if not any(id in rep for a, id in lst):
            continue
        d = files_raw[f]
        offs = sorted(set(a for a, id in lst))
        bounds = offs + [len(d)]
        seg = {}
        for i, a in enumerate(offs):
            seg[a] = d[a:bounds[i + 1]]
        for a, id in lst:
            if id in rep:
                b = rep[id]
                while len(b) % 16: b += bytes(1)
                seg[a] = b
        nd = bytearray(d[:offs[0]]); omap = {}
        for a in offs:
            omap[a] = len(nd); nd += seg[a]
        out[f] = bytes(nd)
        for a, id in lst:
            newoff[id] = omap[a]
    return out, newoff


def main():
    rom = bytearray(open(nisi.ROM, 'rb').read())
    tr = load_tr()
    ovl = {}
    for f in glob.glob(WORK + 'tr_ovl/*.json'):
        k = int(os.path.basename(f)[:4])
        ovl[k] = {int(e['o'], 16): e['ko'] for e in json.load(open(f, encoding='utf-8')) if e.get('ko')}
    texts = [t for v in tr.values() for t in v.values()] + [t for v in ovl.values() for t in v.values()]
    extra = open(WORK + 'extra_chars.txt', encoding='utf-8').read() if os.path.exists(WORK + 'extra_chars.txt') else ''
    chars = charset(texts + [extra])
    print('korean glyphs', len(chars))
    E = Enc(chars)
    fontbin = build_font(rom, chars)
    banks = []
    for bk in (1, 2, 3):
        banks.append(len(fontbin))
        fontbin += build_font(rom, chars, True, bk)
    log = []
    t0, es = nisi.table(rom)
    files = nisi.files(rom)
    newdata = {}
    for k, a, b, c in files:
        if b <= a:
            continue
        if k in tr or k in ovl:
            raw = nisi.decomp(rom[a:b]) if c else rom[a:b]
            if k in tr:
                raw = rebuild_scen(k, raw, tr[k], E, log)
            if k in ovl:
                raw = patch_overlay_strings(k, raw, ovl[k], E, log)
            newdata[k] = compress(k, raw) if c else raw
    texfiles, texoff = build_textures(rom, {k: bytes(rom[a:b]) for k, a, b, c in files if b > a and not c})
    for k, d in texfiles.items():
        newdata[k] = d
        log.append('texture container %d: %d bytes' % (k, len(d)))
    # ROM 재구성
    first = es[0] & 0x7fffffff
    end_old = es[-1] & 0x7fffffff
    blob = bytearray()
    newent = []
    for k in range(len(es) - 1):
        a = es[k] & 0x7fffffff
        b = es[k + 1] & 0x7fffffff
        flag = es[k] & 0x80000000
        off = first + len(blob)
        newent.append(flag | off)
        if b > a:
            data = newdata.get(k, bytes(rom[a:b]))
            blob += data
            while len(blob) % 2:
                blob += b'\0'
    newent.append((es[-1] & 0x80000000) | (first + len(blob)))
    fend = first + len(blob)
    font_rom = (fend + 0xfff) & ~0xfff
    total = font_rom + len(fontbin)
    size = 0x1000000 if total <= 0x1000000 else 0x2000000
    out = bytearray(rom[:first]) + blob
    out += bytes(font_rom - len(out)) + fontbin
    out += b'\xff' * (size - len(out)) if False else bytes(size - len(out))
    for i, v in enumerate(newent):
        out[t0 + i * 4:t0 + i * 4 + 4] = v.to_bytes(4, 'big')
    # 코드 패치
    def ram2rom(a):
        return a - 0x80000450 + 0x1050
    def put(addr, w):
        o = ram2rom(addr)
        out[o:o + 4] = w.to_bytes(4, 'big')
    import cache
    cache.apply(out, put, font_rom, banks)
    # 일시정지 화면 닌자 기술 칸: 코드 0x110(術)을 14x8로 그림 → '기술'
    import fontgen as _fg
    gl = _fg.render_label('기술')
    o = cache.ram2rom(cache.FONTB + 0x88 * 128)
    for y in range(16):
        for x in range(16):
            bi = o + (15 - y) * 8 + x // 2
            sh = 4 if x % 2 == 0 else 0
            out[bi] = (out[bi] & ~(3 << sh)) | (int(gl[y][x]) << sh)
    # 코드 0xEC(両)를 코드에서 직접 그림 → '냥'
    gl = fontgen.render('냥', FONTFILE, 11)
    import numpy as _np
    cs = _np.nonzero(gl.any(0))[0]
    gl = _np.roll(gl, -int(cs[0]), 1)  # 왼쪽 붙임(가격 창 넘침 방지)
    o = cache.ram2rom(cache.FONTB + 0x76 * 128)
    for y in range(16):
        for x in range(16):
            bi = o + (15 - y) * 8 + x // 2
            sh = 4 if x % 2 == 0 else 0
            out[bi] = (out[bi] & ~(3 << sh)) | (int(gl[y][x]) << sh)
    for id, off in texoff.items():
        a = TEXTB + (id - 0x8000) * 4
        o = ram2rom(a)
        old = int.from_bytes(out[o:o + 4], 'big')
        out[o:o + 4] = ((old & 0xff000000) | off).to_bytes(4, 'big')
    # 원본 폰트 영역은 그대로 둠
    crc.fix(out)
    open(OUT, 'wb').write(out)
    json.dump({'chars': ''.join(chars), 'font_rom': font_rom, 'files_end': fend}, open(WORK + 'build_info.json', 'w', encoding='utf-8'), ensure_ascii=False)
    for l in log:
        print(l)
    print('rom size %x files end %x font %x-%x' % (size, fend, font_rom, total))


if __name__ == '__main__':
    main()
