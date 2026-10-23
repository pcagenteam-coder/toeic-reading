#!/usr/bin/env python3
"""QC 辅助：把一批逐题修正（stdin 的 JSON 对象 {item_id: {字段..., "reason": "..."}}）合并进 data/items_open_qc_fixes.json。
同一 id 再次写入时字段合并（后写覆盖），reason 用 "；" 拼接去重。
用法：python3 work/qc/addfix.py < batch.json
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'data', 'items_open_qc_fixes.json')


def main():
    cur = json.load(open(P, encoding='utf-8')) if os.path.exists(P) else {'meta': {}, 'fixes': {}}
    batch = json.loads(sys.stdin.read())
    for k, v in batch.items():
        old = cur['fixes'].get(k, {})
        rs = [r for r in (old.get('reason', '').split('；') + v.get('reason', '').split('；')) if r]
        old.update(v)
        old['reason'] = '；'.join(dict.fromkeys(rs))
        cur['fixes'][k] = old
    cur['fixes'] = dict(sorted(cur['fixes'].items()))
    with open(P, 'w', encoding='utf-8') as f:
        json.dump(cur, f, ensure_ascii=False, indent=1)
    print('fixes total', len(cur['fixes']), '+', len(batch))


if __name__ == '__main__':
    main()
