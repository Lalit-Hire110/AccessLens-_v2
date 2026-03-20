# Access Risk Model v1 — Usage Guide

## Requirements

- Python 3.10+
- `pandas` library

Install dependencies:
```
pip install pandas
```

---

## Running the Model

The script is located at:
```
Access_Lens_v2/
  phase 2 - Access Risk Model v1/
    access_risk_model_v1.py
```

Open a terminal, navigate to the Phase 2 folder, and run:

```bash
python access_risk_model_v1.py
```

---

## Configuring the Target Pair

At the bottom of `access_risk_model_v1.py`, locate the `__main__` block:

```python
TARGET_SCHEME_ID  = "pmmvy"
TARGET_PERSONA_ID = "p05"
```

Change these two strings to any valid ID from the datasets.

### Available Scheme IDs

| ID           | Scheme Name |
|--------------|-------------|
| pmjay        | Ayushman Bharat – PMJAY |
| pmmvy        | Pradhan Mantri Matru Vandana Yojana |
| jsy          | Janani Suraksha Yojana |
| mjpjay       | MJPJAy Maharashtra |
| kasp         | KASP Kerala |
| nmmss        | National Means-cum-Merit Scholarship |
| csss         | Central Sector Scholarship |
| permatricsc  | Pre-Matric Scholarship SC |
| postmatricsc | Post-Matric Scholarship SC |
| mahadbt      | MahaDBT Fee Reimbursement Maharashtra |

### Available Persona IDs

| ID  | Literacy | Digital Access | Doc Completeness | Institutional Dependency |
|-----|----------|---------------|-----------------|--------------------------|
| p01 | high     | high           | high            | low                      |
| p02 | high     | medium         | high            | medium                   |
| p03 | medium   | medium         | medium          | medium                   |
| p04 | medium   | low            | medium          | high                     |
| p05 | low      | low            | low             | high                     |
| p06 | high     | high           | medium          | low                      |
| p07 | high     | low            | high            | medium                   |
| p08 | medium   | high           | low             | medium                   |
| p09 | low      | medium         | low             | high                     |
| p10 | low      | low            | medium          | high                     |
| p11 | medium   | medium         | high            | low                      |
| p12 | high     | medium         | low             | medium                   |

---

## Output Format

The script prints two sections:

### Results Table

```
======================================================================
  ACCESS RISK MODEL v1 — RESULTS
======================================================================
  Scheme ID  : pmmvy
  Persona ID : p05
----------------------------------------------------------------------
  Barrier ID   Type              Severity   Act.Mult  Amp.Factor  Contribution
----------------------------------------------------------------------
  ...per-barrier rows...
----------------------------------------------------------------------
  Raw Risk Score           : X.XXXX
  Normalized Access Risk   : X.XXXX
======================================================================
```

### Checker Section

```
======================================================================
  CHECKER — VALIDATION SECTION
======================================================================
  [1] ACTIVATED BARRIERS (non-zero contribution)
  [2] SKIPPED BARRIERS (zero activation)
  [3] MAXIMUM POSSIBLE SCORE
  [4] SANITY CHECK — score in [0, 1]?
  [5] BARRIER TYPE DOMINANCE SUMMARY
======================================================================
```

---

## Notes

- **No hardcoded logic** — only the two ID strings at the bottom of the script change between runs.
- **Reproducible** — identical inputs always produce identical outputs.
- **No ML, no randomness** — purely deterministic rule-based computation.
- The CHECKER section is designed to be copy-pasted into a reviewer validation document.
