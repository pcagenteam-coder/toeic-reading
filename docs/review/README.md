# 托业阅读提分应用 · 外部专家审查入口

更新：2026-10-24 · 仓库 `pcagenteam-coder/toeic-reading`（公开）+ `toeic-reading-private`（私有，仅授权审查人）

## 1. 产品目标与目标用户
- **目标**：用最少的注意力和时间、不抵触地提升 TOEIC Reading（现行新制：75 分钟 100 题，P5 30 / P6 16 / P7 54）。
- **用户**：工作忙、精力有限、商务词汇量偏低的中文成年考生；不喜欢背单词/学语法；手机碎片时间为主（每天 5–10 分钟），考前做 75 分钟模考。
- **形态**：职场模拟外壳（Halvorsen 公司新人：收件箱=P7、审稿=P5、改稿=P6、紧急任务=模考）+ 提分引擎内核（诊断 → ROI 训练 → FSRS 复习 → 模考验证）。
- **北极星**：每投入 1 分钟涨多少预测分，且第二天愿意回来（docs/ux/UX_SPEC_v2.md §1）。

## 2. 仓库结构
| 路径 | 内容 |
|---|---|
| `app/src/` | 原生 JS 单文件离线 PWA 源码（store/fsrs/mastery/personal/planner/predict/engine/api/app + style/sw） |
| `app/build.py` / `app/dist/` | 构建脚本 / 构建产物（`index.html` 公开版，`index.private.html` 私有版，不发布） |
| `app/test/` | 冒烟、单元、离线、UI 截图测试 |
| `data/` | 能力图谱 graph_v1（305 节点）、公开题库、中文解析、语法微课、词表、技巧库 |
| `docs/` | 产品简报、UX 规格 v1→v2、引擎 API、预测校准、审查报告、本审查包 |
| `demo/prototype_v1/` | v1 视觉原型（hark.css 设计基底） |
| `work/` | 构建/清洗/审题脚本与阶段进度记录（部分在 git） |
| `private_data/` | 独立私有仓库（被 .gitignore），无授权题库与解析，见其 README_REVIEW.md |

## 3. 运行方式
```bash
python3 app/build.py --public        # → app/dist/index.html（只含公开题，可发布）
python3 app/build.py                 # → app/dist/index.private.html（需 private_data/）
node --check app/src/*.js            # 语法检查
node app/test/smoke.js [dist路径]     # 冒烟：诊断/训练/攻克/复习/模考/档案/进度码
node app/test/fsrs.test.js           # FSRS-4.5 单元测试
node app/test/planner.test.js        # ROI 排程/个性化（含 600 档 30 天模拟）
node app/test/predict.test.js [--full]  # 预测分（3PL IRT）+ 校准模拟
python3 app/test/offline.py          # 离线：断网刷新/IDB 恢复/导入导出/新版提示
bash work/setup_browser.sh && python3 app/test/ui_screens.py   # 4 视口 Playwright 截图自检
```
Python 3.8+ 无第三方依赖；node 可选；UI 测试需 Playwright + chrome-headless-shell。

## 4. 架构（详见 docs/engine_api.md）
- **engine.js**：单例 `ToeicEngine`，状态 `E.st`；所有派生量都可由 `st.log` 答题事件日志重放重算。
- **mastery.js**：考点掌握度模型（快对/慢对/错/查词 → 掌握度更新，稳定阈值）。
- **planner.js**：ROI 排程——目标分最小考点集合 `need`、今日任务、分段节奏、回流日、考前阶段。
- **fsrs.js**：FSRS-4.5（自动评分、考前压缩 ≤14 天 R=0.95、日上限 20），MIT 归属 huieric/toefl-miniapp。
- **predict.js**：分层 3PL IRT → 原始分 → 近似量表分区间，含时间预算、模考输入、用户实考校准。
- **api.js**：前端只读门面（缓存预测、内联中文解析/语法/词典）。
- **app.js**：界面（首日流程、今天/做题/结算/复习/进度/我的、模考），personal.js 个人画像与作息。

## 5. 数据与题库
| 池 | 题数 | 来源 | 许可边界 | 中文解析 |
|---|---|---|---|---|
| 公开·自编 pilot | 107（P5 60/P6 20/P7 27） | 本项目原创，对标 ETS 样题格式 | 原创 | 107/107 结构化 |
| 公开·maximcuynat | 600（6 套整卷，模考用） | GitHub maximcuynat/toeic-practice | MIT | 600/600 结构化（zh_open_v1） |
| 公开·kdeppaei | 804（P5 328/P6 119/P7 357） | GitHub kdeppaei，已剔除 ESL Lounge 336 题 | MIT | 804/804 一句中文要点（非结构化） |
| **公开合计** | **1,511** | | 可公开发布 | 结构化 707/1,511 |
| 私有 items_private_v1 | 4,855（11 来源，详见私有 README_REVIEW.md） | ETS 1000 Vol.4 转录 1,000、新东方 2019 1,000、GrittingLeo 400、其他 8 个 GitHub 题库 2,455 | 无授权/无许可证，仅自用，不外传 | 4,849/4,855（DeepSeek 结构化） |

- 用途：私有池 mock 1,200（ETS 10 套 + XDF T09/T10）、train 3,655；ETS 转录只做模考/难度校准。
- **答案键争议**（`private_data/explanations/key_adjudicated_v1.json`）：模型与原答案键不一致的 101 题经二审 → 改判答案(ALT) 57、维持原键(KEY) 38、不确定 6；来源集中在 xdf 44、ninejubu 25、bonnie 14、GrittingLeo 11。排除清单 key_exclude_v1 共 63 题（ALT+UNSURE）：私有构建剔除其中 56 道训练题，7 道模考题保留以保持整套完整；全部待人工复核。
- 公开仓库不含任何无授权题目原文；公开 dist 只打包上述 1,511 题。

## 6. 当前状态
- **已上线 demo**：https://pcagenteam-coder.github.io/toeic-reading/ —— **v1.2**（可见计时、明确对错+一句结论+详细解析、结算 N/M+错题回看、模考交卷后逐题解析、职场外壳、单主按钮）。
- **UX v2**（docs/ux/UX_SPEC_v2.md：工作台预测分卡、《新人工作手册》12 章、难度 4 档、答后掌握度/预测分闭环）**只是规格，未实现**；本包 docs/design/v2/ 为其静态线框稿。
- 引擎（FSRS/掌握度/ROI/预测分）、离线 PWA、导入导出已完成并有测试；云同步（D3）未做。

## 7. 已知问题与待审查重点
1. **题目偏易**：公开/私有池 difficulty_est（1–5 规则档）以 3 档为主（公开 1,511 题中 5 档仅 39 题，私有 4,855 题中 5 档 206 题），800+ 真考难度题不足（v2 计划：重评分档 + 原创难题）。
2. **难度为规则粗估**：difficulty_est 由规则（词汇等级、句长等）打分，未经真实作答 IRT 标定，影响预测分与排程。
3. **技巧未结构化**：技巧库 v2 共 93 条，尚未落成可教学的 12 章手册（示范题、5 题梯度、通关标准）。
4. **私有 dist 体积 7.3MB**（index.private.html，公开版 1.8MB），手机首屏加载与 SW 缓存需评估拆分/懒加载。
5. **真机未测**：仅 Playwright 4 视口截图测试，iOS Safari/微信内置浏览器/安卓未点测（D1）。
6. **预测分换算表近似**：原始分→量表分用公开流传区间中位数，非 ETS 官方表（docs/predict_calibration.md）。
7. 私有池节点为规则粗打（989 题 node_tx_approx）、38 题原文缺失、63 题答案键待人工复核。

请重点审查：难度分档方法、预测分模型与换算、ROI 排程合理性、手册 12 章教学设计、v2 关键屏交互、题库许可边界。

## 8. 文档索引
- 本审查包：[user_journey.md](user_journey.md) · [progress.md](progress.md) · 线框稿 [../design/v2/wireframes.html](../design/v2/wireframes.html)（截图 [../design/v2/png/overview.png](../design/v2/png/overview.png)）· v1 vs v1.2 对照 [../design/v1_vs_v12/](../design/v1_vs_v12/)
- 产品：[../PRODUCT_BRIEF.md](../PRODUCT_BRIEF.md) · [../ROADMAP.md](../ROADMAP.md) · [../upgrade-plan-v2.md](../upgrade-plan-v2.md) · [../../HANDOFF.md](../../HANDOFF.md)
- UX：[../ux/UX_SPEC_v2.md](../ux/UX_SPEC_v2.md) · [../ux/UX_v2_goal_framework.md](../ux/UX_v2_goal_framework.md) · [../ux/v12_gap.md](../ux/v12_gap.md) · [../ux/UX_SPEC_v1_1.md](../ux/UX_SPEC_v1_1.md)
- 引擎：[../engine_api.md](../engine_api.md) · [../predict_calibration.md](../predict_calibration.md) · [../../app/DESIGN.md](../../app/DESIGN.md) · [../../app/README.md](../../app/README.md)
- 既往审查：[product_ux_review_2026-10-24.md](product_ux_review_2026-10-24.md)
- 数据：[../../data/datasets_inventory.md](../../data/datasets_inventory.md) · [../../data/items_open_qc_report.md](../../data/items_open_qc_report.md) · [../../data/graph_v1_summary.md](../../data/graph_v1_summary.md)
