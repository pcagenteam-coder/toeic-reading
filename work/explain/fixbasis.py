"""python3 fixbasis.py <authored file> ID=新依据 ...   替换某题的依据字段（第 3 字段）"""
import sys
f=sys.argv[1]; fixes=dict(a.split('=',1) for a in sys.argv[2:])
out=[]
for line in open(f,encoding='utf-8'):
    p=line.rstrip('\n').split(' | ')
    if p and p[0] in fixes and len(p)>3:
        p[2]=fixes.pop(p[0]); line=' | '.join(p)+'\n'
    out.append(line)
open(f,'w',encoding='utf-8').write(''.join(out))
assert not fixes, fixes
