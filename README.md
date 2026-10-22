# 托业阅读提分（TOEIC Reading）

给工作忙、精力有限的成年人用的托业阅读备考工具：先诊断，再按 ROI 安排练习（知识图谱 + 考试技巧 + 记忆曲线），每天 5/20/75 分钟，职场模拟外壳降低抵触。单文件离线网页，手机/平板/电脑都能用。

- 构建：`python3 app/build.py --public` → `app/dist/index.html`（只含公开题）
- 测试：`node app/test/smoke.js`（可传 dist 路径，如私有构建 `app/dist/index.private.html`）
- 公开题库：自编 pilot 107 题 + 开源 MIT 6 套完整阅读 600 题（data/items_open_maximcuynat.json，模考用）
- 产品原则：docs/PRODUCT_BRIEF.md；设计与算法：app/DESIGN.md；交接说明：HANDOFF.md

## 数据与许可
- 代码、设计文档、能力图谱、技巧库、出题模板、自编题：本项目原创。
- data/open_items/maximcuynat_toeic-practice：MIT，© 2026 Maxim Cuynat。
- data/open_items/alice51849_lumi-open-data：MIT / 数据 CC BY 4.0。
- data/wordlists：NGSL 1.2、TSL 1.2，Browne, C., Culligan, B. & Phillips, J.，CC BY-SA 4.0（https://www.newgeneralservicelist.com）。
- 无授权题库不在本仓库，见私有仓库（private_data/，已 gitignore）。
