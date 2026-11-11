"""번역 검사: python check.py 0095 0092 ...  (인자 없으면 tr 전체)"""
import json, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
import build
W = 'D:/n64/힘내라고에몽-네오모모야마막부의춤/work/'
def cells(s):
    s = re.sub(r'\{[^}]*\}', '', s)
    return sum(3 if c == '…' else 1 for c in s)
def tags(s):
    return re.findall(r'\{[^}]*\}', s)
def check(k):
    p = W + 'tr/%s.json' % k
    tr = json.load(open(p, encoding='utf-8'))
    ja = json.load(open(W + 'ja/%s.json' % k, encoding='utf-8'))
    errs = []
    if [e['o'] for e in tr] != [e['o'] for e in ja]:
        return ['항목 목록(o)이 원본과 다름']
    E = build.Enc([chr(c) for c in range(0xAC00, 0xD7A4)])
    for e in tr:
        ko = e.get('ko')
        if ko is None:
            errs.append('%d: ko 없음' % e['o']); continue
        if tags(ko) != tags(e['ja']):
            errs.append('%d: 태그 불일치 %s / %s' % (e['o'], e['ja'], ko))
        n, m = cells(ko), cells(e['ja'])
        if n > 20 or n > m + 2 and n > 6:
            errs.append('%d: 너무 김 %d칸(원문 %d) %s' % (e['o'], n, m, ko))
        if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', re.sub(r'\{[^}]*\}', '', ko)):
            errs.append('%d: 일본어 문자 남음 %s' % (e['o'], ko))
        try:
            E.enc(ko)
        except Exception as ex:
            errs.append('%d: 인코딩 불가 %s' % (e['o'], ex))
    return errs
if __name__ == '__main__':
    ks = sys.argv[1:] or sorted(os.path.basename(f)[:4] for f in glob.glob(W + 'tr/0*.json'))
    bad = 0
    for k in ks:
        er = check(k)
        bad += len(er)
        for x in er:
            print(k, x)
        print(k, 'OK' if not er else '%d개 문제' % len(er))
