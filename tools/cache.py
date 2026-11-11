import asm
FONTB = 0x80062BC0
HELPER = FONTB + 0xb8 * 128
STAMPS = 0x80068B00
TAGS = 0x80068CC0
SLOTT = 0x80068DA0
CLOCK = 0x80068E90
FLAG = 0x80068E94
SLOTS = list(range(7, 0x57)) + list(range(0x77, 0x81)) + [t for t in range(0x82, 0x92) if t != 0x88]  # 0x76(S), 0x88(術)은 코드에서 직접 사용
NSLOT = len(SLOTS)
SRC = '''
helper:
  lui t9, %hi(FLAG)
  sw t7, %lo(FLAG)(t9)
  andi t9, t7, 0x1fff
  sra t9, t9, 1
  slti t6, t9, 0x100
  beqz t6, cached
  sll t6, t9, 7
  lui t9, 0x8006
  addiu t9, t9, 0x2bc0
  jr t8
  addu t6, t6, t9
cached:
  andi t6, t7, 0x8000
  beqz t6, bkd
  nop
  addiu t6, zero, 8
  beq v1, t6, bk2
  nop
  addiu t6, zero, 6
  beq v1, t6, bk3
  nop
  b bkd
  ori t9, t9, 0x2000
bk2:
  b bkd
  ori t9, t9, 0x4000
bk3:
  addiu v1, zero, 7
  ori t9, t9, 0x6000
bkd:
  addiu sp, sp, -0x30
  sw at, 0(sp)
  sw v0, 4(sp)
  sw v1, 8(sp)
  sw a0, 12(sp)
  sw a1, 16(sp)
  sw a2, 20(sp)
  sw a3, 24(sp)
  sw t0, 28(sp)
  sw t1, 32(sp)
  sw t2, 36(sp)
  lui a0, %hi(TAGS)
  addiu a0, a0, %lo(TAGS)
  move v0, zero
  addiu a1, zero, NSLOT
tl:
  lhu a2, 0(a0)
  beq a2, t9, hit
  nop
  addiu v0, v0, 1
  bne v0, a1, tl
  addiu a0, a0, 2
  lui a0, %hi(STAMPS)
  addiu a0, a0, %lo(STAMPS)
  lw a2, 0(a0)
  move v1, zero
  addiu v0, zero, 1
vl:
  sll t0, v0, 2
  addu t0, a0, t0
  lw t1, 0(t0)
  sltu t2, t1, a2
  beqz t2, vs
  nop
  move a2, t1
  move v1, v0
vs:
  addiu v0, v0, 1
  bne v0, a1, vl
  nop
  lui a0, %hi(TAGS)
  addiu a0, a0, %lo(TAGS)
  sll t0, v1, 1
  addu t0, a0, t0
  sh t9, 0(t0)
  lui a0, %hi(SLOTT)
  addiu a0, a0, %lo(SLOTT)
  sll t0, v1, 1
  addu t0, a0, t0
  lhu t0, 0(t0)
  sll t0, t0, 7
  lui a0, %hi(FONTU)
  addiu a0, a0, %lo(FONTU)
  addu a3, a0, t0
  andi t0, t9, 0x1fff
  sll t0, t0, 7
  lui a0, %hi(KOBASE)
  addiu a0, a0, %lo(KOBASE)
  addu a2, a0, t0
  srl t0, t9, 13
  sll t0, t0, 2
  lui a0, %hi(banktab)
  addu a0, a0, t0
  lw t0, %lo(banktab)(a0)
  addu a2, a2, t0
  mfc0 t1, 12
  addiu t2, zero, -2
  and t2, t1, t2
  mtc0 t2, 12
  nop
  nop
  lui a0, 0xa460
pw:
  lw t2, 0x10(a0)
  andi t2, t2, 3
  bnez t2, pw
  nop
  addiu v0, zero, 32
cp:
  lw t2, 0(a2)
  sw t2, 0(a3)
  addiu a2, a2, 4
  addiu v0, v0, -1
  bnez v0, cp
  addiu a3, a3, 4
  mtc0 t1, 12
  nop
  move v0, v1
hit:
  lui a0, %hi(CLOCK)
  addiu a0, a0, %lo(CLOCK)
  lw t0, 0(a0)
  addiu t0, t0, 1
  sw t0, 0(a0)
  lui a1, %hi(STAMPS)
  addiu a1, a1, %lo(STAMPS)
  sll t1, v0, 2
  addu t1, a1, t1
  sw t0, 0(t1)
  lui a1, %hi(SLOTT)
  addiu a1, a1, %lo(SLOTT)
  sll t1, v0, 1
  addu t1, a1, t1
  lhu t1, 0(t1)
  sll t1, t1, 7
  lui t6, 0x8006
  addiu t6, t6, 0x2bc0
  addu t6, t6, t1
  lw at, 0(sp)
  lw v0, 4(sp)
  lw v1, 8(sp)
  lw a0, 12(sp)
  lw a1, 16(sp)
  lw a2, 20(sp)
  lw a3, 24(sp)
  lw t0, 28(sp)
  lw t1, 32(sp)
  lw t2, 36(sp)
  jr t8
  addiu sp, sp, 0x30
stub1:
  mflo t9
  lui t7, %hi(FLAG)
  lw t7, %lo(FLAG)(t7)
  andi t7, t7, 0x1fff
  slti t7, t7, 0x200
  bnez t7, s1b
  nop
  bltz t9, s1n
  nop
  b s1b
  ori t9, zero, 0x400
s1n:
  ori t9, zero, 0xfc00
s1b:
  j 0x80010b70
  nop
stub2:
  mflo t9
  lui t6, %hi(FLAG)
  lw t6, %lo(FLAG)(t6)
  andi t6, t6, 0x1fff
  slti t6, t6, 0x200
  bnez t6, s2b
  nop
  bltz t9, s2n
  nop
  b s2b
  ori t9, zero, 0x400
s2n:
  ori t9, zero, 0xfc00
s2b:
  andi t8, t9, 0xffff
  addiu t6, zero, 0x4000
  j 0x80010b98
  nop
banktab:
  .word 0
  .word BANK1
  .word BANK2
  .word BANK3
'''
SITE_A = '''
  ori t7, a3, 0x8000
  lui t9, %hi(HELPER)
  addiu t9, t9, %lo(HELPER)
  jalr t8, t9
  sw t6, 0(t3)
  nop
'''
SITE_B = '''
  addu t7, t3, zero
  lui t9, %hi(HELPER)
  addiu t9, t9, %lo(HELPER)
  jalr t8, t9
  lui at, 0x3f80
  mtc1x
  addu a2, t6, zero
  nop
'''
def ram2rom(a):
    return a - 0x80000450 + 0x1050
def apply(out, put, font_rom, banks):
    C = dict(TAGS=TAGS, STAMPS=STAMPS, SLOTT=SLOTT, CLOCK=CLOCK, NSLOT=NSLOT, FONTU=FONTB - 0x80000000 + 0xA0000000,
             KOBASE=(0xB0000000 + font_rom - 0x100 * 128) & 0xffffffff, HELPER=HELPER, BANK1=banks[0], BANK2=banks[1], BANK3=banks[2], FLAG=FLAG)
    code, L = asm.assemble(SRC, HELPER, C)
    C['STUB1'] = L['stub1']; C['STUB2'] = L['stub2']
    assert HELPER + len(code) <= STAMPS, hex(len(code))
    o = ram2rom(HELPER); out[o:o + len(code)] = code
    # 데이터 초기화
    o = ram2rom(STAMPS); out[o:o + NSLOT * 4] = bytes(NSLOT * 4)
    o = ram2rom(TAGS); out[o:o + NSLOT * 2] = bytes(NSLOT * 2)
    o = ram2rom(SLOTT); out[o:o + NSLOT * 2] = b''.join(t.to_bytes(2, 'big') for t in SLOTS)
    o = ram2rom(CLOCK); out[o:o + 4] = bytes(4)
    assert SLOTT + NSLOT * 2 <= CLOCK
    a, _ = asm.assemble(SITE_A, 0x80010a2c, C)
    o = ram2rom(0x80010a2c); out[o:o + len(a)] = a
    src = SITE_B.replace('  mtc1x\n', '')
    b, _ = asm.assemble(src, 0x8000ce28, C)
    b = b[:20] + (0x44812000).to_bytes(4, 'big') + b[20:]  # mtc1 at, f4
    o = ram2rom(0x8000ce28); out[o:o + len(b)] = b
    for at, st in ((0x80010b68, 'STUB1'), (0x80010b90, 'STUB2')):
        w, _ = asm.assemble('  j %s' % st, at, C)
        o = ram2rom(at); out[o:o + 4] = w
    o = ram2rom(0x80010b94); out[o:o + 4] = bytes(4)
    return len(code)
