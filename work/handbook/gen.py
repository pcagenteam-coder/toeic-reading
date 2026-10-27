#!/usr/bin/env python3
"""《新人工作手册》12 章生成 + 独立作答核对。用法: python3 gen.py [--workers 32]
中间结果 state.json（断点续跑）；输出 ../../data/lessons/handbook_v1.json"""
import json, os, re, subprocess, time, random, argparse, threading, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(HERE, 'state.json'); OUTF = os.path.join(HERE, '../../data/lessons/handbook_v1.json')
MODEL = 'deepseek-v4.1-flash-1017'; lock = threading.Lock()

import sys; sys.path.insert(0, os.path.join(HERE, '../llm'))
from multi_chat import chat as _mc
import multi_chat, threading as _t; multi_chat.SEM['kunyou'] = _t.BoundedSemaphore(5)  # Kunyou 另有难度重评子任务在用，留余量
def chat(msgs, max_tokens=6000, temp=0.7, prefer='igrok'):
    msgs = [dict(m) for m in msgs]; msgs[-1]['content'] += '\n\n只输出一个 JSON 对象，不要任何其他文字。'
    return _mc(msgs, max_tokens, temp, prefer)

# (id, part, 章目, 出题要求, 人物)
CH = [
 (1,5,'词性秒判','Part 5 单句填空，四个选项是同一词根不同词性（如 -tion/-tive/-tively/-te），靠空格前后结构判断所需词性','Ken'),
 (2,5,'时态与语态','Part 5 单句填空，四个选项是同一动词的不同时态/语态/非谓语形式，靠时间标志词与主被动关系判断','Ken'),
 (3,5,'介词 vs 连词','Part 5 单句填空，选项混有介词、连词、副词（如 despite/although/however/because of），靠空格后是名词短语还是从句判断','Ken'),
 (4,5,'代词','Part 5 单句填空，选项是同一人称代词的不同格（主格/宾格/所有格/名词性物主/反身）或不同人称，靠位置与指代判断','Ken'),
 (5,5,'词汇搭配与生词止损','Part 5 单句填空，四个选项为同词性近义词，靠固定搭配/语境判断；示范与“一招”需包含遇到生词时如何止损（排除+限时）','Ken'),
 (6,6,'句子插入看前后句','Part 6 短文填空：一篇 4–6 句的原创商务短文（邮件/备忘/公告），含一个空 [BLANK]，四个选项都是完整句子，要求选出最适合插入空格的句子；靠空格前后句的指代、连接词与话题衔接判断','Mia'),
 (7,6,'时态看全文时间线','Part 6 短文填空：一篇 4–6 句的原创商务短文，含一个空 [BLANK]，四个选项为同一动词的不同时态；单句看不出，需根据全文日期/事件先后（已发生/将发生）判断','Mia'),
 (8,7,'先看题再定位','Part 7 阅读：一篇 80–150 词的原创邮件/公告/表单/广告，配 1 道细节题；“一招”是先读题干抓关键词（人名/数字/日期）再回原文定位','Leo'),
 (9,7,'同义替换','Part 7 阅读：一篇 80–150 词的原创邮件/公告/表单，配 1 道题，正确选项是原文措辞的同义改写（不照抄原文），干扰项多为原文词照搬但意思不对','Leo'),
 (10,7,'NOT 与推断排除法','Part 7 阅读：一篇 80–150 词的原创邮件/公告/表单，配 1 道 NOT 题（What is NOT mentioned/indicated…）或推断题（What is suggested/implied…），用逐项排除法解答','Leo'),
 (11,7,'多篇跨文定位','Part 7 多篇阅读：两篇各 50–100 词的原创关联文本（如 邮件+日程表、广告+订单表单），配 1 道必须综合两篇信息才能回答的题','Leo'),
 (12,7,'时间预算与弃题','Part 7 阅读：一篇 80–150 词的原创邮件/公告/表单配 1 道题；“一招”讲整卷 75 分钟时间分配（P5≈每题20秒、P6≈每篇2分钟、P7≈每题1分钟）、卡题超时即猜一个先走的弃题纪律；题目可以是需判断“值不值得花时间”的较长定位题','Dana'),
]
BANDS = [('基础', '<500 分水平：常见词、短句、干扰项弱'), ('进阶', '500–650：中等词汇，干扰项有一定迷惑性'),
         ('进阶', '500–650：中等词汇，干扰项有一定迷惑性'), ('熟练', '650–800：较长句或较长文本，干扰项强，需要细看'),
         ('真考+', '800+：接近或略难于真实考试的难题，词汇较高级、干扰项很强、定位或推理距离远')]
SECS = {5: [15, 20, 20, 25, 30], 6: [30, 40, 40, 50, 60], 7: [45, 60, 60, 75, 90]}
COMMON = '''全部内容必须原创，不得复制或改写任何现有题库/教材/真题文本；英文使用 ETS 托业商务语境（办公、会议、出差、采购、人事、客服、设施等），公司名/人名自拟（主角所在公司叫 Halvorsen）。只输出 JSON。'''
ITEM_SCHEMA = '''题目 JSON 字段：
"passage": Part 5 为 null；Part 6/7 为 [{"type":"email|notice|form|memo|advertisement|schedule|article","title":"标题或主题行","text":"英文原文"}]（多篇阅读给 2 个元素）；
"question": 英文题干（Part 5 为含 _____ 的句子；Part 6 写 "Which sentence best fits [BLANK]?" 或 "Choose the best option for [BLANK]."）；
"options": {"A":"..","B":"..","C":"..","D":".."}；"answer": 唯一正确字母；
"explain_zh": 中文解析 2–4 句，说明依据（引用原文关键词）；
"distractors": {"其余三个字母各一": "中文排除理由一句"}'''

def gen_meta(c):
    i, part, name, req, who = c
    p = f'''你在为托业阅读 App 编写《新人工作手册》第 {i} 章「{name}」（Part {part}）。场景：用户是 Halvorsen 公司新人，{who} 是同事/主管，用职场口吻传授招式。题型：{req}。
{COMMON}
输出 JSON：
"title": 职场化中文章节标题，带人物名，≤14 字，如“Ken 的 3 秒校对法”；
"trick": 一招，中文口诀，最多 3 行（数组，每行 ≤22 字）；
"signals": 适用信号，数组 2–3 条（看到什么就用这招，中文）；
"example": 一道示范题（难度：进阶），按以下字段，另加 "steps": 3 步中文拆解数组（第1步识别信号、第2步运用招式、第3步排除并确认）。
{ITEM_SCHEMA}'''
    return chat([{'role': 'user', 'content': p}], 8000, 0.8)

def gen_item(c, k, meta, avoid):
    i, part, name, req, who = c
    b, bd = BANDS[k]
    p = f'''为托业《新人工作手册》第 {i} 章「{name}」（Part {part}）出 1 道练习题。题型：{req}。
本章一招：{' / '.join(meta.get('trick', []))}
难度档：{b}（{bd}）。本题是该章第 {k+1}/5 题，由易到难。
不要与这些已有题的话题重复：{avoid}
{COMMON}
确保只有一个选项正确、答案无争议。
{ITEM_SCHEMA}'''
    it = chat([{'role': 'user', 'content': p}], 6000, 0.9)
    it['band'] = b; it['ref_seconds'] = SECS[part][k]
    return it

def solve(it, part):
    t = ''
    for d in (it.get('passage') or []):
        t += f"[{d.get('type')}] {d.get('title','')}\n{d.get('text','')}\n\n"
    t += f"Question: {it['question']}\n" + '\n'.join(f'({k}) {v}' for k, v in it['options'].items())
    s = chat([{'role': 'system', 'content': f'你是托业满分考生。独立作答这道 Part {part} 题。只输出 JSON：{{"answer":"字母","confidence":0到1,"unique":true/false（是否只有一个选项正确）,"reason":"一句中文"}}'},
              {'role': 'user', 'content': t}], 4000, 0, 'kunyou')
    return s

def ok_item(it):
    try:
        o = it['options']; return set(o) == set('ABCD') and it['answer'] in 'ABCD' and it.get('question') and it.get('explain_zh') and isinstance(it.get('distractors'), dict)
    except Exception: return False

def check(it, part):
    if not ok_item(it): return False, {'err': 'schema'}
    s = solve(it, part)
    a = str(s.get('answer', '')).strip()[:1].upper()
    return (a == it['answer'] and s.get('unique', True) is not False), s

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=15); ap.add_argument('--rounds', type=int, default=4)
    a = ap.parse_args()
    st = json.load(open(ST)) if os.path.exists(ST) else {'ch': {}, 'log': {'mismatch': 0, 'regen': 0}}
    def save():
        with lock: json.dump(st, open(ST, 'w'), ensure_ascii=False, indent=1)
    # 1) meta+example
    def do_meta(c):
        key = str(c[0])
        for r in range(a.rounds):
            try:
                m = gen_meta(c); ex = m.get('example') or {}
                good, s = check(ex, c[1]) if ok_item(ex) and len(ex.get('steps', [])) == 3 else (False, {'err': 'schema'})
            except Exception as e:
                print('meta err', key, repr(e)[:120], flush=True); continue
            if not good: 
                with lock: st['log']['mismatch'] += 1 if 'err' not in s else 0; st['log']['regen'] += 1
                continue
            ex['band'] = '进阶'; ex['ref_seconds'] = SECS[c[1]][1]; ex['verify'] = s
            with lock: st['ch'][key] = {'meta': m, 'items': st['ch'].get(key, {}).get('items', {})}
            save(); return key, True
        return key, False
    with cf.ThreadPoolExecutor(a.workers) as ex:
        print('meta', list(ex.map(do_meta, [c for c in CH if str(c[0]) not in st['ch']])), flush=True)
    # 2) items
    def do_item(arg):
        c, k = arg; key = str(c[0]); m = st['ch'][key]['meta']
        avoid = (m['example'].get('question', '')[:80])
        for r in range(a.rounds):
            try:
                it = gen_item(c, k, m, avoid)
                good, s = check(it, c[1])
            except Exception as e:
                print('item err', key, k, repr(e)[:120], flush=True); continue
            if good:
                it['verify'] = s
                with lock: st['ch'][key]['items'][str(k)] = it
                save(); return key, k, True
            with lock:
                if 'err' not in s: st['log']['mismatch'] += 1
                st['log']['regen'] += 1
        return key, k, False
    jobs = [(c, k) for c in CH if str(c[0]) in st['ch'] for k in range(5) if str(k) not in st['ch'][str(c[0])]['items']]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(do_item, jobs))
    print('items fail', [r for r in res if not r[2]], flush=True)
    save(); build(st)

def build(st):
    chs = []
    for c in CH:
        e = st['ch'].get(str(c[0]))
        if not e: continue
        m = e['meta']; strip = lambda x: {k: v for k, v in x.items() if k != 'verify'}
        items = [dict(strip(e['items'][str(k)]), id=f'HB{c[0]:02d}-{k+1}') for k in range(5) if str(k) in e['items']]
        ex = dict(strip(m['example']), id=f'HB{c[0]:02d}-0')
        chs.append({'chapter': c[0], 'part': c[1], 'topic': c[2], 'mentor': c[4], 'title': m.get('title'), 'trick': m.get('trick'),
                    'signals': m.get('signals'), 'example': ex, 'practice': items})
    n = sum(len(x['practice']) + 1 for x in chs)
    json.dump({'meta': {'version': 'handbook_v1', 'model': MODEL, 'license': 'original (LLM-generated, independently re-solved)',
                        'chapters': len(chs), 'items': n, 'key_mismatch_regenerated': st['log']['mismatch'], 'regen_total': st['log']['regen']},
               'chapters': chs}, open(OUTF, 'w'), ensure_ascii=False, indent=1)
    print('built', len(chs), 'chapters', n, 'items', st['log'], flush=True)

if __name__ == '__main__':
    main()
