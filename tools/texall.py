import nisi,picdec,picshow,json,os,time
from multiprocessing import Pool
rom=open(nisi.ROM,'rb').read()
RANGES=[(0x8000,129),(0x8023,137),(0x8094,160),(0x8124,161),(0x8126,208),(0x815d,242),(0x81a4,260),(0x81c4,275),(0x823e,289),(0x824d,290),(0x8259,293),(0x8260,294),(0x826a,297),(0x8277,298),(0x8282,301),(0x828f,302),(0x829b,386),(0x82bb,387),(0x8327,388),(0x832c,389),(0x832e,390),(0x8365,391),(0x83b3,392),(0x83df,393),(0x8409,394),(0x8428,395),(0x842b,396),(0x84c4,397),(0x84ee,398),(0x8586,1191),(0x861b,1211),(0x8677,1228),(0x867c,1231),(0x86a8,1237),(0x86c2,1239),(0x8758,1288),(0x8769,0)]
TB=0x6a114
def entries():
    out=[]
    for i in range(len(RANGES)-1):
        s,f=RANGES[i]; e=RANGES[i+1][0]
        for id in range(s,e):
            a=int.from_bytes(rom[TB+(id-0x8000)*4:][:4],'big')&0xffffff
            b=int.from_bytes(rom[TB+(id-0x8000)*4+4:][:4],'big')&0xffffff
            if id==e-1 or b<=a: b=None
            out.append((id,f-1,a,b))
    return out
def work(x):
    id,f,a,b=x
    d=open('../work/files/%04d.bin'%f,'rb').read()
    seg=d[a:b] if b else d[a:]
    p='../work/tex/%04x.png'%id
    if seg[:3]!=b'PIC': return (id,f,a,'raw',len(seg))
    try:
        r=picdec.decode(seg); picshow.img(*r).save(p); return (id,f,a,r[:3])
    except Exception as e: return (id,f,a,'err '+str(e))
if __name__=='__main__':
    os.makedirs('../work/tex',exist_ok=True)
    E=entries(); t=time.time()
    with Pool(8) as p: res=p.map(work,E)
    json.dump(res,open('../work/tex/index.json','w'))
    print(len(res),time.time()-t, sum(1 for r in res if r[3]=='raw'), [r for r in res if str(r[3]).startswith('err')][:5])
