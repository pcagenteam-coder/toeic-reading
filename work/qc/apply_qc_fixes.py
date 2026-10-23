#!/usr/bin/env python3
"""A2-QC：把 data/items_open_qc_fixes.json 的逐题人工修正应用到转换脚本的产物上（原地改写 items_open_*.json）。

复跑顺序（每次重新生成公开题库都按这个顺序）：
    python3 work/convert_maximcuynat.py            # → data/items_open_maximcuynat.json
    python3 data/items_open_kdeppaei_convert.py    # → data/items_open_kdeppaei.json (+ _log.json)
    python3 work/qc/apply_qc_fixes.py              # 应用人工修正（幂等，可重复跑）
    python3 app/build.py --public                  # 构建读的就是修正后的 items_open_*.json

修正条目（fixes 的 key = item id 或 bundle id）：
- 题目字段：stem / q / options / answer / explain_zh / translation_zh / difficulty_est
  * 改 options 不给 answer 时，要求原正确项文本不变（防止错位）；给 answer 时同步 answer_letter
- 节点：node（主节点）/ node_ids（核心节点全集，脚本会自动保留原有的 TX.* / VO.SCENE.* / QT.P6.CLASSIFY）
  * 只给 node 时把 node_ids 里的旧主节点换成新主节点
- bundle 修正（"bundle": true）：text_type / doc_types（逐篇）；同步 bundle 与其题目的 TX 节点，
  单篇 P7 的 题型×文本 交叉叶节点按新文本类型重算（没有对应叶节点则退回题型分组节点）
- P7 跨篇状态改变且未显式给 difficulty_est 时，按 cm.p7_rule_diff 重算难度（kdeppaei 再与原难度档 2:1 加权）
- 每道被修正的题加 qc_fix 字段（修正原因），meta 记 qc_applied
"""
import json, os, re, sys, importlib.util
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXES = os.path.join(ROOT, 'data', 'items_open_qc_fixes.json')
FILES = [os.path.join(ROOT, 'data', 'items_open_maximcuynat.json'), os.path.join(ROOT, 'data', 'items_open_kdeppaei.json')]
spec = importlib.util.spec_from_file_location('cm', os.path.join(ROOT, 'work', 'convert_maximcuynat.py'))
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)
G = cm.G
_ids = [n['id'] for n in json.load(open(os.path.join(ROOT, 'data', 'graph_v1.json'), encoding='utf-8'))['nodes']]
LEAVES = {n for n in _ids if not any(m.startswith(n + '.') for m in _ids)}
ITEM_FIELDS = ('stem', 'q', 'options', 'answer', 'explain_zh', 'translation_zh', 'difficulty_est')
DIFF_SRC = {'400': 2, '600': 3, '800': 4}


def is_cross(n):
    return n.startswith('QT.P7X.CROSS_REF') or n == 'QT.P7.CROSS_REF'


def p7_qtype(item):
    for n in [item['node']] + item['node_ids']:
        m = re.match(r'QT\.P7\.([A-Z_]+)$', n)
        if m and m.group(1) not in ('CROSS_REF', 'CALC_LOOKUP'):
            return m.group(1)
        m = re.match(r'QT\.P7X\.([A-Z_]+)\.', n)
        if m and m.group(1) not in ('CROSS_REF', 'CALC_LOOKUP'):
            return m.group(1)
    return 'DETAIL'


def recompute_p7_diff(item, bundle):
    nwords = len(re.findall(r"[A-Za-z']+", ' '.join(d.get('text', '') for d in bundle['docs'])))
    r = cm.p7_rule_diff(bundle['kind'], nwords, p7_qtype(item), is_cross(item['node']))
    if item.get('source') == 'kdeppaei_mit':
        d = DIFF_SRC.get(str(item.get('difficulty_src')), 3)
        return max(1, min(5, int((2 * r + d) / 3 + 0.5)))
    return r


def remap_p7x(n, new_tx):
    m = re.match(r'QT\.P7X\.([A-Z_]+)\.[A-Z_]+$', n)
    if not m or m.group(1) in ('CROSS_REF',):
        return n
    return cm.p7x(m.group(1), new_tx) or ('QT.P7.' + m.group(1))


def main():
    fx = json.load(open(FIXES, encoding='utf-8'))['fixes']
    seen = set()
    for path in FILES:
        d = json.load(open(path, encoding='utf-8'))
        items = {i['id']: i for i in d['items']}
        bundles = {b['bundle_id']: b for b in d['bundles']}
        n_item = n_bundle = 0
        # ---- bundle 修正 ----
        for k, f in fx.items():
            if not f.get('bundle') or k not in bundles:
                continue
            seen.add(k); n_bundle += 1
            b = bundles[k]
            old_txs = {b['text_type']} | {x['doc_type'] for x in b['docs']}
            if f.get('doc_types'):
                assert len(f['doc_types']) == len(b['docs']), k
                for doc, t in zip(b['docs'], f['doc_types']):
                    doc['doc_type'] = t
            if f.get('text_type'):
                b['text_type'] = f['text_type']
            new_doc_txs = [x['doc_type'] for x in b['docs']]
            new_txs = ([b['text_type']] if b['kind'] != 'single' else []) + new_doc_txs
            b['node_ids'] = cm.uniq(new_txs + [n for n in b['node_ids'] if n not in old_txs])
            b['qc_fix'] = f.get('reason', '')
            for i in d['items']:
                if i.get('bundle_id') != k:
                    continue
                keep = [n for n in i['node_ids'] if n not in old_txs]
                if b['kind'] == 'single' and i['part'] == 7:
                    keep = [remap_p7x(n, new_doc_txs[0]) for n in keep]
                    qt = p7_qtype(i)
                    grp = 'QT.P7.' + qt
                    if i['node'] == grp or re.match(r'QT\.P7X\.%s\.' % qt, i['node']):   # 题型主节点：按新文本类型取叶节点，没有则用分组
                        i['node'] = cm.p7x(qt, new_doc_txs[0]) or grp
                    else:
                        i['node'] = remap_p7x(i['node'], new_doc_txs[0])
                    keep = [i['node']] + ([grp] if i['node'] != grp else []) + [n for n in keep if n not in (i['node'], grp)]
                aux = new_doc_txs[:1] if b['kind'] == 'single' else [b['text_type']] + sorted(set(new_doc_txs))
                if i['part'] == 6:
                    aux = [b['text_type']]
                sc = [n for n in keep if n.startswith('VO.SCENE.')]
                core = [n for n in keep if not n.startswith('VO.SCENE.')]
                i['node_ids'] = cm.uniq([i['node']] + core + aux + sc)
        # ---- 题目修正 ----
        for k, f in fx.items():
            if f.get('bundle') or k not in items:
                continue
            seen.add(k); n_item += 1
            i = items[k]
            old_ans_text = i['options'][i['answer']]
            was_cross = is_cross(i['node'])
            for fld in ITEM_FIELDS:
                if fld in f:
                    i[fld] = f[fld]
            if 'options' in f and 'answer' not in f:
                assert i['options'][i['answer']] == old_ans_text, (k, '改选项后正确项文本变了，需同时给 answer')
            assert len(i['options']) == 4 and len({o.lower() for o in i['options']}) == 4, k
            i['answer_letter'] = 'ABCD'[i['answer']]
            if 'stem' in f:
                assert i['stem'].count('-------') == 1, (k, 'P5 题干空位必须恰好 1 个')
            if 'node_ids' in f:
                prim = f.get('node', f['node_ids'][0])
                aux = [n for n in i['node_ids'] if n.startswith(('TX.', 'VO.SCENE.')) or n == 'QT.P6.CLASSIFY']
                core = [n for n in f['node_ids'] if n != prim]
                if i['part'] == 6 and 'QT.P6.CLASSIFY' not in core:
                    core = ['QT.P6.CLASSIFY'] + core
                i['node'] = prim
                i['node_ids'] = cm.uniq([prim] + core + [n for n in aux if n not in core])
            elif 'node' in f:
                old = i['node']
                i['node'] = f['node']
                i['node_ids'] = cm.uniq([f['node']] + [n for n in i['node_ids'] if n != old])
            if i['part'] == 7 and 'difficulty_est' not in f and is_cross(i['node']) != was_cross:
                i['difficulty_est'] = recompute_p7_diff(i, bundles[i['bundle_id']])
            i['qc_fix'] = f.get('reason', '')
        # ---- 校验 ----
        bad = [(i['id'], n) for i in d['items'] for n in i['node_ids'] if n not in G] + \
              [(b['bundle_id'], n) for b in d['bundles'] for n in b['node_ids'] if n not in G]
        assert not bad, ('UNKNOWN NODES', bad[:10])
        nonleaf = [(k, n) for k, f in fx.items() if k in items for n in f.get('node_ids', []) + ([f['node']] if 'node' in f else []) if n not in LEAVES]
        assert not nonleaf, ('修正里用了非叶节点', nonleaf[:10])
        badp = [i['id'] for i in d['items'] if i['node'] not in LEAVES]
        assert not badp, ('主节点不是叶节点', badp[:10])
        for i in d['items']:
            assert i['node'] == i['node_ids'][0], i['id']
            if i['part'] == 7 and is_cross(i['node']):
                assert bundles[i['bundle_id']]['kind'] != 'single', (i['id'], '单篇不可能跨篇')
        d['meta']['qc_applied'] = {'fixes_file': 'data/items_open_qc_fixes.json', 'items_fixed': n_item, 'bundles_fixed': n_bundle,
                                   'by': 'work/qc/apply_qc_fixes.py'}
        with open(path, 'w', encoding='utf-8') as fo:
            json.dump(d, fo, ensure_ascii=False, indent=1)
        print(os.path.basename(path), 'items fixed', n_item, 'bundles fixed', n_bundle,
              'primary P7 cross', sum(1 for i in d['items'] if is_cross(i['node'])))
    miss = sorted(set(fx) - seen)
    if miss:
        sys.exit('fix ids not found: %s' % miss)


if __name__ == '__main__':
    main()
