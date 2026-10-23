# 引擎 API（C2：ROI 排程 + 个性化）

给 B2 前端用。引擎是单例 `ToeicEngine`（= engine.js 里的 `E`，构建后为全局），当前档案状态在 `E.st`。
所有派生量（掌握度、卡片、画像、个人 FSRS 参数）都能由 `st.log` 答题事件日志重算（UX_SPEC_v1 §15）。

加载顺序（build.py 拼接）：`store.js → fsrs.js → mastery.js → personal.js → planner.js → engine.js → app.js`。
`mastery.js / personal.js / planner.js / fsrs.js` 都是纯函数模块，Node 里可直接 `require`。

## 1. 主 API

| 调用 | 返回 | 说明 |
|---|---|---|
| `getTodayPlan(state, minutes=5)` | 今日任务 | 用户只选时长；内容全由排程决定 |
| `getProgress(state)` | 进度 | “离目标还差 N 个考点、约 X 小时”、维持模式、作战卡 |
| `recordAnswer(event)` | `{correct, node, mastery}` | 记一次作答（写日志 + FSRS + 掌握度） |
| `getProfile(state)` | 个人画像 | 用时、作战卡、作息建议、FSRS 参数来源 |
| `setSetting(key, value)` | — | 追加 `setting_change` 事件；`circadian:false` 关作息建议；`daily_min` 默认时长 |
| `dueItems()` / `dueWords()` | id 数组 | 今天该复习的题卡 / 生词（两者合计 ≤20） |

`state` 可省略（默认 `E.st`）；传入别的档案状态时只读计算，不改当前档案。

### getTodayPlan(state, minutes)
```js
{ mode: 'learn'|'maintain'|'review_only', phase: 'none'|'base'|'strengthen'|'sprint'|'final3'|'examday',
  daysLeft, minutes, band: '≤500'|'600'|'730'|'860+',
  units: [ { ids:[itemId…], b?: bundleId, kind:'review'|'learn'|'maintain', node, est /*秒*/ } ],
  words: ['invoice', …],          // 今天要复习的生词（与 units 里的复习共用每日上限 20）
  reviewCount, backlog,           // 复习条数；顺延到以后几天的积压数（不显示“逾期”）
  estSec, nodes:[{id,nm,m,stuck}], progress: '离目标还差 …', tip /* 作息建议或 null */ }
```
- 单元格式与 v2 的 `E.plan()` 一致（`{ids, b?}`），旧 app.js 直接可用；`E.plan(m)` 现在就是 `getTodayPlan(E.st, m).units`。
- 时长按个人用时估：每题 `目标秒 × 本 Part 个人用时比 + 10 秒反馈`；P6/P7 复习另加 30 秒重读。到时就停（UX §3：做完当前篇再结算由前端负责）。
- 配比：复习占 50%（冲刺期 60%，维持模式 70%，考前 3 天 100%），复习不满则余时给新学。
- `review_only`（考前 3 天/当天）：不出新考点；复习做完后的余时只练已学过的高考频考点。

### getProgress(state)
```js
{ band, target, targetMastery, mode: 'learn'|'maintain', phase, daysLeft,
  remainingNodes, remainingHours, achievedNodes, totalNodes, text,
  next: [{id,nm,m,roi}],      // 接下来最该练的 3 个考点
  stuck: [id], dropped: [{id,nm}],   // 学不动的；考前排不下、按放弃规则处理的
  ruleNodes,                  // 目标档内无题可练的节点数（技巧/词包等，由规则卡/词卡交付）
  nodes: [{id,m,achieved,stuck,dropped,unlocked,remainMin}],
  battle }                    // 同 getProfile().battle
```

### recordAnswer(event)
接受 UX §15 `answer_submit` 字段：`{item_id, choice, ms, lookups?, viewed_hint?, mode?}`；也接受 v2 的 `{id, c, lu}`。
内部仍写 v2 `answer` 事件（B2 迁移日志格式时只改 `E.record`，回放两种格式都支持）。

### getProfile(state)
```js
{ pace: {5:{n,ratio},6:{…},7:{…}},          // 个人用时 / 目标用时（10 题先验收缩）
  battle: { band, finishLine:{base, personal, reachable, spareMin, tip},
            skipBudget:{base:[lo,hi], personal}, p56Min, p5CutSec, p7CutSec, pace },
  circadian: { enabled, best, name, n, slots:{slot:{n,acc,lift}}, tip },
  fsrs: { personal: bool, reviews, before, after } }
```

## 2. 模型与规则（实现要点）

**图谱字段**（`data/graph_v1_cost.json`，`data/graph_v1_cost_build.py` 生成，build.py 合并进 `nodes[]`：`lc` 学会分钟、`mb` 必须档、`pr` 前置）。规则说明见 `data/graph_v1_cost.md`。

**掌握度（mastery.js）**：每节点 θ~N(mu,v) 的 Elo/1PL-IRT（Glicko 式近似贝叶斯）。题难度 b=(difficulty_est−3)×0.7；得分 r：错 0 / 查词或看提示 0.5 / 慢于 1.5×目标 0.8 / 正常 1；证据权重：主节点 1、副标签 0.5、主节点的前置 0.15（弱证据传播）；每天不确定度 +0.01（久不练回落）。m = 中等难度题的预期答对率（已计入不确定度）。`Mastery.replay(log)` 与增量 `apply` 结果逐字节一致（有测试）。

**排程（planner.js）**
- 档位：目标总分 ≤550→≤500，551–665→600，666–795→730，≥796→860+。达标掌握度 0.6/0.7/0.8/0.88，且证据量 ≥3；回差 0.05 防止维持模式来回切换。
- 考点 = 该档 must 集合里、训练池中作主节点 ≥3 题的节点。
- ROI = 考频权重 × (1−m) / 剩余成本；剩余成本 = learn_cost_min × max(0.1, 缺口比例)，学不动（主节点 ≥10 次、近 8 次涨幅 <0.03、仍未达标）×3。
- 前置：前置考点 m<0.5 且练不到 6 次 → 后继不排。
- 倒排：考前可用新学时间（逐日按阶段的新学占比累加）放不下全部剩余成本 → 按 ROI 截断，其余进 `dropped`。
- 选题：P5 单题优先（未做过、难度贴近该节点能力，且题目主考点也须在档内），否则 P6/P7 篇章（≤600 档只出单篇，730 档单/双篇）。训练池排除 `item.u==='mock'` 和已模考过的整套。

**复习（Planner.reviewQueue）**：题卡 + 生词合计每日上限 20（含今天已复习的）；到期日早于今天的积压平摊 `clamp(ceil(积压/10), 5, 7)` 天，每天取 `ceil(积压/天数)` 张，其余给今天到期的；考前 3 天只留考频权重 ≥0.12 的题卡（P7 设问×文本组合按其设问类型权重；生词按 0.15 保留）。

**个性化（personal.js）**
- 终点线：基准遵循 strategies_v2（≤500/600 Q175、730 Q185、860+ 不设）；按个人 P5/P6/P7 用时推算 75 分钟（留 1 分钟涂卡）能做到第几题，个人线只会提前不会越过基准；做到基准线还剩 ≥5 分钟时提示 S2-ALL-15 多篇捡分。跳题预算 = 200 − 终点线（≤500 另加插入句 4 + 长篇报道约 4，600 另加插入句 4）。
- 作息：按本地时段（早上/上午/中午/下午/晚上/深夜）统计“实际 − 模型预期”的残差（控制难度与能力），收缩估计；总 ≥60 题、≥2 个时段各 ≥15 题、最佳与最差差 ≥0.04 才建议。`setSetting('circadian', false)` 关闭。
- FSRS 个人参数：每多 100 次作答检查一次；可计损失的复习（隔天以上）≥300 次才用坐标搜索 + L2 先验重拟合 17 个 w，拟合后 log loss 比默认至少低 0.002 才采用，并按新参数重放全部卡片。结果缓存在 `st.fsrsFit`（派生，可删）。

## 3. 状态新增字段（派生，可由日志重算）
- `st.settings`：`{circadian, daily_min}`（同时写 `setting_change` 事件）
- `st.fsrsFit`：`{at, use, w, n, before, after}`

## 4. 测试
```
python3 app/build.py --public && node app/test/smoke.js && node app/test/fsrs.test.js && node app/test/planner.test.js
python3 app/build.py && node app/test/smoke.js app/dist/index.private.html && node app/test/planner.test.js app/dist/index.private.html
```
planner.test.js：600 档用户 30 天模拟（只学 must、达标进维持、每日复习 ≤20、mock 不进训练、回放一致）、积压平摊、考前 3 天、倒排放弃、学不动、用时/作息/FSRS 个性化、API 字段。
