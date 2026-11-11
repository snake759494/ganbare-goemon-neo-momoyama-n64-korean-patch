"""PIC(X68000) 인코더: 16bpp, 체인/캐시 미사용. 게임 디코더 출력(RGBA5551)과 동일하게 복원됨"""
def _V(a1): return ((a1&0xffc0)>>5)|((a1&0x3e)<<10)|(a1&1)
def _S(c): return (((c&0x3e)>>1)<<11)|(((c&0x7c0)>>6)<<6)|(((c&0xf800)>>11)<<1)|(c&1)
INV={}
for _a in range(65536): INV.setdefault(_S(_V(_a)),_a)
class BW:
    def __init__(s): s.b=bytearray(); s.acc=0; s.n=0
    def put(s,v,n):
        for i in range(n-1,-1,-1):
            s.acc=(s.acc<<1)|((v>>i)&1); s.n+=1
            if s.n==8: s.b.append(s.acc); s.acc=0; s.n=0
    def bytes(s):
        b=bytearray(s.b)
        if s.n: b.append(s.acc<<(8-s.n))
        return bytes(b)+b'\0'*8
def putlen(w,L):
    a=1
    while not ((1<<a)-1<=L<(1<<(a+1))-1): a+=1
    for _ in range(a-1): w.put(1,1)
    w.put(0,1); w.put(L-(1<<a)+1,a)
def encode(px,wd,ht):
    """px: RGBA5551 정수 리스트 (wd*ht)"""
    w=BW()
    hdr=b'PIC0000\x1a\x00\x00'
    w.b+=hdr
    w.put(0,4); w.put(0,4); w.put(16,16); w.put(wd,16); w.put(ht,16)
    last=-1; cur=None
    class C: pass
    cache=C(); cache.col=[None]*128; cache.prev=[(i-1)%128 for i in range(128)]; cache.nxt=[(i+1)%128 for i in range(128)]; cache.head=0
    slot={}
    for i,t in enumerate(px):
        if t!=cur:
            if i==0 and t==0:
                cur=0; continue   # 초기색 0과 같으면 생략 불가 -> 처리 아래
            putlen(w,i-last); last=i; cur=t
            a1=INV[t]; c=_V(a1)
            if c in slot:
                i=slot[c]
                w.put(1,1); w.put(i,7)
                if i!=cache.head:
                    p,n=cache.prev[i],cache.nxt[i]
                    cache.prev[n]=p; cache.nxt[p]=n
                    h=cache.head; hn=cache.nxt[h]
                    cache.prev[hn]=i; cache.nxt[i]=hn; cache.nxt[h]=i; cache.prev[i]=h; cache.head=i
            else:
                w.put(0,1); w.put(a1,16)
                h=cache.nxt[cache.head]; cache.head=h
                old=cache.col[h]
                if slot.get(old)==h: del slot[old]
                cache.col[h]=c; slot[c]=h
            w.put(0,1)
    putlen(w,len(px)-last)
    return w.bytes()
