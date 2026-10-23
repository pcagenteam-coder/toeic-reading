"""打印下一批未完成的题（紧凑格式，供撰写解析）。
用法：python3 work/explain/dump.py --pool open --n 40 [--part 5] [--ids A,B] [--ref]
"""
import argparse, json, os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *


def has_zh(it):
    return bool((it.get('explain_zh') or '').strip())


def order_items(pool, items):
    if pool == 'private':
        # 先 train 中无中文解析，其次 train 有中文，再其他
        def k(it):
            return (0 if it.get('use') == 'train' else 1, 1 if has_zh(it) else 0)
        return sorted(items, key=k)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pool', default='open')
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--part', type=int)
    ap.add_argument('--ids')
    ap.add_argument('--ref', action='store_true', help='附原有解析作参考')
    ap.add_argument('--only-train', action='store_true')
    ap.add_argument('--show-ans', action='store_true', help='显示答案（默认隐藏，便于独立判断后由 merge 比对）')
    a = ap.parse_args()
    items, bundles = load_pool(a.pool)
    st = json.load(open(POOLS[a.pool]['state'])) if os.path.exists(POOLS[a.pool]['state']) else {}
    done = set(st.get('done', {})) | set(st.get('flagged', {}))
    ids = set(a.ids.split(',')) if a.ids else None
    todo = [it for it in order_items(a.pool, items) if it['id'] not in done
            and (ids is None or it['id'] in ids) and (a.part is None or it['part'] == a.part)
            and (not a.only_train or it.get('use') == 'train')]
    # 按 bundle 补齐
    out, seen_b, n = [], set(), 0
    for it in todo:
        if n >= a.n:
            break
        b = it.get('bundle_id')
        if b:
            if b in seen_b:
                continue
            seen_b.add(b)
            grp = [x for x in todo if x.get('bundle_id') == b]
            out.append((bundles.get(b), grp)); n += len(grp)
        else:
            out.append((None, [it])); n += 1
    print('# pending total %d, this batch %d' % (len(todo), n))
    for b, grp in out:
        if b:
            print('\n=== %s %s' % (b['bundle_id'], b.get('text_type', '')))
            for i, d in enumerate(b['docs']):
                if len(b['docs']) > 1:
                    print('--- doc%d %s' % (i + 1, d.get('doc_type', '')))
                if d.get('header'):
                    print(d['header'].replace('\n', ' / '))
                print(re.sub(r'\n\s*\n', '\n', d.get('text') or ''))
        for it in grp:
            stem = it.get('stem') or it.get('q') or ('[%s]' % it.get('blank_n'))
            print('\n%s%s %s :: %s' % (it['id'], (' ans=' + it['answer_letter']) if a.show_ans else '', it['node'].replace('QT.', ''), stem))
            print('  ' + '  '.join('%s) %s' % (LET[i], o) for i, o in enumerate(it['options'])))
            if a.ref:
                r = (it.get('explain_zh') or it.get('explain_en') or '').replace('\n', ' ')
                if r:
                    print('  ref: ' + r[:160])


if __name__ == '__main__':
    main()
