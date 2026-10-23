# TOEIC 阅读提分应用 · 交接说明（给接手的人/agent）

更新：2026-10-22（加入独立网页应用 v2：app/）。本文件夹是 Hark 项目工作目录的同步副本。自用、非商用。

- 产品原则与用户决策：docs/PRODUCT_BRIEF.md（先读）

## 目标
用最少注意力和时间，不抵触地提升 TOEIC Reading。职场模拟游戏外壳 + 提分引擎内核；游戏只服务分数，非答题时间约 10% 以内。
闭环：诊断 → 针对训练 → 间隔复习（FSRS）→ 混合迁移（P5→P6→P7）→ 模考验证。用户只选 5/20/75 分钟。

## 考试版本
只按现行线性新制：Reading 75 分钟 100 题（P5 30 / P6 16 含句子插入 / P7 54 含双篇三篇、群聊、意图题）。中国 2018-04 起，日韩 2016-05 起。旧制（P5 40/P6 12/P7 48、改错题）标 deprecated，不进图谱。ETS MSA 自适应版（37 分钟 45 题）以后再支持。

## 词汇范围
NGSL 1.2 + TSL 1.2 约 4,000 词为主。600 前高频商务词，800+ 补 TSL、搭配、易混词；其余点词查义。题目新增/修改后用两个词表做超纲检查。

## 目录
- data/graph_v1.json、graph_v1_summary.md：能力图谱 v1，305 节点（已校验：ID 唯一、前置存在、无环）。
- data/items_v0.json：20 节点 v0 图谱 + 18 道原型题。
- data/templates/item_templates.json：75 套出题模板（覆盖全部 67 个 qtype 叶子；P5 按题型细分、P6 含 3 种插入位置、P7 = 设问族 × 文本类型），含选项构造规则、30 种干扰套路、篇幅范围、难度旋钮、中文解析模板。生成脚本 work/templates/build_item_templates.py。
- data/items_pilot_v1.json：试点题 107 道（P5 60 / P6 5 篇 20 / P7 8 组 27，含双篇、三篇、群聊意图题、插入句题），兼容 v0 字段 + node_ids/template_id/difficulty_est/target_time_sec/逐项错因/bundle_id/qnum。题源 work/pilot/src_p5.py、src_p67.py，组装 work/pilot/build_pilot.py。
- data/items_pilot_v1_audit.md：试点题审题报告（100% 通过、超纲修正、节点覆盖、答案分布）。
- data/items_xdf1000.json：新东方 2019《阅读全真模拟1000题》10 套 1000 题题库（2026-10-21 解析；来源 github.com/TastyHeadphones/TOEIC 文本抽取，无授权、仅自用）。schema 兼容 items_pilot_v1（id XDF-Txx-qnum、form=Txx、answer、explain_zh 原书解析、translation_zh、bundle 原文 docs + 中文翻译），加 source=xdf2019_1000、flags。969 题完整可用；8 个 bundle/30 题原文是图片缺失（已标 passage_missing）。节点为规则粗打。报告 data/items_xdf1000_report.md；脚本 work/tasty/parse_reading.py。原始 md 在 data/external/tasty_toeic/。
- data/strategies/tasty_notes.md：TastyHeadphones《真题总结》阅读要点 + 与技巧库 v1 不同的 6 条新技巧（N1–N6，待并入 v1.1）。
- work/item_audit.py：自动审题脚本（超纲词、四选项/答案/错因、答案分布、与 v0 和外部题库近似重复、P6/P7 bundle 与新制题号题数、篇幅）。用法：python3 work/item_audit.py data/xxx.json --json out.json。
- data/strategies/：books.json（54 条/21 本书）、books_taxonomy.md、exam_pattern_stats.json/.md（35 来源考频）。
- data/strategies/strategy_library_v1.json/.md：统一技巧库 v1（2026-10-21 完成）——五路去重合并 82 条（P5 23 / P6 10 / P7 24 / 全卷 25；共识 高 36/中 32/个人 14），每条绑定 graph_v1 qtype/texttype/strategy 节点（已校验存在）、分段、权重、工作规则、练习/模考可用性；旧制 3 条单列 deprecated、违规 4 条排除。构建：work/strategies/build_strategy_library.py（+ _md.py 生成报告）。
- data/datasets_inventory.md：数据集清单、许可、用途、风险。
- data/wordlists/：NGSL、TSL 词表。
- data/external/：已下载外部数据（EdNet 元数据、KT、词表、语料、干扰项数据集、Part 5 参考题库——无许可，仅自用参考，不可复制进产品）。
- data/external/github_inventory.md + data/external/github/：GitHub 扩展检索（2026-10-21）——细查 51 个仓库，可入库 24 / 仅参考 14 / 不用 12；已下载约 8,200 道阅读题（含 23 套完整新制套题：ETS 1000 Vol.4 真题 10 套、maximcuynat 6 套、marcvasseur 4 套、asaiibowl 3 套）、词表、估分表、参考代码（FSRS、估分、出题提示词）；新技巧 N1–N11。规则：GitHub 上能拿到的都可以自用、不外传，许可证只记录。
- work/：构建脚本（graph_v1/build.py、build_exam_pattern_stats.py 等）和 reports/strategy_findings_summary.md（中文论坛/英文/日韩技巧要点）。work/bili（B 站原始抓取，约 600MB）未同步。
- **app/：托业阅读提分 v2 独立网页应用（2026-10-22）**——原生 JS 单文件离线应用，手机优先。源码 app/src/（index.html、style.css、store.js 存储/档案/进度码、engine.js 引擎、app.js 界面），构建 `python3 app/build.py` → app/dist/index.html（约 0.9 MB，内嵌 1077 题 = pilot 107 + xdf 970，195 个 bundle、305 节点、82 条技巧）；冒烟测试 `node app/test/smoke.js`。演示副本 demo/v2/index.html（手机浏览器直接打开）。功能：入职诊断、工作台（预测分区间/达标概率/5·20·75 分钟任务卡/连续天数）、P5/P6/P7 答题器（计时条、稍后处理、划依据、生词本、错因、工作规则卡）、整套模考（75 分钟倒计时、题号导航、交卷报告）、结算与职级、薄弱点榜+攻克、错题/生词复习（简化 FSRS）、图谱、多档案、进度码导入导出、作答日志导出、本地 PK。接手先读 app/README.md（构建、schema）和 app/DESIGN.md（产品设计、算法、界面清单、已知问题）。题库含无授权资料，仓库须私有。
- demo/prototype_v1/：原型 v1 静态网页（打开 index.html 即可）。未完成真实点测；无持久化。
- docs/upgrade-plan-v2.md：原型 v2 升级计划。

## 进行中
- 试点题 v1 已出（107 题，审题全过），待人工盲做验证唯一答案，再接入原型 v2。
- 新东方/B 站技巧检索 → data/strategies/xdf_bilibili.json（已完成，已并入统一技巧库）。

## 下一步（按顺序）
1. ~~合并五路技巧成统一技巧库~~（已完成：strategy_library_v1，82 条）。后续：graph v1.1 考虑新增 8 个建议 strategy 节点（见 strategy_library_v1.md §4），补 QT.P7X.DETAIL.INSTRUCTIONS / TX.APP_FORM 的技巧。
2. ~~每种题型的出题模板 + 自动审题~~（已完成：templates + item_audit.py + 试点 107 题）。
3. 按模板扩到约 500 题：补未覆盖高权重节点（VO.TITLES_DEPTS、VO.SCENE.SALES_DEAL、TX.AD、VO.SCENE.RND_PRODUCT、VO.SCENE.MEDIA_PUBLISH、TX.APP_FORM），P6 篇幅加长到 100–150 词，P7 补满单篇 10 篇/多篇 5 组的整套结构，接入原型 v2；自用目标约 2,500 题 + 4 套模考。
4. ~~原型 v2 独立网页~~（已完成 app/，见上）。B2 第 2 段已完成首日 S1–S6/复习/进度/我的/页面状态；待：真机点测、预测分校准、提醒设置、诊断起始难度按词汇量调。
5. 引擎：EdNet 先验设初始难度/用时（P5 中位 26.4s、P6 33.8s、P7 67.4s）；305 节点知识追踪；FSRS；预测分区间按模考校准。

## 规则
- 来源规则（2026-10-21 用户明确）：GitHub 上可获取的资料可以自用、不外传；仍不进产品发布、不分享。已据此导入 github.com/TastyHeadphones/TOEIC 的新东方 2019 阅读 1000 题文本（items_xdf1000），PDF 本身未下载。其他盗版资料仍不主动找（仅目录、试读、书评、笔记）。
- Google Drive 同步文件夹保持私有，不分享给任何人。
- 03_新题型600题（アルク，日文双栏 OCR）含阅读 3 套，但文本混排质量差，未解析；要用需重新按栏 OCR。
- 中文、大白话；先产品/UX 后技术。
