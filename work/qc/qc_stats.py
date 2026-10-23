#!/usr/bin/env python3
"""A2-QC 统计：对比 QC 前基线（work/qc/_baseline/，即 A2 节点规则修正后、全量复核前的产物）与当前 items_open_*.json，
按来源 × Part 统计全量复核发现的错误率。输出 work/qc/qc_stats.json 并打印摘要。

错误口径（一道题命中任一项即算 1 道错题）：
- answer：答案不唯一 / 选项有误（qc_fixes 中 cat=answer）
- text：题干或篇章文本错误（题干改写、篇章重复句等；文本类型 text_type 误判单列为 tx，不计入错题）
- node：主节点题型错误（P7 先把 题型×文本 叶节点折回题型分组再比较，避免把“改用叶节点”这一约定变化算成错误；
        跨篇状态改变算错误）或 P5/P6 的考点节点（GR./VO.LEX/VO.COLLO/QT.P6.*）集合改变
- 场景标签（VO.SCENE.*）、难度单列，不计入错题
用法：python3 work/qc/qc_stats.py   （需先跑完转换脚本 + apply_qc_fixes.py；基线文件不入库，缺失时退出）
"""
import json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, 'work', 'qc', '_baseline')
SRC = {'maximcuynat': 'items_open_maximcuynat.json', 'kdeppaei': 'items_open_kdeppaei.json'}
FIX = json.load(open(os.path.join(ROOT, 'data', 'items_open_qc_fixes.json'), encoding='utf-8'))['fixes']


def qtype(n):
    if n.startswith('QT.P7X.CROSS_REF') or n == 'QT.P7.CROSS_REF':
        return 'CROSS'
    m = re.match(r'QT\.P7X\.([A-Z_]+)\.', n)
    return 'QT.P7.' + m.group(1) if m else n


def core(i):
    return sorted(n for n in i['node_ids'] if n.startswith(('GR.', 'VO.LEX', 'VO.COLLO', 'QT.P6.')) and n != 'QT.P6.CLASSIFY')


def scenes(i):
    return sorted(n for n in i['node_ids'] if n.startswith('VO.SCENE.'))


def text_of(b):
    return [d.get('text', '') for d in b['docs']]


def main():
    if not os.path.isdir(BASE):
        sys.exit('baseline missing: ' + BASE)
    out = {}
    for name, fn in SRC.items():
        a = json.load(open(os.path.join(BASE, fn), encoding='utf-8'))
        b = json.load(open(os.path.join(ROOT, 'data', fn), encoding='utf-8'))
        ai = {i['id']: i for i in a['items']}
        ab = {x['bundle_id']: x for x in a['bundles']}
        bb = {x['bundle_id']: x for x in b['bundles']}
        text_bundles = {k for k in bb if text_of(bb[k]) != text_of(ab[k])}
        tx_bundles = {k for k in bb if [d['doc_type'] for d in bb[k]['docs']] != [d['doc_type'] for d in ab[k]['docs']] or bb[k]['text_type'] != ab[k]['text_type']}
        st = defaultdict(Counter)
        lists = defaultdict(list)
        for i in b['items']:
            o = ai[i['id']]
            p = 'P%d' % i['part']
            st[p]['items'] += 1
            cats = set()
            if i['options'] != o['options'] or i['answer'] != o['answer'] or FIX.get(i['id'], {}).get('cat') == 'answer':
                cats.add('answer')
            if (i.get('stem') != o.get('stem') or i.get('q') != o.get('q')) and 'answer' not in cats:
                cats.add('text')
            if i.get('bundle_id') in text_bundles:
                cats.add('text')
            if qtype(i['node']) != qtype(o['node']) or (i['part'] in (5, 6) and core(i) != core(o)):
                cats.add('node')
            if i['part'] == 7 and (qtype(i['node']) == 'CROSS') != (qtype(o['node']) == 'CROSS'):
                cats.add('cross')
            for c in cats:
                st[p][c] += 1
            if cats & {'answer', 'text', 'node', 'cross'}:
                st[p]['error_items'] += 1
                lists[p].append(i['id'])
            if scenes(i) != scenes(o):
                st[p]['scene_changed'] += 1
            if i.get('difficulty_est') != o.get('difficulty_est'):
                st[p]['difficulty_changed'] += 1
            if 'qc_fix' in i:
                st[p]['manual_fix'] += 1
        res = {}
        for p in sorted(st):
            c = st[p]
            res[p] = dict(c)
            res[p]['error_rate'] = round(c['error_items'] / c['items'], 4)
        tot = Counter()
        for c in st.values():
            tot.update(c)
        res['ALL'] = dict(tot)
        res['ALL']['error_rate'] = round(tot['error_items'] / tot['items'], 4)
        res['bundles_text_fixed'] = sorted(text_bundles)
        res['bundles_tx_fixed'] = sorted(tx_bundles)
        out[name] = res
        print(name)
        for p in sorted(st) + ['ALL']:
            r = res[p]
            print('  %-4s n=%-4d err=%-4d (%.1f%%) answer=%d text=%d node=%d cross=%d | manual=%d scene=%d diff=%d' % (
                p, r['items'], r.get('error_items', 0), 100 * r['error_rate'], r.get('answer', 0), r.get('text', 0), r.get('node', 0),
                r.get('cross', 0), r.get('manual_fix', 0), r.get('scene_changed', 0), r.get('difficulty_changed', 0)))
        print('  text bundles', len(text_bundles), 'tx bundles', len(tx_bundles))
    with open(os.path.join(ROOT, 'work', 'qc', 'qc_stats.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
