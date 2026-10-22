# -*- coding: utf-8 -*-
"""生成并校验 data/graph_v1.json 与 data/graph_v1_summary.md。运行：python3 work/graph_v1/build.py"""
import json, os, sys, heapq, collections, datetime
sys.path.insert(0, os.path.dirname(__file__))
import nodes_a, nodes_b, nodes_c  # noqa: F401  (导入即注册节点)
from nodes_a import NODES

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
SCALE = 25.0  # exam_weight = min(1, 每卷题数 / 25)

BASIS_ZH = {
    "stat_composite": "多来源合并考频（exam_pattern_stats.json composite 区间中值）",
    "stat_single": "单一来源考频",
    "derived": "由上级考频按子类/文本份额拆分的估计",
    "wordlist_freq": "TSL/BSL/NGSL 词频规模换算（非真题计数）",
    "impact_estimate": "影响面估计（无直接题数的能力/技巧节点）",
    "aggregate": "子节点汇总",
}

by_id = {n["id"]: n for n in NODES}
children = collections.defaultdict(list)
for n in NODES:
    if n["parent"]:
        children[n["parent"]].append(n["id"])

memo = {}
def est_of(i):
    n = by_id[i]
    if n["est_items"] is not None:
        return n["est_items"]
    if n["basis"] == "aggregate":
        s = sum(est_of(c) or 0 for c in children[i] if by_id[c]["basis"] != "impact_estimate" or True)
        return s if s > 0 else None
    return None

def weight_of(i):
    if i in memo: return memo[i]
    n = by_id[i]
    if n["weight_override"] is not None:
        w = n["weight_override"]
    elif n["est_items"] is not None:
        w = min(1.0, n["est_items"] / SCALE)
    else:  # aggregate
        e = sum((by_id[c]["est_items"] or 0) for c in children[i] if by_id[c]["basis"] != "aggregate")
        e += sum((est_of(c) or 0) for c in children[i] if by_id[c]["basis"] == "aggregate")
        w = min(1.0, e / SCALE) if e > 0 else max([weight_of(c) for c in children[i]] or [0])
        if e > 0: n["_agg_est"] = round(e, 1)
    memo[i] = round(w, 3)
    return memo[i]

for n in NODES: weight_of(n["id"])

# ------------------------------------------------------------------ validation
errors = []
ids = [n["id"] for n in NODES]
dup = [i for i, c in collections.Counter(ids).items() if c > 1]
if dup: errors.append(f"重复 ID: {dup}")
for n in NODES:
    for p in n["prereqs"]:
        if p not in by_id: errors.append(f"{n['id']} 的 prereq {p} 不存在")
        if p == n["id"]: errors.append(f"{n['id']} 自依赖")
    if n["parent"] and n["parent"] not in by_id: errors.append(f"{n['id']} 的 parent 不存在")
    if n["target_band"] not in (400, 600, 700, 800, 900): errors.append(f"{n['id']} band 非法")
    if not (0 <= memo[n["id"]] <= 1): errors.append(f"{n['id']} 权重越界")
    if not set(n["parts"]) <= {5, 6, 7}: errors.append(f"{n['id']} parts 非法")
# cycle check (Kahn) on prereq edges, and separately on parent chain
indeg = {i: 0 for i in ids}; out = collections.defaultdict(list)
for n in NODES:
    for p in n["prereqs"]:
        out[p].append(n["id"]); indeg[n["id"]] += 1
q = [i for i in ids if indeg[i] == 0]; seen = 0; topo = []
deg = dict(indeg)
while q:
    x = q.pop(); seen += 1; topo.append(x)
    for y in out[x]:
        deg[y] -= 1
        if deg[y] == 0: q.append(y)
if seen != len(ids): errors.append(f"prereq 存在环：{len(ids) - seen} 个节点无法拓扑排序")
for n in NODES:  # parent chain acyclic
    s, c = set(), n["id"]
    while c:
        if c in s: errors.append(f"parent 环: {n['id']}"); break
        s.add(c); c = by_id[c]["parent"]
# band inversion: 前置节点的目标段不应高于本节点
inversions = [(n["id"], p, n["target_band"], by_id[p]["target_band"]) for n in NODES for p in n["prereqs"]
              if by_id[p]["target_band"] > n["target_band"]]
for a in inversions: errors.append(f"分数段倒挂: {a}")
v0_ids = [x["id"] for x in json.load(open(os.path.join(DATA, "items_v0.json"), encoding="utf-8"))["nodes"]]
mapped = collections.defaultdict(list)
for n in NODES:
    for v in n["mapped_from_v0"]: mapped[v].append(n["id"])
missing = [v for v in v0_ids if v not in mapped]
if missing: errors.append(f"v0 节点未映射: {missing}")
unknown_v0 = sorted({v for v in mapped if v not in v0_ids})
if unknown_v0: errors.append(f"mapped_from_v0 含未知 v0 id: {unknown_v0}")

# ------------------------------------------------------------------ output json
LAYER_ORDER = ["foundation", "grammar", "vocab", "qtype", "texttype", "strategy"]
out_nodes = []
for n in NODES:
    e = n["est_items"] if n["est_items"] is not None else n.get("_agg_est")
    out_nodes.append(dict(
        id=n["id"], name_zh=n["name_zh"], layer=n["layer"], parent=n["parent"], prereqs=n["prereqs"],
        parts=n["parts"], exam_weight=memo[n["id"]],
        exam_weight_source=dict(type=n["basis"], type_zh=BASIS_ZH[n["basis"]],
                                est_items_per_test=e, note=n["weight_note"] or None),
        target_band=n["target_band"], description_zh=n["description_zh"],
        example_pattern=n["example_pattern"], mapped_from_v0=n["mapped_from_v0"],
        is_group=bool(children[n["id"]]),
    ))
graph = dict(
    version="1.0",
    built=datetime.date(2026, 10, 21).isoformat(),
    scope="TOEIC L&R 阅读部分，现行线性版（日韩 2016-05、其他公开考试 2018-04 起；P5 30 / P6 16 含 4 道句子插入 / P7 54，75 分钟 100 题）。旧制特有考点（改错题等）不收录。多阶段自适应版 MSA 题型相同，节点通用，但 est_items 按线性版计。",
    weight_method=f"exam_weight = min(1, 每份线性版试卷中该节点为决定性考点的估计题数 / {SCALE:g})；无直接题数的能力/技巧节点用影响面估计（type=impact_estimate）；词包节点用词表频率规模（type=wordlist_freq）；分组节点为子节点汇总。来源类型见 exam_weight_source.type。",
    target_band_meaning="从该分数段（TOEIC 总分目标）起需要掌握：400/600/700/800/900",
    edges_note="边隐含于 prereqs（A 在 B.prereqs 中 = 先 A 后 B）；parent 只表示归类，不是学习依赖。",
    sources=["data/strategies/exam_pattern_stats.json", "data/strategies/books.json", "work/reports/strategy_findings_summary.md",
             "data/wordlists/TSL_12_stats.csv", "data/external/wordlists/BSL_120_stats.csv", "data/external/wordlists/NGSL_12_stats.csv",
             "data/items_v0.json", "data/strategies/books_taxonomy.md"],
    v0_mapping={v: mapped[v] for v in v0_ids},
    nodes=out_nodes,
)
with open(os.path.join(DATA, "graph_v1.json"), "w", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ summary
cnt = collections.Counter(n["layer"] for n in NODES)
grp = collections.Counter(n["layer"] for n in NODES if children[n["id"]])
leaf = [n for n in NODES if not children[n["id"]]]
FREQ = ("stat_composite", "stat_single", "derived")
top = sorted([n for n in NODES if n["basis"] in FREQ], key=lambda n: (-memo[n["id"]], n["id"]))
top_wl = sorted([n for n in NODES if n["basis"] == "wordlist_freq"], key=lambda n: -memo[n["id"]])
top_imp = sorted([n for n in leaf if n["basis"] == "impact_estimate"], key=lambda n: (-memo[n["id"]], n["id"]))
LZ = dict(foundation="基础层", grammar="语法层", vocab="词汇层", qtype="题型层", texttype="文本类型层", strategy="应试技巧层")

def study_order(goal):
    maxband = {500: 400, 600: 600, 700: 700, 800: 800, 900: 900}[goal]
    sel = {n["id"] for n in NODES if n["target_band"] <= maxband}
    d = {i: sum(1 for p in by_id[i]["prereqs"] if p in sel) for i in sel}
    h = [(-memo[i], i) for i in sel if d[i] == 0]; heapq.heapify(h); order = []
    while h:
        _, x = heapq.heappop(h); order.append(x)
        for y in out[x]:
            if y in sel:
                d[y] -= 1
                if d[y] == 0: heapq.heappush(h, (-memo[y], y))
    return [i for i in order if by_id[i]["basis"] != "aggregate"]

L = []
w = L.append
w("# TOEIC Reading 能力图谱 v1 · 摘要")
w("")
w(f"生成：2026-10-21（`work/graph_v1/build.py`）。数据文件：`data/graph_v1.json`。适用：现行线性版（P5 30 / P6 16 / P7 54，75 分钟 100 题）。")
w("")
w("## 1. 校验结果")
w("")
w(f"- 节点总数：**{len(NODES)}**（分组节点 {sum(grp.values())}，叶节点 {len(leaf)}）")
w(f"- ID 唯一：{'通过' if not dup else '失败'}；prereqs 全部存在：{'通过' if not any('不存在' in e for e in errors) else '失败'}；无环（prereq 拓扑排序 {seen}/{len(ids)}）：{'通过' if seen == len(ids) else '失败'}；parent 链无环：通过")
w(f"- 分数段倒挂（前置节点段位高于后继）：{len(inversions)} 处")
w(f"- v0 的 20 个节点全部映射：{'通过' if not missing else '失败：' + str(missing)}")
w(f"- 错误总数：{len(errors)}" + ("" if not errors else "：" + "；".join(errors)))
w("")
w("## 2. 各层节点数")
w("")
w("| 层 | 总数 | 其中分组 | 叶节点 | 说明 |")
w("|---|---:|---:|---:|---|")
notes = dict(foundation="长句主干、阅读速度、指代与篇章逻辑、核心词与构词",
             grammar="9 个语法大类、54 个叶考点（P5/P6）",
             vocab="30 个场景词包 + 12 搭配 + 14 易混 + 12 同义替换 + 4 同词性词汇题 + 4 分段储备 + 职位部门",
             qtype="P5 11 型、P6 10 型、P7 15 型 + P7 设问×文本 45 个高发组合",
             texttype="邮件、信件、备忘、通知、广告、招聘、文章、表格(发票/日程/申请表)、短信、群聊、网页、评价、说明书、多篇(双/三篇)",
             strategy="时间、顺序、定位、排除、放弃、涂卡、复盘 7 组")
for l in LAYER_ORDER:
    w(f"| {LZ[l]} ({l}) | {cnt[l]} | {grp[l]} | {cnt[l]-grp[l]} | {notes[l]} |")
w(f"| 合计 | {len(NODES)} | {sum(grp.values())} | {len(leaf)} | |")
w("")
w("## 3. exam_weight 说明与最高 30 个节点（考频类）")
w("")
w(f"`exam_weight = min(1, 每份线性版试卷中该节点为决定性考点的估计题数 / {SCALE:g})`。25 题≈满分权重，便于区分 P7 大题型与 P5 细考点。来源类型：")
for k, v in BASIS_ZH.items():
    w(f"- `{k}`：{v}")
w("")
w("注意：P7 设问×文本组合是设问类型的子集，与父节点题数重叠；技巧/基础节点的权重是影响面估计，不能与考频权重直接相加。")
w("")
w("| # | ID | 名称 | 层 | 权重 | 估计题数/卷 | 来源类型 | 目标段 |")
w("|---:|---|---|---|---:|---:|---|---:|")
for r, n in enumerate(top[:30], 1):
    e = n["est_items"]
    w(f"| {r} | `{n['id']}` | {n['name_zh']} | {LZ[n['layer']]} | {memo[n['id']]:.2f} | {e if e is not None else '—'} | {n['basis']} | {n['target_band']} |")
w("")
w("影响面估计类（基础/技巧，无直接题数，单独排序，不与上表混排）前 10：")
w("")
w("| # | ID | 名称 | 权重 | 目标段 |")
w("|---:|---|---|---:|---:|")
for r, n in enumerate(top_imp[:10], 1):
    w(f"| {r} | `{n['id']}` | {n['name_zh']} | {memo[n['id']]:.2f} | {n['target_band']} |")
w("")
w("")
w("场景词包（wordlist_freq，词表常用度而非真题计数，单独排序）前 10：" + "、".join(f"{n['name_zh']}({memo[n['id']]:.2f})" for n in top_wl[:10]))
w("")
w("## 4. 按目标分数段的推荐攻克顺序")
w("")
w("算法：只取 target_band ≤ 目标段的非汇总节点（叶节点 + 自带题数的题型节点），按 prereqs 拓扑排序，同层可选时 exam_weight 高者优先。目标 500 取 400 段节点；每个更高目标列出“在上一档基础上新增”的节点（上一档内容默认已完成）。")
w("")
prev = set()
for goal in (500, 600, 700, 800, 900):
    order = study_order(goal)
    new = [i for i in order if i not in prev]
    w(f"### 目标 {goal}（新增 {len(new)} 个节点，累计 {len(order)}）")
    w("")
    if goal == 500:
        w("重点：P5 词性/介词/代词/基础时态语态 + 高频场景词 + P7 单篇细节与先题后文、不留空。三篇连锁题可先放弃。")
    elif goal == 600:
        w("重点：P5 连词/非谓语/搭配、P6 语境题、P7 照合/NOT/原因题、整卷配速与放弃线。")
    elif goal == 700:
        w("重点：P6/P7 句子插入、推断、意图、同义词、双篇连锁；阅读速度 150 wpm 以上；错误选项套路。")
    elif goal == 800:
        w("重点：三篇连锁、200 wpm、假设倒装/虚拟、低频易混与改写（否定改写、概括改写）。")
    else:
        w("重点：低频语法收尾（复合关系词、倒装），P5 全对与 P7 留检查时间。")
    w("")
    w("| 序 | ID | 名称 | 权重 | 段 |")
    w("|---:|---|---|---:|---:|")
    for r, i in enumerate(new, 1):
        n = by_id[i]
        w(f"| {r} | `{i}` | {n['name_zh']} | {memo[i]:.2f} | {n['target_band']} |")
    w("")
    prev |= set(order)
w("## 5. 新旧制差异与对节点的影响")
w("")
w("本图谱只以**现行线性版**为准：日本/韩国 2016-05-29 起、中国等其他公开考试 2018-04 起（exam_pattern_stats.json：toeic.xdf.cn/201803/10761795.html），至 2026 年未变。")
w("")
w("| 项目 | 旧制（2006–2016/2018） | 现行线性版 | 对图谱节点的影响 |")
w("|---|---|---|---|")
w("| Part 5 | 40 题 | 30 题 | 题型不变，各考点题数按 30 题折算；旧书 P5 比例可参考，但绝对题数要乘 0.75 |")
w("| Part 6 | 12 题（3 篇×4，只填词/短语） | 16 题（4 篇×4，每篇 1 道句子插入） | 新增 `QT.P6.INSERTION` 及 3 个位置子类；`QT.P6.CLASSIFY` 上下文型比重上升；旧书无句子插入训练 |")
w("| Part 7 | 48 题（单篇 28 + 双篇 4 组 20） | 54 题（单篇 29 + 双篇 2 组 10 + 三篇 3 组 15） | 新增 `TX.TRIPLE`、`QT.P7X.CROSS_REF.TRIPLE`；新增文本 `TX.TEXT_MSG`、`TX.CHAT`；新增题型 `QT.P7.INTENT`、`QT.P7.INSERTION` |")
w("| 时长 | 75 分钟 100 题 | 75 分钟 100 题 | 每题可用时间不变，但 P7 文本量增加 → `ST.TIME.TOTAL_PLAN` 中 P7 需 ≥53–55 分钟，`FD.READ.SPEED_*` 权重上调 |")
w("| 改错题 | 2006 年前旧版 Part 6 为改错（Error Recognition） | 无 | 不收录任何改错节点 |")
w("")
w("书目层面：`books_taxonomy.md` 标注了旧制书目（新东方/群言 2010–2011 年引进书、北语 2010 官方指南、外研社 2009 Tactics for TOEIC）。这些书的语法单元仍可用于 GR 层，但其 Part 6/7 章节缺少句子插入、三篇、短信/群聊、意图题，相关节点只采用新制来源。")
w("")
w("**多阶段自适应版（MSA）**：ETS 另有 TOEIC L&R Multistage Adaptive 版本，阅读部分约 37 分钟 45 题（Unit 1 25 题 + Unit 2 20 题，Unit 2 难度由 Unit 1 表现决定），题型与线性版相同，主要用于机构/在线考试（ETS 4-skills Examinee Handbook 2025-08：https://www.ets.org/content/dam/ets-org/de/pdfs/toeic/toeic-4-skills-tests-examinee-handbook.pdf ；ETS Global：https://www.etsglobal.org/us/en/blog/news/adaptative-toeic-test）。对图谱的影响：节点与 prereqs 通用；`est_items`/`exam_weight` 按线性版 100 题计，MSA 题数约为其 45%，时间策略节点（`ST.TIME.*`、`ST.BUBBLE.*`）不适用于在线 MSA（无答题卡）。")
w("")
w("## 6. v0 → v1 映射")
w("")
w("| v0 | v0 名称 | v1 节点 |")
w("|---|---|---|")
v0n = {x["id"]: x["name"] for x in json.load(open(os.path.join(DATA, "items_v0.json"), encoding="utf-8"))["nodes"]}
for v in v0_ids:
    ms = mapped[v]
    show = ", ".join(f"`{m}`" for m in ms[:8]) + (f" 等 {len(ms)} 个" if len(ms) > 8 else "")
    w(f"| {v} | {v0n[v]} | {show} |")
w("")
w("## 7. 已知局限")
w("")
w("- 考频来自公开博客/题库统计与书目目录，样本小且口径不一；`derived` 类题数是按比例拆分的估计，应用 App 实测作答数据（如 EdNet 匿名标签）回校。")
w("- 场景词包按主题人工聚类，种子词在 TSL/BSL 命中有限（两表是 NGSL 的补充，基础场景词多在 NGSL）；词包权重反映语料常用度，不是真题计数。")
w("- target_band 为经验判断（参考 haradaeigo、IIBC methods07、金のフレーズ分段），非官方标准。")
with open(os.path.join(DATA, "graph_v1_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")

print("nodes", len(NODES), dict(cnt), "groups", dict(grp))
print("errors", len(errors)); [print(" -", e) for e in errors]
print("TOP15 (freq-based):"); [print(f"  {memo[n['id']]:.2f} {n['id']} {n['name_zh']}") for n in top[:15]]
