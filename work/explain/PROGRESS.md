# A3 进度（续做用）

- 公开题：`python3 work/explain/dump.py --n 45` 取下一批（默认隐藏答案，独立作答后由 merge 比对）→ 写 `authored_open/bNNN.txt` → `python3 work/explain/merge.py`。
- 依据超 12 词：`python3 work/explain/fixbasis.py authored_open/bNNN.txt ID=新依据`。
- 私有题：`--pool private`，authored 在 `private_data/work_private/explain/authored/`；默认先 train 且无中文解析。
- 语法微讲解：源 `work/explain/lessons_src.txt` → `python3 work/explain/build_lessons.py` → `data/lessons/grammar_v1.json`。
- 顺序：pilot → maximcuynat T01..T06 → kdeppaei。
