import emu,sys
from PIL import Image
W='D:/n64/힘내라고에몽-네오모모야마막부의춤/work/'
# walk.py out x,y,n x,y,n ...  (각 이동 후 스샷)
c=[];k=0
for a in sys.argv[2:]:
    if a.startswith('load='): c.append('load '+W+a[5:]);continue
    if a.startswith('save='): c.append('save '+W+a[5:]);continue
    q=a.split(',')
    if q[0].isalpha() or '_' in q[0]: c+=emu.press(q[0],4,int(q[1]) if len(q)>1 else 60)
    else: c+=['stick %s %s %s %s'%(q[0],q[1],q[2],q[3] if len(q)>3 else ''),'wait 10']
    c+=['wait 3','shot %s_w%02d.png'%(W,k),'wait 17','shot %s_v%02d.png'%(W,k)];k+=1
emu.run(c,900)
s=Image.new('RGB',(320*4,240*((k+3)//4)))
for i in range(k):
    m=Image.open('%s_w%02d.png'%(W,i))
    if max(m.convert('L').getextrema())<20: m=Image.open('%s_v%02d.png'%(W,i))
    s.paste(m,(i%4*320,i//4*240))
s.save(W+sys.argv[1])
