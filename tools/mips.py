R={n:i for i,n in enumerate('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split())}
def I(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def lui(rt,imm): return I(0x0f,'zero',rt,imm)
def ori(rt,rs,imm): return I(0x0d,rs,rt,imm)
def addiu(rt,rs,imm): return I(0x09,rs,rt,imm)
def andi(rt,rs,imm): return I(0x0c,rs,rt,imm)
def sw(rt,off,base): return I(0x2b,base,rt,off)
def lw(rt,off,base): return I(0x23,base,rt,off)
def bne(rs,rt,off): return I(0x05,rs,rt,off)
def jr(rs): return (R[rs]<<21)|8
NOP=0
def pack(ws): return b''.join(w.to_bytes(4,'big') for w in ws)
