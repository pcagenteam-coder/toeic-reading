# 手册 + 私有解析补完 + data_todo 进度（2026-10-27）

## 1. 私有解析 6 题补完
- ids: NJB-S13-P5-01-105, XDF-T01-P7-186, XDF-T03-P6-144, XDF-T07-P7-182, XDF-T08-P7-194, XDF-T09-198
- 脚本 private_data/work_private/zhx/retry6.py（打印失败原因），后台跑 → retry6.log；然后 merge.py
- [ ] 跑完 [ ] merge [ ] 私有 commit

## 2. 手册 12 章
- 脚本 work/handbook/gen.py（workers≤10，用户要求），state.json 断点续跑，后台：
  `setsid nohup python3 gen.py --workers 10 >> gen.log 2>&1 &`
- 流程：每章 meta(标题/一招/信号/示范题+3步) → 5 练习(基础/进阶/进阶/熟练/真考+) → 每题独立 solve 核对，答案不一致或 unique=false 即重生成（最多 4 轮）
- [ ] 生成 [ ] 原创性 n-gram 检查 [ ] README schema [ ] sample.md [ ] commit

## 3. data_todo
- [ ] docs/review/data_todo.md
