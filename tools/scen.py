import struct,table
F='D:/n64/힘내라고에몽-네오모모야마막부의춤/work/files/%04d.bin'
SCEN=list(range(80,122))
def strings(d):
    """return dict offset->(end, codes) for TXT targets"""
    seg=None;res={};refs=[]
    for i in range(4,len(d)-3,4):
        v=int.from_bytes(d[i:i+4],'big')
        if d[i-4:i]==b'\0\0\x80\x10' and (v>>24) in (8,9) and (v&0xffffff)<len(d):
            o=v&0xffffff;refs.append((i,o))
            if o not in res:
                w=[];p=o
                while p+2<=len(d):
                    x=int.from_bytes(d[p:p+2],'big');w.append(x);p+=2
                    if x==0xffff: break
                res[o]=(p,w)
    return res,refs
CTRL={0xffba:'{BEGIN}',0xffb9:'{END}',0xffc1:'{WIN}',0xffc2:'{WAIT}',0xffc3:'{BTN}',0xffc4:'{NL}',0xffc7:'{/BIG}',0xffc8:'{BIG}',0xffcd:'{/BLINK}',0xffce:'{BLINK}',0xffdb:'{DB}',0xffdc:'{G}',0xffdd:'{B}',0xffde:'{R}',0xffdf:'{Y}',0xffe0:'{/C}'}
def dec(w):
    s=''
    for x in w:
        if x==0xffff: break
        if x in table.T: s+=table.T[x]
        elif x in CTRL: s+=CTRL[x]
        else: s+='{%04X}'%x
    return s
if __name__=='__main__':
    tot=0;n=0;import collections;cc=collections.Counter()
    for k in SCEN:
        d=open(F%k,'rb').read();res,refs=strings(d)
        for o,(e,w) in sorted(res.items()):
            s=dec(w);n+=1;tot+=len(s)
            import re
            for m in re.findall(r'\{[0-9A-F]{4}\}',s): cc[m]+=1
    print(n,tot,cc.most_common(20))
