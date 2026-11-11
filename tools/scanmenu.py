import table,glob,os,re
ROM='D:/n64/힘내라고에몽-네오모모야마막부의춤/Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64'
def kana(x): return 0x0e<=x<=0xaf or 0xe5<=x<=0x18b
def scan(d,minlen=3):
    out=[];i=0;n=len(d)//2
    w=[int.from_bytes(d[j*2:j*2+2],'big') for j in range(n)]
    j=0
    while j<n:
        if kana(w[j]):
            k=j
            while k<n and (w[k] in table.T or w[k] in (1,2,3)) and w[k]!=0: k+=1
            seg=w[j:k]
            if len(seg)>=minlen and sum(kana(x) for x in seg)>=len(seg)*0.6 and k<n and w[k]==0:
                # back up to start
                s=j
                while s>0 and w[s-1]!=0 and (w[s-1] in table.T): s-=1
                out.append((s*2,k*2,w[s:k]))
            j=k+1
        else: j+=1
    return out
if __name__=='__main__':
    import sys
    tot=0
    srcs=[('main',open(ROM,'rb').read()[0x55750:0x84410])]
    for f in sorted(glob.glob('D:/n64/힘내라고에몽-네오모모야마막부의춤/work/files/*.bin')):
        k=int(os.path.basename(f)[:4])
        if 80<=k<=121: continue
        srcs.append((k,open(f,'rb').read()))
    for name,d in srcs:
        r=scan(d)
        if len(r)>=3:
            c=sum(len(x[2]) for x in r);tot+=c
            print(name,len(r),c,' | '.join(''.join(table.T.get(v,'_') for v in x[2]) for x in r[:6]))
    print(tot)
