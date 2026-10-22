# TOEIC raw-to-scaled approximation

Approximate TOEIC Listening & Reading raw-correct to scaled-score reference.

**File:** `toeic-raw-to-scaled.json`

ETS equates official TOEIC Listening & Reading scores by test form and does not publish one universal raw-score conversion table. This dataset is for practice-test estimation only.

## Fields

- `anchors`: published-style 5-point anchor curve
- `listening`: `raw_correct` 0–100 to `scaled_score_estimate` 5–495
- `reading`: same transparent approximation curve
- `source_urls`: official scoring information and an example published conversion chart

```python
import json

data = json.load(open("toeic-raw-to-scaled.json"))
score = data["listening"][85]["scaled_score_estimate"]
print(score)
```

Relevant Lumi Studio app: [Aim990](https://apps.apple.com/app/id6784974530).
