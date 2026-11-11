import subprocess,time,os,sys
E='D:/n64/힘내라고에몽-네오모모야마막부의춤/emu/'
ROM='D:/n64/힘내라고에몽-네오모모야마막부의춤/Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64'
n=[0]
def start(rom=ROM):
    for f in ['cmd.txt','ack.txt']:
        try: os.remove(E+f)
        except: pass
    si=subprocess.STARTUPINFO();si.dwFlags=1;si.wShowWindow=7  # SW_SHOWMINNOACTIVE
    return subprocess.Popen([E+'BizHawk/EmuHawk.exe','--lua='+E+'bridge.lua',rom],cwd=E+'BizHawk',startupinfo=si)
def run(cmds,timeout=600):
    n[0]+=1;tag=f'a{n[0]}{int(time.time()*1000)%100000}'
    while os.path.exists(E+'cmd.txt'): time.sleep(0.05)
    cmds=[c.replace('D:/n64/힘내라고에몽-네오모모야마막부의춤/','../') for c in cmds]
    open(E+'cmd.tmp','w').write('\n'.join(cmds+[f'ack {tag}'])+'\n');os.replace(E+'cmd.tmp',E+'cmd.txt')
    t=time.time()
    while time.time()-t<timeout:
        try:
            if open(E+'ack.txt').read()==tag: return True
        except: pass
        time.sleep(0.05)
    raise Exception('timeout')
def press(b,n=4,after=20): return [f'hold {b} {n}',f'wait {after}']
if __name__=='__main__':
    run(sys.argv[1:])
