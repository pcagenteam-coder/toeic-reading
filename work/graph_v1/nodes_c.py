# -*- coding: utf-8 -*-
"""第三部分：题型层（P5/P6/P7 + P7 设问×文本）、文本类型层、应试技巧层。"""
from nodes_a import N, P5, P6, P7, P56, P567, P67
CS = "exam_pattern_stats.json composite"

# ================================================================ texttype
L = "texttype"
N("TX", "文本类型层（Part6/7 文本）", L, None, [], P67, 400,
  "现行版 P7：单篇 10 篇（29 题）+ 双篇 2 组（10 题）+ 三篇 3 组（15 题），约 23 份文档；P6 4 篇。邮件/信件+文章约占 50–60%。",
  "—", basis="aggregate", src=CS)
TX = [
 # key, name, band, est(题), desc, example, prereqs
 ("EMAIL", "电子邮件", 400, 14, "最高频文本（含 P6 约一半篇目）：看收发件人、主题行、首段目的、末段请求/附件。",
  "To: / From: / Subject: Change to delivery schedule — 'I am writing to let you know…'", []),
 ("LETTER", "商务信件", 400, 5, "Dear…/Sincerely 格式，常见于通知客户、确认合同、投诉回复。", "Dear Mr. Okafor, Thank you for your recent order…", ["TX.EMAIL"]),
 ("MEMO", "备忘录（内部通知）", 400, 4, "To: All staff 内部文件，考目的、受影响部门与要求。", "MEMO To: All employees  Re: Parking lot repaving", ["TX.EMAIL"]),
 ("NOTICE", "通知/公告/政策", 400, 6, "公共或内部公告：变更、关闭时间、新规定、政策条款。", "NOTICE: The library will close at 5 P.M. on Friday for maintenance.", []),
 ("AD", "广告（产品/服务/促销）", 400, 4, "看产品特点、优惠条件、有效期、购买/联系方式；NOT 题高发。", "Grand Opening Sale! 20% off all items through June 30.", []),
 ("JOB_POSTING", "招聘广告", 600, 2, "职位、资格要求、福利、申请方式与截止日期；常与简历/邮件组成多篇。", "Now hiring: Assistant Manager. Requirements: 2+ years of retail experience…", ["TX.AD"]),
 ("ARTICLE", "文章/新闻报道/新闻稿", 600, 9, "公司新闻、行业动态、人物介绍；主旨、推断、插入句、同义词题集中。", "LOCAL BUSINESS — Harlow Foods announced on Monday that it will open…", []),
 ("FORM", "表格类（发票/日程/申请表/问卷）", 400, 8, "信息以表格或字段呈现，按格式定位，常与其他文本连锁出题。", "Invoice #4471 | Item | Qty | Unit price | Total", []),
 ("INVOICE", "发票/收据/订单确认", 400, 2.5, "数量、单价、合计、折扣、付款期限；计算与对照题。", "Subtotal $240.00  Discount (10%) −$24.00  Total $216.00", ["TX.FORM"]),
 ("SCHEDULE", "日程/行程/议程表", 400, 3, "时间、地点、负责人；变更后对照是跨篇常见考点。", "9:00 Registration | 9:30 Keynote: J. Ortiz | 11:00 Workshop A (Room 2)", ["TX.FORM"]),
 ("APP_FORM", "申请表/问卷/评价表", 600, 2.5, "勾选项、评分、备注栏；推断填表人身份与需求。", "Satisfaction survey: Food ★★★★☆  Comments: The room was too cold.", ["TX.FORM"]),
 ("TEXT_MSG", "短信链（2 人）", 400, 2.5, "非正式口语化；意图题必出于短信/聊天（gotop：每篇 2 题或 4 题短信/聊天各 1 题意图）。",
  "Ana (10:02): The client's flight is delayed. / Ben (10:03): I'll let the driver know.", []),
 ("CHAT", "在线群聊（多人）", 600, 4, "3 人以上群聊，需追踪谁说了什么、谁负责什么。", "Lee: Can someone cover the 3 P.M. call? / Kim: I can. / Park: Thanks, Kim.", ["TX.TEXT_MSG"]),
 ("WEB", "网页", 600, 5, "公司主页、FAQ、产品页、预约页；看栏目标签与链接。", "Home | About Us | Services | Contact — Frequently Asked Questions", []),
 ("REVIEW", "评价/顾客反馈", 600, 2, "顾客点评、评分；考满意/不满点与推断。", "★★★☆☆ 'The service was fast, but the dessert menu was limited.'", []),
 ("INSTRUCTIONS", "说明书/保修条款/操作指南", 700, 1.5, "步骤、条件、例外条款；NOT 与条件推断。", "Warranty: This product is covered for one year, except for damage caused by misuse.", ["TX.NOTICE"]),
 ("MULTI", "多篇文本（双篇/三篇）", 600, 25, "现行版 5 组 25 题（双篇 2 组、三篇 3 组）；跨篇连锁题约 6–10 题。", "—", ["TX.EMAIL", "TX.FORM"]),
 ("DOUBLE", "双篇组合", 600, 10, "常见：广告+邮件、邮件+回复、日程+邮件；每组约 1–2 题跨篇。", "Text 1: event flyer / Text 2: e-mail asking to change a session", ["TX.MULTI"]),
 ("TRIPLE", "三篇组合", 700, 15, "常见：网页+邮件+表格/评价；每组约 2–3 题跨篇，最难（ETS p 值多篇 0.42–0.51）。",
  "Text 1: web page (rates) / Text 2: invoice / Text 3: complaint e-mail", ["TX.DOUBLE"]),
]
for k, nm, b, est, d, ex, pre in TX:
    par = "TX"
    if k in ("INVOICE", "SCHEDULE", "APP_FORM"): par = "TX.FORM"
    if k in ("DOUBLE", "TRIPLE"): par = "TX.MULTI"
    N("TX." + k, nm, L, par, pre, [7] if k not in ("EMAIL", "LETTER", "MEMO", "NOTICE", "AD", "ARTICLE", "WEB") else P67, b, d, ex,
      est=None if k in ("MULTI", "FORM") else est, basis="aggregate" if k in ("MULTI", "FORM") else "derived",
      v0=["R5"] if k in ("MULTI", "DOUBLE", "TRIPLE") else [],
      src="题数=该文本类型上的题目数（P6+P7）；依 toeicstory 邮件+文章 50–60%、现行版多篇 25 题与 scordia 题库文本分布估算")

# ================================================================ qtype
L = "qtype"
N("QT", "题型层（Part5/6/7 设问类型）", L, None, [], P567, 400, "按现行线性版题型切分。", "—", basis="aggregate")
# ---- Part 5
N("QT.P5", "Part 5 短句填空（30 题）", L, "QT", [], P5, 400, "30 题；语法 vs 词汇约 6:4（各来源 55–70% 语法）。", "—", basis="aggregate", src=CS)
P5Q = [
 ("IDENTIFY", "看选项判题型（结构先行 vs 语境先行）", 400, ["FD.SENT.CORE"], "先扫四选项：同根异形→词性；同动词异形→动词；介/连/副混排→连接；异义同词性→词汇（P5-01；文法特急第0章两路径）。",
  "options: effective / effectively / effect / effectiveness → 词性题，只看空格前后", None, 0.5, "impact_estimate", ["G1", "S1"]),
 ("WORD_FORM", "词性题", 400, ["QT.P5.IDENTIFY", "GR.POS"], "同词根四词形，按位置定词性；20–27%（6–8 题）。", "The ------- of the plan took two months. (implementation)", 7, None, "stat_composite", ["G1"]),
 ("VERB_FORM", "动词形态题", 400, ["QT.P5.IDENTIFY", "GR.VERB"], "同一动词的时态/语态/数/非谓语；8–12%（2–4 题）。", "The package ------- tomorrow. (will be delivered)", 3, None, "stat_composite", ["G3", "G4", "G5"]),
 ("PREP", "介词题", 400, ["QT.P5.IDENTIFY", "GR.CONN"], "四个介词或含介词短语；10–13%（3–4 题）。", "The museum is closed ------- renovations. (for)", 3.5, None, "stat_composite", ["G7"]),
 ("CONNECTOR_MIX", "介词/连词/副词混排题", 600, ["QT.P5.IDENTIFY", "GR.CONN.PREP_VS_CONJ"], "despite/although/however 混排，先看空格后结构（P5-05）。", "------- it rained, the event continued. (Although / Despite / However / Nevertheless)", 1.5, None, "derived", ["G7"]),
 ("CONJ", "连词题", 600, ["QT.P5.CONNECTOR_MIX", "GR.CONN.CONJ_ADVERBIAL"], "从属/并列/成对连词按逻辑选；3–9%（1–3 题）。", "Please call us ------- you have any questions. (if)", 1.5, None, "stat_composite", ["G7"]),
 ("PRONOUN", "代词/限定词题", 400, ["QT.P5.IDENTIFY", "GR.PRON"], "格、反身、数量限定词；7–10%（2–3 题）。", "Mr. Tan will lead the session -------. (himself)", 2.5, None, "stat_composite", ["G8"]),
 ("RELATIVE", "关系词题", 600, ["QT.P5.IDENTIFY", "GR.REL"], "who/which/whose/that/what；0–3%（0–1 题，证据弱）。", "The intern ------- report won the award is Ms. Cho. (whose)", 0.5, None, "stat_composite", ["G6"]),
 ("COMPARATIVE", "比较题", 600, ["QT.P5.IDENTIFY", "GR.COMP"], "比较级/最高级/原级；1–3%（0–1 题）。", "This is the ------- option available. (cheapest)", 0.5, None, "stat_composite", []),
 ("PAIR_GRAMMAR", "成对表达/语法搭配/数量一致题", 600, ["QT.P5.IDENTIFY", "GR.CONN.CONJ_CORRELATIVE", "GR.VERB.AGREE_QUANT"], "both–and、each+单数、so…that 等（でる1000問第7章）。", "Neither the manager ------- the staff knew. (nor)", 0.5, None, "derived", []),
 ("VOCAB", "词汇题（同词性异义）", 400, ["QT.P5.IDENTIFY", "VO.LEX"], "30–40%（9–12 题），P5 份额最大；先找搭配线索，不行再读全句。", "We ------- a 10% discount to members. (offer)", 10.5, None, "stat_composite", ["V1", "V2", "V3", "V4"]),
]
for k, nm, b, pre, d, ex, est, w, basis, v in P5Q:
    N("QT.P5." + k, nm, L, "QT.P5", pre, P5, b, d, ex, est=est, w=w, basis=basis, v0=v, src=CS)
# ---- Part 6
N("QT.P6", "Part 6 长文填空（4 篇×4 题=16 题）", L, "QT", ["QT.P5"], P6, 400,
  "每篇固定 1 道句子插入（文选择）；约一半题句内可解，其余需上下文（mikan、alc）。", "—", basis="aggregate", v0=["R6"], src=CS)
P6Q = [
 ("CLASSIFY", "独立型 vs 上下文型判别", 400, ["QT.P5.IDENTIFY"], "先分清句内可解（按 P5 速答）与需前后文（时态/代词/接续副词/词汇/插入句）（P6-02）。",
  "空格句: We ------- the venue. 选项全是 book 的时态 → 需看前后文判断事件是否已发生", None, 0.35, "impact_estimate", ["R6"]),
 ("INDEPENDENT", "独立型语法/词性题", 400, ["QT.P6.CLASSIFY", "QT.P5.WORD_FORM"], "仅靠本句即可解；P6 语法 3–5 题。", "...our ------- staff will assist you. (experienced)", 4, None, "stat_composite", ["G1"]),
 ("CTX_TENSE", "语境时态题", 600, ["QT.P6.CLASSIFY", "GR.VERB.TENSE_PERFECT"], "本句多个时态都通，以发信日期与事件时间线为准（P6-03）；约 2 题。", "(发信 3 月 2 日) The workshop ------- on March 10. → will be held", 2, None, "stat_composite", ["G4"]),
 ("CTX_PRONOUN", "语境代词题", 600, ["QT.P6.CLASSIFY", "FD.READ.REFERENCE"], "回前文找指代对象（公司/个人/单复数）（P6-04）。", "Brix Co. ... ------- new office → its", 0.7, None, "derived", ["G8"]),
 ("CTX_VOCAB", "语境词汇题", 600, ["QT.P6.CLASSIFY", "VO.LEX"], "几个选项本句都通，以全文主题定（P6-06）；5–8 题。", "...the ------- will be finished by June. (renovation, 前文讲装修)", 5, None, "stat_composite", ["V4"]),
 ("CTX_CONJ_ADV", "接续副词题", 600, ["QT.P6.CLASSIFY", "GR.CONN.CONJ_ADVERB"], "判断两句逻辑关系再选（P6-05）；约 1 题。", "The item is out of stock. -------, we can offer a similar model. (However)", 1, None, "stat_composite", ["G7"]),
 ("INSERTION", "句子插入（文选择）题", 700, ["QT.P6.CLASSIFY", "FD.READ.DISCOURSE", "FD.READ.REFERENCE"], "每篇 1 题、每卷 4 题固定；靠指代词、连接词、新旧信息衔接选句（P6-07）。",
  "[空] 前: We are moving to a new location. 后: The new address is... → 'The move will take place on May 1.'", 4, None, "stat_single", ["R6"]),
 ("INS_OPENING", "插入句：段首/引入句", 700, ["QT.P6.INSERTION"], "空格在首段时选能引出下文主题的句子。", "空格→后文讲新会员福利 → 'We are excited to introduce our new rewards program.'", 1, None, "derived", ["R6"]),
 ("INS_TRANSITION", "插入句：段中衔接句", 700, ["QT.P6.INSERTION"], "前后句之间的承接（举例、补充、转折）；看指代与连接词。", "前: Parking is limited. [空] 后: Please use public transit. → 'Only 20 spaces are available.'", 1.8, None, "derived", ["R6"]),
 ("INS_CLOSING", "插入句：结尾/行动号召句", 700, ["QT.P6.INSERTION"], "末段常选联系方式、期待回复、感谢类句子；须与正文目的一致。", "'Please contact me if you have any questions.'", 1.2, None, "derived", ["R6"]),
]
for k, nm, b, pre, d, ex, est, w, basis, v in P6Q:
    N("QT.P6." + k, nm, L, "QT.P6", pre, P6, b, d, ex, est=est, w=w, basis=basis, v0=v,
      src=CS + "；插入句子类位置分布据 toiguru '文头/中/末规律'分摊（估计）")
# ---- Part 7
N("QT.P7", "Part 7 阅读理解（54 题）", L, "QT", ["FD.READ.SCAN"], P7, 400,
  "单篇 29 题 + 多篇 25 题；设问类型按 junpei/mikan/scordia 合并。", "—", basis="aggregate", src=CS)
P7Q = [
 ("MAIN_PURPOSE", "主旨/目的题", 400, ["FD.READ.SKIM"], "答案多在开头（I am writing to…）；过宽过窄选项排除（P7-02）；5–10 题。",
  "What is the purpose of the e-mail? → To request a schedule change", 6, "stat_composite", []),
 ("DETAIL", "细节题（5W1H）", 400, ["FD.READ.SCAN", "VO.PARA.WORD_SYNONYM"], "题干关键词扫读定位，精读附近句，选改写选项（P7-03）；细节类合计 20–25 题。",
  "Where will the reception take place? → In the hotel garden", 14, "stat_composite", ["R1"]),
 ("DETAIL_NUMBER", "数字/日期/金额细节题", 400, ["QT.P7.DETAIL", "VO.PARA.NUMBER_TIME"], "人名、数字、日期类定位最快，注意换算改写（FLTRP Unit21）。",
  "When is the payment due? → By March 31", 4, "derived", ["R1"]),
 ("REASON", "原因题（Why…?）", 600, ["QT.P7.DETAIL", "VO.PARA.CAUSE_EFFECT"], "找 because/due to/so that 附近的原因表述（scordia 题库 4.5%）。",
  "Why was the event moved? → The original venue was being repaired.", 2, "stat_single", ["R1"]),
 ("REQUEST_ACTION", "要求/建议行动题（What is X asked to do?）", 400, ["QT.P7.DETAIL"], "定位 please/should/be asked to/we recommend，多在末段。",
  "What is Mr. Lim asked to do? → Return a signed contract", 2, "derived", ["R1"]),
 ("TRUE_INDICATED", "选项照合题（What is indicated/stated/true about…?）", 600, ["QT.P7.DETAIL", "VO.PARA.GENERALIZE"], "无明确关键词，需逐项对照；约 10–12 题（与推断重叠）。",
  "What is indicated about the store? → It has more than one location.", 6, "stat_composite", ["R1", "R4"]),
 ("NOT_TRUE", "NOT/TRUE 题", 600, ["QT.P7.TRUE_INDICATED", "ST.ELIM.OPTIONS"], "逐项回文核对排除，耗时则后做（P7-04）；1–3 题。",
  "What is NOT mentioned as a benefit? → Free parking", 2, "stat_composite", ["R4"]),
 ("INFERENCE", "推断题（suggested/implied/most likely）", 600, ["QT.P7.TRUE_INDICATED", "VO.PARA.SUMMARY_NOMINAL"], "依据必须在原文，选稳妥推论，不靠常识（P7-05）；8–15 题，ETS RM-17-05：推断量最大。",
  "What is suggested about Ms. Diaz? → She has worked with the company before.", 8, "stat_composite", ["R3"]),
 ("INFER_WHO", "推断身份/读者对象题", 600, ["QT.P7.INFERENCE", "VO.TITLES_DEPTS"], "Who most likely is X? / For whom is the notice intended?，看职责描述与称谓。",
  "For whom is the notice most likely intended? → Building tenants", 2, "derived", ["R3"]),
 ("INFER_NEXT", "推断下一步/将来行为题", 700, ["QT.P7.INFERENCE"], "What will X most likely do next? 看末尾的计划与承诺。",
  "What will Mr. Ford probably do next? → Contact a supplier", 1.5, "derived", ["R3"]),
 ("INTENT", "意图题（引号中的话）", 700, ["QT.P7.INFERENCE", "TX.TEXT_MSG"], "看前后几条消息定语境，判断这句话的功能（P7-06）；每卷约 2 题，只出于短信/聊天。",
  "At 10:05, what does Ms. Ito mean when she writes, 'I'm on it'? → She will handle the task.", 2, "stat_composite", ["R3"]),
 ("INSERTION", "句子位置题（[1]–[4]）", 700, ["QT.P6.INSERTION"], "先读插入句抓指代/连接词线索，预测前文内容再验证（P7-07）；每卷约 2 题，多在文章/邮件。",
  "'This was the second time the award was given to her.' → 放在提及获奖的句子后", 2, "stat_composite", ["R6"]),
 ("SYNONYM", "同义词题（closest in meaning）", 700, ["VO.CONF.POLYSEMY_CONTEXT"], "按语境义选，避开最常见义（P7-08）；2–4 题，多在多篇。",
  "'cover' in paragraph 2 is closest in meaning to → pay for", 3, "stat_composite", ["R2", "V4"]),
 ("CALC_LOOKUP", "计算/表格对照题", 600, ["QT.P7.DETAIL_NUMBER", "TX.FORM"], "按条件查表、加减折扣（scordia 题库 6.9%，偏高）。",
  "How much will the customer pay? → 原价 − 会员折扣", 1.5, "stat_single", ["R1"]),
 ("CROSS_REF", "跨篇连锁题（多篇对照）", 700, ["QT.P7.DETAIL", "QT.P7.INFERENCE", "TX.MULTI"], "一篇给条件、另一篇给数据，两篇对照作答（P7-12）；双篇每组 1–2、三篇每组 2–3，每卷约 6–10 题。",
  "Text1: 满 $100 免运费 / Text2: 订单 $120 → Q: What is true about the order? → Shipping was free.", 8, "stat_composite", ["R5"]),
]
for k, nm, b, pre, d, ex, est, basis, v in P7Q:
    N("QT.P7." + k, nm, L, "QT.P7", pre, P7, b, d, ex, est=est, basis=basis, v0=v, src=CS)

# ---- Part 7 设问 × 文本 组合（只收真实高发组合）
X = [
 # q, t, est, band, desc, ex
 ("MAIN_PURPOSE", "EMAIL", 2.5, 400, "邮件目的：首段 I am writing to / I'd like to；回复邮件看 Thank you for your…之后。", "Why did Mr. Ali send the e-mail? → To confirm an order"),
 ("MAIN_PURPOSE", "LETTER", 0.8, 400, "信件目的：常为通知、感谢、致歉、确认。", "What is the purpose of the letter? → To apologize for an error"),
 ("MAIN_PURPOSE", "NOTICE", 0.8, 400, "公告目的：通知变更/关闭/新规。", "What is the purpose of the notice? → To announce a temporary closure"),
 ("MAIN_PURPOSE", "MEMO", 0.6, 400, "内部备忘目的：宣布政策、提醒截止。", "What is the memo mainly about? → A new expense policy"),
 ("MAIN_PURPOSE", "ARTICLE", 1.0, 600, "文章主旨：标题+首段；人物介绍类注意'主要讲什么'。", "What is the article mainly about? → A company's expansion"),
 ("MAIN_PURPOSE", "AD", 0.3, 400, "广告宣传什么服务。", "What is being advertised? → A cleaning service"),
 ("DETAIL", "EMAIL", 3.0, 400, "邮件细节：时间、地点、附件、要求。", "What is attached to the e-mail? → A revised floor plan"),
 ("DETAIL", "ARTICLE", 2.0, 600, "文章细节：人物经历、公司数据。", "According to the article, what did Ms. Lee do in 2019? → Open a second store"),
 ("DETAIL", "NOTICE", 1.5, 400, "公告细节：生效时间、受影响对象。", "When will the new policy take effect? → July 1"),
 ("DETAIL", "WEB", 1.5, 600, "网页细节：按栏目标签定位。", "What can users do on the Web page? → Track an order"),
 ("DETAIL_NUMBER", "FORM", 2.0, 400, "表格数字：按列名与行名交叉定位。", "How many units were ordered? → 40"),
 ("DETAIL_NUMBER", "SCHEDULE", 1.0, 400, "日程：时间/地点/负责人对照。", "What time does the workshop start? → 11:00 A.M."),
 ("REQUEST_ACTION", "EMAIL", 1.2, 400, "邮件末段的请求事项。", "What is the recipient asked to do? → Submit a form by Friday"),
 ("REQUEST_ACTION", "MEMO", 0.5, 400, "备忘录对员工的要求。", "What are employees asked to do? → Remove items from their desks"),
 ("TRUE_INDICATED", "ARTICLE", 1.5, 600, "文章照合：逐项对照段落。", "What is indicated about the bakery? → It was founded by two brothers."),
 ("TRUE_INDICATED", "WEB", 1.0, 600, "网页照合：服务条款与栏目。", "What is stated about the membership? → It can be renewed online."),
 ("TRUE_INDICATED", "REVIEW", 0.8, 600, "评价照合：满意/不满点。", "What is indicated about the reviewer's stay? → The room was noisy."),
 ("TRUE_INDICATED", "JOB_POSTING", 0.7, 600, "招聘照合：资格、福利、工作地点。", "What is a requirement for the position? → A driver's license"),
 ("NOT_TRUE", "AD", 0.8, 600, "广告 NOT：列举的优惠/特点逐项排除。", "What is NOT included in the package? → Airport transfer"),
 ("NOT_TRUE", "ARTICLE", 0.5, 700, "文章 NOT：散布在多段的列举。", "What is NOT mentioned about the new plant? → Its opening date"),
 ("NOT_TRUE", "JOB_POSTING", 0.4, 600, "招聘 NOT：资格/职责列表。", "What is NOT listed as a responsibility? → Hiring staff"),
 ("INFERENCE", "ARTICLE", 2.0, 700, "文章推断：人物/公司状态的稳妥推论。", "What is suggested about Harlow Foods? → It has received positive reviews."),
 ("INFERENCE", "EMAIL", 2.0, 700, "邮件推断：收发件人关系、此前发生了什么。", "What is implied about Mr. Wu? → He has ordered from the shop before."),
 ("INFER_WHO", "NOTICE", 0.6, 600, "公告对象推断。", "For whom is the notice intended? → Hotel guests"),
 ("INFER_WHO", "JOB_POSTING", 0.6, 600, "招聘广告：应聘者/发布者推断。", "What kind of business is most likely hiring? → A travel agency"),
 ("INFER_WHO", "CHAT", 0.5, 700, "群聊成员身份推断。", "Who most likely is Mr. Sato? → A warehouse supervisor"),
 ("INFER_NEXT", "CHAT", 0.6, 700, "群聊末尾的下一步行动。", "What will Ms. Hale most likely do next? → Call the caterer"),
 ("INTENT", "TEXT_MSG", 1.0, 700, "短信链意图：2 人对话的语用功能。", "What does Ben mean when he writes, 'That works'? → He agrees to a time."),
 ("INTENT", "CHAT", 1.0, 700, "群聊意图：需确认引语回应的是谁的哪句话。", "What does Kim imply when she writes, 'Not again'? → A problem has happened before."),
 ("INSERTION", "ARTICLE", 1.2, 700, "文章插入句：看人物/事件顺序与指代。", "[1]–[4] 中放 'She later joined the board.'"),
 ("INSERTION", "EMAIL", 0.5, 700, "邮件/信件插入句：请求与说明的衔接。", "[1]–[4] 中放 'I have enclosed a copy for your records.'"),
 ("INSERTION", "LETTER", 0.3, 700, "信件插入句。", "[1]–[4] 中放 'We regret any inconvenience this may cause.'"),
 ("SYNONYM", "ARTICLE", 1.0, 700, "文章同义词题。", "'run' in paragraph 1 is closest in meaning to → manage"),
 ("SYNONYM", "EMAIL", 0.8, 700, "邮件同义词题。", "'address' in line 3 is closest in meaning to → deal with"),
 ("SYNONYM", "MULTI", 1.2, 700, "多篇中的同义词题（toeicstory：多集中于双/三篇）。", "In the second e-mail, 'secure' is closest in meaning to → obtain"),
 ("CALC_LOOKUP", "INVOICE", 0.8, 600, "发票计算：单价×数量、折扣、运费。", "How much was the customer charged for shipping? → $15"),
 ("CALC_LOOKUP", "SCHEDULE", 0.5, 600, "日程对照：找符合条件的场次。", "Which session can Ms. Kay attend? → Session C"),
 ("CROSS_REF", "DOUBLE", 3.0, 700, "双篇连锁：每组约 1–2 题（gotop/toeicstory）。", "Text1 规则 + Text2 个案 → 推出适用条件"),
 ("CROSS_REF", "TRIPLE", 6.0, 800, "三篇连锁：每组约 2–3 题，常需三篇中两篇对照，最难。", "网页（价目表）+发票+投诉邮件 → 哪项收费有误"),
 ("DETAIL", "TRIPLE", 3.0, 700, "三篇中的单篇细节题：先做，再做连锁题（P7 多篇策略）。", "According to the invoice, when was the order placed?"),
 ("DETAIL", "DOUBLE", 2.0, 600, "双篇中的单篇细节题。", "According to the flyer, where is the event held?"),
 ("MAIN_PURPOSE", "MULTI", 2.0, 600, "多篇中每篇的目的题（多为第一题）。", "What is the purpose of the first e-mail?"),
 ("DETAIL", "TEXT_MSG", 1.0, 400, "短信细节：时间地点与谁做什么。", "Where is Ana waiting? → At the main entrance"),
 ("INFERENCE", "REVIEW", 0.6, 700, "评价推断：评分理由、是否会再光顾。", "What is suggested about the reviewer? → She will return to the restaurant."),
 ("DETAIL", "INSTRUCTIONS", 0.8, 700, "说明书/保修：条件与例外。", "What is NOT covered by the warranty? → Damage from misuse"),
]
QN = {q[0]: q[1] for q in P7Q}
TN = {t[0]: t[1] for t in TX}
for q, t, est, b, d, ex in X:
    pre = ["QT.P7." + q, "TX." + t]
    if t == "TRIPLE" and q == "CROSS_REF": pre.append("QT.P7X.CROSS_REF.DOUBLE")
    N(f"QT.P7X.{q}.{t}", f"{QN[q].split('（')[0]} × {TN[t].split('（')[0]}", L, "QT.P7." + q, pre, P7, b, d, ex,
      est=est, basis="derived",
      v0={"DETAIL": ["R1"], "DETAIL_NUMBER": ["R1"], "INFERENCE": ["R3"], "NOT_TRUE": ["R4"], "CROSS_REF": ["R5"],
          "INSERTION": ["R6"], "SYNONYM": ["R2"], "INTENT": ["R3"], "TRUE_INDICATED": ["R1"]}.get(q, []),
      src="设问类型题数 × 文本类型份额（估计）；意图题位置据 gotop ARE001800、插入句位置据同源")

# ================================================================ strategy
L = "strategy"
N("ST", "应试技巧层", L, None, [], P567, 400, "时间、顺序、定位、排除、放弃、涂卡与复盘。", "—", basis="aggregate", v0=["S1", "S2"])
N("ST.TIME", "时间分配", L, "ST", [], P567, 400, "75 分钟 100 题的配速。", "—", basis="aggregate", v0=["S1"])
N("ST.ORDER", "做题顺序", L, "ST", [], P567, 600, "Part 间与 Part 内的顺序。", "—", basis="aggregate")
N("ST.LOCATE", "定位", L, "ST", [], P67, 400, "先题后文、关键词与改写定位。", "—", basis="aggregate", v0=["R1"])
N("ST.ELIM", "排除", L, "ST", [], P567, 600, "错误选项识别与排除。", "—", basis="aggregate")
N("ST.GIVEUP", "放弃与猜题", L, "ST", [], P567, 400, "设定放弃线，不留空。", "—", basis="aggregate", v0=["S2"])
N("ST.BUBBLE", "涂卡（纸笔考试）", L, "ST", [], P567, 400, "答题卡填涂节奏。", "—", basis="aggregate")
N("ST.REVIEW", "诊断·复盘·模考", L, "ST", [], P567, 400, "按题型诊断、错题归因、限时模考。", "—", basis="aggregate")
S = [
 ("TIME", "TOTAL_PLAN", "整卷配速（P5 10–12 / P6 8–10 / P7 ≥53–55 分钟）", 600, ["FD.READ.SPEED_150"],
  "中英日韩来源共识：P5+P6 约 20 分钟，P7 留 50–55 分钟（P5-15、strategy_findings_summary）。", "开考 0:00 P5 → 0:11 P6 → 0:20 P7 开始", 0.6, ["S1", "S2"]),
 ("TIME", "PER_ITEM_P5", "P5 单题限时（词性 5–15 秒 / 词汇 ≤30 秒）", 600, ["QT.P5.IDENTIFY"],
  "结构题秒答、词汇题≤30 秒，超时即猜（english-route、toeicstory 1061）。", "词性题 10 秒内；卡 30 秒 → 选一个，标记", 0.45, ["S1"]),
 ("TIME", "PER_SET_P7", "P7 每题/每组用时目标", 700, ["ST.TIME.TOTAL_PLAN"],
  "单篇每题约 1 分钟、三篇组约 5–6 分钟；以时间表检查点核对。", "2 题短信 ≈ 1.5 分钟；三篇 5 题 ≈ 6 分钟", 0.45, ["S1"]),
 ("TIME", "CHECKPOINTS", "看表检查点（如 147 题时剩 X 分钟）", 700, ["ST.TIME.TOTAL_PLAN"],
  "在固定题号核对剩余时间，落后就提速或放弃难题（english-route 看表检查点）。", "Q131 前 ≤ 12 分钟；Q147 前 ≤ 20 分钟；Q176 时剩 ≥ 25 分钟", 0.35, ["S1"]),
 ("ORDER", "PART_SEQUENCE", "Part 间顺序（按序 vs 先做 P7）", 700, ["ST.TIME.TOTAL_PLAN"],
  "多数来源按顺序做；倒序有争议。官方规定听力时间不得翻看阅读（违者可取消成绩）。", "默认 P5→P6→P7；仅在模考验证过后才尝试先 P7", 0.2, []),
 ("ORDER", "WITHIN_P7", "P7 内部顺序（先易后难，多篇不整块留后）", 700, ["ST.ORDER.PART_SEQUENCE", "QT.P7.CROSS_REF"],
  "先拿把握大的题，耗时 NOT/长推断留后；多篇不要整块留到最后（P7-13）。", "三篇组：先做单篇细节，再做连锁题", 0.35, ["S2"]),
 ("ORDER", "HARD_ITEMS_LAST", "难题后做（插入句/NOT 题延后）", 700, ["ST.ORDER.WITHIN_P7", "QT.P7.NOT_TRUE"],
  "插入句、NOT 题放到同组最后做；做完其他题后对全文已熟悉。", "先答 1–3 题，最后做 [1]–[4] 位置题", 0.3, ["S2"]),
 ("LOCATE", "QUESTION_FIRST", "先读题干再回文定位", 400, ["FD.READ.SCAN"],
  "先看题干（判断题型）带关键词回文，避免无目的通读（P7-01；中英日韩共识 TOP1）。", "Q: When will the store reopen? → 扫读 'reopen' 所在句", 0.6, ["R1"]),
 ("LOCATE", "KEYWORD_SCAN", "关键词选择（专名/数字/独特名词）", 400, ["ST.LOCATE.QUESTION_FIRST"],
  "优先用人名、日期、数字、少见名词作定位词，不用 company/new 等泛词。", "Q 中 'Brightway Hotel' 比 'hotel' 更好定位", 0.4, ["R1"]),
 ("LOCATE", "PARAPHRASE_MATCH", "按改写而非原词匹配", 600, ["ST.LOCATE.KEYWORD_SCAN", "VO.PARA"],
  "定位到原句后在选项中找同义改写，照搬原词的选项警惕（P7-09）。", "原文 'postponed' → 正解 'delayed'，干扰项含 'posted'", 0.5, ["R2"]),
 ("LOCATE", "QUESTION_ORDER", "题序≈文序、两题一组读", 600, ["ST.LOCATE.QUESTION_FIRST"],
  "细节题顺序基本与原文顺序一致；读两题→读一段（hackersingang、english-study-cafe）。", "Q1 答案在第 1 段，Q2 多在第 2 段", 0.35, ["R1"]),
 ("LOCATE", "DEPTH_BY_QTYPE", "按题型决定读多少", 700, ["ST.LOCATE.QUESTION_ORDER", "QT.P7.INFERENCE"],
  "主旨/有关键词细节题只读相关部分；NOT/推断读到能确定为止（P7-14）。", "推断题读完整段再选", 0.3, ["R3"]),
 ("ELIM", "OPTIONS", "逐项排除法", 600, ["ST.LOCATE.PARAPHRASE_MATCH"],
  "四个选项逐个回文核对，划掉无依据项（P7-04；800+ 不应依赖消去法，IIBC methods07）。", "A 原文没提 / B 时间错 / C 张冠李戴 → D", 0.4, ["R4"]),
 ("ELIM", "TRAP_TYPES", "错误选项套路（未提及/部分正确/张冠李戴/过度推断/照搬原词）", 600, ["ST.ELIM.OPTIONS"],
  "掌握错误选项套路并在复盘时归类（P7-10；K7 错误选项识别）。", "选项 'The store will close permanently' ← 原文只说 temporarily", 0.45, ["R3", "R4"]),
 ("ELIM", "SCOPE", "范围陷阱（过宽/过窄/绝对化）", 700, ["ST.ELIM.TRAP_TYPES", "QT.P7.MAIN_PURPOSE"],
  "主旨题选项过宽过窄排除；all/always/never 等绝对化表述多为错（egsty 范围陷阱）。", "原文只讲一个部门 → 'company-wide changes' 过宽", 0.3, ["R3"]),
 ("GIVEUP", "NO_BLANK", "不留空（答错不扣分）", 400, [],
  "ETS 考生手册：答错不扣分；任何题都不要空着。", "剩 1 分钟 → 未答题全部涂同一字母", 0.4, ["S2"]),
 ("GIVEUP", "CUTOFF_RULE", "设定放弃线（卡住即猜，先跳后回）", 600, ["ST.GIVEUP.NO_BLANK", "ST.TIME.PER_ITEM_P5"],
  "P5/6 单题 ≤30 秒、P7 单题超 1–1.5 分钟即猜并标记，有时间再回（官方：可跳题后回）。", "NOT 题读 1 分钟仍无头绪 → 选最可能项，继续", 0.5, ["S2"]),
 ("GIVEUP", "TARGET_BASED", "按目标分数决定放弃哪些题", 600, ["ST.GIVEUP.CUTOFF_RULE"],
  "目标 600 可主动放弃部分三篇连锁/插入句，把时间换给单篇细节（haradaeigo 分数段策略）。", "目标 600：最后两组三篇只做细节题", 0.3, ["S2"]),
 ("BUBBLE", "BATCH", "分段涂卡（每页/每组集中涂）", 400, [],
  "按页或题组集中涂卡，节省切换时间；全卷涂卡 ≤3 分钟（toeicstory 1061）。官方规定不得在试题本写字。", "每做完一页 P5 统一涂 10 题", 0.2, []),
 ("BUBBLE", "FINAL_MINUTES", "最后几分钟统一猜涂", 400, ["ST.BUBBLE.BATCH", "ST.GIVEUP.NO_BLANK"],
  "距结束约 2–3 分钟时停下，把未答题全部涂上。", "剩 3 分钟 → 涂完未答题，再回到当前题", 0.25, ["S2"]),
 ("REVIEW", "DIAGNOSE_BY_TYPE", "按题型统计正确率诊断弱项", 400, [],
  "按题型（可对照官方 Abilities Measured）统计正确率，针对弱项练（G-01）。", "P5 词性 90% / 介词 60% → 本周专攻介词", 0.35, []),
 ("REVIEW", "ERROR_CAUSE_LOG", "错题按原因分类（词汇/语法/定位/时间）", 600, ["ST.REVIEW.DIAGNOSE_BY_TYPE"],
  "错题四类原因（不认识词/不会语法/没定位到/没时间）（haradaeigo；中文论坛共识：错题本+生词本）。", "Q168 错因：定位到了但没识别改写 → 归 VO.PARA", 0.4, []),
 ("REVIEW", "EXPLAIN_DISTRACTORS", "逐项说明错误选项为何错", 600, ["ST.REVIEW.ERROR_CAUSE_LOG", "ST.ELIM.TRAP_TYPES"],
  "复盘时说明每个错误选项错在哪（G-02，6 本书提及）。", "B 错：原文是 'next Friday' 不是 'this Friday'", 0.35, []),
 ("REVIEW", "TIMED_MOCK", "限时整卷模考（含涂卡）", 600, ["ST.TIME.TOTAL_PLAN"],
  "用官方/真题整套限时模考并换算分数，留 1–2 套考前做（G-03；共识 TOP1）。", "周六 75 分钟整卷 → 换算表估分 → 按题型复盘", 0.5, ["S1"]),
 ("REVIEW", "AUDIO_SHADOW", "用题目音频复习阅读（听写/跟读）", 600, ["FD.READ.CHUNK"],
  "Part5/6 听音频写空格、Part7 跟音频读（G-04；7 本书提及，IIBC 公式题集附音频）。", "P7 文章跟读 3 遍，目标速度 150 wpm", 0.25, ["S1"]),
 ("REVIEW", "VOCAB_FROM_ITEMS", "从真题/错题中摘词（生词本）", 400, ["FD.VOC.NGSL_CORE"],
  "单词从真题题干与选项中摘，按场景词包归档（V-03；中文论坛共识）。", "错题中的 'complimentary' → 归入 HOTEL_LODGING + SYN_ADJ", 0.3, ["V4"]),
 ("REVIEW", "SPEED_REPEAT", "测时→复读同一篇提速", 600, ["FD.READ.CHUNK"],
  "先测用时，再以目标用时反复读同一篇（P7-17，IIBC 速读演习 5 步）。", "第一次 4 分钟 → 第三次 2.5 分钟", 0.25, ["S1"]),
]
for g, k, nm, b, pre, d, ex, w, v in S:
    N(f"ST.{g}.{k}", nm, L, "ST." + g, pre, P567 if g in ("TIME", "GIVEUP", "BUBBLE", "REVIEW") else P67 if g == "LOCATE" else P567,
      b, d, ex, w=w, basis="impact_estimate", v0=v,
      src="技巧节点无直接题数；权重=影响题数×书目/来源共识度的估计")
