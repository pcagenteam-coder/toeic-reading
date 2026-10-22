---
pretty_name: 完整 TOEIC 單字庫 (English–Traditional Chinese)
license: cc-by-sa-4.0
language:
- en
- zh
language_bcp47:
- zh-Hant
configs:
- config_name: default
  data_files:
  - data/toeic_vocabulary.json
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
- 10K<n<100K
---

# 完整 TOEIC 單字庫（English–Traditional Chinese）

一份面向 TOEIC 情境的雙語單字庫，涵蓋商務、辦公、會議、客戶服務、財務會計、行銷銷售、採購物流、法律合規、資訊技術等多個常見領域。資料以 JSON 提供，並依重要度劃分 5★–1★ 等級，附詞性、詞形變化與中英雙語例句，便於教學、備考、應用開發與語言學習研究。

## Dataset Summary

- Title: 完整 TOEIC 單字庫
- Version: 112.0
- Total Words: 11,154
- Language Pair: English ↔ Traditional Chinese (繁體中文)
- Structure: 單一 JSON 陣列（每列一個詞條）
- Features: 包含星級評分、TOEIC 分數範圍、考試技巧

## Files

- `data/toeic_vocabulary.json`：主資料檔（頂層為陣列，每列一個詞條）

## Schema

主檔（`data/toeic_vocabulary.json`）為「頂層陣列」，每個詞條包含：

- `english_word`：英文單字
- `chinese_definition`：中文定義
- `star_rating`：整數（1–5），星級評分
- `toeic_score_range`：TOEIC 分數範圍（如 "400-600"、"600-780"、"780-900"、"900+"）
- `category`：所屬主題分類
- `parts_of_speech`：詞性陣列（如 `["noun", "verb"]`）
- `word_forms`：詞形變化陣列，每個元素包含：
  - `part_of_speech`：詞性（noun/verb/adjective/adverb）
  - `forms`：該詞性的所有變化形式陣列
- `examples`：例句陣列，每個例句包含：
  - `english`：英文例句
  - `chinese`：中文翻譯
- `exam_tips`：TOEIC 考題重點（包含常見搭配詞、使用情境、易混淆詞辨析、考試技巧等）

### Category List

- 一般專業
- 人力資源
- 住宿與餐飲
- 客戶服務
- 採購與物流
- 旅遊與交通
- 會議與簡報
- 法務合規與安全
- 溝通互動
- 營運管理
- 物業與不動產
- 科技與技術支援
- 行銷與銷售
- 辦公日常
- 金融與會計

### Star System 說明

- 5★ 核心高頻詞彙：TOEIC 必備基礎商業詞彙，所有考生都應掌握
- 4★ 常見重要詞彙：商務場合常用，中高分考生應熟悉
- 3★ 進階專業詞彙：特定情境專業詞彙，高分考生需要掌握
- 2★ 較少見詞彙：專業或高階表達，850 分以上考生才需要
- 1★ 罕見詞彙：極少出現於 TOEIC，了解即可

### TOEIC 分數範圍說明

- **0-400**：入門程度（簡單日常對話，語言能力侷限）
- **400-600**：基礎程度（文字溝通尚可，掌握少量相關語言）
- **600-780**：中級程度（可進行一般社交談話，應付例行業務需求）
- **780-900**：高級程度（可有效運用英文滿足社交及工作需求，措辭恰當）
- **900+**：近母語程度（能流暢有條理表達意見，近似英語母語人士）

## Example Instance

```json
{
  "english_word": "accept",
  "chinese_definition": "接受；同意；答允",
  "star_rating": 5,
  "toeic_score_range": "400-600",
  "category": "溝通互動",
  "parts_of_speech": ["verb"],
  "word_forms": [
    {
      "part_of_speech": "verb",
      "forms": ["accept", "accepts", "accepting", "accepted"]
    }
  ],
  "examples": [
    {
      "english": "The company will accept credit card payments from now on.",
      "chinese": "從現在開始，公司將接受信用卡付款。"
    },
    {
      "english": "We need to accept the revised proposal to move forward with the project.",
      "chinese": "為了推進專案，我們需要接受修改後的提案。"
    }
  ],
  "exam_tips": [
    "常見搭配詞：在 TOEIC 中經常出現的詞組包含 accept an offer (接受提議/錄取)、accept responsibility (承擔責任) 以及 accept an invitation (接受邀請)。",
    "商業情境應用：常出現在招募、合約談判與客戶服務情境，例如：'We only accept returns within 30 days.' (我們僅接受30天內的退貨) 或 'accept the terms and conditions' (接受條款與條件)。",
    "易混淆詞辨析：最常與發音相近的 'except' (除...之外) 混淆；請記住 accept 是動詞 (同意/接納)，而 except 通常作為介係詞 (排除)。",
    "聽力與閱讀考點：在聽力 Part 2 中，accept 常作為對建議或邀請的正面回答；在閱讀 Part 5 與 6 中，常考察詞彙選擇題，考生需根據上下文判斷是「收到 (receive)」還是「同意並接納 (accept)」。",
    "注意與 receive 的區別：'receive' 僅代表客觀的收到某項物品或資訊，而 'accept' 則隱含了主觀上的同意、認可或正式收下的動作。"
  ]
}
```

## Usage

### Local (JSON)

```python
import json
from pathlib import Path

path = Path("data/toeic_vocabulary.json")
words = json.loads(path.read_text(encoding="utf-8"))

print(f"總詞條數: {len(words)}")

# 篩選 5★ 詞條
five_star_words = [w for w in words if w.get("star_rating") == 5]
print(f"5星詞條數: {len(five_star_words)}")

# 查看第一個詞條
first_word = words[0]
print(f"單字: {first_word['english_word']}")
print(f"定義: {first_word['chinese_definition']}")
print(f"詞形: {first_word['word_forms']}")
```

### After Upload (datasets)

上傳到 Hugging Face 後，可使用 `datasets` 套件讀取：

```python
from datasets import load_dataset

# 載入資料集
ds = load_dataset(
    "kknono668/toeic-vocab-tw",
    split="train"
)

# 或直接從檔案載入
ds = load_dataset(
    "json",
    data_files="https://huggingface.co/datasets/kknono668/toeic-vocab-tw/resolve/main/data/toeic_vocabulary.json",
    split="train"
)

# 篩選特定星級
five_star = ds.filter(lambda x: x["star_rating"] == 5)
print(f"5星詞彙數量: {len(five_star)}")
```

## Intended Uses

- TOEIC 應試準備、語言教學與練習
- 商務英語學習應用（查詢、測驗、卡片、練習題生成）
- 詞彙表與例句檢索工具

## Limitations

- 定義與例句聚焦於職場/商務情境，對一般語境未必全面
- 詞性與詞形為常見用法彙整，未涵蓋所有罕見變化

## License

本資料集以 CC BY-SA 4.0 釋出。請在使用時適當標註來源與作者，並附上授權連結；若有衍生作品需以相同授權釋出。

- Name: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- Link: https://creativecommons.org/licenses/by-sa/4.0/

## Citation

如果你在研究或產品中使用了本資料集，請引用：

```
@misc{toeic_vocab_2025,
  title  = {完整 TOEIC 單字庫 (English–Traditional Chinese)},
  year   = {2025},
  note   = {CC BY-SA 4.0},
  howpublished = {Hugging Face Dataset}
}
```

## Changelog

- v111.1 (2026-02): 重新評級星級與分數區間；目前共 11,154 詞條。
- v111.0 (2026-01): 擴充至 11,339 詞條；分類合併調整為 15 類（科技/資訊合併、法律合規併入法務合規與安全）。
- v110.5 (2025-01): 資料結構改為扁平陣列格式；移除人名/公司名等佔位詞條；共 9,537 詞條。
- v34.8: 初版公開；9,855 詞條；依 5★–1★ 分組；含詞性、詞形、例句與分類。
