import table,json,sys
F='D:/n64/힘내라고에몽-네오모모야마막부의춤/work/files/%04d.bin'
def dec(w):
    return ''.join('{%04X}'%x if x in (1,2,3) else table.T.get(x,'{%04X}'%x) for x in w)
def scan(k):
    d=open(F%k,'rb').read();n=len(d)//2;w=[int.from_bytes(d[j*2:j*2+2],'big') for j in range(n)]
    res=[];j=1
    def good(s):
        kk=sum(1 for x in s if 0x0e<=x<=0xaf or 0xe5<=x<=0x18b)
        return len(s)>=2 and kk>=len([x for x in s if x>3])*0.6 and kk>=2
    while j<n:
        if w[j-1]==0 and w[j]!=0:
            e=j
            while e<n and w[e]!=0 and (w[e] in table.T or w[e] in (1,2,3)): e+=1
            if e<n and w[e]==0 and good(w[j:e]): res.append({'o':'%x'%(j*2),'ja':dec(w[j:e])})
            j=e+1
        else: j+=1
    return res
if __name__=='__main__':
    for k in map(int,sys.argv[1:]):
        r=scan(k);json.dump(r,open('D:/n64/힘내라고에몽-네오모모야마막부의춤/work/ja/ovl_%04d.json'%k,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
        for e in r: print(k,e['o'],e['ja'])
