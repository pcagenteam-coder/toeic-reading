#!/usr/bin/env python3
"""QC 阅读辅助：把 items_open_*.json 按 Part/题组打印成紧凑文本，便于逐题人工复核。
用法：python3 work/qc/dump.py kd|mx <part> [start] [count]   （start/count 按题组（P6/P7）或题（P5）计）
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = {'kd': 'data/items_open_kdeppaei.json', 'mx': 'data/items_open_maximcuynat.json'}


def short(ns, prim):
    return ','.join(n.replace('VO.SCENE.', 'SC.') for n in ns if n != prim and not n.startswith(('FD.', 'ST.', 'VO.PARA', 'TX.')))


def main():
    src, part = sys.argv[1], int(sys.argv[2])
    st = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    cnt = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 6
    d = json.load(open(os.path.join(ROOT, F[src]), encoding='utf-8'))
    its = [i for i in d['items'] if i['part'] == part]
    if part == 5:
        for i in its[st:st + cnt]:
            o = ' | '.join(('*' if k == i['answer'] else '') + x for k, x in enumerate(i['options']))
            print('%s d%s %s [%s] :: %s :: %s' % (i['id'], i.get('difficulty_est', '-'), i['node'], short(i['node_ids'], i['node']), i['stem'], o))
        return
    by = {}
    for i in its:
        by.setdefault(i['bundle_id'], []).append(i)
    bs = [b for b in d['bundles'] if b['part'] == part]
    for b in bs[st:st + cnt]:
        print('=== %s %s %s %s' % (b['bundle_id'], b['kind'], b['text_type'], ','.join(x.replace('VO.SCENE.', 'SC.') for x in b['node_ids'] if x.startswith('VO.'))))
        for k, doc in enumerate(b['docs'], 1):
            print('--[%d %s] %s' % (k, doc['doc_type'], doc.get('title', '')))
            if doc.get('header'):
                print(doc['header'])
            print(doc['text'])
        for i in sorted(by.get(b['bundle_id'], []), key=lambda x: x['qnum']):
            o = ' | '.join(('*' if k == i['answer'] else '') + x for k, x in enumerate(i['options']))
            q = i.get('q') or ('[%d]' % i.get('blank_n', 0))
            print('  > %s d%s %s [%s] Q: %s :: %s' % (i['id'], i.get('difficulty_est', '-'), i['node'], short(i['node_ids'], i['node']), q, o))
        print()


if __name__ == '__main__':
    main()
