# 托业阅读提分 v2（独立网页应用）

单文件、离线、手机优先（360–420px）的 TOEIC Reading 训练应用。原生 JS，无框架、无网络请求。
两种构建：`--public` 只含公开题（pilot 自编 + open 开源 MIT 题），可公开发布；不带参数时若有 private_data/ 则另含 xdf 无授权题，产物 `index.private.html` **只能自用，不可公开**。

## 构建
```bash
python3 app/build.py --public # → app/dist/index.html（公开：pilot + open，可发布）
python3 app/build.py          # → app/dist/index.private.html（私有：另含 xdf；需要 private_data/，已 gitignore）
node --check app/src/*.js     # 语法检查
node app/test/smoke.js                               # 冒烟测试公开构建（DOM 桩 + 诊断/训练/攻克/复习/模考/档案/进度码）
node app/test/smoke.js app/dist/index.private.html   # 冒烟测试私有构建
node app/test/fsrs.test.js                           # FSRS 单元测试
node app/test/planner.test.js                        # C2 排程/个性化测试（600 档 30 天模拟等）
python3 work/convert_maximcuynat.py                  # 重新生成 data/items_open_maximcuynat.json
python3 work/item_audit.py data/items_open_maximcuynat.json   # 审题（无 template_id 的导入题自动用导入题模式）
```
Python 3.8+，无第三方依赖。node 仅用于检查，可选。

## 文件结构
```
app/
  build.py          读 data/ → 统一 schema、精简字段 → 内嵌到 dist（"</" 转义为 "<\/"）
  src/index.html    外壳（/*CSS*/ /*JS*/ /*DATA*/ 三个占位符）
  src/style.css     样式
  src/store.js      存储适配器（localStorage → 失败降级内存）、多档案、进度码
  src/engine.js     数据索引、Elo 掌握度、预测分、简化 FSRS、选题/组卷
  src/app.js        界面：5 个 Tab、答题器、模考、结算、事件
  test/smoke.js     冒烟测试
  dist/index.html   构建产物（约 0.9 MB，其中代码约 46 KB）
  DESIGN.md         产品设计、引擎算法、界面清单
```
build.py 按 `store.js → fsrs.js → mastery.js → personal.js → planner.js → engine.js → app.js` 顺序拼接。C2 排程/个性化 API 见 `docs/engine_api.md`；图谱排程字段由 `data/graph_v1_cost.json` 合并（`lc` 学会分钟、`mb` 必须档、`pr` 前置）。

## 数据来源与统一（build.py）
| 源文件 | 用法 |
|---|---|
| data/items_pilot_v1.json | 自编试点题 107 道（有 difficulty_est、target_time_sec、逐项错因）；诊断只用这批 |
| data/items_open_maximcuynat.json | 开源（MIT，maximcuynat/toeic-practice）6 套完整阅读 MXT01–MXT06 × 100 = 600 题，src='open'；英文解析 explain_en（无中文解析时界面显示英文）；公开/私有构建都纳入 |
| private_data/items/items_xdf1000.json | （仅私有构建）新东方 1000 题 10 套；跳过 `passage_missing` 题和 `text_missing` 的 bundle（共 30 题），剩 970 |
| data/strategies/strategy_library_v1.json | 82 条技巧 → 工作规则卡 |
| data/graph_v1.json | 305 节点 → 掌握度、薄弱点、图谱 |

两套题库的差异与统一方式：
- 空位标记：pilot/open P6 用 `[n]`（n=blank_n），xdf 用 `(131) -------` → 统一为 `{{题号}}`，界面渲染为行内空位。P7 的插入位置 `[1]–[4]` 保持原样。
- 题干：pilot 有 `stem`(P5) / `q`(P7)，xdf 有 `stem` 或 `q` → 统一为 `s`；P6 题干为空（就是原文里的空）。
- xdf/open 无 difficulty_est / target_time_sec / distractor_reasons → 难度默认 3；目标用时 P5 22s、P6 30s、P7 单篇 55s、多篇 65s。
- 原文 docs：pilot 有 `title`/`header`，open 有 `title`(文本类型名)+可选 `header`(To/From 信头)，xdf 只有 `text` → 统一为 `{t 类型, h 信头或标题(信头优先), x 正文}`。
- 丢弃：translation_zh（省体积，约 140k 字）、template_id、来源元数据。

### 内嵌数据 schema（window.TDATA）
```
items[]   {id, p 部分, f 套/form, q 题号, n 主节点, ns 其他节点[], s 题干, o 选项[4], a 答案下标,
           e 解析 explain_zh（空则 explain_en）, d 难度1–5, t 目标秒, src 'pilot'|'open'|'xdf', b? bundle_id, dr? {选项下标: why_zh}}
bundles[] {id, p, f, k single|double|triple, tt 文本类型, docs[{t,h,x}], qs[题 id]}
nodes[]   {id, nm 中文名, l 层, pa 父节点, w 考频权重, bd 目标分段, g 是否分组节点}
strats[]  {id, ti 标题, wr 工作规则一句话, r 规则说明, ns 绑定节点[], p 部分[], w 权重, pm 练习可用}
```

### 本地状态 schema（每档案一份，localStorage key `t2:p:<id>`，索引 `t2:index`）
```
{ver:2, target, exam, diag, th 全局能力(logit), N 作答数, nd{节点:[θ,次数]}, seen{题:[次数,上次对错]},
 cards{题:{ivl,due(天号)}}, words{词:{c 例句,ivl,due,ts}}, wrong{题:时间}, mocks[], used[已模考套],
 streak{d,n}, days{日期:题数}, log[事件], hist[[时间,预测分]], cons{节点:连错数}, hl{bundle:di:[句号]}, run 进行中会话}
```
事件日志 `log[]`：`{t, e: answer|start|end|word|wordrev|hl|later|rule|export|profile, ...}`；answer 含 id/mode/c/ok/ms/lu。

## 下一步
1. 真机点测（手机 Safari/微信内置浏览器），按 DESIGN.md §5 清单逐项过。
2. 预测分用真实模考/考试成绩校准（目前换算表是近似）。
3. 词汇：点词即查（离线释义表，NGSL/TSL + 中文义），开局词汇量测试。
4. 公开版本已可用（pilot + open 600 题，模考用 MXT01–06）；open 题补中文解析 explain_zh、校对节点粗打。
5. 云端同步：实现 store.js 里预留的 SupabaseAdapter（同接口 get/set/del）。
6. 精读：恢复 translation_zh（按需懒加载或分文件）。

## 离线 / 存储（D2）
- `src/sw.js`：同源 GET cache-first，预缓存应用壳（页面、manifest、图标）；build.py 注入 `VERSION`（dist 页面内容哈希）。新版装好后 waiting，页面在不做题时右下角提示「刷新获取新版」，点了才 skipWaiting+刷新。另含本地通知点击。需 https（或 localhost）部署，dist 下全部文件同目录。
- `src/manifest.webmanifest` + `src/icons/`：可添加到主屏幕；iOS 用 apple-touch-icon / apple-mobile-web-app-* meta。
- `store.js`：内存缓存为真相，同步双写 localStorage + 节流（400ms）写 IndexedDB `toeic-r/kv`，页面隐藏/关闭时 flush；双方记 `t2:__ts`，启动时 IDB 更新（或 LS 丢了索引）则从 IDB 恢复；旧 LS 数据首启自动镜像进 IDB；IDB 不可用/超时 1.5s → 只用 LS；都不可用 → 内存 + 顶部提示导出。启动调用 `navigator.storage.persist()`。
- 我的 → 数据：导出文件（JSON）/ 从文件导入（新建档案，不覆盖）/ 进度码。
- 测试：`python3 app/test/offline.py`（自起 http.server；断网刷新、中途刷新、IDB 恢复与迁移、导出导入往返、新版提示、IDB 不可用降级）。
