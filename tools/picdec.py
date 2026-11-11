import nisi
from unicorn import *
from unicorn.mips_const import *
ROMD=open(nisi.ROM,'rb').read()
RAM=open('D:/n64/힘내라고에몽-네오모모야마막부의춤/work/ram.bin','rb').read()
def mk():
    mu=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32+UC_MODE_BIG_ENDIAN)
    mu.mem_map(0,0x800000)
    mu.mem_write(0,RAM)
    return mu
def decode(data):
    mu=mk()
    SRC=0x80500000;DST=0x80600000;CTX=0x80700000;STOP=0x80001000
    mu.mem_write(STOP&0x1fffffff,b'\0'*8)
    mu.mem_write(SRC&0x1fffffff,data)
    mu.reg_write(UC_MIPS_REG_SP,0x807f0000)
    def call(f,*a):
        for r,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2),a): mu.reg_write(r,v)
        mu.reg_write(UC_MIPS_REG_RA,STOP)
        mu.emu_start(f,STOP,count=200000000)
    call(0x80014900,SRC,CTX)
    call(0x80014968,SRC,DST,CTX)
    c=mu.mem_read(CTX&0x1fffffff,0x40)
    w,h,bpp=[int.from_bytes(c[i:i+4],'big') for i in (0,4,8)]
    size=int.from_bytes(c[0xc:0x10],'big')
    return w,h,bpp,size,bytes(mu.mem_read(DST&0x1fffffff,max(size,w*h*2)))
