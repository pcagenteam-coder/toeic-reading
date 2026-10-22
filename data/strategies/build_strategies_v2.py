# -*- coding: utf-8 -*-
"""统一技巧库 v2 构建脚本（工作包 A5）。

输入：data/strategies/strategy_library_v1.json（82 条）+ strategy_additions_v1_1.md（SL11-01～16 + 2 条升级，内容在下方 NEW 表里转述）
      data/graph_v1.json（节点校验与考频）；private_data/strategies/*（若存在，仅用于“是否照抄”检查，不读入任何文本）
输出：data/strategies/strategies_v2.json
用法：python3 data/strategies/build_strategies_v2.py      （重跑即重建并校验；校验失败退出码 1）

公开版文本规则：title_zh / plain_zh / detail_zh 均为本项目自写的中文转述；不得照抄原始抓取。
“照抄检查”：与 private_data/strategies 原始文本的最长公共子串若含 ≥12 个连续汉字即判失败。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
V1 = json.load(open(P('data/strategies/strategy_library_v1.json'), encoding='utf-8'))
G = json.load(open(P('data/graph_v1.json'), encoding='utf-8'))
NODES = {n['id']: n for n in G['nodes']}
OLD = {e['id']: e for e in V1['entries']}

BANDS = ['≤500', '600', '730', '860+']
BMAP = {'A': '≤500', 'B': '600', 'C': '730', 'D': '860+'}
CONS = {'高': 1.0, '中': 0.6, '个人经验': 0.3, '个人': 0.3}


def b(s):
    return [BMAP[c] for c in s]


# ---------------------------------------------------------------------------
# v1.1 新增条目（转述自 strategy_additions_v1_1.md；来源 URL 保留供追溯，文本不含原文）
NEW = {
    'SL11-01': dict(title='考前定好弃题预算', consensus='高', parts=[5, 6, 7], nodes=['ST.GIVEUP.TARGET_BASED'],
                    src=['https://fumi-eigo.com/toeic-skip-question/', 'http://toiguide.jp/reading-abandon/', 'https://eigonotomo.com/toeic/toeic-lr_reading']),
    'SL11-02': dict(title='P7 终点线', consensus='高', parts=[7], nodes=['ST.GIVEUP.TARGET_BASED', 'ST.ORDER.WITHIN_P7', 'TX.MULTI', 'TX.DOUBLE', 'TX.TRIPLE'],
                    src=['http://toiguide.jp/reading-abandon/', 'https://m.blog.naver.com/siwonschoollab/221907410585', 'https://fumi-eigo.com/toeic-skip-question/']),
    'SL11-03': dict(title='低分档 P5+P6 放慢做对', consensus='高', parts=[5, 6], nodes=['ST.TIME.TOTAL_PLAN', 'ST.TIME.PER_ITEM_P5'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading', 'http://toiguide.jp/reading-abandon/', 'https://note.com/arkaive/n/nd0e52dba8676', 'https://mikan.com/eigo-note/toeic-part5-guide']),
    'SL11-04': dict(title='P7 每题时间按档定', consensus='个人', parts=[7], nodes=['ST.TIME.PER_SET_P7'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading']),
    'SL11-05': dict(title='各 Part 做对多少就够', consensus='中', parts=[5, 6, 7], nodes=['ST.GIVEUP.TARGET_BASED', 'ST.REVIEW.DIAGNOSE_BY_TYPE'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading', 'https://m.blog.naver.com/siwonschoollab/221907410585']),
    'SL11-06': dict(title='词汇题一眼不会就涂', consensus='中', parts=[5, 6], nodes=['QT.P5.VOCAB', 'QT.P6.CTX_VOCAB', 'ST.GIVEUP.CUTOFF_RULE'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading', 'http://toiguide.jp/reading-abandon/']),
    'SL11-07': dict(title='P5 读三遍止损', consensus='中', parts=[5], nodes=['ST.GIVEUP.CUTOFF_RULE', 'ST.TIME.PER_ITEM_P5'],
                    src=['http://toiguide.jp/reading-abandon/', 'https://www.youtube.com/watch?v=paE50R6hog8']),
    'SL11-08': dict(title='600 档语法只练两样', consensus='中', parts=[5, 6],
                    nodes=['QT.P5.WORD_FORM', 'QT.P5.CONNECTOR_MIX', 'GR.POS', 'GR.CONN.PREP_VS_CONJ', 'ST.REVIEW.DIAGNOSE_BY_TYPE'],
                    src=['https://m.blog.naver.com/siwonschoollab/221907410585', 'data/strategies/exam_pattern_stats.md（本项目考频合成表）']),
    'SL11-09': dict(title='低分档 P6 插入句直接涂', consensus='高', parts=[6], nodes=['QT.P6.INSERTION', 'ST.GIVEUP.TARGET_BASED'],
                    src=['https://m.blog.naver.com/siwonschoollab/221907410585', 'https://eigonotomo.com/toeic/toeic-lr_reading', 'http://toiguide.jp/reading-abandon/']),
    'SL11-10': dict(title='读不完的篇只答第一题', consensus='个人', parts=[7], nodes=['QT.P7.MAIN_PURPOSE', 'ST.GIVEUP.TARGET_BASED'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading']),
    'SL11-11': dict(title='按文体挑篇（跳篇不跳序）', consensus='高', parts=[7],
                    nodes=['ST.GIVEUP.TARGET_BASED', 'TX.TEXT_MSG', 'TX.CHAT', 'TX.NOTICE', 'TX.FORM', 'TX.AD', 'TX.ARTICLE'],
                    suggested='ST.ORDER.TEXT_TYPE_TRIAGE',
                    src=['https://fumi-eigo.com/toeic-skip-question/', 'https://eigonotomo.com/toeic/toeic-lr_reading', 'https://www.haradaeigo.com/studyhack/column/toeic3-guessing-strategy-time-shortage/']),
    'SL11-12': dict(title='多篇只拿一篇能答的题', consensus='中', parts=[7], nodes=['TX.MULTI', 'ST.GIVEUP.TARGET_BASED'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading', 'http://toiguide.jp/reading-abandon/']),
    'SL11-13': dict(title='残局先做词义题', consensus='中', parts=[7], nodes=['QT.P7.SYNONYM', 'ST.ORDER.HARD_ITEMS_LAST', 'ST.BUBBLE.FINAL_MINUTES'],
                    src=['http://toiguide.jp/reading-abandon/', 'https://f0ghua.github.io/toeic_experience/']),
    'SL11-14': dict(title='按篇长分配速度', consensus='中', parts=[7], nodes=['ST.TIME.PER_SET_P7', 'ST.LOCATE.QUESTION_ORDER'],
                    src=['https://hackers.ac/community/secret-method/218892', 'https://academy.kirihara.co.jp/blog/toeic/toeic-part7-reading-comprehension-guide/']),
    'SL11-15': dict(title='记“改写对”', consensus='中', parts=[7], nodes=['ST.REVIEW.VOCAB_FROM_ITEMS', 'ST.LOCATE.PARAPHRASE_MATCH', 'VO.PARA'],
                    suggested='ST.REVIEW.PARAPHRASE_LOG',
                    src=['https://hackers.ac/community/secret-method/218892', 'https://aimpass.org/free-tools/toeic-resources']),
    'SL11-16': dict(title='跳过也先涂', consensus='高', parts=[5, 6, 7], nodes=['ST.BUBBLE.FINAL_MINUTES', 'ST.GIVEUP.NO_BLANK'],
                    src=['https://eigonotomo.com/toeic/toeic-lr_reading', 'https://fumi-eigo.com/toeic-skip-question/', 'https://www.haradaeigo.com/studyhack/column/toeic3-guessing-strategy-time-shortage/']),
    'N5': dict(title='剩余题统一涂一个字母', consensus='高', parts=[5, 6, 7], nodes=['ST.GIVEUP.NO_BLANK', 'ST.BUBBLE.FINAL_MINUTES'],
               src=['https://fumi-eigo.com/toeic-skip-question/', 'https://www.haradaeigo.com/studyhack/column/toeic3-guessing-strategy-time-shortage/', 'https://eigonotomo.com/toeic/toeic-lr_reading']),
}

# ---------------------------------------------------------------------------
# v2 条目规格。字段：g 组；old 合并来源（第一个为主条）；ti 标题（None=沿用 v1）；pl 一句话大白话；
# de 详细说明（None=沿用 v1 rule_zh）；bd 适用档；ms 最小集档；roi 1–3；st own/paraphrase；cf 冲突编号；nt 备注
S = []


ENGINE = {'SL-P5-22', 'SL-P6-10', 'SL11-15', 'SL-ALL-03', 'SL11-05', 'SL-ALL-12', 'SL-ALL-18', 'SL-ALL-19'}  # 由 App 引擎/计时器/自动卡片执行


def E(g, old, pl, bd, ms, roi, ti=None, de=None, st='paraphrase', cf=(), nt='', parts=None, extra=()):
    S.append(dict(g=g, old=old if isinstance(old, list) else [old], ti=ti, pl=pl, de=de, bd=b(bd), ms=b(ms), roi=roi,
                  st=st, cf=list(cf), nt=nt, parts=parts, extra=list(extra)))


# ---- P5 ----
E('P5', 'SL-P5-01', '先扫一眼四个选项，看出是考语法还是考词义，再决定这句读多少。', 'ABCD', 'ABCD', 1)
E('P5', 'SL-P5-02', '四个选项只是词尾不同，就只看空格前后两三个词定词性，别读全句。', 'ABCD', 'ABCD', 1)
E('P5', 'SL11-08', '目标 600 以内，语法只练两样：词性放哪儿、介词和连词怎么分；其余语法点先放下。', 'AB', 'AB', 1,
  de='目标总分 600 及以下：P5 语法只练“名/动/形/副该放在哪个位置”和“空格后是名词用介词、是整句用连词”。名词性从句、虚拟语气、比较级、倒装、分词结构等先不学，遇到就按限时规则猜。本项目考频合成表显示比较级约 1–3%、关系词约 0–3%，砍掉它们损失很小。',
  cf=['C8'], nt='韩国来源为单一作者；用本项目 exam_pattern_stats 考频交叉核对后共识升为“中”。')
E('P5', 'SL-P5-20', '不认识的词先看词尾：-tion/-ment 多是名词，-ive/-able 多是形容词，-ly 多是副词。', 'ABCD', 'ABCD', 1)
E('P5', ['SL-P5-21', 'SL11-07'], 'P5 每题有时限：词性约 15 秒、语法约 20 秒、词汇约 30 秒；考场不看表时，同一句读了三遍还没思路就涂、走。', 'ABCD', 'ABCD', 1,
  de='练习时用 App 倒计时：词性题 15 秒、其他语法题 20 秒、词汇题 30 秒为上限，到点就选一个最像的。正式考试不方便每题看表，改用“读三遍”计数：同一句来回读了三遍仍没有头绪，立刻涂一个固定字母，进入下一题。',
  nt='合并：SL11-07 是本条的“计数版”，并入同一条。秒数口径沿用 v1 裁决（按题型分档）。')
E('P5', 'SL11-06', '词汇题四个词都没把握、空格前后也找不到搭配线索，马上涂一个字母走人。', 'ABC', 'ABC', 1,
  de='词汇题靠“认不认识”决定，想不出来就是想不出来。先花几秒看空格后面的介词或名词有没有固定搭配可以排除选项；若没有线索、四个词也都拿不准，立即涂固定字母，把时间留给能靠规则推出来的词性和介连题。',
  cf=['C9'])
E('P5', 'SL-P5-18', '词汇题先看空格和谁搭配（后面的介词、名词），搭不上的先划掉，再看意思。', 'ABCD', 'BCD', 1, cf=['C9'])
E('P5', 'SL-P5-09', '看空格后面：跟名词用介词，跟完整句子用连词，前后两句都完整就用 however 这类副词。', 'ABCD', 'BCD', 1)
E('P5', 'SL-P5-05', '长句先把介词短语、逗号插入语这些枝叶去掉，只看主谓宾。', 'ABCD', 'BCD', 2)
E('P5', 'SL-P5-04', '数一下句子里有几个动词、几个连接词：缺谓语就补动词，不缺就别选能当谓语的形式。', 'BCD', 'D', 2)
E('P5', 'SL-P5-06', '动词题按顺序问四句：要不要当谓语→主动还是被动→什么时态→单数还是复数。', 'BCD', 'CD', 2, cf=['V1-1'])
E('P5', 'SL-P5-10', '介词题先想固定搭配（如 on 加星期、in 加月份），想不起来再按意思选。', 'BCD', 'D', 2)
E('P5', 'SL-P5-11', '代词先看空格位置该用哪种形式（he/him/his/himself），再看指的是一个还是几个。', 'BCD', 'D', 2)
E('P5', 'SL-P5-03', '确定填名词后，再看一眼：指人还是指物、要不要加 s。', 'BCD', 'D', 2)
E('P5', 'SL-P5-19', '熟词别按日常意思选，先想它在公司里的意思（比如 address 是“处理”）。', 'CD', 'D', 2)
E('P5', 'SL-P5-22', '先练考得多的（词汇、词性、介词），比较级、关系词这些冷门的最后补。', 'ABCD', '', 2, st='own',
  de='按本项目考频合成表排学习顺序：P5 词汇（同词性词义）约 30–40%、词性约 20–27%、介词约 11%、动词形态约 10%、代词约 8%、连词约 6%，比较级与关系词各约 1–3%。由排程引擎自动执行，用户无需记。',
  nt='考频口径改为本项目 exam_pattern_stats.md 合成表（取代 v1 的日韩 240 题口径）；引擎规则，不进用户最小集。')
E('P5', 'SL-P5-23', 'P5 已经稳定只错三四题，就别再刷 P5，把时间挪给长阅读。', 'D', 'D', 2)
E('P5', 'SL-P5-12', '关系词问两件事：前面有没有名词、后面的句子缺不缺成分。', 'CD', 'D', 3, cf=['C8'])
E('P5', 'SL-P5-13', '看到 than 选比较级，看到 the…of/in 选最高级，看到 as…as 选原级。', 'CD', 'D', 3, cf=['C8'])
E('P5', 'SL-P5-07', 'to do 还是 -ing 看前面那个词；-ing 还是 -ed 看名词是自己在做还是被做。', 'CD', 'D', 3, cf=['C8'])
E('P5', 'SL-P5-08', '选动词前先看它后面跟的结构，结构对不上的直接排除。', 'CD', 'D', 3)
E('P5', 'SL-P5-15', '先看 each/every/a number of 这类数量词，再决定名词和动词带不带 s。', 'CD', '', 3)
E('P5', 'SL-P5-17', 'already/still/yet、so/such 这类副词按作用选，别按中文意思选。', 'CD', '', 3)
E('P5', 'SL-P5-14', '看到 both/either/neither/whether，去句子里找它的另一半。', 'CD', '', 3, cf=['C8'])
E('P5', 'SL-P5-16', '见到 suggest/request that 或句首 Should/Had，直接套固定格式。', 'D', '', 3)

# ---- P6 ----
E('P6', 'SL-P6-02', 'P6 先分两类：本句就能做的按 P5 方法秒做，要看上下文的再放慢。', 'ABCD', 'ABCD', 1)
E('P6', 'SL11-09', '目标 600 以内：P6 每篇的插入句题不做，直接涂一个字母。', 'AB', 'AB', 1,
  de='目标总分 600 及以下：P6 的句子插入题（每篇 1 题，全卷 4 题）是 P6 最难、最费时的题，直接涂固定字母，每篇可省 30–60 秒，用来把同篇其他 3 题做对。', cf=['C3'])
E('P6', 'SL-P6-01', 'P6 从头顺着读，读到空就填，别只看空格那一句。', 'ABCD', 'CD', 1)
E('P6', 'SL-P6-09', '（730 以上）插入句放到每篇最后做，30 秒没思路就猜一个。', 'CD', 'CD', 2,
  de='目标 730 及以上：句子插入题先跳过，做完本篇另外 3 题再回来；30 秒内看不出衔接线索就涂一个最像的。目标 600 及以下改用“插入句直接涂”。', cf=['C3'])
E('P6', 'SL-P6-03', '时态题几个都说得通时，看信是哪天写的、事情发生了没有。', 'BCD', 'CD', 2)
E('P6', 'SL-P6-05', '先判断前后两句是转折、因果还是补充，再选 however/therefore/in addition。', 'BCD', 'CD', 2)
E('P6', 'SL-P6-06', '词汇题本句都说得通时，回头看整篇在讲什么再选。', 'BCD', 'D', 2)
E('P6', 'SL-P6-07', '插入句看候选句里的 this、they、also，问它接的是前面哪件事。', 'CD', 'CD', 2,
  de='句子插入题：先弄清全文在讲什么、每段往哪走，再看候选句里的指代词、连接词和“新信息/旧信息”，检查它放进空里能否和前后句接上。')
E('P6', 'SL-P6-04', '代词题往前找它到底指谁：一个人、几个人还是一家公司。', 'BCD', '', 3)
E('P6', 'SL-P6-08', '空在开头找开场白，在中间找承上启下的句子，在结尾找“欢迎联系”这类收尾句。', 'CD', '', 3)
E('P6', 'SL-P6-10', 'P6 正确率低于本档目标才开专项，达标就按常规练。', 'ABCD', '', 3, st='own',
  de='是否开 P6 专项，以本档 P6 目标正确率为线（约：≤500/600 档 50%、730 档 60%、860+ 档每篇错不超过 1 题）；低于目标连续两次才安排专项。由诊断引擎判断。',
  cf=['C7'], nt='v1 固定阈值（错误率 >1/3）对 600 档过严，改为按档目标。')

# ---- P7 ----
E('P7', 'SL-P7-01', '先看题目问什么、记住里面的人名和数字，再进文章找。', 'ABCD', 'ABCD', 1, cf=['V1-4'],
  de='先读题干（必要时连选项），判断题型，把人名、日期、数字、动作词记在脑子里，再回原文扫读定位，在定位句前后细读比对。考场题本不能写画，所以是“记住”而不是“划出”。')
E('P7', 'SL-P7-03', '拿题里的人名、数字、日期当路标，找到后只细读前后两句。', 'ABCD', 'ABCD', 1)
E('P7', 'SL-P7-05', '问“为什么写这封信/这则通知”，答案多半在第一段。', 'ABCD', 'ABCD', 1,
  de='主旨/目的题的答案多在开头几句；常见的开场说法如 I am writing to、We are pleased to、Please be advised 后面紧跟的就是目的。')
E('P7', 'SL11-10', '目标 500 左右：读不完的篇只花约一分钟看开头，答第一题，其余涂掉。', 'A', 'A', 1,
  de='目标总分约 500 及以下：时间不够读完整篇时，只读开头约 60 秒，答这篇的第 1 题（多为目的/主旨题，配合“目的题看开头”），其余题涂固定字母。用 1 分钟换约 1 分，比硬啃整篇划算。')
E('P7', 'SL11-11', '单篇里短信、通知、表格、广告这类短的认真做；碰到长篇新闻报道，整篇涂掉往下走。', 'ABC', 'AB', 1,
  de='低中分档按文体决定做不做：短信/群聊、通知、表格/表单、广告篇幅短、好定位，认真做；长篇报道（article）最难，目标 600 及以下遇到就整篇涂固定字母跳过。顺序仍然从前往后，不回头挑（跳篇不跳序）。App 可按个人各文体正确率提示“你的顺手文体”。',
  cf=['C4'])
E('P7', 'SL-P7-04', '正确答案通常换了个说法；跟原文一字不差的选项反而要多看一眼。', 'ABCD', 'BCD', 1)
E('P7', 'SL-P7-08', 'NOT 题和没有关键词的题最费时间，放到这一篇最后做。', 'ABCD', 'BCD', 1)
E('P7', 'SL-P7-10', '推断题也要能指出原文哪句话撑腰，靠常识脑补的不选。', 'BCD', 'CD', 1)
E('P7', 'SL-P7-14', '同义词题把选项代回原句读一遍，通顺的才对，别选这个词最常见的意思。', 'ABCD', 'BCD', 1)
E('P7', 'SL-P7-15', '先认出是邮件、广告还是通知，再去这类文件通常放答案的位置找。', 'ABCD', 'BCD', 1)
E('P7', 'SL-P7-20', '读到生词先跳过，靠前后文猜个大概，读完再查。', 'ABCD', 'BCD', 1)
E('P7', 'SL11-15', '每篇做完记一组“原文说法↔答案说法”，做对的题也记（App 自动弹卡，点“记住了”即可）。', 'ABCD', '', 2,
  de='复盘时把“原文证据句”和“正确选项”之间的换说法记成一对（例：free of charge ↔ complimentary），做对的题也要记。App 在答题后自动生成 1 张改写对卡片，用户只需确认，直接服务“答案通常换了说法”这条。')
E('P7', 'SL-P7-02', '题目顺序基本跟文章顺序一致：一次拿两道题进文，顺路找完。', 'BCD', 'CD', 2)
E('P7', 'SL-P7-07', 'NOT 题把四个选项挨个回原文核对，对得上的划掉，剩下的就是答案。', 'BCD', 'CD', 2, cf=['V1-2'],
  de='NOT/TRUE 题：四个选项一个个回原文找对应信息，能找到的排除；NOT 题选找不到（或与原文相反）的那个，TRUE 题选唯一能对上的那个。')
E('P7', 'SL-P7-06', '选项说得太大、太小，或带 always/only 这类绝对词，先打个问号。', 'CD', 'D', 2)
E('P7', 'SL-P7-09', '问“关于 X 哪项正确”，先认准 X 是谁，把文中提到它的地方都找出来再比。', 'CD', 'D', 2)
E('P7', 'SL-P7-11', '细节题读一两句就够，推断题和 NOT 题要读一整段。', 'CD', 'D', 2)
E('P7', 'SL-P7-12', '聊天里带引号那句话是什么意思，先看上一条消息在问什么。', 'BCD', 'CD', 2)
E('P7', 'SL-P7-17', '多篇题先想：条件在哪篇、具体数据在哪篇，两篇对着看。', 'CD', 'CD', 2)
E('P7', 'SL-P7-18', '多篇先看 5 道题各问哪一篇，被问最多的那篇细读。', 'CD', 'D', 2)
E('P7', 'SL11-14', '两三题的短篇做快点，把省下的时间留给四五题的长篇。', 'CD', '', 2,
  de='P7 按每篇题数分配速度：2–3 题的短篇压缩用时，把时间留给 4–5 题的长篇；长篇先读前两题再进文（与“两题一组”一致）。')
E('P7', 'SL-P7-24', '先认熟题目里反复出现的词和职位名，读题会快很多。', 'ABC', '', 2)
E('P7', 'SL-P7-13', '先读要插进去的那句，猜它前面该讲过什么，再去 [1]–[4] 对。', 'CD', 'D', 3)
E('P7', 'SL-P7-16', '邮件留意附件和人的职位，广告留意最后一句的优惠和购买方式。', 'BCD', '', 3,
  de='按文体记几个常考点：邮件/信件常问附件（enclosed、attached）、收发件人的职位（常被换说法）、FYI 等缩写；广告和表格的最后一句常给申请/购买方法或最大的优惠。')
E('P7', 'SL-P7-22', '看到 although、unless、note that，后面那句重点读，常是考点。', 'D', 'D', 3,
  de='冲高分提速：although/while/unless 之后的转折信息、who 从句里的谓语、whoever/whatever 结构要读准；announce、ensure、note that 后面的内容经常被出成题。')
E('P7', 'SL-P7-19', '按意群一块一块往前读，不回头、不逐词翻译。', 'BCD', '', 3)
E('P7', 'SL-P7-21', '同一篇限时读三遍，每遍时间更短。', 'BCD', '', 3)
E('P7', 'SL-P7-23', '刚起步时先看中文提要再读英文，先找回能读下去的感觉。', 'AB', '', 3)

# ---- ALL（整卷：配速 / 放弃 / 涂卡 / 复盘 / 考场） ----
E('ALL', ['SL-ALL-08', 'SL11-01'], '考前按目标定好放弃几题：≤500 档 30 题以上、600 档 20–30 题、730 档 10–15 题、860+ 档 5 题以内，没做完是计划内的。', 'ABCD', 'ABCD', 1, st='own',
  ti='考前定好弃题预算',
  de='先算阅读目标：总分目标 − 预估听力分。再按目标定可放弃的题数（≤500 档约 30–35 题以上，600 档 20–30 题，730 档 10–15 题，860+ 档不超过 5 题），放弃的优先是难题集中区：P6 插入句、P7 长篇报道、跨篇对照题。考前定好，考场不再犹豫。App 根据诊断正确率自动算出“你只需认真做 A 题”（见 meta.target_table）。',
  cf=['C1', 'C2'], nt='合并：SL11-01 给出各档题数，吸收 SL-ALL-08 的“放弃哪些区域”。题数区间来自两种公开换算口径的综合，非官方。')
E('ALL', 'SL11-02', 'P7 定一条终点线：600 档做完单篇（到 175 题）就停，730 档做完双篇（到 185 题）就停，后面统一涂。', 'ABC', 'ABC', 1,
  de='按目标设 P7 终点线：≤500/600 档做到第 175 题（单篇做完）为止，730 档做到第 185 题（双篇做完）为止，终点线之后统一涂固定字母；若到线时还剩 ≥5 分钟，再用“多篇捡分”规则。860+ 档不设终点线。',
  cf=['C2'])
E('ALL', 'SL11-03', '目标 600 以内：P5+P6 可以花 25–30 分钟慢慢做对，P7 本来就不必做完。', 'AB', 'AB', 1,
  de='目标总分 600 及以下：P5 约 15 分钟（每题约 30 秒）+ P6 约 10–15 分钟。这一档 P7 按终点线本来就做不完，P5/P6 每多花一分钟换来的分更多（ETS 试测 P5 正确率约 .67，多篇约 .42–.45）。',
  cf=['C1'])
E('ALL', 'SL-ALL-01', '（目标 730 左右）P5+P6 合计 20 分钟内做完，剩下的全给 P7。', 'C', 'C', 1, cf=['C1', 'V1-3'],
  de='目标 730 档：P5 约 10–12 分钟、P6 约 8–10 分钟，合计不超过 20 分钟，P7 留 53–55 分钟；开考约 20 分钟时应翻到第 147 题。600 及以下档改用“P5+P6 放慢”，860+ 档改用“高分档加速配速”。',
  nt='适用档从 <600/600-800 收窄为 730（additions §2 升级 + C1 裁决）。')
E('ALL', 'SL-ALL-02', '冲 860 以上：P5+P6 压到 15–18 分钟，三篇每组留 6–7 分钟。', 'D', 'D', 1, cf=['C1', 'V1-3'])
E('ALL', ['SL-ALL-05', 'N5'], '答错不扣分，任何题都别空着；来不及的统一涂同一个字母（选哪个字母都一样，不是 C 更容易对）。', 'ABCD', 'ABCD', 1, st='own',
  de='TOEIC 答错不扣分，空着就是白扔分。来不及做的题统一涂同一个字母：正确答案的字母分布基本均衡，统一涂并不会提高期望（约 25%），好处是不用做决定、不易涂串；“C 最容易对”是没有依据的说法，App 不这样宣传。',
  nt='合并 github_inventory N5（共识 个人→高，additions §2 升级）。')
E('ALL', ['SL-ALL-11', 'SL11-16'], '跳过的题当场先涂一个固定字母再走；最后 5 分钟不管做到哪，先把空格全部涂满。', 'ABCD', 'ABCD', 1, st='own',
  ti='跳过先涂、最后 5 分钟涂满',
  de='纸笔考试：做完一段（或每个 Part）集中涂一次卡；任何跳过的题都先涂固定字母再往下走，因为题本不能做记号，“回头再做”在实战中很少真的发生。倒计时 5 分钟时停下，先把所有空格涂满，再做别的。',
  cf=['C5', 'C6'], nt='合并：SL11-16 细化 SL-ALL-11 的涂卡节奏。')
E('ALL', 'SL-ALL-06', '一题卡住超过时限，就涂一个最像的往下走，别指望回头。', 'ABCD', 'CD', 1, cf=['C5'],
  de='每题设放弃线：P5 约 30 秒（考场用“读三遍”），P7 约等于本档每题预算（≤600 档约 90 秒，730+ 约 60 秒）。超线先涂一个最像的，继续往下；有富余时间再回看只是额外收获，不作计划。')
E('ALL', 'SL11-13', '最后几分钟先把空全涂满，再用剩下的时间做“意思最接近”的词义题。', 'ABCD', 'BCD', 1,
  de='残局优先级：倒计时约 5 分钟时，先用约 1 分钟把所有空格涂满；剩下的时间跳过 NOT 题和跨篇题，专挑“与××意思最接近”的词义题（只读该词所在句前后），每题约 15–20 秒，答出来就改涂。',
  cf=['C6'])
E('ALL', 'SL11-05', '每个 Part 做对多少就够：600 档 P5 约三分之二、P6 约一半；730 档 P5 八成、P6 六成；860+ 档 P5 九成、P6 每篇最多错一题。', 'ABCD', '', 1,
  de='分档正确率目标（经验值，非官方）：≤500 档 P5 约一半、P6 约一半、P7 单篇约三分之二（只做到终点线）；600 档 P5 约 2/3、P6 约 1/2、P7 单篇约 2/3；730 档 P5 约 80%、P6 约 60%；860+ 档 P5 约 90%、P6 每篇错不超过 1 题。达到就够，不在 P5 上追满分。',
  cf=['C7'])
E('ALL', 'SL-ALL-25', '题本上不能写画、没有草稿纸，听力时间不能偷做阅读；平时练习就别在题上写字。', 'ABCD', 'ABCD', 1)
E('ALL', 'SL-ALL-16', '考前至少做一次 75 分钟整套限时模考，把弃题计划演练一遍，第二天专门复盘。', 'ABCD', 'BCD', 1)
E('ALL', 'SL-ALL-09', '按 P5→P6→P7 顺序做，P7 里也从前往后，跳过的篇不回头挑。', 'ABCD', '', 2, cf=['C4'],
  de='默认按 P5→P6→P7 顺序作答，不先跳去做多篇；P7 内部也从前往后，碰到要放弃的篇就涂完往下走（跳篇不跳序）。要预期 P7 篇型顺序可能被打乱。')
E('ALL', ['SL-ALL-03', 'SL11-04'], 'P7 每题时间按档：600 以内约 90 秒一题，730 以上约 60 秒；冲 860+ 时单篇控制在 25–30 分钟，多篇留 25 分钟以上。', 'ABCD', '', 2,
  ti='P7 按档配时',
  de='P7 时间预算按档定：≤500/600 档按每题约 90 秒算（2 题一篇约 3 分钟、3 题一篇约 4.5 分钟）；730 档以上按每题约 60 秒。860+ 档全做：单篇（147–175）不超过 25–30 分钟，多篇（176–200）至少 25 分钟、三篇每组约 6–7 分钟。由 App 计时器提示。',
  cf=['C2', 'C5'], nt='合并：SL11-04 的分档每题预算 + SL-ALL-03 的分段配时（后者仅 860+ 适用，见 C2）。')
E('ALL', ['SL-ALL-07', 'SL11-12'], '多篇做不完时，每组只挑词义题和只问其中一篇的细节题，跨篇对照题直接涂。', 'ABC', 'BC', 2,
  ti='多篇只捡好拿的分',
  de='多篇（双篇/三篇）时间不够或已过终点线但还剩 ≥5 分钟：每组扫一遍 5 道题干，只做两类——词义题、只问其中一篇细节的题（2–3 道），需要几篇对照的题直接涂固定字母。',
  nt='合并：SL11-12（只做一篇能答的题）与 SL-ALL-07（做三蒙二）是同一做法。')
E('ALL', 'SL-ALL-04', '别每篇都看表，只在 P6 开头、147 题、176 题这几个点看一下，落后就启用放弃线。', 'CD', 'CD', 2)
E('ALL', 'SL-ALL-10', '（冲 860+）P7 全做：多篇组里先做单篇就能答的题，跨篇题放组内最后，但别把多篇整块留到最后。', 'D', 'D', 2, cf=['C2'],
  de='目标 860+ 档不设终点线：P7 内先拿把握大的题；多篇组里先做单文档就能答的题，跨篇题组内最后做；但不要把整块多篇留到最后。730 及以下档改用“P7 终点线”。')
E('ALL', 'SL-ALL-24', '冲高分先在原文找到支持答案的证据再选，划掉法只用于二选一纠结时（NOT 题仍逐项核对）。', 'D', 'D', 2, cf=['V1-2'])
E('ALL', 'SL-ALL-13', '每道错题标一个原因：词不认识、语法、没找到、超时、没认出换了说法。', 'BCD', 'D', 2)
E('ALL', 'SL-ALL-15', '错误选项就那几种：没提到、只对一半、张冠李戴、脑补过头、照抄原词、因果反了。', 'BCD', 'CD', 2)
E('ALL', 'SL-ALL-18', '生词只从做过的题里挑，每篇挑两三个放进词卡。', 'ABCD', '', 2, cf=['V1-5'])
E('ALL', 'SL-ALL-19', '只背自己目标档的词，提分了再往上加。', 'ABCD', '', 2)
E('ALL', 'SL-ALL-20', '背词就背短语（如 meet the deadline），别背单个词。', 'BCD', 'D', 2)
E('ALL', 'SL-ALL-12', '看按题型的正确率，哪类错得多就练哪类（App 自动统计）。', 'ABCD', '', 2)
E('ALL', 'SL-ALL-14', '复盘时四个选项都要能说出对或错的理由。', 'CD', '', 3)
E('ALL', 'SL-ALL-17', '做完的题听一遍音频、跟着读一遍。', 'CD', '', 3)
E('ALL', 'SL-ALL-21', '一篇里不认识的词超过 5 个，先回去补词再做模考。', 'AB', '', 3)
E('ALL', 'SL-ALL-22', '冲 860+ 要找比官方题集更难的 P7 来练。', 'D', '', 3)
E('ALL', 'SL-ALL-23', '两次模考分数差 35 分以内多半是正常波动，别据此大改计划。', 'ABCD', '', 3)

# ---------------------------------------------------------------------------
CONFLICTS = [
    dict(id='C1', topic='P5+P6 总用时', rules=['SL-ALL-01', 'SL11-03', 'SL-ALL-02'],
         adopted='按档分：≤500/600 用 25–30 分钟（SL11-03）；730 用 ≤20 分钟（SL-ALL-01）；860+ 用 15–18 分钟（SL-ALL-02）',
         why='低分档 P7 按终点线本来做不完，P5/P6 每分钟得分效率更高（ETS 试测 P5 正确率 .67 vs 多篇 .42–.45）；additions §2 已建议 SL-ALL-01 收窄。v2 档位细化后 600 也归入放慢档（日方出版社 600 档即 15+10～15 分钟）。'),
    dict(id='C2', topic='P7 是否做完 / 多篇怎么安排', rules=['SL11-02', 'SL-ALL-10', 'SL-ALL-03'],
         adopted='≤500/600/730 用终点线（600 停 175 题、730 停 185 题）；SL-ALL-10“多篇不整块留后”与 SL-ALL-03 分段配时只适用 860+',
         why='目标用户时间少、读得慢，终点线把“做不完”变成计划内；只有冲高分的人才需要全做完 P7。'),
    dict(id='C3', topic='P6 插入句', rules=['SL11-09', 'SL-P6-09'],
         adopted='≤500/600 直接涂（SL11-09）；730+ 最后做、30 秒没思路就猜（SL-P6-09）',
         why='插入句是 P6 最难题，低分档做它的期望收益低于把同篇其他 3 题做对；三家独立来源一致。'),
    dict(id='C4', topic='按顺序做 vs 按文体挑篇', rules=['SL-ALL-09', 'SL11-16', 'SL11-11'],
         adopted='跳篇不跳序：仍从前往后，遇到长篇报道（低分档）整篇涂掉往下走，不回头挑',
         why='纸笔考题本不能做记号，回头找篇易漏涂、串行；保留 SL11-11 的“按文体决定做不做”，去掉“挑着做”的乱序部分。倒序先做多篇维持 v1/v1.1 不采纳。'),
    dict(id='C5', topic='卡住后“先跳后回、标记”', rules=['SL-ALL-06', 'SL11-16', 'SL11-04'],
         adopted='采纳 SL11-16：跳过时当场先涂固定字母，回头只是富余时间的额外收获；P7 卡题线改为本档每题预算（≤600 档 90 秒）',
         why='题本禁止标记（v1 EXC-02/03），实战中“回头”很少发生，先涂可防漏涂；P7 1 分钟一刀切对低分档过紧。'),
    dict(id='C6', topic='最后 5 分钟：先涂满还是先捡同义词题', rules=['SL-ALL-11', 'SL11-16', 'SL11-13'],
         adopted='先用约 1 分钟全部涂满，再用剩余时间做词义题并改涂',
         why='涂满是保底分、错过就无法挽回；词义题是加分项，顺序颠倒的风险不对称。'),
    dict(id='C7', topic='P6 专项触发线', rules=['SL-P6-10', 'SL11-05'],
         adopted='按档目标正确率触发（600 档约 50%、730 档约 60%、860+ 每篇错 ≤1）',
         why='v1 固定“错误率 >1/3”会让 600 档用户（目标本就只要一半）被错误地推去 P6 专项，浪费时间。'),
    dict(id='C8', topic='低分档语法范围', rules=['SL11-08', 'SL-P5-13', 'SL-P5-14', 'SL-P5-12', 'SL-P5-07'],
         adopted='采纳 SL11-08：600 及以下只练词性位置 + 介/连；比较级、成对连词、关系词、非谓语移到 730+',
         why='本项目考频合成表：比较级约 1–3%、关系词约 0–3%；砍掉它们最省学习量，契合“不擅长语法”的用户。'),
    dict(id='C9', topic='词汇题：找搭配 vs 一眼不会就涂', rules=['SL-P5-18', 'SL11-06'],
         adopted='先几秒找搭配线索，有就用来排除；无线索且四词都没把握 → 立刻涂（≤730）',
         why='两条不矛盾但顺序要定；词汇题不会时硬想几乎无收益，时间应留给可推理的语法题。'),
]
CARRIED = [
    dict(id='V1-1', topic='动词题排查顺序', rules=['SL-P5-06'], adopted='谓语→主被动→时态→单复数（沿用 v1）', why='先排除非谓语选项最省时。'),
    dict(id='V1-2', topic='排除法 vs 正向确认', rules=['SL-P7-07', 'SL-ALL-24'], adopted='NOT/TRUE 题逐项核对；860+ 其余题先找证据再选（沿用 v1，按题型/档）', why='NOT 题本质就是逐项核对。'),
    dict(id='V1-3', topic='整卷配速口径', rules=['SL-ALL-01', 'SL-ALL-02'], adopted='按档取舍（v2 并入 C1）', why='见 C1。'),
    dict(id='V1-4', topic='先题后文 vs 先文后题', rules=['SL-P7-01'], adopted='先题后文（沿用 v1，提及 23 次、共识高）', why='定位效率高，适合读得慢的人。'),
    dict(id='V1-5', topic='要不要专门背单词', rules=['SL-ALL-18', 'SL-ALL-19'], adopted='分档词包打底 + 从题里摘，两者并用（沿用 v1）', why='兼顾“不擅长背词”与考分必需词。'),
]

TARGET_TABLE = {
    'note': '阅读量表分与答对数无官方固定换算（ETS 按卷等化）。区间综合两种公开近似口径（约“答对 N 题≈5N−5 分”与日方经验表），仅作规划参考。认真做 A 题、其余统一涂一个字母时：答对 ≈ A×正确率 + (100−A)×0.25。阅读目标 = 总分目标 − 预估听力分。',
    'rows': [
        dict(reading=200, need_correct='41–55', do_at_70='36–67', do_at_80='29–55', do_at_90='25–46', can_skip='30–35 题以上', total_band='≤500'),
        dict(reading=250, need_correct='51–61', do_at_70='58–80', do_at_80='47–65', do_at_90='40–55', can_skip='20–30 题', total_band='600'),
        dict(reading=300, need_correct='61–67', do_at_70='80–93', do_at_80='65–76', do_at_90='55–65', can_skip='15–25 题', total_band='600–730'),
        dict(reading=350, need_correct='71–74', do_at_70='全做', do_at_80='84–89', do_at_90='71–75', can_skip='10–15 题', total_band='730'),
        dict(reading=400, need_correct='81–85', do_at_70='全做', do_at_80='全做', do_at_90='86–92', can_skip='≤5 题', total_band='860+'),
    ],
}


def cat(ns):
    out = {'qtype_nodes': [], 'texttype_nodes': [], 'strategy_nodes': [], 'skill_nodes': []}
    for n in ns:
        k = 'qtype_nodes' if n.startswith('QT.') else 'texttype_nodes' if n.startswith('TX.') else 'strategy_nodes' if n.startswith('ST.') else 'skill_nodes'
        if n not in out[k]:
            out[k].append(n)
    return out


def freq(c):
    leaf = [NODES[n]['exam_weight'] for n in c['qtype_nodes'] + c['strategy_nodes'] if n in NODES]
    if not leaf:
        leaf = [NODES[n]['exam_weight'] for n in c['skill_nodes'] + c['texttype_nodes'] if n in NODES]
    return min(1.0, (max(leaf) if leaf else 0) / 0.6)


def build():
    errs = []
    entries, seen_old, cnt = [], [], {}
    for s in S:
        cnt[s['g']] = cnt.get(s['g'], 0) + 1
        nid = 'S2-%s-%02d' % (s['g'], cnt[s['g']])
        olds = s['old']
        srcs, nodes, parts, cons, ment, pm, mm, notes, sugg, fmt = [], [], set(), 0.0, 0, True, True, [], None, 'universal'
        weights = []
        for o in olds:
            seen_old.append(o)
            if o in OLD:
                e = OLD[o]
                srcs += e['sources']; nodes += e['qtype_nodes'] + e['texttype_nodes'] + e['strategy_nodes'] + e['skill_nodes']
                parts |= set(e['parts']); cons = max(cons, CONS[e['consensus']]); ment += e['mention_count']
                pm = pm and e['practice_mode']; mm = mm and e['mock_mode']; weights.append(e['weight'])
                if e['format_version'] == 'current':
                    fmt = 'current'
                if e.get('suggested_new_node'):
                    sugg = e['suggested_new_node']
            elif o in NEW:
                e = NEW[o]
                srcs += e['src']; nodes += e['nodes']; parts |= set(e['parts']); cons = max(cons, CONS[e['consensus']])
                ment += len(e['src']); sugg = e.get('suggested') or sugg
            else:
                errs.append('unknown old id %s' % o)
        main = olds[0]
        if main == 'SL11-08':
            cons = max(cons, CONS['中'])
        title = s['ti'] or (OLD[main]['title_zh'] if main in OLD else NEW[main]['title'])
        detail = s['de'] or (OLD[main]['rule_zh'] if main in OLD else None)
        if not detail:
            errs.append('%s no detail' % nid)
        c = cat(nodes + s['extra'])
        for n in sum(c.values(), []):
            if n not in NODES:
                errs.append('%s bad node %s' % (nid, n))
        if len(olds) == 1 and main in OLD:
            w = OLD[main]['weight']; wb = 'v1 weight 沿用'
        else:
            f = freq(c); w = round(0.5 * f + 0.3 * cons + 0.2 * min(1, ment / 15), 2)
            wb = '0.5×考频(%.2f)+0.3×共识(%.1f)+0.2×提及(min(1,%d/15))' % (f, cons, ment)
        if not set(s['ms']) <= set(s['bd']):
            errs.append('%s min_set not subset of bands' % nid)
        cons_lbl = {1.0: '高', 0.6: '中', 0.3: '个人'}[cons]
        qlabels = [NODES[n]['name_zh'] for n in c['qtype_nodes'] if n in NODES and NODES[n]['layer'] == 'qtype']
        entries.append(dict(
            id=nid, title_zh=title, plain_zh=s['pl'], detail_zh=detail,
            parts=sorted(s['parts'] or parts), qtype_labels=qlabels[:6],
            bands=s['bd'], min_set_bands=s['ms'], roi=s['roi'],
            graph_nodes=sum(c.values(), []), **c,
            source_type=s['st'], source_refs=sorted(set(srcs)), consensus=cons_lbl,
            old_ids=olds, conflicts=s['cf'], note=s['nt'],
            delivery='engine' if main in ENGINE else 'user',
            practice_mode=pm, mock_mode=mm, format_version=fmt,
            weight=w, weight_basis=wb, suggested_new_node=sugg,
            work_rule_v1=OLD[main]['work_rule'] if main in OLD else None,
        ))
    # 覆盖校验：82 条 v1 + 16 条 v1.1 + N5 全部映射且只映射一次
    expect = set(OLD) | set(NEW)
    dup = {x for x in seen_old if seen_old.count(x) > 1}
    if dup:
        errs.append('old ids mapped twice: %s' % sorted(dup))
    miss = expect - set(seen_old)
    if miss:
        errs.append('old ids not mapped: %s' % sorted(miss))
    for c in CONFLICTS + CARRIED:
        for r in c['rules']:
            if r not in expect:
                errs.append('conflict %s bad rule %s' % (c['id'], r))
    cf_ids = {c['id'] for c in CONFLICTS + CARRIED}
    for e in entries:
        for x in e['conflicts']:
            if x not in cf_ids:
                errs.append('%s bad conflict ref %s' % (e['id'], x))
    # 照抄检查
    raw = ''
    pdir = P('private_data', 'strategies')
    if os.path.isdir(pdir):
        for fn in sorted(os.listdir(pdir)):
            raw += open(os.path.join(pdir, fn), encoding='utf-8', errors='ignore').read()
    copy_hits = []
    if raw:
        for e in entries:
            for f in ('title_zh', 'plain_zh', 'detail_zh'):
                t = e[f]
                for m in re.finditer(r'[\u4e00-\u9fff，、；：（）]{12,}', t):
                    seg = m.group(0)
                    for i in range(len(seg) - 11):
                        if re.sub(r'[，、；：（）]', '', seg[i:i + 12]).__len__() >= 12 and seg[i:i + 12] in raw:
                            copy_hits.append((e['id'], f, seg[i:i + 12])); break
    if copy_hits:
        errs.append('copy check failed: %s' % copy_hits[:5])
    min_sets = {bd: [e['id'] for e in sorted(entries, key=lambda x: (x['roi'], -x['weight'])) if bd in e['min_set_bands']] for bd in BANDS}
    from collections import Counter
    out = dict(
        meta=dict(version='2.0', built='2026-10-22', builder='data/strategies/build_strategies_v2.py',
                  inputs=['data/strategies/strategy_library_v1.json (82)', 'data/strategies/strategy_additions_v1_1.md (SL11-01～16 + 升级 N5、SL-ALL-01)', 'data/graph_v1.json'],
                  exam_format=V1['meta']['exam_format'],
                  target_user='35–40 岁为主、工作家庭忙、四六级基础但多年未考、不擅长背词和语法；只教考分必需的最小集合，按 ROI 排序',
                  fields=dict(
                      id='S2-<组>-<序号>，v2.0 起固定，不随重建变化（新增条目接在组尾）',
                      plain_zh='一句话大白话（App“工作规则卡”主行）', detail_zh='展开说明（自写转述）',
                      bands='适用的目标总分档（≤500/600/730/860+）；带“（730 以上）”等字样的是档专属条目，其余为该档起累积适用',
                      min_set_bands='该条进入哪些档的“最小技巧集”（用户必须主动会用的最少规则，各档独立列出，低档放弃类规则在高档会退出）；空=引擎执行或选学',
                      delivery='user=用户需要记住并执行；engine=由 App 排程/计时器/自动卡片执行，不要求用户记',
                      roi='1=几乎零成本当场多拿分；2=需少量练习；3=投入较多或收益小',
                      graph_nodes='graph_v1 节点 id（已校验存在），另按层拆成 qtype/texttype/strategy/skill_nodes',
                      source_type='own=本项目自有数据/推算/产品裁决为主；paraphrase=转述外部来源（文本均为自写，不含原文）',
                      old_ids='v1 SL-* / v1.1 SL11-* / github_inventory N5', conflicts='冲突裁决编号，见 conflicts[]',
                      weight='0–1 价值权重，单条沿用 v1，合并/新增按 v1 公式重算（0.5×考频+0.3×共识+0.2×提及）',
                      work_rule_v1='v1 的职场比喻版工作规则，保留供 B2 职场外壳选用'),
                  bands=BANDS, target_table=TARGET_TABLE, public_text_policy='所有中文文本为自主转述；build 时与私有原始抓取做 ≥12 连续汉字的照抄检查'),
        entries=entries, conflicts=CONFLICTS, carried_conflicts=CARRIED,
        deprecated=V1['deprecated'], excluded=V1['excluded'],
        not_adopted=[
            dict(rule='倒序先做多篇', reason='对低精力用户风险大；v1 已列为 SL-ALL-09 反例'),
            dict(rule='用粗芯涂卡笔省时间', reason='考场用品建议，不是可训练技巧；可放“考前须知”'),
            dict(rule='利用考场广播节点安排时间', reason='中国考场是否有同样广播未核实'),
        ],
        min_sets=min_sets,
        stats=dict(n_entries=len(entries), n_v1=len(OLD), n_v11_new=len([k for k in NEW if k.startswith('SL11')]),
                   merged_away=len(seen_old) - len(entries), n_conflicts_new=len(CONFLICTS), n_conflicts_carried=len(CARRIED),
                   by_group=dict(Counter(e['id'].split('-')[1] for e in entries)), by_roi=dict(Counter(e['roi'] for e in entries)),
                   by_source_type=dict(Counter(e['source_type'] for e in entries)),
                   min_set_sizes={k: len(v) for k, v in min_sets.items()}),
        validation=dict(passed=not errs, errors=errs, copy_check='ran' if raw else 'skipped (private_data 不存在)'),
    )
    json.dump(out, open(P('data/strategies/strategies_v2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(out['stats'], ensure_ascii=False))
    print('validation', 'PASS' if not errs else 'FAIL', errs[:10])
    return 0 if not errs else 1


if __name__ == '__main__':
    sys.exit(build())
