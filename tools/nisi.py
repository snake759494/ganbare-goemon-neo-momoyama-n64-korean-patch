import sys
ROM='D:/n64/힘내라고에몽-네오모모야마막부의춤/Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64'
def table(d):
    t=d.find(b'Nisitenma-Ichigo')+16
    es=[];i=t
    while True:
        v=int.from_bytes(d[i:i+4],'big')
        if v==0: break
        es.append(v);i+=4
    return t,es
def decomp(b):
    end=int.from_bytes(b[1:4],'big')
    p=4;o=bytearray()
    while p<end:
        c=b[p];p+=1
        if c<0x80:
            n=(c>>2)+2;off=(b[p]+(c<<8))&0x3ff;p+=1
            for _ in range(n): o.append(o[-off])
        elif c<0xC0:
            n=c&0x1f;o+=b[p:p+n];p+=n
        else:
            if c<0xE0: n=(c&0x1f)+2;v=b[p];p+=1
            elif c<0xFF: n=(c&0x1f)+2;v=0
            else: n=b[p]+2;v=0;p+=1
            o+=bytes([v])*n
    return bytes(o)
def files(d):
    t,es=table(d);r=[]
    for k in range(len(es)-1):
        a=es[k]&0x7fffffff;b=es[k+1]&0x7fffffff
        r.append((k,a,b,es[k]>>31))
    return r
if __name__=='__main__':
    import os
    d=open(ROM,'rb').read();os.makedirs(sys.argv[1],exist_ok=True)
    for k,a,b,c in files(d):
        if b<=a: continue
        x=decomp(d[a:b]) if c else d[a:b]
        open(f'{sys.argv[1]}/{k:04d}.bin','wb').write(x)
