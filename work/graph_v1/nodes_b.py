# -*- coding: utf-8 -*-
"""第二部分：词汇层（场景词包 30 + 搭配/易混/同义替换/词汇题/分段 约 50）。"""
from nodes_a import N, P5, P6, P7, P56, P567, P67

L = "vocab"
N("VO", "词汇层", L, None, [], P567, 400,
  "场景词包解决“认识”，搭配/易混/同义替换解决“会用、会辨、会认改写”。P5 词汇题 30–40%（9–12 题）、P6 词汇 5–8 题，P7 同义替换贯穿全部设问。",
  "—", basis="aggregate", src="exam_pattern_stats.json composite")
N("VO.SCENE", "场景词包（按 TSL/BSL 主题聚类）", L, "VO", ["FD.VOC.NGSL_CORE"], P567, 400,
  "以 TSL 1.2（TOEIC 语料）与 BSL 1.20（商务语料）词表为底，按 TOEIC 常见场景人工聚为 30 簇；每簇列种子词并统计在词表中的命中。",
  "—", basis="aggregate")

# (key, name, band, seeds, desc, example, v0)
SCENES = [
 ("OFFICE_ADMIN", "办公行政与文书", 400, "office supply file document copy printer desk form deadline submit approve handle task assign colleague",
  "日常办公、文件流转、审批与分工。", "Please ------- the signed form to the front office. (submit)", []),
 ("MEETING_SCHEDULE", "会议与日程安排", 400, "meeting schedule agenda reschedule postpone appointment attend conference minutes calendar available confirm cancel",
  "约会议、改期、议程与纪要。", "The board meeting has been ------- until Thursday. (postponed)", ["V1"]),
 ("RECRUIT", "招聘与求职", 400, "applicant candidate position resume interview qualify qualification hire recruit opening experience reference apply",
  "招聘广告、简历、面试、录用。", "Candidates must have at least three years of relevant -------. (experience)", ["V2"]),
 ("HR_TRAINING", "人事：培训·晋升·福利·考核", 600, "employee training promote promotion benefit salary performance evaluation retire workshop orientation personnel bonus",
  "入职培训、绩效、晋升、薪酬福利、退休。", "New hires must complete a two-day ------- session. (orientation)", ["V2"]),
 ("PURCHASE_QUOTE", "采购与报价", 400, "purchase quote estimate supplier vendor price discount bulk order cost budget contract invoice",
  "询价、比价、批量折扣、供应商选择。", "Please send us a ------- for 500 units. (quote)", ["V3"]),
 ("ORDER_SHIP", "订单·配送·物流", 400, "order ship shipment deliver delivery package track warehouse freight courier dispatch arrive delay",
  "下单、发货、追踪、延误、配送。", "Your ------- is expected to arrive within five business days. (shipment)", ["V3"]),
 ("INVENTORY_PRODUCTION", "库存·生产·供应链", 600, "inventory stock supply manufacture factory plant production assemble quality capacity component material output",
  "工厂产能、库存、零部件、质检。", "The plant will increase its production ------- next year. (capacity)", []),
 ("MARKETING_AD", "市场推广与广告", 600, "marketing advertise advertisement campaign promote promotion brand launch survey target consumer audience feature",
  "推广活动、品牌、市场调研、新品上市。", "The ------- campaign will target young professionals. (marketing)", []),
 ("SALES_DEAL", "销售·合同·谈判", 600, "sale client customer contract negotiate deal agreement revenue sign term renew offer proposal",
  "销售业绩、客户谈判、合同条款与续约。", "Both parties agreed to the ------- of the contract. (terms)", []),
 ("CUSTOMER_SERVICE", "客服·投诉·退换", 400, "customer complaint refund return exchange warranty repair replace service satisfaction inquiry feedback apologize",
  "投诉处理、退款、保修、换货、道歉。", "Defective items may be ------- within 30 days. (returned)", []),
 ("FINANCE_ACCOUNT", "财务·会计·预算", 600, "finance account accounting budget expense revenue profit audit tax fiscal quarter reimburse report",
  "预算、报销、财报、审计、季度业绩。", "Travel expenses will be ------- upon receipt of the original receipts. (reimbursed)", []),
 ("BANK_PAYMENT", "银行·支付·账单", 400, "bank payment pay bill balance credit card charge fee transfer account deposit due",
  "账单、付款方式、滞纳金、转账。", "Payment is ------- by the end of the month. (due)", []),
 ("CORP_STRATEGY", "企业经营：并购·扩张·业绩", 700, "company firm merger acquire acquisition expand expansion branch headquarters subsidiary executive board shareholder",
  "公司新闻：并购、开新分店、高管变动。", "The firm plans to ------- into Asian markets. (expand)", []),
 ("TECH_IT", "IT 与技术支持", 600, "computer software system network upgrade install update technical device online password access data",
  "系统升级、软件安装、故障与技术支持。", "The system will be unavailable during the scheduled -------. (upgrade)", []),
 ("RND_PRODUCT", "研发与产品", 700, "research develop development design product prototype test innovation patent laboratory improve model",
  "研发、原型测试、新产品特性。", "Engineers are testing a ------- of the new device. (prototype)", []),
 ("TRAVEL_FLIGHT", "出差·航班·行程", 400, "travel trip flight airline airport passenger boarding itinerary luggage depart arrival reservation",
  "订票、登机、行程单、行李。", "Please check the attached -------  for your flight times. (itinerary)", []),
 ("HOTEL_LODGING", "住宿与酒店", 400, "hotel room guest accommodation suite reservation lobby amenity check stay rate booking",
  "订房、入住退房、设施与房价。", "All rooms include complimentary -------, such as Wi-Fi. (amenities)", []),
 ("DINING_CATERING", "餐饮·宴会·外烩", 400, "restaurant menu dish meal catering cater chef dinner reservation banquet beverage serve",
  "餐厅、菜单、宴会与外烩服务。", "Lunch will be ------- by a local company. (catered)", []),
 ("EVENT_CONFERENCE", "活动·会展·研讨会", 600, "event conference seminar workshop exhibition registration register venue speaker keynote attendee session",
  "会议注册、场地、演讲人、展会。", "Early ------- for the conference ends on May 1. (registration)", []),
 ("REAL_ESTATE", "物业·租赁·办公空间", 700, "property rent lease tenant landlord apartment building space facility occupy relocate move",
  "租约、搬迁、办公楼与房东租户。", "The ------- expires at the end of the year. (lease)", []),
 ("CONSTRUCTION_MAINT", "施工·维修·设施管理", 600, "construction renovate renovation repair maintenance contractor install inspect site project complete closure",
  "装修、维修、施工通知与关闭时间。", "The lobby will be closed for ------- next week. (renovation)", []),
 ("LEGAL_COMPLIANCE", "法务与合规", 800, "legal law regulation comply compliance policy permit license authorize violate liability clause",
  "法规遵从、许可、条款与责任。", "All vendors must ------- with the new regulations. (comply)", []),
 ("SAFETY", "安全规定与检查", 600, "safety secure security inspection hazard protective emergency procedure equipment wear guideline precaution",
  "安全检查、防护装备、紧急程序。", "Workers must wear ------- gear at all times. (protective)", []),
 ("HEALTH_MEDICAL", "医疗·保健·预约", 600, "health medical clinic patient doctor appointment insurance pharmacy prescription treatment wellness",
  "诊所预约、保险、健康计划。", "Please arrive 15 minutes before your -------. (appointment)", []),
 ("MEDIA_PUBLISH", "媒体·出版·报道", 700, "article publish publication editor magazine newspaper journal author issue edition review interview",
  "报刊、编辑、出版、采访报道。", "The article will appear in the next ------- of the magazine. (issue)", []),
 ("COMMUNITY_CULTURE", "社区·文化·公共活动", 600, "community museum library volunteer festival exhibit gallery donation charity local resident park",
  "博物馆、图书馆、志愿者、社区活动。", "Local ------- are invited to the opening. (residents)", []),
 ("RETAIL_SHOPPING", "零售·购物·会员", 400, "store shop retail customer purchase item merchandise coupon membership sale receipt brand",
  "门店、商品、优惠券、会员制度。", "Show your ------- card to receive 10% off. (membership)", []),
 ("ENVIRONMENT_ENERGY", "环境·能源·可持续", 700, "environment environmental energy recycle waste reduce efficient sustainable emission solar conserve",
  "节能、回收、环保倡议。", "The new building is highly energy -------. (efficient)", []),
 ("TRANSPORT_COMMUTE", "城市交通·通勤·停车", 400, "transportation commute traffic parking vehicle bus train route station shuttle fare road",
  "通勤、班车、停车与道路施工。", "A free ------- bus runs between the hotel and the airport. (shuttle)", []),
 ("CORRESPONDENCE", "通信往来与商务套语", 400, "attach enclose regard sincerely inquiry respond reply request confirm inform notify convenience",
  "邮件/信件常用动作词与套语（请见附件、尽早回复）。", "Please find ------- the revised schedule. (attached)", []),
]

def scene_stats():
    import csv, os
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    U = {}
    def load(path, wcol, ucol):
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            r = csv.reader(f); hdr = next(r)
            for row in r:
                if len(row) > ucol and row[wcol].strip():
                    try: U.setdefault(src_of[path], {})[row[wcol].strip().lower()] = float(row[ucol])
                    except ValueError: pass
    src_of = {}
    for tag, p, wc, uc in [("TSL", "wordlists/TSL_12_stats.csv", 0, 3), ("BSL", "external/wordlists/BSL_120_stats.csv", 0, 4),
                           ("NGSL", "external/wordlists/NGSL_12_stats.csv", 0, 3)]:
        full = os.path.join(base, p); src_of[full] = tag; load(full, wc, uc)
    out = {}
    for k, nm, b, seeds, d, ex, v in SCENES:
        ws = seeds.split()
        hit_t = [w for w in ws if w in U["TSL"]]; hit_b = [w for w in ws if w in U["BSL"]]
        hit_n = [w for w in ws if w in U["NGSL"]]
        SUF = ("er","or","ee","ion","ation","ment","al","ly","ity","able","ible","ive","ant","ent","ance","ence","ing","ed","ure","ist","ize","y")
        fam = set()
        for w in ws:
            stems = {w, w[:-1] if w.endswith("e") else w, w[:-1] + "i" if w.endswith("y") else w}
            for x in list(U["TSL"]) + list(U["BSL"]):
                if x != w and any(x == st + sf for st in stems for sf in SUF):
                    if x not in {'ration','dual','duly','compliment','contraction','audition','appliance','materially','projection','informal','respondent'}: fam.add(x)
        usum = sum(max(U["TSL"].get(w, 0), U["BSL"].get(w, 0), U["NGSL"].get(w, 0) * 0.3) for w in ws)
        out[k] = dict(seeds=ws, tsl=hit_t, bsl=hit_b, ngsl=hit_n, usum=usum, fam=sorted(fam))
    return out

STATS = scene_stats()
mx = max(s["usum"] for s in STATS.values())
for k, nm, b, seeds, d, ex, v in SCENES:
    s = STATS[k]
    w = round(0.04 + 0.12 * s["usum"] / mx, 3)
    desc = (f"{d} 种子词 {len(s['seeds'])} 个：命中 TSL {len(s['tsl'])}、BSL {len(s['bsl'])}、NGSL {len(s['ngsl'])}"
            f"（{', '.join(s['seeds'][:8])}…）；TSL/BSL 中的同族派生词：{', '.join(s['fam'][:10]) or '无'}。TSL/BSL 是 NGSL 的补充表，基础场景词多在 NGSL 中。")
    N("VO.SCENE." + k, nm, L, "VO.SCENE", ["VO.SCENE"], P567, b, desc, ex, w=w, basis="wordlist_freq", v0=v,
      src="种子词在 TSL/BSL 的调整频率 U 之和（NGSL 仅计 0.3 倍）相对最大簇，映射到 0.04–0.16；反映场景词在 TOEIC/商务语料中的常用度，不是真题计数")

# --- 搭配
N("VO.COLLO", "搭配与固定表达", L, "VO", ["VO.SCENE"], P567, 400,
  "以短语为单位记词（V-02，金のフレーズ）；P5 词汇题“不翻译解”的主要线索（P5-12）。", "—", basis="aggregate")
COLLO = [
 ("VERB_NOUN", "动词+名词搭配", 600, "meet the deadline / place an order / address concerns / conduct a survey", "Please ------- your order online. (place)", 1.2),
 ("ADJ_NOUN", "形容词+名词搭配", 600, "competitive salary / substantial increase / extensive experience / prompt reply", "We offer a ------- salary. (competitive)", 1.0),
 ("ADV_VERB_ADJ", "副词+动词/形容词搭配", 700, "highly recommended / conveniently located / significantly reduced / carefully review", "The book is ------- recommended. (highly)", 0.9),
 ("VERB_PREP", "动词+介词（comply with/adhere to/account for/depend on）", 600, "动词固定介词，选介词或选动词都会考。", "All staff must ------- with the dress code. (comply)", 0.8),
 ("NOUN_PREP", "名词+介词（demand for/access to/increase in/solution to）", 600, "名词固定接的介词。", "There has been an increase ------- sales. (in)", 0.5),
 ("ADJ_PREP", "形容词+介词（eligible for/responsible for/aware of/familiar with）", 600, "常见于 be + adj + prep。", "Full-time staff are ------- for the bonus. (eligible)", 0.6),
 ("BE_PP_PREP", "be + 过去分词 + 介词（be equipped with/be located in/be committed to）", 600, "被动形式的固定表达。", "Each room is equipped ------- a coffee maker. (with)", 0.4),
 ("FIXED_PHRASE", "固定短语（in charge of/on short notice/at no extra cost）", 600, "整块记忆的介词短语。", "Repairs will be made at no additional -------. (cost)", 0.7),
 ("TIME_EXPR", "时间表达（in advance/ahead of schedule/until further notice）", 600, "日程类常考短语。", "The project was completed ahead of -------. (schedule)", 0.5),
 ("NUM_EXPR", "数量与范围表达（up to/as many as/no later than/at least）", 600, "数字前的限定表达，P7 数字题也常改写。", "Applications must arrive no ------- than May 5. (later)", 0.4),
 ("PHRASAL_VERB", "短语动词（carry out/set up/fill out/turn in）", 600, "P7 同义替换常把短语动词改写为单词。", "Please ------- out the survey. (fill)", 0.5),
 ("REQUEST_EXPR", "请求/提醒/告知句式（be advised that/kindly/feel free to）", 600, "通知和邮件中的功能句式，帮助判断写作目的。", "Please be ------- that the office will close early. (advised)", 0.3),
]
for k, nm, b, d, ex, est in COLLO:
    N("VO.COLLO." + k, nm, L, "VO.COLLO", ["VO.COLLO"], P567, b, d, ex, est=est,
      src="P5 词汇 9–12 题中可借搭配线索解的比例（书目共识，非真题计数）")

# --- 易混
N("VO.CONF", "易混词辨析", L, "VO", ["VO.SCENE", "FD.VOC.AFFIX"], P567, 600,
  "形近、义近、多义词辨析（P5-13）；近年 P5 趋势：形近派生词增多（toeicstory 2577）。", "—",
  basis="aggregate", v0=["V4"])
CONF = [
 ("FORM_ADJ", "同根形容词（considerable/considerate, economic/economical, reliable/reliant）", 700, "同词根不同后缀，意义不同。",
  "We made ------- progress this year. (considerable)", 0.5),
 ("FORM_NOUN", "同根名词（attendance/attendee/attendant, product/production/productivity）", 600, "人/事/抽象名词分化。",
  "------- at the seminar was higher than expected. (Attendance)", 0.5),
 ("FORM_VERB", "形近动词（affect/effect, rise/raise, lie/lay, ensure/insure）", 600, "形近或拼写近似的动词。",
  "Prices are expected to ------- next month. (rise)", 0.3),
 ("SYN_VERB_PATTERN", "近义动词的句型差异（inform sb of / explain sth to sb / discuss sth）", 700, "近义但宾语结构不同，靠语法排除。",
  "Please ------- us of any changes. (inform)", 0.5),
 ("SYN_NOUN", "近义名词（fee/fare/charge/rate, client/patron/customer）", 700, "费用、顾客等近义名词按搭配区分。",
  "The bus ------- is $2. (fare)", 0.5),
 ("SYN_ADJ", "近义形容词（available/accessible, complimentary/free, possible/potential）", 700, "按修饰对象与搭配区分。",
  "Breakfast is ------- for all guests. (complimentary)", 0.5),
 ("ADV_TIME", "时间副词（already/yet/still/soon/recently/once）", 600, "与时态和肯否定配合。",
  "The report has not been finished -------. (yet)", 0.5),
 ("ADV_FOCUS", "焦点/程度副词（only/just/even/also/too/either/nearly/almost）", 700, "almost all vs most；only/even 修饰位置。",
  "------- all of the seats were taken. (Almost)", 0.6),
 ("SO_SUCH_TOO", "so/such/too/enough", 600, "so+adj；such+(a)+adj+n；too…to；adj+enough。",
  "It was ------- a popular event that tickets sold out. (such)", 0.2),
 ("QUANT_WORDS", "数量名词与修饰（amount/number, few/little, a variety of）", 600, "可数/不可数配合。",
  "A large ------- of applications was received. (number)", 0.3),
 ("PREP_LOOKALIKE", "形近/义近介词（beside/besides, among/between, by/until, within/during）", 600, "与 GR.CONN 交叉，靠语义区分。",
  "------- salary, the job offers health benefits. (Besides)", 0.4),
 ("BUSINESS_SENSE", "常用词的商务义（address/issue/term/figure/branch/party/run）", 700, "基础词在商务语境的特定义项，是 P7 同义词题主来源。",
  "We need to address the issue → address = deal with", 0.8),
 ("POLYSEMY_CONTEXT", "多义词按语境取义", 700, "同义词题不选最常见义（P7-08）。", "a top priority → top = highest；cover the cost → cover = pay for", 0.6),
 ("PREFIX_NEG", "否定/反义前缀（un-/in-/dis-/non-/mis-）", 600, "前缀改变正负义，易在选项中设陷阱。", "The item is ------- for use outdoors. (unsuitable)", 0.2),
]
for k, nm, b, d, ex, est in CONF:
    pre = ["VO.CONF"]
    if k == "POLYSEMY_CONTEXT": pre = ["VO.CONF.BUSINESS_SENSE"]
    if k == "PREP_LOOKALIKE": pre = ["VO.CONF", "GR.CONN.PREP_MEANING"]
    N("VO.CONF." + k, nm, L, "VO.CONF", pre, P567, b, d, ex, est=est, v0=["V4"],
      src="P5 词汇 9–12 题 + P6 词汇 5–8 题中涉及辨析的估计份额；P7 同义词 2–4 题")

# --- 同义替换
N("VO.PARA", "同义替换（改写）类型", L, "VO", ["VO.SCENE", "VO.COLLO"], P67, 400,
  "P7 正确选项多为原文改写，照搬原词的选项要警惕（P7-09、summitedu：约 70% 为替换）。按改写方式分类训练。", "—",
  basis="aggregate", v0=["R2"])
PARA = [
 ("WORD_SYNONYM", "单词同义替换（purchase→buy, complimentary→free）", 400, "最基础的改写形式。", "原文: complimentary parking → 选项: free parking", 4.0),
 ("WORD_TO_PHRASE", "单词↔短语（postpone→put off, inspect→look over）", 600, "单词与短语动词互换。", "原文: postponed → 选项: put off", 2.0),
 ("GENERALIZE", "具体→概括（laptops, printers → office equipment）", 600, "选项用上位词概括原文具体事物，正确答案常更抽象（muu_toeic 趋势）。",
  "原文: a free mug and T-shirt → 选项: promotional items", 3.0),
 ("SPECIFY", "概括→具体（按条件推回具体实例）", 700, "题干用概括词，原文给具体实例。", "Q: What is offered to members? 原文: 10% off all books", 1.0),
 ("POS_SHIFT", "词性转换（decide→decision, expand→expansion）", 600, "同根词换词性改写。", "原文: We will expand → 选项: An expansion is planned", 1.5),
 ("VOICE_SHIFT", "主被动/视角转换", 700, "主语换成动作承受者或另一方。", "原文: The client approved the design → 选项: The design was accepted", 1.0),
 ("NEGATION_SHIFT", "否定/反义改写（not until→only after, unable→cannot）", 800, "反义词+否定、双重否定的等价改写。", "原文: not available until May → 选项: will be available starting in May", 1.0),
 ("CAUSE_EFFECT", "因果改写（due to→because, result in→cause）", 600, "原因/结果表达互换（egsty）。", "原文: due to heavy rain → 选项: because of the weather", 1.0),
 ("NUMBER_TIME", "数字/时间换算（two weeks→14 days, every Monday→weekly）", 400, "数字、日期、频率换算后出现在选项。", "原文: every three months → 选项: quarterly", 1.5),
 ("SUMMARY_NOMINAL", "句子→抽象名词概括（a ceremony to honor… → an awards event）", 600, "整句意思浓缩为名词短语，主旨/目的题常见。", "原文: to thank volunteers for their work → 选项: to express appreciation", 2.0),
 ("ROLE_REFERENCE", "人物/机构代称（the accountant→a finance employee, Brix Co.→the firm）", 700, "职位、部门、公司换称谓。", "原文: Ms. Park, head of payroll → 选项: a manager in the finance department", 1.0),
 ("IDIOM_EXPR", "习语/惯用说法改写（hit the shelves→go on sale）", 800, "惯用表达与其直白说法互换。", "原文: hit the shelves → 选项: become available in stores", 0.5),
]
for k, nm, b, d, ex, est in PARA:
    N("VO.PARA." + k, nm, L, "VO.PARA", ["VO.PARA"], P67, b, d, ex, est=est, v0=["R2"],
      src="P7 54 题中正确选项为改写的约 70%（summitedu 摘要）→按改写方式分摊（估计）")

# --- Part5 同词性词汇题
N("VO.LEX", "同词性词汇题（四选项同词性不同词义）", L, "VO", ["VO.SCENE", "VO.COLLO"], P56, 400,
  "P5 词汇 30–40%（9–12 题），P6 词汇 5–8 题；先找搭配/语法线索，再按语义选（P5-12）。", "—",
  basis="aggregate", v0=["V1", "V2", "V3", "V4"], src="exam_pattern_stats.json composite")
for k, nm, est, ex in [("VERB", "动词词汇题", 3.5, "The company will ------- a new policy. (implement / install / insist / involve)"),
                       ("NOUN", "名词词汇题", 3.5, "Please send your ------- by e-mail. (inquiries / instances / intentions / inclusions)"),
                       ("ADJ", "形容词词汇题", 3.5, "The offer is ------- for one week only. (valid / vivid / vital / vacant)"),
                       ("ADV", "副词词汇题", 3.5, "The store is ------- closed on holidays. (temporarily / typically / tightly / totally)")]:
    N("VO.LEX." + k, nm, L, "VO.LEX", ["VO.LEX"], P56, 400 if k in ("VERB", "NOUN") else 600,
      f"四个{nm[:3]}选项，靠搭配与语境语义判断。", ex, est=est, basis="stat_single",
      src="get-toeic：动词/形容词/名词各 8%、副词 9%（P5）+P6 词汇按比例分摊")

# --- 分段词汇储备 + 职位部门
N("VO.BAND", "按目标分数段的词汇储备", L, "VO", ["FD.VOC.NGSL_CORE"], P567, 400,
  "按目标分数段分层背词，先背目标分以下各段（V-01；金のフレーズ按 600/730/860/990 分段）。", "—", basis="aggregate")
for i, (k, b, d) in enumerate([("B600", 400, "600 分段：TSL 高频词 + 基础商务词（约 400 词）"),
                               ("B730", 600, "730 分段：常见搭配与派生词（约 300 词）"),
                               ("B860", 700, "860 分段：低频商务词、多义词商务义（约 200 词）"),
                               ("B990", 800, "990 分段：难词与细微辨析（约 100 词）")]):
    pre = ["VO.BAND"] if i == 0 else ["VO.BAND." + ["B600", "B730", "B860"][i - 1]]
    N("VO.BAND." + k, "词汇储备 " + k[1:] + " 段", L, "VO.BAND", pre, P567, b, d + "；词数为参考书分段规模（KF 共 1000 词），非本项目统计。",
      "—", w=[0.35, 0.3, 0.2, 0.1][i], basis="impact_estimate", src="分段越高、边际题数越少（估计）")
N("VO.TITLES_DEPTS", "部门与职位名称（accounting, HR, CFO, receptionist）", L, "VO", ["VO.SCENE.OFFICE_ADMIN"], P67, 600,
  "专记题干/选项里常见的部门、职位名称，读题更快（V-03），也服务 P7 推断身份题。",
  "Who most likely is Ms. Ruiz? → (C) A personnel manager", w=0.2, basis="impact_estimate")
