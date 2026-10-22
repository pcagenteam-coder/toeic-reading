# -*- coding: utf-8 -*-
import json, collections, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
d = json.load(open(os.path.join(ROOT, 'data/strategies/strategy_library_v1.json')))
g = {n['id']: n for n in json.load(open(os.path.join(ROOT, 'data/graph_v1.json')))['nodes']}
L = d['entries']; v = d['validation']
o = []
w = o.append
w('# 统一技巧库 v1（strategy_library_v1）\n')
w('更新：2026-10-21。只按现行新制。数据：`data/strategies/strategy_library_v1.json`；构建脚本 `work/strategies/build_strategy_library.py`（重跑即重建并校验），本文件由 `work/strategies/build_strategy_library_md.py` 生成。\n')
w('输入五路：书籍 54 条（books.json）、新东方/B 站 49 条（xdf_bilibili.json）、中文论坛/英文·ETS/日韩三路汇总（strategy_findings_summary.md）；考频取自 graph_v1 节点 exam_weight（其来源为 exam_pattern_stats.json）。\n')
w(f'## 1. 总数\n\n- 主库条目：**{len(L)}** 条（全部 format_version 为 current/universal）\n- 旧制弃用（单列，不进主库）：{len(d["deprecated"])} 条\n- 违规/不可靠排除：{len(d["excluded"])} 条\n- 原始 103 条（54+49）全部被合并、弃用或排除，无遗漏（脚本校验）。\n')
def part_key(e):
    p = e['parts']
    return 'P5' if p == [5] else 'P6' if p == [6] else 'P7' if p == [7] else '全卷/跨 Part'
pc = collections.Counter(part_key(e) for e in L)
prefix = collections.Counter(e['id'].split('-')[1] for e in L)
cc = collections.Counter(e['consensus'] for e in L)
fc = collections.Counter(e['format_version'] for e in L)
bc = collections.Counter(b for e in L for b in e['target_band'])
w('## 2. 分布\n')
w('按条目分组（ID 前缀）：' + '，'.join(f'{k} {v}' for k, v in sorted(prefix.items())) + '\n')
w('按适用 Part（parts 字段精确为单一 Part / 跨 Part）：' + '，'.join(f'{k} {v}' for k, v in pc.items()) + '\n')
w('按共识度：' + '，'.join(f'{k} {cc[k]}' for k in ['高', '中', '个人经验']) + '\n')
w('按格式：' + '，'.join(f'{k} {v}' for k, v in fc.items()) + '\n')
w('按目标分段（可多选）：' + '，'.join(f'{k} {bc[k]}' for k in ['<600', '600-800', '800+']) + '\n')
cross = collections.Counter((e['id'].split('-')[1], e['consensus']) for e in L)
w('\n| 组 | 高 | 中 | 个人经验 | 合计 |\n|---|---|---|---|---|')
for k in ['P5', 'P6', 'P7', 'ALL']:
    w(f'| {k} | {cross[(k,"高")]} | {cross[(k,"中")]} | {cross[(k,"个人经验")]} | {prefix[k]} |')
w('\n## 3. Top 15 高价值规则（按 weight）\n')
w('权重 = 0.5×考频（绑定 qtype/strategy 叶子节点 exam_weight 最大值 ÷0.6 封顶 1）+ 0.3×共识（高 1 / 中 0.6 / 个人 0.3）+ 0.2×提及数（÷15 封顶 1）。\n')
w('| # | id | 规则 | 工作规则 | Part | 分段 | 共识 | 提及 | weight |\n|---|---|---|---|---|---|---|---|---|')
top = sorted(L, key=lambda e: (-e['weight'], -e['mention_count']))[:15]
for i, e in enumerate(top, 1):
    w(f'| {i} | {e["id"]} | {e["title_zh"]} | {e["work_rule"]} | {"/".join(map(str,e["parts"]))} | {" ".join(e["target_band"])} | {e["consensus"]} | {e["mention_count"]} | {e["weight"]} |')
w('\n## 4. 与图谱 strategy 节点的映射\n')
w('| strategy 节点 | 名称 | 绑定技巧 |\n|---|---|---|')
for nid, n in g.items():
    if n['layer'] == 'strategy' and not n.get('is_group'):
        es = [e['id'] for e in L if nid in e['strategy_nodes']]
        w(f'| {nid} | {n["name_zh"]} | {", ".join(es) or "**无**"} |')
w(f'\n- 没有技巧的 strategy 叶子节点：{f"无（{sum(1 for n in g.values() if n['layer']=='strategy' and not n.get('is_group'))} 个叶子全部至少 1 条）" if not v["strategy_nodes_without_technique"] else ", ".join(v["strategy_nodes_without_technique"])}。只有 1 条支撑、偏薄的：' +
  ', '.join(nid for nid, n in g.items() if n['layer']=='strategy' and not n.get('is_group') and sum(nid in e['strategy_nodes'] for e in L)==1) + '。')
w(f'- 没有技巧的 qtype 叶子：{", ".join(v["qtype_leaves_without_technique"]) or "无"}；没有技巧的 texttype：{", ".join(v["texttype_without_technique"]) or "无"}（来源里没有专门技巧，未硬编）。')
w('- 没有 strategy 节点、只绑定了 qtype/skill 的技巧：P5/P6 语法与词汇解法（SL-P5-02~20、SL-P6-03~08）——它们本就是 qtype/grammar 节点的解题法，不需要新 strategy 节点。')
sug = collections.defaultdict(list)
for e in L:
    if e['suggested_new_node']: sug[e['suggested_new_node']].append(e['id'])
w('\n**建议新增的 strategy 节点（未改 graph_v1，留待 v1.1）：**\n')
w('| 建议节点 | 来自技巧 |\n|---|---|')
for k, ids in sug.items(): w(f'| {k} | {", ".join(ids)} |')
w('\n## 5. 冲突点与取舍\n')
for row in [
 ('P7 先题后文 vs 先文后题（论坛分歧；濵﨑“设问→本文→选项单向不回读”）', '默认先题后文（英文 12 源、书籍 4、B 站 5 源共识）；短信/表格等短文本可先扫全文；推断/主旨题需读段落（SL-P7-01、SL-P7-11）。'),
 ('动词题顺序：书籍“数→态→时” vs 青藤/Cindy“谓语→态→时→数”', '取“先判谓语/非谓语→态→时→数”：先排除非谓语选项最省时（SL-P5-06）。'),
 ('P5+P6 用时：20 分钟（主流） vs 15–18 分钟（邹 2023、日韩 900 档） vs 30 分钟（论坛少数）', '按分段：<800 用 20 分钟（SL-ALL-01），800+ 用 15–18（SL-ALL-02）；30 分钟不采纳（P7 必然做不完，与 ETS 完成率数据不符）。'),
 ('Part 间顺序：按序做（邹 XB-08） vs 倒序先做 P7（论坛） vs “不能先做 P7”（toeic.ai，错误）', '默认按序（与游戏 P5→P6→P7 闭环一致）；规则上允许倒序，作为 SL-ALL-09 的“何时不适用”。'),
 ('组内调序：NOT/插入句后做（书籍、英文、日韩） vs 不跳着做（邹）', '组内调序可以（SL-P7-08、SL-ALL-10），跨组跳做不建议，兼顾涂卡不错位。'),
 ('主旨题看首段（书籍/Cindy/新东方） vs 新题首段可能全是铺垫（邹 2026）', '默认看开头，找不到读到第一个请求/通知句；邹的观察放在“何时不适用”。'),
 ('同词选项是陷阱 vs 约 30% 正解保留原词（summitedu）', '“警惕”不等于“排除”：同词选项要核对意思；数字/专名题常原样（SL-P7-04）。'),
 ('逐项排除法（书籍/新东方/英文） vs 800+ 不靠消去法（IIBC）', '低中分段用排除；800+ 先正向找依据，排除作两选一的后备；NOT 题仍逐项核对（SL-P7-07、SL-ALL-24）。'),
 ('插入句：600–700 没把握直接猜（邹） vs 认真用衔接线索做（书籍/日韩）', '按分段：<800 先做其他 3 题、30 秒无头绪就猜；800+ 必做（SL-P6-07、SL-P6-09）。'),
 ('要不要专门背单词（论坛分歧）', '两者并用：NGSL/TSL 词包打底（SL-ALL-19/20）+ 从题里摘词（SL-ALL-18）；生词 ≥5/篇先补词（SL-ALL-21）。'),
 ('P6 只读空格句（旧制 XB-27） vs 读上下文', '旧制做法弃用（DEP-01），新制取 SL-P6-01。'),
 ('“划关键词/划依据”（XB-28 等） vs ETS 禁止题本标记', '练习模式保留“划依据”作为训练手段；模考模式关闭所有标记工具（SL-ALL-25）。'),
]:
    w(f'- **{row[0]}** → {row[1]}')
w('\n## 6. 弃用（旧制）与排除\n')
w('| id | 来源 | 内容 | 原因 | 替代 |\n|---|---|---|---|---|')
for x in d['deprecated']: w(f'| {x["id"]} | {x["from_source"]} | {x["rule_zh"]} | {x["reason"]} | {x["replaced_by"]} |')
w('\n| id | 内容 | 来源 | 排除原因 |\n|---|---|---|---|')
for x in d['excluded']: w(f'| {x["id"]} | {x["rule_zh"]} | {x["source"]} | {x["reason"]} |')
w('\n## 7. 校验\n')
w(f'- 所有节点 ID 存在于 graph_v1：{v["all_node_ids_exist"]}；节点层级与字段一致（qtype/texttype/strategy）：通过\n- 无重复 id：{v["unique_ids"]}\n- deprecated 不在主库、主库不引用弃用来源：{v["deprecated_not_in_main"]}\n- 总体：{"通过" if v["passed"] else "失败：" + "; ".join(v["errors"])}')
w('\n## 8. 已知局限\n- mention_count 是下限且会重复计同一作者的多个视频；三路汇总（论坛/英文/日韩）原始 JSON 未落盘，未给数的按 1 计。\n- 共识度为人工判定（规则见 json meta）。\n- B 站内容为 ASR 机器转写后归纳，数字可能有误。\n')
w('## 9. 全部条目一览\n\n| id | 标题 | 工作规则 | 共识 | weight | 练习 | 模考 |\n|---|---|---|---|---|---|---|')
for e in L: w(f'| {e["id"]} | {e["title_zh"]} | {e["work_rule"]} | {e["consensus"]} | {e["weight"]} | {"✓" if e["practice_mode"] else "—"} | {"✓" if e["mock_mode"] else "—"} |')
open(os.path.join(ROOT, 'data/strategies/strategy_library_v1.md'), 'w').write('\n'.join(o) + '\n')
print('ok')
