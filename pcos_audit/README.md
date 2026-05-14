# PCOS Forensic Audit Tool — Teammate 1

Visit-history input form + Rotterdam criteria checker + missed diagnosis report.

## Setup (do this once)

```bash
cd pcos_audit
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Opens in your browser at http://localhost:8501

## File structure

```
pcos_audit/
├── app.py                  # Main Streamlit UI
├── requirements.txt
└── utils/
    ├── predict.py          # mock_predict() — swap for real model on Day 2
    └── audit.py            # Rotterdam rule engine + missed opportunity report
```

## Day 2 — swapping in the real model

In `utils/predict.py`, replace `mock_predict()` with a call to the real model:

```python
import requests

def mock_predict(inputs: dict) -> dict:
    response = requests.post("http://YOUR_MODEL_ENDPOINT/predict", json=inputs)
    return response.json()
```

The input and output schema is already identical — nothing else needs to change.

## Output JSON schema

```json
{
  "patient_summary": {
    "visits_analysed": 2,
    "first_positive_visit": 2,
    "total_flagged_visits": 1,
    "missed_opportunities": 1,
    "missed_opportunity_visits": [...],
    "criteria_pattern": { "O_ever_met": true, ... }
  },
  "visits": [
    {
      "visit": 1,
      "pcos_probability": 0.38,
      "pcos_positive": false,
      "phenotype": "insufficient_data",
      "criteria_met": { "O": true, "H": false, "P": false },
      "confidence_level": "moderate",
      "missing_tests": ["lh_miu_ml", "amh_ng_ml"],
      "is_adolescent": false,
      "equity_flags": []
    }
  ]
}
```
