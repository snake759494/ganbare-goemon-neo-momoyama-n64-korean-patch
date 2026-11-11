def crc(rom):
    # CIC 6102/7101 seed
    seed=0xF8CA4DDC
    t1=t2=t3=t4=t5=t6=seed
    M=0xffffffff
    d=rom
    for i in range(0x1000,0x101000,4):
        c1=int.from_bytes(d[i:i+4],'big')
        k1=(t6+c1)&M
        if k1<t6: t4=(t4+1)&M
        t6=k1
        t3^=c1
        r=c1&0x1f
        k2=((c1<<r)|(c1>>(32-r)))&M if r else c1
        t5=(t5+k2)&M
        if t2>c1: t2^=k2
        else: t2^=(t6^c1)
        t1=(t1+(t5^c1))&M
    return ((t6^t4^t3)&M,(t5^t2^t1)&M)
def fix(rom):
    a,b=crc(rom);rom[0x10:0x14]=a.to_bytes(4,'big');rom[0x14:0x18]=b.to_bytes(4,'big')
if __name__=='__main__':
    import sys;r=open(sys.argv[1],'rb').read();a,b=crc(r);print(hex(a),hex(b),r[0x10:0x18].hex())
