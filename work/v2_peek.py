import json,sys
def sh(v,n=110):
    s=json.dumps(v,ensure_ascii=False); return s[:n]+('…' if len(s)>n else '')
def peek(path):
    d=json.load(open(path)); print('==',path,type(d).__name__)
    if isinstance(d,dict):
        for k,v in d.items():
            print(' ',k,type(v).__name__,len(v) if hasattr(v,'__len__') else '', sh(v if not isinstance(v,(list,dict)) else (v[0] if isinstance(v,list) and v else list(v)[:8] if isinstance(v,dict) else v)))
    return d
for p in sys.argv[1:]: peek(p)
