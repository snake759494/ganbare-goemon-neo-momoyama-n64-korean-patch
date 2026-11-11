import emu,sys
W='D:/n64/힘내라고에몽-네오모모야마막부의춤/work/'
# usage: go.py out.png  btn:frames:wait ...
cmds=[]
for a in sys.argv[2:]:
    if a.startswith('save=') : cmds.append('save '+W+a[5:]);continue
    if a.startswith('load=') : cmds.append('load '+W+a[5:]);continue
    if a.startswith('@'): q=a[1:].split(',');cmds+=['stick %s %s %s %s'%(q[0],q[1],q[2],'+'.join(q[3:]).replace('+',',') if len(q)>3 else ''),'wait 5'];continue
    if a.startswith('w'): cmds.append('wait '+a[1:]);continue
    b,n,w=(a.split(':')+['4','30'])[:3] if a.count(':')<2 else a.split(':')
    cmds+=emu.press(b,int(n),int(w))
cmds.append('shot '+W+sys.argv[1])
emu.run(cmds)
