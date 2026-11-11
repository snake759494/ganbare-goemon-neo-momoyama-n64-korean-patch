import sys,glob,os
ram=open(sys.argv[1],'rb').read()
fs={int(os.path.basename(f)[:4]):open(f,'rb').read() for f in glob.glob('D:/n64/힘내라고에몽-네오모모야마막부의춤/work/files/*.bin')}
rom=open('D:/n64/힘내라고에몽-네오모모야마막부의춤/Ganbare Goemon - Neo Momoyama Bakufu no Odori (Japan).z64','rb').read()
for a in sys.argv[2:]:
    a=int(a,16);key=ram[a:a+64]
    hit=[(k,hex(d.find(key))) for k,d in fs.items() if key in d]
    print(hex(a),hit,'rom',hex(rom.find(key)))
