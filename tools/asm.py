"""아주 작은 MIPS 어셈블러 (라벨 지원)"""
import re
REG = {n: i for i, n in enumerate('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split())}


def r(x):
    return REG[x.strip().lstrip('$')]


def imm(x, labels=None):
    x = x.strip()
    m = re.fullmatch(r'%hi\((\w+)\)', x)
    if m:
        v = labels[m.group(1)]
        return ((v + 0x8000) >> 16) & 0xffff
    m = re.fullmatch(r'%lo\((\w+)\)', x)
    if m:
        return labels[m.group(1)] & 0xffff
    if labels and x in labels:
        return labels[x]
    return int(x, 0)


def assemble(src, base, consts=None):
    lines = []
    for l in src.splitlines():
        l = l.split(';')[0].strip()
        if not l:
            continue
        lines.append(l)
    labels = dict(consts or {})
    pc = base
    for l in lines:
        if l.endswith(':'):
            labels[l[:-1]] = pc
        else:
            pc += 4
    out = []
    pc = base
    for l in lines:
        if l.endswith(':'):
            continue
        op, _, rest = l.partition(' ')
        a = [x.strip() for x in rest.split(',')] if rest else []
        def I(o, rs, rt, v):
            return (o << 26) | (rs << 21) | (rt << 16) | (v & 0xffff)
        def R(fn, rs=0, rt=0, rd=0, sh=0):
            return (rs << 21) | (rt << 16) | (rd << 11) | (sh << 6) | fn
        def br(lbl):
            return ((labels[lbl] - (pc + 4)) >> 2) & 0xffff
        def mem(s):
            m = re.fullmatch(r'(.*)\((\$?\w+)\)', s)
            return imm(m.group(1) or '0', labels), r(m.group(2))
        if op == 'nop': w = 0
        elif op == 'lui': w = I(0x0f, 0, r(a[0]), imm(a[1], labels))
        elif op == 'addiu': w = I(0x09, r(a[1]), r(a[0]), imm(a[2], labels))
        elif op == 'ori': w = I(0x0d, r(a[1]), r(a[0]), imm(a[2], labels))
        elif op == 'andi': w = I(0x0c, r(a[1]), r(a[0]), imm(a[2], labels))
        elif op == 'slti': w = I(0x0a, r(a[1]), r(a[0]), imm(a[2], labels))
        elif op == 'sltiu': w = I(0x0b, r(a[1]), r(a[0]), imm(a[2], labels))
        elif op in ('lw', 'sw', 'lhu', 'sh', 'lh'):
            o, b = mem(a[1])
            w = I({'lw': 0x23, 'sw': 0x2b, 'lhu': 0x25, 'sh': 0x29, 'lh': 0x21}[op], b, r(a[0]), o)
        elif op == 'beq': w = I(0x04, r(a[0]), r(a[1]), br(a[2]))
        elif op == 'bne': w = I(0x05, r(a[0]), r(a[1]), br(a[2]))
        elif op == 'beqz': w = I(0x04, r(a[0]), 0, br(a[1]))
        elif op == 'bnez': w = I(0x05, r(a[0]), 0, br(a[1]))
        elif op == 'b': w = I(0x04, 0, 0, br(a[0]))
        elif op == 'bltz': w = I(0x01, r(a[0]), 0, br(a[1]))
        elif op == 'addu': w = R(0x21, r(a[1]), r(a[2]), r(a[0]))
        elif op == 'subu': w = R(0x23, r(a[1]), r(a[2]), r(a[0]))
        elif op == 'and': w = R(0x24, r(a[1]), r(a[2]), r(a[0]))
        elif op == 'or': w = R(0x25, r(a[1]), r(a[2]), r(a[0]))
        elif op == 'sltu': w = R(0x2b, r(a[1]), r(a[2]), r(a[0]))
        elif op == 'move': w = R(0x21, r(a[1]), 0, r(a[0]))
        elif op == 'sll': w = R(0x00, 0, r(a[1]), r(a[0]), imm(a[2]))
        elif op == 'srlx': w = R(0x02, 0, r(a[1]), r(a[0]), imm(a[2]))
        elif op == 'srl': w = R(0x02, 0, r(a[1]), r(a[0]), imm(a[2]))
        elif op == 'sra': w = R(0x03, 0, r(a[1]), r(a[0]), imm(a[2]))
        elif op == 'j': w = (0x02 << 26) | ((imm(a[0], labels) >> 2) & 0x3ffffff)
        elif op == 'mflo': w = R(0x12, 0, 0, r(a[0]))
        elif op == 'jr': w = R(0x08, r(a[0]))
        elif op == 'jalr': w = R(0x09, r(a[1]), 0, r(a[0]))
        elif op == 'mfc0': w = (0x10 << 26) | (0 << 21) | (r(a[0]) << 16) | (int(a[1]) << 11)
        elif op == 'mtc0': w = (0x10 << 26) | (4 << 21) | (r(a[0]) << 16) | (int(a[1]) << 11)
        elif op == '.word': w = imm(a[0], labels) & 0xffffffff
        else:
            raise ValueError(l)
        out.append(w)
        pc += 4
    return b''.join(w.to_bytes(4, 'big') for w in out), labels
