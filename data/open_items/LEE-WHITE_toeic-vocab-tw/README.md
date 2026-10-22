---
pretty_name: 完整 TOEIC 單字庫 (English–Traditional Chinese)
license: cc-by-4.0
language:
- en
- zh
language_bcp47:
- zh-Hant
configs:
- config_name: default
  data_files:
  - data/toeic_vocabulary_view.json
tags:
- toeic
- vocabulary
- bilingual
- english-chinese
- traditional-chinese
- business
- education
task_categories:
- other
size_categories:
- 1K<n<10K
---

# 完整 TOEIC 單字庫（English–Traditional Chinese）

一份面向 TOEIC 情境的雙語單字庫，涵蓋商務、辦公、會議、客戶服務、財務會計、行銷銷售、採購物流、法律合規、資訊技術等多個常見領域。資料以 JSON 提供，並依重要度劃分 5★–1★ 等級，附詞性、詞形變化與中英雙語例句，便於教學、備考、應用開發與語言學習研究。

## Dataset Summary

- Title: 完整 TOEIC 單字庫
- Version: 110.5
- Total Words: 9,537
- Language Pair: English ↔ Traditional Chinese (繁體中文)
- Structure: 單一 JSON 陣列（每列一個詞條）+ `data/metadata.json`

## Files

- `data/toeic_vocabulary.json`：主資料檔（頂層為陣列，每列一個詞條）
- `data/metadata.json`：資料集中繼資料（title/version/last_updated/total_words…）
  
可選（仍為 JSON，便於 Viewer 預覽）：
- `data/toeic_vocabulary_view.json`：Viewer 友善版（巢狀欄位以字串存放，如 `word_forms_json`、`examples_json`，方便 HF 轉成表格）

## Schema

- 主檔（`data/toeic_vocabulary.json`）為「頂層陣列」，每個詞條包含：

- `english_word`：英文單字
- `chinese_definition`：中文定義
- `star_rating`：整數（1–5）
- `category`：所屬主題分類
- `parts_of_speech`：詞性陣列（如 noun/verb/adj/adv 等）
- `word_forms`：依詞性細分的詞形（例：名詞複數、動詞三單/過去式/分詞/動名詞等）
- `examples`：例句陣列（`english`、`chinese`）
- `importance_group`：原始分組標籤（如 `5_stars_essential`）

- 中繼資料（`data/metadata.json`）：
  - `title`、`version`、`description`、`total_words`、`creation_date`、`language_pair`
  - `categories`、`star_system`、`last_updated`

### Star System 說明

- 5★ 核心商業詞彙：最高優先級，TOEIC 必備
- 4★ 重要專業詞彙：商務場合常用
- 3★ 職場/學術詞彙：有助提升語言能力
- 2★ 有用支援詞彙：擴展詞彙量
- 1★ 一般詞彙：建議了解

## Example Instance

```json
{
  "english_word": "answer",
  "chinese_definition": "回覆；答覆；回應",
  "star_rating": 5,
  "category": "溝通互動",
  "parts_of_speech": ["noun", "verb"],
  "word_forms": {
    "noun": {"plural": "answers"},
    "verb": {
      "third_person_sg": "answers",
      "past": "answered",
      "past_participle": "answered",
      "present_participle": "answering"
    }
  },
  "examples": [
    {"english": "Could you please answer the questionnaire before the meeting?", "chinese": "請在會議前填寫問卷並回覆。"},
    {"english": "The applicant needs to answer all the questions truthfully.", "chinese": "申請人需要誠實地回答所有問題。"}
  ],
  "importance_group": "5_stars_essential"
}
```

## Usage

### Local (JSON)

```python
import json
from pathlib import Path

path = Path("data/toeic_vocabulary.json")
rows = json.loads(path.read_text(encoding="utf-8"))  # 頂層為陣列

print(len(rows), "words total")
# 篩選 5★ 詞條
top_words = [r for r in rows if r.get("importance_group") == "5_stars_essential"]
print(len(top_words), "top words")
print(top_words[0]["english_word"], top_words[0]["chinese_definition"])
```

### After Upload (datasets)

上傳到 Hugging Face 後，可使用 `datasets` 套件讀取：

```python
from datasets import load_dataset

# 直接載入主檔（頂層陣列 JSON；保留巢狀欄位）
ds = load_dataset(
    "json",
    data_files="https://huggingface.co/datasets/kknono668/toeic-vocab-tw/resolve/main/data/toeic_vocabulary.json",
    split="train",
)

# 若要簡化成純表格欄位，可改載入 viewer 友善版（巢狀欄位已字串化）
# ds = load_dataset(
#   "json",
#   data_files="https://huggingface.co/datasets/kknono668/toeic-vocab-tw/resolve/main/data/toeic_vocabulary_view.json",
#   split="train",
# )
```

> 提示：若要轉為扁平表格（如 Pandas DataFrame），可將各重要度群組展開並加上 `importance_group` 欄位。

## Intended Uses

- TOEIC 應試準備、語言教學與練習
- 商務英語學習應用（查詢、測驗、卡片、練習題生成）
- 詞彙表與例句檢索工具

## Limitations

- 定義與例句聚焦於職場/商務情境，對一般語境未必全面
- 詞性與詞形為常見用法彙整，未涵蓋所有罕見變化

## License

本資料集以 CC BY 4.0 釋出。請在使用時適當標註來源與作者，並附上授權連結。

- Name: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Link: https://creativecommons.org/licenses/by/4.0/

## Citation

如果你在研究或產品中使用了本資料集，請引用：

```
@misc{toeic_vocab_2025,
  title  = {完整 TOEIC 單字庫 (English–Traditional Chinese)},
  year   = {2025},
  note   = {CC BY 4.0},
  howpublished = {Hugging Face Dataset}
}
```

## Changelog

- v34.8: 初版公開；9,855 詞條；依 5★–1★ 分組；含詞性、詞形、例句與分類。

