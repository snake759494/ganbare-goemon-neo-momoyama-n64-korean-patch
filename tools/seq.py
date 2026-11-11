import emu,sys
from PIL import Image
W='D:/n64/힘내라고에몽-네오모모야마막부의춤/work/'
# seq.py prefix btn n wait [load=x]
p,b,n,w=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
c=[]
for a in sys.argv[5:]:
    if a.startswith('load='): c.append('load '+W+a[5:])
for i in range(n):
    c+=emu.press(b,4,w) if b!='-' else ['wait %d'%w]
    c.append('shot %s%s%02d.png'%(W,p,i))
emu.run(c)
ims=[Image.open('%s%s%02d.png'%(W,p,i)) for i in range(n)]
s=Image.new('RGB',(320*4,240*((n+3)//4)))
for i,m in enumerate(ims): s.paste(m,(i%4*320,i//4*240))
s.save(W+p+'.png')
