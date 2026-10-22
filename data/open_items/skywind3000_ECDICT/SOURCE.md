# 来源
- 仓库：https://github.com/skywind3000/ECDICT（commit bc015ed2e24a7abef49fc6dbbb7fe32c1dadaf8b）
- 许可：MIT（见 LICENSE）
- 文件：ecdict_toeic_subset.csv = 从 ecdict.csv（770,611 条）**过滤**出 17,894 条，只保留字段 word, phonetic, translation, pos, collins, oxford, tag, bnc, frq, exchange
- 过滤词集（20,532 个）：data/wordlists 的 NGSL 1.2 / TSL 1.2 词形 + LEE-WHITE、kknono668、chunchiech 三份 TOEIC 词表词头 + data/items_open_maximcuynat.json、items_pilot_v1.json、items_v0.json 中出现的词；覆盖 87%
- 用途：点词即查的简体中文兜底词典；exchange 字段可做词形还原
