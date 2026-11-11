import emu,sys
from PIL import Image
W='D:/n64/힘내라고에몽-네오모모야마막부의춤/work/'
# 사용: play.py 단계... 단계= 버튼:누름프레임:대기 | wN | save=이름 | load=이름 ; 각 단계 후 캡처하여 grid.png
steps=sys.argv[1:];cmds=[];shots=[]
for i,a in enumerate(steps):
    if a.startswith('save='): cmds.append('save '+W+a[5:]+'.State');continue
    if a.startswith('load='): cmds.append('load '+W+a[5:]+'.State');continue
    if a.startswith('w'): cmds.append('wait '+a[1:])
    else:
        p=(a.split(':')+['4','40'])[:3] if a.count(':')<2 else a.split(':')
        cmds+=emu.press(p[0],int(p[1]),int(p[2]))
    f=W+'p%02d.png'%i;cmds.append('shot '+f);shots.append(f)
emu.run(cmds)
if shots:
    ims=[Image.open(f) for f in shots];n=len(ims);c=min(n,4);r=(n+c-1)//c
    g=Image.new('RGB',(c*320,r*240))
    for i,im in enumerate(ims): g.paste(im.resize((320,240)),((i%c)*320,(i//c)*240))
    g.save(W+'grid.png')
    import os
    for f in shots: os.remove(f)
