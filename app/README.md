# 托业阅读提分 v2（独立网页应用）

单文件、离线、手机优先（360–420px）的 TOEIC Reading 训练应用。原生 JS，无框架、无网络请求。自用、非商用（题库含无授权资料，**不可公开发布**；做 GitHub 仓库请设为私有，或构建时去掉 xdf 题库）。

## 构建
```bash
python3 app/build.py          # → app/dist/index.html（单文件，直接用手机浏览器打开）
node --check app/src/*.js     # 语法检查
node app/test/smoke.js        # 无浏览器冒烟测试（DOM 桩 + 跑完诊断/训练/攻克/复习/模考/档案/进度码）
cp app/dist/index.html demo/v2/index.html
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
build.py 按 `store.js → engine.js → app.js` 顺序拼接。

## 数据来源与统一（build.py）
| 源文件 | 用法 |
|---|---|
| data/items_pilot_v1.json | 自编试点题 107 道（有 difficulty_est、target_time_sec、逐项错因）；诊断只用这批 |
| data/items_xdf1000.json | 新东方 1000 题 10 套；跳过 `passage_missing` 题和 `text_missing` 的 bundle（共 30 题），剩 970 |
| data/strategies/strategy_library_v1.json | 82 条技巧 → 工作规则卡 |
| data/graph_v1.json | 305 节点 → 掌握度、薄弱点、图谱 |

两套题库的差异与统一方式：
- 空位标记：pilot P6 用 `[n]`（n=blank_n），xdf 用 `(131) -------` → 统一为 `{{题号}}`，界面渲染为行内空位。P7 的插入位置 `[1]–[4]` 保持原样。
- 题干：pilot 有 `stem`(P5) / `q`(P7)，xdf 有 `stem` 或 `q` → 统一为 `s`；P6 题干为空（就是原文里的空）。
- xdf 无 difficulty_est / target_time_sec / distractor_reasons → 难度默认 3；目标用时 P5 22s、P6 30s、P7 单篇 55s、多篇 65s。
- 原文 docs：pilot 有 `title`/`header`，xdf 只有 `text` → 统一为 `{t 类型, h 标题, x 正文}`。
- 丢弃：translation_zh（省体积，约 140k 字）、template_id、来源元数据。

### 内嵌数据 schema（window.TDATA）
```
items[]   {id, p 部分, f 套/form, q 题号, n 主节点, ns 其他节点[], s 题干, o 选项[4], a 答案下标,
           e 解析 explain_zh, d 难度1–5, t 目标秒, src 'pilot'|'xdf', b? bundle_id, dr? {选项下标: why_zh}}
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
4. 题库扩到约 500 自编题后，可以去掉 xdf 做可公开版本。
5. 云端同步：实现 store.js 里预留的 SupabaseAdapter（同接口 get/set/del）。
6. 精读：恢复 translation_zh（按需懒加载或分文件）。
