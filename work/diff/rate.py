#!/usr/bin/env python3
"""难度重评 v2：按 UX_SPEC_v2 §6 四档，用 LLM 给每题输出 ETS 风格特征 + 0–100 难度分。
单位：P5 每 5 题一次调用；P6/P7 一个题组（篇章）一次调用。
输出 jsonl（断点续跑）：公开 → work/diff/out_open.jsonl；私有 → private_data/work_private/diff/out_private.jsonl
用法: python3 work/diff/rate.py --set open|private [--limit N(单位数)] [--workers 24]
私有题文本只发往 API、结果只写 private_data/ 下，绝不写入公开仓库。"""
import json, os, re, sys, subprocess, concurrent.futures as cf, threading, argparse, time, random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
SETS = {'open': ['data/items_pilot_v1.json', 'data/items_open_maximcuynat.json', 'data/items_open_kdeppaei.json'],
        'private': ['private_data/items/items_private_v1.json']}
OUTS = {'open': 'work/diff/out_open.jsonl', 'private': 'private_data/work_private/diff/out_private.jsonl'}
MODEL = 'deepseek-v4.1-flash-1017'
L = 'ABCD'
lock = threading.Lock()

RUBRIC = r'''你是 ETS 托业（TOEIC Listening & Reading 新制）阅读部分的命题与难度评估专家。按下面固定 rubric 给每道题评难度，必须一致、可复现。

【难度分 score 0–100 与 990 量表档位（固定映射）】
- 0–34 = 基础(<500)：约 450 分考生即能稳定答对（正确率≈70%）。高频 A2–B1 词；干扰项一眼可排；答案原词复现在一句之内。
- 35–54 = 进阶(500–650)：约 600 分考生能答对。B1–B2 词；需要基本语法判断或简单同义替换；1–2 句内定位。
- 55–74 = 熟练(650–800)：约 730 分考生能答对。B2–C1 词/商务搭配；干扰项有迷惑性（同词复现、语义相近）；需跨句整合、NOT/推断、较复杂句法。
- 75–100 = 真考+(800+)：约 860+ 分考生才能稳定答对。C1–C2 词或细微辨义；强干扰（两个选项都"看起来对"）；跨段/跨篇整合、隐含推断、句子插入需全局逻辑。
score 必须落在与你判断的档位对应的区间内。用满整个区间，不要把所有题都打在 40–60。

【锚定示例】
1) P5 "Please ------- the attached form and return it by Friday." (A) attend (B) achieve (C) perform (D) complete → 答案 D。高频搭配 complete a form，干扰项无关 → score 18，基础。
2) P5 "The board has approved the ------- of two new warehouses." (A) construct (B) constructed (C) construction (D) constructively → C。词性题，the__of 填名词 → score 30，基础。
3) P5 "------- the inclement weather, the outdoor ceremony proceeded as scheduled." (A) Despite (B) Although (C) Because of (D) Instead → A。需辨介词/连词及语义让步 → score 50，进阶。
4) P5 "The new policy is intended to ------- the risk of data breaches." (A) mitigate (B) moderate (C) diminish (D) relieve → A。C1 近义辨析+搭配 mitigate the risk，干扰项都可"减少" → score 80，真考+。
5) P7 单篇通知问"What is the purpose of the notice?"，首句即点明 → score 25；同篇问"What is NOT mentioned as a benefit?"需逐项核对三处 → score 60。
6) P7 三篇题"What will Ms. Ito most likely receive?"须把邮件中的会员等级与网页价目表、表格条件三处对照推断 → score 82。
7) P6 句子插入题，四个句子语法都通，需理解前后段逻辑与指代 → score 70–85；同篇 P6 简单时态题（"last week" 提示过去时）→ score 25。

【对每题输出的特征】
- "cefr": 理解/作答所需最难关键词的 CEFR 等级 "A1"–"C2"
- "hard_words": 最多 3 个最难关键词（英文原词）
- "distractor": 干扰项强度 0–3（0 一眼排除；1 一个略有迷惑；2 两个以上有迷惑或同词复现陷阱；3 至少一个干扰项与正确项几乎同样合理，须细辨）
- "locate": 定位距离 "none"(P5 无篇章) | "one_sentence" | "cross_sentence" | "cross_paragraph" | "cross_doc"
- "reasoning": 主要认知类型，取一个 "grammar"|"vocab"|"literal"|"paraphrase"|"inference"|"not_true"|"synonym_in_context"|"insertion"|"intent"|"cross_ref"
- "paraphrase": 正确选项与原文是否为同义改写 true/false（P5 填 false）
- "syntax": 相关句子语法复杂度 1–3（1 简单句；2 含从句/分词/被动；3 多重嵌套、倒装、省略或长名词短语）
- "sent_len": 相关句子平均词数（整数估计）
- "time_sec": 一名 700 分考生做这一题的合理用时秒数（P6/P7 含分摊读文时间）
- "score": 0–100 难度分（按上表）
- "band": "基础"|"进阶"|"熟练"|"真考+"，必须与 score 区间一致
- "handbook_chapter": 解这题最该用的《工作手册》章节号数组（1–12，主章在前，1–3 个）。章目：1词性秒判 2时态与语态 3介词vs连词 4代词 5词汇搭配与生词止损 6句子插入看前后句 7时态看全文时间线 8先看题再定位 9同义替换 10 NOT/推断排除法 11多篇跨文定位 12时间预算与弃题
- "technique_zh": 简体中文 ≤40 字，说明这题怎么用主章这一招快速解出（点出具体信号词/定位点，不要复述题目全文）

只输出 JSON：{"items":[{"qid":"题目标号", ...上述字段...}]}，每道题一条，qid 原样照抄，不得遗漏。不要输出解释。'''

ARGS = None


# 两个端点各自 ≤10 路并发（用户要求），合计 ≤20；失败时换另一端点重试
EPS = [('https://api.kunyou.asia/v1/chat/completions', 'deepseek-v4.1-flash-1017'),
       ('https://igrok.lvyrix.com/v1/chat/completions', 'deepseek-v4.1-flash')]
SEMS = [threading.Semaphore(10), threading.Semaphore(10)]
EP_STAT = [[0, 0], [0, 0]]   # ok, fail


def _pick(prefer):
    for k in (prefer, 1 - prefer):
        if SEMS[k].acquire(blocking=False):
            return k
    SEMS[prefer].acquire(); return prefer


def chat(msgs, max_tokens=2500, temp=0):
    err = None
    for a in range(6):
        k = _pick((a + threading.get_ident()) % 2)
        url, model = EPS[k]
        body = json.dumps({'model': model, 'messages': msgs, 'max_tokens': max_tokens, 'temperature': temp,
                           'response_format': {'type': 'json_object'}})
        out = ''
        try:
            r = subprocess.run(['curl', '-s', '--max-time', '300', url, '-H', 'Content-Type: application/json', '-d', '@-'],
                               input=body, capture_output=True, text=True, timeout=310)
            out = r.stdout
            j = json.loads(out)
            c = j['choices'][0]['message']['content']
            c = re.sub(r'^```(json)?|```$', '', c.strip()).strip()
            res = json.loads(c)
            EP_STAT[k][0] += 1
            return res, dict(j.get('usage') or {}, ep=k)
        except Exception as e:
            EP_STAT[k][1] += 1
            err = f'ep{k} {type(e).__name__}: {str(e)[:100]} | {out[:160]}'
        finally:
            SEMS[k].release()
        time.sleep(1 + 2 * a + random.random())
    raise RuntimeError(f'api fail: {err}')


def passage(b):
    out = []
    for d in b['docs']:
        h = ('[' + d.get('title', '') + ']\n') if d.get('title') else ''
        if d.get('header'):
            h += d['header'] + '\n'
        out.append(h + d.get('text', ''))
    return '\n\n'.join(out)[:9000]


def qblock(q, label):
    s = q.get('stem') or q.get('q') or ''
    opts = '  '.join(f'({L[i]}) {o}' for i, o in enumerate(q['options']))
    head = f'[{label}] Part {q["part"]}' + (f' 空格[{q.get("blank_n")}]' if q.get('blank_n') else '')
    return f'{head}\n{s}\n{opts}\n正确答案：{q.get("answer_letter") or L[q["answer"]]}'


def units(set_name):
    us = []
    for f in SETS[set_name]:
        d = json.load(open(os.path.join(ROOT, f)))
        bmap = {b['bundle_id']: b for b in d['bundles']}
        byb, p5 = {}, []
        for q in d['items']:
            if not q.get('options') or len(q['options']) != 4:
                continue
            if q.get('bundle_id') and q['bundle_id'] in bmap:
                byb.setdefault(q['bundle_id'], []).append(q)
            else:
                p5.append(q)
        for i in range(0, len(p5), 5):
            g = p5[i:i + 5]
            us.append({'uid': 'P5:' + g[0]['id'], 'qs': g, 'b': None})
        for bid, g in byb.items():
            us.append({'uid': bid, 'qs': sorted(g, key=lambda x: int(x['qnum'])), 'b': bmap[bid]})
    return us


def work(u):
    labels = [f'Q{k + 1}' for k in range(len(u['qs']))]
    t = ''
    if u['b']:
        b = u['b']
        t += f'TOEIC Part {b["part"]} 题组（{b.get("kind", "single")}，{len(b["docs"])} 篇）\n【文章】\n{passage(b)}\n\n'
    else:
        t += 'TOEIC Part 5 独立句子填空，每题单独评分。\n\n'
    t += '【题目】\n' + '\n\n'.join(qblock(q, lb) for q, lb in zip(u['qs'], labels))
    for _try in range(3):
      res, usage = chat([{'role': 'user', 'content': RUBRIC + '\n\n===== 待评题目 =====\n' + t}],  # 网关会丢弃长 system 消息，rubric 并入 user
                      max_tokens=1800 + 550 * len(u['qs']))
      got = {str(x.get('qid')): x for x in (res.get('items') or []) if isinstance(x, dict)}
      if all(lb in got and 'score' in got[lb] for lb in labels):
          break
    out = []
    for q, lb in zip(u['qs'], labels):
        x = got.get(lb)
        if x is None or 'score' not in x:
            raise RuntimeError(f'missing {lb}')
        x = {k: v for k, v in x.items() if k != 'qid'}
        out.append({'id': q['id'], 'f': x})
    return {'uid': u['uid'], 'items': out, 'usage': usage}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True, choices=list(SETS))
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=20)
    ap.add_argument('--sample', type=int, default=0, help='随机抽样单位数（试点）')
    a = ap.parse_args(); a.workers = min(a.workers, 20)  # 两端点各≤10
    outp = os.path.join(ROOT, OUTS[a.set]); os.makedirs(os.path.dirname(outp), exist_ok=True)
    done = set()
    if os.path.exists(outp):
        for ln in open(outp):
            try:
                done.add(json.loads(ln)['uid'])
            except Exception:
                pass
    us = units(a.set)
    todo = [u for u in us if u['uid'] not in done]
    if a.sample:
        random.seed(7); todo = random.sample(todo, min(a.sample, len(todo)))
    if a.limit:
        todo = todo[:a.limit]
    print(f'units {len(us)} todo {len(todo)} done {len(done)}', flush=True)
    n = fail = 0; fails = []
    with cf.ThreadPoolExecutor(a.workers) as ex, open(outp, 'a') as f:
        futs = {ex.submit(work, u): u['uid'] for u in todo}
        for fu in cf.as_completed(futs):
            try:
                r = fu.result()
                with lock:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
                n += 1
            except Exception as e:
                fail += 1; fails.append((futs[fu], str(e)[:200]))
            if (n + fail) % 50 == 0:
                print(f'{n} ok {fail} fail', flush=True)
    print(f'finished {n} ok {fail} fail  endpoint ok/fail {EP_STAT}', flush=True)
    for x in fails[:10]:
        print('FAIL', x)


if __name__ == '__main__':
    main()
