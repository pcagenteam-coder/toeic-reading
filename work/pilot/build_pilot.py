#!/usr/bin/env python3
"""把 src_p5.py / src_p67.py 组装成 data/items_pilot_v1.json（兼容 items_v0 字段：id/node/stem|q/options/answer/explain_zh）。
答案位置按 Part 均衡（每个字母约 25%，连续同答案 ≤3），INSERTION 固定 [1]–[4]，数字选项从小到大。"""
import json, random, sys, os
ROOT = "/workspace/projects/58061e9e-e075-4f3f-880c-32a61b21a72c"
sys.path.insert(0, os.path.dirname(__file__))
from src_p5 import P5, VOCAB_EXCEPTIONS
from src_p67 import P6, P7
TPL = {t["template_id"]: t for t in json.load(open(f"{ROOT}/data/templates/item_templates.json"))["templates"]}
BASE = {5: 26.4, 6: 33.8, 7: 67.4}
FAST = {"T5.WORD_FORM": 0.7, "T5.VERB_FORM": 0.85, "T5.PRONOUN": 0.8, "T5.VOCAB": 1.1, "T5.CONJ": 1.0, "T5.CONNECTOR_MIX": 1.0}
rng = random.Random(20261021)

def uniq(xs):
    out = []
    for x in xs:
        if x not in out: out.append(x)
    return out

def ttime(part, tpl, diff, extra=1.0):
    f = 1.0
    for k, v in FAST.items():
        if tpl.startswith(k): f = v
    return round(BASE[part] * f * (0.8 + 0.1 * diff) * extra)

class Balancer:
    def __init__(self): self.cnt = [0, 0, 0, 0]; self.hist = []
    def pick(self, fixed=None):
        if fixed is not None: pos = fixed
        else:
            cands = [p for p in range(4) if not (len(self.hist) >= 3 and all(h == p for h in self.hist[-3:]))]
            m = min(self.cnt[p] for p in cands)
            pos = rng.choice([p for p in cands if self.cnt[p] == m])
        self.cnt[pos] += 1; self.hist.append(pos); return pos

def place(ans, dis, bal, fixed_order=False, numeric=False):
    """返回 options, answer_idx, distractor_reasons(按选项字母)"""
    if fixed_order or numeric:
        allopts = [ans] + [d[0] for d in dis]
        if fixed_order: allopts = sorted(allopts)
        else: allopts = sorted(allopts, key=lambda s: float(s.replace("$", "").replace(",", "")))
        idx = allopts.index(ans); bal.pick(idx)
        opts = allopts
    else:
        idx = bal.pick()
        ds = dis[:]; rng.shuffle(ds)
        opts = [d[0] for d in ds]; opts.insert(idx, ans)
    reasons = {}
    for d in dis:
        reasons["ABCD"[opts.index(d[0])]] = {"trap": d[1], "why_zh": d[2]}
    return opts, idx, reasons

items, bundles = [], []
# ---- P5 ----
bal5 = Balancer()
for i, (tpl, extra, diff, stem, ans, dis, exp) in enumerate(P5):
    t = TPL[tpl]
    nodes = uniq([n for n in t["node_ids"] if n.startswith("QT.")][:1] + extra + ["QT.P5.IDENTIFY"])
    opts, idx, rs = place(ans, dis, bal5)
    form = "P5-A" if i < 30 else "P5-B"
    items.append({"id": f"PL5-{i+1:03d}", "part": 5, "form": form, "qnum": 101 + (i % 30),
        "node": nodes[0], "node_ids": nodes, "template_id": tpl, "stem": stem, "options": opts,
        "answer": idx, "answer_letter": "ABCD"[idx], "explain_zh": exp, "distractor_reasons": rs,
        "difficulty_est": diff, "target_time_sec": ttime(5, tpl, diff), "format_version": "current"})
    exc = {o: VOCAB_EXCEPTIONS[o] for o in opts if o in VOCAB_EXCEPTIONS}
    if exc: items[-1]["vocab_exceptions"] = exc
# 打乱 P5 呈现顺序但保持题号连续：按 form 内随机重排题号
for form in ("P5-A", "P5-B"):
    group = [it for it in items if it["form"] == form]
    nums = [it["qnum"] for it in group]; rng.shuffle(nums)
    for it, n in zip(group, nums): it["qnum"] = n
# ---- P6 ----
bal6 = Balancer()
for bi, b in enumerate(P6):
    form = "P6-A" if bi < 4 else "P6-B"
    start = 131 + 4 * (bi % 4)
    bundles.append({"bundle_id": b["bundle"], "part": 6, "form": form, "kind": "single",
        "text_type": b["text_type"], "node_ids": [b["text_type"], b["scene"]],
        "docs": [{"doc_type": b["text_type"], "header": b["header"], "text": b["text"]}],
        "qnums": list(range(start, start + 4)), "blank_marker": "[n] = 第 n 个空格（显示时替换为 -------）", "format_version": "current"})
    for k, q in enumerate(b["items"]):
        t = TPL[q["tpl"]]
        nodes = uniq([t["node_ids"][0]] + t["node_ids"][1:] + q["nodes"] + [b["text_type"], b["scene"]])
        if q["tpl"].startswith("T6.INS"): nodes = uniq(["QT.P6.INSERTION"] + nodes)
        opts, idx, rs = place(q["ans"], q["dis"], bal6)
        items.append({"id": f"PL6-{bi+1}-{k+1}", "part": 6, "form": form, "bundle_id": b["bundle"], "blank_n": k + 1,
            "qnum": start + k, "node": nodes[0], "node_ids": nodes, "template_id": q["tpl"], "options": opts,
            "answer": idx, "answer_letter": "ABCD"[idx], "explain_zh": q["exp"], "distractor_reasons": rs,
            "difficulty_est": q["diff"], "target_time_sec": ttime(6, q["tpl"], q["diff"], 1.3 if q["tpl"].startswith("T6.INS") else 1.0),
            "format_version": "current"})
# ---- P7 ----
bal7 = Balancer()
qn_single, qn_multi = 147, 176
for s in P7:
    n = len(s["items"])
    if s["kind"] == "single": start = qn_single; qn_single += n
    else: start = qn_multi; qn_multi += n
    bundles.append({"bundle_id": s["set"], "part": 7, "form": "P7-A", "kind": s["kind"], "text_type": s["text_type"],
        "node_ids": uniq([s["text_type"], s["scene"]] + [d["doc_type"] for d in s["docs"]]),
        "docs": s["docs"], "qnums": list(range(start, start + n)), "format_version": "current"})
    for k, q in enumerate(s["items"]):
        t = TPL[q["tpl"]]
        nodes = uniq(t["node_ids"] + q["nodes"] + [s["scene"]])
        opts, idx, rs = place(q["ans"], q["dis"], bal7, fixed_order=q.get("fixed", False), numeric=q.get("numeric", False))
        mult = {"single": 1.0, "double": 1.2, "triple": 1.3}[s["kind"]]
        items.append({"id": f"PL7-{s['set'][3:]}-{k+1}", "part": 7, "form": "P7-A", "bundle_id": s["set"],
            "qnum": start + k, "node": nodes[0], "node_ids": nodes, "template_id": q["tpl"], "q": q["q"], "options": opts,
            "answer": idx, "answer_letter": "ABCD"[idx], "explain_zh": q["exp"], "distractor_reasons": rs,
            "difficulty_est": q["diff"], "target_time_sec": ttime(7, q["tpl"], q["diff"], mult), "format_version": "current"})

out = {"meta": {"version": "pilot-v1", "built": "2026-10-21", "format_version": "current",
    "scope": "TOEIC Reading 现行线性版（P5 30 / P6 16 / P7 54）",
    "compat": "沿用 items_v0 字段 id/node/stem|q/options/answer(0-3)/explain_zh；新增 node_ids、template_id、difficulty_est、target_time_sec、distractor_reasons、bundle_id、qnum、form、format_version",
    "originality": "全部原创；data/external/toeic_items 仅看风格，审题脚本做近似重复比对",
    "vocab_constraint": "NGSL 1.2 + TSL 1.2（专有名词、数字、星期月份除外，允许屈折变化）",
    "templates": "data/templates/item_templates.json",
    "target_time_basis": "EdNet 中位用时 P5 26.4s / P6 33.8s / P7 67.4s × 题型系数 × 难度系数",
    "forms_note": "试点题按“迷你卷”编号：P5-A/P5-B 各 101–130；P6-A 131–146（4 篇）+ P6-B 131–134（第 5 篇）；P7-A 单篇 147 起、多篇 176 起（试点不满 54 题）",
    "counts": {"P5": sum(1 for i in items if i["part"] == 5), "P6": sum(1 for i in items if i["part"] == 6), "P7": sum(1 for i in items if i["part"] == 7)}},
  "bundles": bundles, "items": items}
json.dump(out, open(f"{ROOT}/data/items_pilot_v1.json", "w"), ensure_ascii=False, indent=1)
print(out["meta"]["counts"], "bundles", len(bundles), "ans dist P5", bal5.cnt, "P6", bal6.cnt, "P7", bal7.cnt)
