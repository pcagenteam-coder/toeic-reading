import json
OUT="/workspace/projects/58061e9e-e075-4f3f-880c-32a61b21a72c/data/strategies/books.json"
U=dict(
HK="https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000007732270",
HKB="https://hackersbook.com/book/detail/216",
HK777="https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012553679",
HKTIP="https://hackerslive.co.kr/contents/?bid=secret_method&m=bbs&uid=218892",
HKBRD="https://www.hackers.co.kr/?c=s_toeic%2Ftoeic_board%2FB_TOEIC_secret&uid=1563266",
SN="https://www.bookprice.co.kr/compare.jsp?isbn=9791159242083",
SN56="https://www.gilbut.co.kr/book/view?bookcode=BN001486",
SNP56="https://www.yes24.com/product/goods/126795158",
YST="https://www.ybmbooks.com/book/book_view.asp?seq=2576",
ETSIN="https://www.ybmbooks.com/reader/free_class_toeic_primer_rc.asp",
ETS1000="https://www.ybmbooks.com/book/book_view.asp?seq=2961&step_1=&step_2=&step_3=",
ETS1000L="https://m.toeic.ybmclass.com/toeic/toeic_view_app.asp?idx=10008",
XDFRD="http://www.queshu.com/book/10698313/",
XDF1000="http://www.dogwood.com.cn/book/toeic/925.html",
XDFVOC="https://www.dushu.com/book/12641557/",
XDFOG="https://www.dushu.com/book/12142606/",
XDFART="http://gz.xdf.cn/study/toeic/201607/8280589.html",
FLTRP="https://www.books.com.tw/products/CN10236961",
IIBCQ="https://www.iibc-global.org/toeic/support/prep/lr_ud_07.html",
IIBCQ10="https://www.iibc-global.org/toeic/support/prep/lr_ud_10/pr.html",
IIBCP7="https://www.iibc-global.org/toeic/support/prep/lr_part_07/pr.html",
IIBCAM="https://www.iibc-global.org/toeic/test/lr/guide04/guide04_02.html",
DERU="https://www.kinokuniya.co.jp/f/dsg-01-9784866390833",
DERUR="https://english-route.com/toeic-deru1000/",
DERUR2="https://jsjapan.xsrv.jp/tc_kyouzai_deru1000/",
KB="https://www.kinokuniya.co.jp/f/dsg-01-9784023322509",
KBR="https://my-studies.org/toeic-kin-no-bunpo/",
KF="https://www.kinokuniya.co.jp/f/dsg-01-9784023324640",
KFM="https://www.monokakido.jp/ja/wordbook/expressgp2/index.html",
BT="https://www.kinokuniya.co.jp/f/dsg-01-9784023319332",
BTR="http://toiguide.jp/bunpotokkyu/",
K56="https://www.kinokuniya.co.jp/f/dsg-01-9784757428706",
K56EJ="https://ej.alc.co.jp/tag/STUDY/20170922-toeicbook-p56",
K56AMZ="https://www.amazon.co.jp/%E3%80%90%E6%96%B0%E5%BD%A2%E5%BC%8F%E5%95%8F%E9%A1%8C%E5%AF%BE%E5%BF%9C%E3%80%91TOEIC-%E3%83%86%E3%82%B9%E3%83%88-%E7%A9%B6%E6%A5%B5%E3%81%AE%E3%82%BC%E3%83%9F-Part-%E3%83%92%E3%83%AD/dp/4757428707",
K7="https://book.alc.co.jp/book/b10029664.html",
K7EJ="https://ej.alc.co.jp/tag/STUDY/20170929-toeicbook-p7",
K7R="https://home-native.com/ultimate7/",
)
B={
"HK":"해커스 토익 Reading (David Cho, 해커스어학연구소, 기본서)",
"HK777":"해커스 토익 Part 7 집중공략 777",
"SN":"시나공 토익 Reading (구원, 길벗이지톡)",
"SN56":"시나공 토익 출제순위 파트 5&6 (구원, 길벗이지톡)",
"SNP56":"시나공 토익 파트 5, 6 실전문제집 (강진오, 길벗이지톡)",
"YST":"YBM 전략토익 RC (토익 주관사 YBM)",
"ETSIN":"ETS 토익 정기시험 기출입문서 RC (YBM)",
"ETS1000":"ETS 토익 정기시험 기출문제집 1000 RC (Vol.4/Vol.5, YBM)",
"XDFRD":"TOEIC托业阅读专项突破（新东方托业考试指定培训教材，群言出版社）",
"XDF1000":"托业阅读全真模拟1000题（新东方大愚，群言出版社）",
"XDFVOC":"托业词汇词根+联想记忆法（俞敏洪，新东方）",
"XDFOG":"托业考试官方指南（ETS，北京语言大学出版社/新东方大愚）",
"FLTRP":"新托业考试官方指南·听力 阅读（Grant Trew，外研社，ETS授权；原书 Tactics for TOEIC）",
"IIBCQ":"公式TOEIC Listening & Reading 問題集（IIBC，1–13）",
"IIBCP7":"公式TOEIC Listening & Reading Part 7 速読演習（IIBC）",
"DERU":"TOEIC L&Rテスト 文法問題 でる1000問（TEX加藤，アスク出版）",
"KB":"TOEIC L&R TEST 出る問特急 金の文法（TEX加藤，朝日新聞出版）",
"KF":"TOEIC L&R TEST 出る単特急 金のフレーズ（TEX加藤，朝日新聞出版）",
"BT":"1駅1題 TOEIC L&R TEST 文法特急（花田徹也，朝日新聞出版）",
"K56":"TOEIC L&Rテスト 究極のゼミ Part 5&6（ヒロ前田，アルク）",
"K7":"TOEIC L&Rテスト 究極のゼミ Part 7（ヒロ前田，アルク）",
}
books_meta=[
 dict(key="HK",region="KR",title=B["HK"],toc_public=True,content="文法20章+词汇12章+Part6 2章+Part7 20章",sources=[U["HK"],U["HKB"]]),
 dict(key="HK777",region="KR",title=B["HK777"],toc_public=True,content="Part7 文本9类出题模式 + 7类设问策略 + 模考",sources=[U["HK777"]]),
 dict(key="SN",region="KR",title=B["SN"],toc_public=True,content="Part5/6 按'不翻译就能解/需要翻译'切分；Part7 按设问7类+文本9类",sources=[U["SN"]]),
 dict(key="SN56",region="KR",title=B["SN56"],toc_public=True,content="按出题频率（每月→两年一次）切分语法；词汇按词性；Part6单独一章",sources=[U["SN56"]]),
 dict(key="SNP56",region="KR",title=B["SNP56"],toc_public=True,content="20套 Part5/6 实战（只有试题，含'파트별 유형 및 전략'导言）",sources=[U["SNP56"]]),
 dict(key="YST",region="KR",title=B["YST"],toc_public=True,content="Part5&6 12单元；Part7 设问8类+文本6类",sources=[U["YST"]]),
 dict(key="ETSIN",region="KR",title=B["ETSIN"],toc_public=True,content="由官方配套免费讲座目录还原：Part5 14单元、Part6 5类题、Part7 3章",sources=[U["ETSIN"]]),
 dict(key="ETS1000",region="KR",title=B["ETS1000"],toc_public=True,content="仅10套真题+解析，无技巧章节",sources=[U["ETS1000"],U["ETS1000L"]]),
 dict(key="XDFRD",region="CN",title=B["XDFRD"],toc_public=True,content="Part5/6 语法7单元+搭配/词汇；Part7 只按7种文本类型",sources=[U["XDFRD"]]),
 dict(key="XDF1000",region="CN",title=B["XDF1000"],toc_public=True,content="10套模拟题，无技巧章节；简介强调正确答案特征与错项陷阱",sources=[U["XDF1000"]]),
 dict(key="XDFVOC",region="CN",title=B["XDFVOC"],toc_public=True,content="Word List 词表（重点/认知词汇）+ 语法精要",sources=[U["XDFVOC"]]),
 dict(key="XDFOG",region="CN",title=B["XDFOG"],toc_public=True,content="2套官方全真题+题型范例，无技巧章节",sources=[U["XDFOG"]]),
 dict(key="FLTRP",region="CN",title=B["FLTRP"],toc_public=True,content="28单元螺旋式：每单元一个Part一个技能焦点",sources=[U["FLTRP"]]),
 dict(key="IIBCQ",region="JP",title=B["IIBCQ"],toc_public=True,content="2套试题+解答解析（含误答解说、Words&Phrases），无技巧章节",sources=[U["IIBCQ"],U["IIBCQ10"]]),
 dict(key="IIBCP7",region="JP",title=B["IIBCP7"],toc_public=True,content="速读基础训练3法 + 文本类型9单元×5步 + Part7实战54题",sources=[U["IIBCP7"]]),
 dict(key="DERU",region="JP",title=B["DERU"],toc_public=True,content="按题型7章（品詞/動詞/前置詞or接続詞/代名詞/前置詞/関係詞/ペア表現・語法・数・比較）+模试13套",sources=[U["DERU"],U["DERUR"]]),
 dict(key="KB",region="JP",title=B["KB"],toc_public=True,content="同でる1000问的7类题型；82条'金のルール'",sources=[U["KB"],U["KBR"]]),
 dict(key="KF",region="JP",title=B["KF"],toc_public=True,content="按目标分数段（600/730/860/990）切分1000词+补充专题",sources=[U["KF"]]),
 dict(key="BT",region="JP",title=B["BT"],toc_public=True,content="按分数段（550/730/900+）分章；第0章讲两种解题路径",sources=[U["BT"],U["BTR"]]),
 dict(key="K56",region="JP",title=B["K56"],toc_public=True,content="Part5 按题型6类；Part6 独立型/文脈型(时态/词汇/代词·接续副词)/文选择",sources=[U["K56"],U["K56EJ"]]),
 dict(key="K7",region="JP",title=B["K7"],toc_public=True,content="15次ゼミ：设问类型别 + 改写(パラフレーズ) + 错误选项识别；题型参照官方 Abilities Measured",sources=[U["K7"],U["K7R"]]),
]
for i,b in enumerate(books_meta,1): b["id"]=f"B{i:02d}"

T=[]
def t(id,part,cat,tech,steps,applies,keys,srcs,ev,nodes=None,note=None):
    d=dict(id=id,part=part,category=cat,technique=tech,steps=steps,applies_to=applies,
           books=[B[k] for k in keys],mention_count=len(keys),sources=[U[s] for s in srcs],
           evidence=ev)
    if nodes: d["maps_to_nodes"]=nodes
    if note: d["note"]=note
    T.append(d)

# ---------- Part 5 ----------
t("P5-01","Part5","题型识别","先扫四个选项判断题型（品词/动词形/介词vs连词/代词/词汇），再决定只看空格周边还是读全句。",
 ["看选项：同词根不同词形→品词题；同一动词不同时态语态→动词题；介词连词副词混排→连接题；四个不同词义→词汇题",
  "语法类（结构先行/速读）：只看空格前后及句子结构",
  "词汇类（语境先行/精读）：读全句找语义线索",
  "按题型分配时间，结构题快速作答"],
 "Part 5 全部题；Part 6 的独立型题",["K56","DERU","BT","SN"],["K56EJ","DERUR2","BTR","SN"],
 "目录+出版社/书评描述（究極のゼミ为讲座文章摘录；文法特急为书评转述第0章'構文先行型/文脈先行型'）",["G1","S1"])
t("P5-02","Part5","品词","品词题按空格位置定词性：限定词/介词后→名词，名词前→形容词，be/系动词后→形容词，完整句中修饰动词/形容词/全句→副词。",
 ["确认是品词题（同词根四词形）","看空格左侧（冠词/所有格/介词/be/助动词）和右侧（名词/动词/句号）",
  "按位置规则定词性，再用后缀（-tion/-ive/-ly 等）挑出对应选项","必要时检查单复数与名词种类（人vs物）"],
 "Part 5 品词题（各书中题量最大的一类）；Part 6 同类空格",
 ["SN","HK","DERU","KB","K56","FLTRP","XDFRD","YST","ETSIN"],
 ["SN","HK","DERU","KB","K56","K56EJ","FLTRP","XDFRD","YST","ETSIN","XDFART"],
 "目录章节（시나공 'Unit01 빈 칸 앞 뒤만 보고 푼다'；でる1000問 第1章品詞334问为最大章）",["G1","G2"])
t("P5-03","Part5","句子结构","先数句子的谓语动词与连接词数量：缺谓语就选限定动词，已有谓语则选非谓语或连接成分。",
 ["找出句中已有的限定动词","数连接词：从句数=连接词数+1","缺谓语→选谓语形式；不缺→选 to do/-ing/-ed 或连接词/介词"],
 "动词形态题、介词/连词/动词位置题",["SN","HK"],["SN","HK"],
 "目录章节（시나공 'Unit02 동사의 개수와 문장의 형태로 푼다'；해커스 'Ch01 동사 자리'）",["G4","G7"])
t("P5-04","Part5","动词","动词题按'数→态→时'三步排查：主语单复数定数、有无宾语定主被动、时间状语定时态。",
 ["找真正主语（跳过修饰语）定单复数","看空格后有无宾语：无宾语且及物→被动","找时间线索（since/by the time/next/ago 等）定时态",
  "检查假设语气、要求/建议类 that 从句用动词原形"],
 "Part 5 动词题；Part 6 动词题需结合上下文",
 ["SN","HK","DERU","KB","K56","YST","ETSIN","XDFRD"],["SN","HK","DERU","KB","K56","YST","ETSIN","XDFRD"],
 "目录章节（시나공 'Unit03 주어의 수와 목적어 유무 / Unit04 시제 단서'）",["G3","G4","G5"])
t("P5-05","Part5","连接：介词vs连词","介词、连词、副词三选一时看空格后面：接名词（短语）用介词，接主谓完整从句用连词，句子已完整且两句间仅需逻辑衔接用副词。",
 ["看空格后是否有主语+谓语","名词/动名词→介词；从句→连词","再按语义（时间/条件/让步/原因）在同类中选"],
 "Part 5 '前置詞 or 接続詞' 题；Part 6 连接题",
 ["DERU","KB","HK","SN","K56","XDFRD","YST","FLTRP"],["DERU","KB","HK","SN","K56","XDFRD","YST","FLTRP"],
 "目录章节（でる1000問/金の文法 第3章；해커스 'Ch17-06 부사절 접속사 vs. 전치사'）",["G7"])
t("P5-06","Part5","代词","代词题先看位置定格（主格/宾格/所有格/所有代词/反身），再看指代对象的单复数和人/物。",
 ["空格位置：主语→主格；动词/介词后→宾格；名词前→所有格；独立作主宾→所有代词","主宾为同一人或强调→反身代词（by oneself）",
  "不定代词 one/another/the other(s)、some/any、most/almost 按数和可数性选","需要时再读语义确定所指"],
 "Part 5 代词题；Part 6 代词（需看前文所指）",
 ["HK","SN","DERU","KB","K56","FLTRP","YST","ETSIN","XDFRD"],["HK","SN","DERU","KB","K56","FLTRP","YST","ETSIN","XDFRD"],
 "目录章节（시나공 'Unit09 주변을 볼지 해석을 할지 구분 / Unit10 단수/복수, 사람/사물 확인'）",["G8"])
t("P5-07","Part5","关系词/名词从句","关系词与名词从句连接词：看先行词有无、指人还是物，再看后面从句是否完整。",
 ["有先行词→关系代词/关系副词；无先行词→名词从句连接词（what/whether/that 等）","先行词人/物→who/which","后接不完整句（缺主/宾）→关系代词或 what；完整句→关系副词或 that",
  "注意介词+关系代词、数量表达+of whom/which、复合关系词 whoever/whatever"],
 "Part 5 关系词/名词从句题",["SN","HK","DERU","KB","K56","XDFRD","ETSIN"],["SN","HK","DERU","KB","K56","XDFRD","ETSIN"],
 "目录章节（시나공 'Unit11 선행사의 유/무, 사람/사물 … 완전/불완전 절을 구분'）",["G6"])
t("P5-08","Part5","非谓语","非谓语题：记住只接 to do 或只接 -ing 的动词/名词/形容词，分词按与被修饰名词的主动/被动关系选 -ing 或 -ed。",
 ["先确认句中已有谓语→空格为非谓语","查固定搭配（plan to / consider -ing / be committed to -ing 等）","分词：名词主动做→-ing；被动→-ed；情感动词修饰人多用 -ed"],
 "Part 5 to不定式/动名词/分词题",["HK","SN","YST","ETSIN","XDFRD","FLTRP"],["HK","SN","YST","ETSIN","XDFRD","FLTRP"],
 "目录章节（시나공 'Unit05 3/10기능과 공식 / Unit06 5기능과 공식'；外研社 Unit12 gerunds and infinitives）",["G4","G5"])
t("P5-09","Part5","比较","比较题看标志词：than→比较级，the+…of/in/among→最高级，as…as→原级；强调比较级用 much/even/far。",
 ["找 than / the / as / of all 等标志","确定原级/比较级/最高级","检查修饰比较级的副词"],
 "Part 5 比较题",["HK","SN","DERU","ETSIN","XDFRD"],["HK","SN","DERU","ETSIN","XDFRD"],"目录章节",["G2"])
t("P5-10","Part5","名词","名词题除了词性还要辨可数/不可数、限定词搭配、人名词与事物名词、复合名词。",
 ["看冠词 a/an 或复数形式判断可数性","看限定词（each/many/much/a number of）","语义上是'人'还是'事'（applicant vs application）","名词+名词的复合名词（customer satisfaction）"],
 "Part 5 名词相关品词题",["HK","SN","XDFRD","K56","YST","ETSIN"],["HK","SN","XDFRD","K56","YST","ETSIN"],
 "目录章节（해커스 Ch10 '가산/불가산·한정사·사람명사 vs 사물명사·복합명사'）",["G1"])
t("P5-11","Part5","介词","介词题先按'空格前后搭配'快速解（时间点/时段、地点），无法判断时再按语义（原因/让步/目的/关于）翻译解。",
 ["看前后搭配：in/on/at、by/until、for/during、within","看动词/形容词/名词+介词固定搭配","剩余按语义：despite/because of/regarding 等"],
 "Part 5 介词题",["HK","SN","DERU","KB","YST"],["HK","SN","DERU","KB","YST"],
 "目录章节（시나공 'Unit13 빈 칸 앞 뒤를 보고 푼다 / Unit14 해석해서 푼다'）",["G7"])
t("P5-12","Part5","词汇","词汇题先找搭配与语法线索（介词搭配、及物性、固定短语）'不翻译解'，线索不足再读全句按语义选。",
 ["看空格前后的介词/宾语，排除搭配不对的选项","判断动词及物/不及物、名词可数性","仍剩多个选项→读全句选语义合适者"],
 "Part 5/6 词汇题（动词/名词/形容词/副词）",["SN","HK","K56","SN56","XDFRD","FLTRP","KF","YST"],["SN","HK","K56","SN56","XDFRD","FLTRP","KF","YST"],
 "目录章节（시나공 Section3 '필요할 때만 해석해서 푼다'；해커스 Vocabulary '어구·짝을 이루는 표현'）",["V1","V2","V3","V4"])
t("P5-13","Part5","词汇","近义词与多义词：成组辨析意思相近的词，记住常见词的商务义项。",
 ["按'유사의미어'成组记（动词/名词/形容词副词）","记多义词的考试义项","做题时用搭配区分近义词"],
 "Part 5 词汇题；Part 7 同义词题",["HK","KF"],["HK","KF"],"目录章节（해커스 Vocabulary Section 3；金のフレーズ Supplement '多義語'）",["V4"])
t("P5-14","Part5","学习策略","按出题频率排序学习：先攻高频题型（品词、动词、介词/连词），低频语法点后补。",
 ["统计/参照题型频率表","先练高频章","低频章节（关系词、特殊句式）放后"],
 "Part 5 复习规划",["SN56","DERU","BT","KB"],["SN56","DERUR","BTR","KB"],
 "目录（시나공 출제순위 按'每月/两个月/…/两年一次'分章）+书评（でる1000问频率排序；文法特急出题频度排行15位）",["G1"])
t("P5-15","Part5","时间策略","给 Part 5（及 Part 6）设硬性时限，把时间省给 Part 7：例如 Part 5&6 约20分钟（究極のゼミ）或15分钟内（시나공实战集），品词题每题约5–15秒。",
 ["做题计时","结构题即答，词汇难题先猜后标记","整套模考中控制 Part 5/6 总时长"],
 "Part 5/6 时间管理",["K56","SNP56","FLTRP","BT"],["K56EJ","SNP56","FLTRP","BTR"],
 "讲座文章/书店简介/目录（外研社 Unit5 'Using your time wisely'）",["S1","S2"])
t("P5-16","Part5","句子结构","先划掉修饰语（介词短语、分词短语、插入从句），找出主干后再判断空格成分。",
 ["识别介词短语/从句等修饰成分（修饰语'泡泡'）","找主语与谓语","确定空格是必需成分还是修饰语"],
 "Part 5 结构类题；长句阅读",["HK","SN","YST","ETSIN"],["HK","SN","YST","ETSIN"],
 "目录章节（해커스 'Ch02-05 수식어 거품'；시나공 'Unit04 필수어와 수식어'）",["G1","G3"])
t("P5-17","Part5","构词","用词缀判断生词词性和词义：后缀定词性，词根词缀辅助记忆。",
 ["记常见名/形/副/动后缀","遇生词按后缀判断词性","背词时按词根+联想"],
 "Part 5 品词题；词汇记忆",["FLTRP","XDFVOC"],["FLTRP","XDFVOC","XDFART"],
 "目录章节（外研社 Unit19 suffixes and prefixes）+简介（词根+联想记忆法）",["G1"])
t("P5-18","Part5","特殊句式","特殊句式要记固定形式：要求/建议类 that 从句用动词原形，省略 if 的假设倒装，并列结构前后词性一致，否定词前置倒装。",
 ["看到 request/suggest/require that → 动词原形","Should/Had/Were 开头→倒装假设","and/or 连接的成分保持同形（平行结构）"],
 "Part 5 中低频语法题",["HK","SN","YST","XDFRD"],["HK","SN","YST","XDFRD"],"目录章节（해커스 Ch06/Ch20；전략토익 '특수구문'；新东方 '虚拟语气'）",["G4"])
t("P5-19","Part5","连接：成对表达","成对表达看搭档词：both–and、either–or、neither–nor、not only–but also、whether–or。",
 ["看句中是否已有 both/either/neither/not only/whether","选对应搭档","注意就近原则的主谓一致"],
 "Part 5 成对表达题（书评称近年出题减少）",["DERU","HK","SN","ETSIN"],["DERU","HK","SN","ETSIN","BTR"],"目录章节（でる1000問 第7章'ペア表現'；해커스 Ch15 상관접속사）",["G7"])
t("P5-20","Part5","副词","按功能辨副词：时间副词（already/still/yet）、频率副词、强调副词（just/only/even）、so/such/too，以及 also/too/either 等。",
 ["判断空格是副词位置","按句子时态/肯否定选时间副词（yet 用于否定/疑问）","so+形/副，such+名词短语"],
 "Part 5 副词选择题",["HK","SN","SN56"],["HK","SN","SN56"],"目录章节（해커스 Ch13 '부사 선택 1–6'）",["G2"])
t("P5-21","Part5","动词用法","掌握动词句型：及物/不及物、双宾语与宾补动词、宾补用 to do 还是动词原形（make/let/have）。",
 ["判断动词是否可接宾语","记双宾/宾补动词及其被动形式","使役动词后接原形"],
 "Part 5 动词用法（語法）题",["HK","DERU","KB","SN"],["HK","DERU","KB","SN"],"目录章节（해커스 Ch03-03, Ch07-04；でる1000問 第7章'語法'）",["G4","G5"])
t("P5-22","Part5","数量表达","数量表达与名词、动词的单复数必须一致（each/every+单数，a number of+复数，the number of+单数谓语）。",
 ["看数量词","确定后接名词单复数","确定谓语单复数"],
 "Part 5 数量/主谓一致题",["HK","DERU"],["HK","DERU"],"目录章节（해커스 Ch12-02 수량 표현, Ch04-02；でる1000問 第7章'数'）",["G3"])

# ---------- Part 6 ----------
t("P6-01","Part6","阅读方式","Part 6 按顺序通读全文，不要只读空格所在句：只靠本句就能解的题很少（究極のゼミ估计约4题）。",
 ["从标题/首句判断文本类型和主题","按顺序读，到空格时结合已读内容作答","答完回看后文验证（有的线索在后文）"],
 "Part 6 全部题",["K56","SN56","HK","FLTRP"],["K56EJ","SN56","HK","FLTRP","XDFART"],
 "讲座文章（究極のゼミ）+目录（시나공 'Ch13 빈칸 문장만으로는 풀 수 없는 파트 6 문제'；해커스'지문의 흐름을 예상'）",["R6","S1"])
t("P6-02","Part6","题型识别","把 Part 6 题分成'句内独立可解'与'需上下文'两类：前者按 Part 5 方法速答，后者（时态/代词/接续副词/词汇/插入句）必须看前后文。",
 ["先看选项判断题型","独立型→用 Part 5 方法","文脈型→定位相关前后句再选"],
 "Part 6 全部题",["K56","SN56","HK","ETSIN"],["K56","SN56","HK","ETSIN"],
 "目录章节（究極のゼミ'独立型問題/文脈から解く問題1–3/文選択問題'；ETS 기출입문서 Part6 UNIT01–05）",["R6"])
t("P6-03","Part6","时态（语境）","Part 6 时态题以全文时间线为准：本句语法上几个时态都通，要看前后句和发信日期、事件是否已发生。",
 ["找文中日期、已发生/将发生事件","确定空格事件在时间线上的位置","选与时间线一致的时态/语态"],
 "Part 6 动词时态题",["K56","ETSIN","FLTRP"],["K56","ETSIN","FLTRP"],"目录章节（究極のゼミ'文脈から解く問題1（動詞の時制）'；ETS 기출입문서'동사 시제 고르기'；外研社 Unit20）",["G4","R6"])
t("P6-04","Part6","代词（语境）","Part 6 代词题回前文找指代对象，按其单复数、人/物、公司/个人选代词。",
 ["找可能的先行名词","核对数与人/物","代回句子检查语义"],"Part 6 代词题",["K56","ETSIN"],["K56","ETSIN"],
 "目录章节（究極のゼミ'代名詞'；ETS 기출입문서'대명사 고르기'）",["G8","R6"])
t("P6-05","Part6","接续副词","接续副词题判断前后两句的逻辑关系（转折/因果/追加/举例/顺序），再选 however/therefore/in addition/for example 等。",
 ["读空格前一句和本句","判断逻辑关系","选对应接续副词（注意它不能连接两个从句）"],
 "Part 6 接续副词题",["K56","ETSIN","HK","KF"],["K56","ETSIN","HK","KF"],
 "目录章节（究極のゼミ'代名詞・接続副詞'；ETS 기출입문서'접속부사 고르기'；해커스 Ch13-05；金のフレーズ Supplement'前置詞・接続詞・接続副詞'）",["G7","R6"])
t("P6-06","Part6","词汇（语境）","Part 6 词汇题：几个选项在本句都通顺时，以全文主题和前后信息为准。",
 ["本句排除明显不通的","回看全文主题/前后事实","选与上下文一致者"],"Part 6 词汇题",["K56","ETSIN","HK"],["K56","ETSIN","HK"],
 "目录章节（究極のゼミ'文脈から解く問題2（語彙問題）'；ETS 기출입문서'어휘 고르기'；해커스 Part6 Ch01）",["V4","R6"])
t("P6-07","Part6","句子插入","句子插入（文选择）题：先抓全文主题和段落走向，再用指代词、连接词、新旧信息衔接检查候选句是否接得上前后句。",
 ["概括文章主题与该段作用","看空格前后句","检查候选句中的 this/these/they/also/however 等是否有着落","排除话题跑偏或信息重复的句子"],
 "Part 6 每篇1道文选择题",["SN","HK","K56","ETSIN","BT"],["SN","HK","K56","ETSIN","BT"],
 "目录章节（시나공'Unit15 주제와 흐름을 알고 푼다'；해커스'문장 고르기 문제'；究極のゼミ'文選択問題'；ETS 기출입문서'문장 넣기'）",["R6"])

# ---------- Part 7 ----------
t("P7-01","Part7","阅读方式","先看题干（并判断题型），带着关键词回文定位，避免无目的通读。",
 ["读本篇题干，标出人名/日期/数字/动作等关键词","判断题型决定阅读范围","回文扫读定位，精读线索句"],
 "Part 7 单篇与多篇",["FLTRP","IIBCP7","SN","ETS1000"],["FLTRP","IIBCP7","SN","ETS1000L"],
 "目录章节（外研社 Unit7 'Scanning the questions to decide which ones to answer first'；IIBC 速読演習 STEP2'設問文のキーワード'）；ETS 기출문제집为 YBM 配套讲座页'선택적 읽기법'",["R1","S1"],
 "究極のゼミ Part 7 主张'尽量读全文再解'，与此为不同流派，见 taxonomy 差异说明")
t("P7-02","Part7","设问：主旨/目的","主旨/目的题的答案多在开头几行（如 'I am writing to…'），选项过宽或过窄都排除。",
 ["读开头段（시나공：前三行内）","找 purpose 信号句","比较选项范围是否与全文一致"],
 "What is the purpose of… / mainly about…",["SN","HK","HK777","YST","K7","ETSIN"],["SN","HK","HK777","YST","K7R","ETSIN"],
 "目录章节（시나공'Unit01 초반부 세 줄 안에 단서가 있다'）",["R1"])
t("P7-03","Part7","设问：细节","细节（5W1H）题用题干关键词扫读定位，只精读关键词附近的句子，注意选项是原文的改写。",
 ["划题干关键词（专有名词/数字/日期最好定位）","扫读找到对应位置","读前后一两句，选与原文意思一致的改写选项"],
 "When/Where/What/How much 等细节题",["SN","HK","HK777","YST","FLTRP","K7"],["SN","HK","HK777","YST","FLTRP","K7R"],
 "目录章节（시나공'Unit02 키워드 주변에 단서가 있다'；外研社 Unit21 names, numbers, dates or times）",["R1","R2"])
t("P7-04","Part7","设问：NOT/TRUE","NOT/TRUE 题逐个选项回文核对、用排除法；无关键词又耗时的，先跳过最后做。",
 ["先读四个选项抓各自关键词","分段读原文逐一核对（시나공：读三行对照一次）","NOT 题：原文没提或相反的为答案","时间紧时标记跳过，最后回做"],
 "What is NOT mentioned / What is true about…",["SN","HK","HK777","YST","FLTRP","K7"],["SN","HK","HK777","YST","FLTRP","K7R","HKTIP"],
 "目录章节+讲师公开文章（해커스 박영선：无关键词的 NOT/TRUE 留到最后）",["R4","S2"])
t("P7-05","Part7","设问：推断","推断题的依据必须能在原文找到，不靠常识或想象；正确答案是原文信息的稳妥推论。",
 ["找与题干相关的原文信息","只做一步推理","排除原文无依据、过度推断的选项"],
 "most likely / suggested / implied 类题",["SN","HK","HK777","YST","FLTRP","K7"],["SN","HK","HK777","YST","FLTRP","K7R","IIBCAM"],
 "目录章节（시나공'Unit04 추론의 근거는 상상이 아닌 지문에서'）",["R3"])
t("P7-06","Part7","设问：意图","意图题（聊天/短信中引号里的话）看前后几条消息确定语境，再判断这句话在当时的作用。",
 ["定位引用句","读前一两条和后一两条消息","判断回应的对象和语气（同意/拒绝/确认）"],
 "What does X most likely mean when he writes '…'?",["SN","HK","HK777","YST","K7"],["SN","HK","HK777","YST","K7"],
 "目录章节（시나공'Unit06 앞뒤의 말로 상황을 파악'；究極のゼミ'意図問題'）",["R3"])
t("P7-07","Part7","设问：句子位置","句子位置题先读要插入的句子，抓指代词/连接词/冠词等线索，预测它前面应出现什么内容，再在[1]–[4]中验证。",
 ["先读给定句，找 this/such/also/however/the 等线索","推测前文应讲什么","逐个位置代入检查衔接"],
 "In which position… does the following sentence best belong?",["SN","HK","HK777","YST","K7"],["SN","HK","HK777","YST","K7"],
 "目录章节（시나공'Unit05 삽입할 문장의 앞에 위치한 내용을 예상'；究極のゼミ'位置選択問題'）",["R6"])
t("P7-08","Part7","设问：同义词","同义词题按原文语境选意思，不要直接选该词最常见的意思（多义词陷阱）。",
 ["定位原文该词所在句","理解该句意思","把选项代入替换，选语义一致者"],
 "The word '…' in paragraph X, line Y, is closest in meaning to",["SN","HK","HK777","YST","FLTRP","K7","KF"],
 ["SN","HK","HK777","YST","FLTRP","K7R","KF"],
 "目录章节（시나공'Unit07 문맥 안에서 확인'；外研社 Unit14 'Using context to answer vocabulary questions'）",["V4","R2"])
t("P7-09","Part7","同义替换","识别改写：正确选项通常用不同措辞表达原文意思；照搬原文词语的选项要警惕。",
 ["积累常见改写对（free of charge ↔ at no extra cost 等）","答题时先在原文找意思对应句","比较意思而非字面"],
 "Part 7 细节/推断题；Part 3/4 也适用",["K7","ETSIN"],["K7","ETSIN","IIBCAM"],
 "出版社简介（究極のゼミ'パラフレーズ'）+ETS 讲座目录（'PART 7 패러프레이징'）；官方 Score Descriptors 也把'改写后仍能理解事实信息'列为能力",["R2"])
t("P7-10","Part7","错误选项","掌握错误选项的套路（原文没提、部分正确、张冠李戴、过度推断、照搬原词）并在复盘时归类。",
 ["每道错题标注错误选项类型","统计自己最常掉的陷阱","下次答题时先排除该类选项"],
 "Part 7 全部题",["K7","XDF1000"],["K7","XDF1000"],"出版社简介（究極のゼミ'不正解の見抜き方'；托业阅读全真模拟1000题'规避错项陷阱'）",["R2","R3"])
t("P7-11","Part7","文本类型","按文本类型掌握结构与常考点：邮件/信看目的、收发件人、请求事项；广告看产品特点与购买方式；公告/备忘看目的与要求；文章看主题与发展；聊天看情境；表格/日程按格式找考点。",
 ["开头先判断文本类型","按该类型的'固定考点清单'预判题目","读时优先找这些信息位置"],
 "Part 7 单篇（邮件、信、表格、文章、短信聊天、广告、公告、备忘录、说明/网页）",
 ["SN","HK","HK777","YST","ETSIN","XDFRD","IIBCP7"],["SN","HK","HK777","YST","ETSIN","XDFRD","IIBCP7"],
 "目录章节（시나공 Unit08–14 各类型给出要点；IIBC 速読演習 9 单元按文本类型）",["R1","R5"])
t("P7-12","Part7","多篇连锁","双篇/三篇先预判跨文连接题：一篇给条件（如折扣规则、日程），另一篇给具体数据，答题时在两篇间对照。",
 ["先看各篇标题/类型与关系（如广告+邮件+评论）","找出明显需要两篇信息的题（常为第2–4题）","在一篇找条件，另一篇找对应数据，合并作答"],
 "Part 7 多篇（176–200 题）",["SN","HK","HK777","YST","ETSIN","FLTRP","K7"],["SN","HK","HK777","YST","ETSIN","FLTRP","K7"],
 "目录章节（시나공'Unit15/16 연계 문제를 예상하여 푼다'；外研社 Unit28 charts, tables, forms and double passages；究極のゼミ'トリプルパッセージ'）",["R5"])
t("P7-13","Part7","时间策略","Part 7 做题顺序：先拿把握大的题，耗时的 NOT/TRUE、长选项推断留到最后；多篇不要整块留到最后。",
 ["整卷先保证 Part 7 有足够时间","单篇中遇耗时题先标记跳过","按'多拿正确数'而非'读懂全文'为目标"],
 "Part 7 整体",["HK","K7","FLTRP"],["HKTIP","K7EJ","FLTRP"],
 "讲师公开文章（해커스 박영선）+讲座文章（究極のゼミ：优先'选出更多正确答案'）+目录（外研社 Unit7）",["S2"])
t("P7-14","Part7","阅读方式","按题型决定读多少：主旨和有关键词的细节题只读相关部分；NOT/TRUE、推断题要读到能确定为止。",
 ["判断题型","主旨/细节→局部读","NOT/TRUE/推断→扩大阅读范围直到确定"],
 "Part 7 单篇",["SN","HK"],["SN","HKBRD"],
 "书籍简介（시나공'파트 7은 다 읽지 않고 단서를 찾는 전략'）+해커스社区帖子",["S1"],
 "与究極のゼミ'できるだけ読んで解く'立场相反")
t("P7-15","Part7","速读训练","用意群斜线读法训练顺序直读（不回读、不逐词翻译），并跟着题目朗读音频按目标速度读。",
 ["把句子按意群切分，按语序理解","听原文音频同步跟读","逐步提高到目标速度"],
 "Part 7 速度；Part 6",["IIBCP7","IIBCQ","SN"],["IIBCP7","IIBCQ10","SN"],
 "官方教材介绍（IIBC 'スラッシュ読み'、公式問題集音频用法）+目录（시나공'직독직해'）",["S1"])
t("P7-16","Part7","速读训练","遇到生词不停下（'虫食い読み'），先靠上下文把握大意，读完再查。",
 ["标记生词但不停","用上下文推测大意","读后复盘查词"],"Part 7 阅读",["IIBCP7"],["IIBCP7"],"官方教材介绍",["S1"])
t("P7-17","Part7","速读训练","先测自己的阅读用时，再以目标用时反复练习同一篇（测时→抓要点→斜线读→答题→提速）。",
 ["计时读一篇并做理解题","对照目标用时","按5步法练习后再计时"],"Part 7 速度",["IIBCP7"],["IIBCP7"],"官方教材介绍（Chapter 2 五步法）",["S1"])
t("P7-18","Part7","阅读方式","先看中文（母语）概要再读英文，建立'英文能顺读'的感觉，适合基础阶段。",
 ["读母语概要","读英文原文","对比理解，逐步去掉母语提示"],"Part 7 基础阶段",["IIBCP7"],["IIBCP7"],"官方教材介绍（'日本語先読み'）",["S1"])

# ---------- General ----------
t("G-01","All","诊断与复盘","按题型统计正确率诊断薄弱点，再针对弱项练习（题型划分可对照官方 Abilities Measured 5项）。",
 ["做诊断/迷你模考","按题型统计正确率","按薄弱题型回到对应章节","练后再测"],
 "Part 5–7 全部",["K7","K56","HK","HK777","SN56"],["K7","K56AMZ","HK","HK777","SN56","IIBCAM"],
 "出版社简介/目录（究極のゼミ'問題タイプ別正答率''弱点問題タイプ診断'；해커스'진단고사+수준별 학습플랜'；777'나의 PART 7 취약점 극복하기'）",["S1","S2"])
t("G-02","All","诊断与复盘","复盘时逐个说明每个错误选项为什么错，而不只看正确答案。",
 ["对答案后逐项写出排除理由","标出原文依据位置","归档错因"],"Part 5–7",["DERU","IIBCQ","K56","K7","SNP56","XDF1000"],
 ["DERU","IIBCQ","K56AMZ","K7","SNP56","XDF1000"],
 "出版社/书店简介（でる1000問'間違い選択肢がダメな理由'；公式問題集'誤答に関する解説'；시나공实战集'정답과 오답의 이유'）",["R2"])
t("G-03","All","模考","用官方/真题做限时整套模考，并用分数换算表估分。",
 ["严格按75分钟计时","对答案后按换算表估分","记录各 Part 用时"],"Reading 全卷",["IIBCQ","ETS1000","XDFOG","K7","K56"],["IIBCQ","ETS1000","XDFOG","K7","K56AMZ"],
 "出版社简介（参考分数换算表；ETS 점수 환산표；官方指南'计分体制'；究極のゼミ'ミニ模試'）",["S1","S2"])
t("G-04","All","音频复习","用题目朗读音频复习阅读题：Part 5/6 听音频写出空格，Part 7 跟着音频读原文。",
 ["复印题目，听音频写出空格内容","与原文对照","Part 7 跟音频按语序读懂"],"Part 5–7 复习",["IIBCQ","KF","KB","BT","DERU","K56","K7"],
 ["IIBCQ10","KFM","KB","BT","DERU","K56AMZ","K7"],
 "出版社简介（公式問題集10 音声学习例；金の文法'速読力もUP!リスニング力もUP!'；文法特急/でる1000問/究極のゼミ 均附朗读音频）",["S1"])
t("V-01","Vocab","词汇","按目标分数段分层背词：先背目标分以下各段，提分后再扩展。",
 ["确定目标分","先背该分数段及以下的词","达标后进入下一段"],"词汇积累",["KF","XDFVOC"],["KF","XDFVOC"],
 "目录（金のフレーズ 600/730/860/990 四段）+简介（新东方：重点词汇/认知词汇区分）",["V1","V2","V3"])
t("V-02","Vocab","词汇","以短语/搭配为单位记词（金のフレーズ每条不超过7个词），兼顾 Part 5 搭配题和 Part 7 阅读。",
 ["背整条短语而非单词","把短语与考题场景联系","复习时做短语填空"],"Part 5 词汇题；Part 7 阅读",["KF","HK","XDFRD","IIBCP7","XDFVOC"],
 ["KFM","HK","XDFRD","IIBCP7","XDFVOC"],
 "简介/目录（金のフレーズ 7語以内フレーズ；해커스'어구·짝을 이루는 표현'；新东方'常用搭配'；IIBC'Part 7 厳選フレーズ200'）",["V1","V2","V3","V4"])
t("V-03","Vocab","词汇","专门记题干和选项里常见的词，以及部门、职位名称，读题更快。",
 ["整理题干/选项常见词","背部门、职位名称","做题时快速识别人物身份"],"Part 7 题干与选项",["KF"],["KF"],"目录（金のフレーズ Supplement'設問文・選択肢に出る単語・表現''部署・職業・学問名'）",["R1"])

data=dict(
 meta=dict(
  title="主流托业阅读备考书技巧体系（Part 5/6/7）",
  built="2026-10-20",
  scope="个人非商用备考研究；只用出版社/书店/图书馆目录、出版社简介、官方说明、公开书评与讲座页面，未使用任何盗版内容",
  mention_count_definition="books[] 中有多少本书，其公开目录或出版社/书评描述能对应到该技巧。是下限：多数书只看到目录，正文里的技巧没法核对",
  steps_note="steps 由章节标题、出版社简介和书评整理，用词是本研究自己的话，不是原书原文；具体规则（如位置规则）以章节标题为依据，细节属于整理推断",
  maps_to_nodes="对应 data/items_v0.json 中现有20个节点的 id（G=语法，V=词汇，R=题型，S=策略）",
  counts=dict(books=len(books_meta),techniques=len(T)),
 ),
 books=books_meta,
 techniques=T)
json.dump(data,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(len(books_meta),len(T))
for x in sorted(T,key=lambda x:-x["mention_count"])[:14]: print(x["mention_count"],x["id"],x["technique"][:30])
