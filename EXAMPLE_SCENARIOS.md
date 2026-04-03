# Example Scenarios - UI Behavior

## Scenario 1: High Eligibility, Low Risk (Best Case)

### Data
```json
{
  "scheme_name": "PM-KISAN Direct Benefit Transfer",
  "eligibility_score": 0.95,
  "risk_score": 0.15,
  "access_gap": 0.10
}
```

### Display
```
┌─────────────────────────────────────────────────────────┐
│ 1. PM-KISAN Direct Benefit Transfer    [fully_eligible] │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ✓ Low Access Gap                          [GREEN]  │  │
│ │    Gap Score: 0.100                                │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Eligibility              Risk                      │  │
│ │ HIGH (0.950)             LOW (0.150)               │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ You are highly eligible and face minimal barriers.      │
│                                                          │
│ [View Details ▼]                                         │
└─────────────────────────────────────────────────────────┘
```

**User Insight:** This is an excellent match - apply immediately!

---

## Scenario 2: High Eligibility, High Risk (Access Gap Problem)

### Data
```json
{
  "scheme_name": "Pradhan Mantri Awas Yojana",
  "eligibility_score": 0.88,
  "risk_score": 0.72,
  "access_gap": 0.55
}
```

### Display
```
┌─────────────────────────────────────────────────────────┐
│ 1. Pradhan Mantri Awas Yojana           [fully_eligible]│
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ⚠ High Access Gap                          [RED]   │  │
│ │    Gap Score: 0.550                                │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Eligibility              Risk                      │  │
│ │ HIGH (0.880)             HIGH (0.720)              │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ You qualify, but significant barriers may prevent        │
│ successful access. Review barriers carefully.            │
│                                                          │
│ [View Details ▼]                                         │
│                                                          │
│ (When expanded:)                                         │
│ Why You Qualify                                          │
│ You meet income and housing criteria...                 │
│                                                          │
│ Potential Barriers                                       │
│ ⚠ Complex documentation requirements                     │
│ ⚠ Limited institutional support in your area             │
│ ⚠ Digital application process with no offline option     │
│                                                          │
│ Access Gap Explanation                                   │
│ While you qualify, the high documentation burden and     │
│ digital-only process create significant access barriers. │
│                                                          │
│ Recommended Next Steps                                   │
│ 1. Gather all required documents before starting         │
│ 2. Seek help from local NGO or community center          │
│ 3. Consider applying with assistance from a facilitator  │
└─────────────────────────────────────────────────────────┘
```

**User Insight:** You qualify, but need help to successfully access this scheme.

---

## Scenario 3: Moderate Eligibility, Moderate Risk

### Data
```json
{
  "scheme_name": "National Rural Employment Guarantee",
  "eligibility_score": 0.62,
  "risk_score": 0.38,
  "access_gap": 0.28
}
```

### Display
```
┌─────────────────────────────────────────────────────────┐
│ 1. National Rural Employment Guarantee  [partially_elig]│
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ⚠ Moderate Access Gap                    [YELLOW]  │  │
│ │    Gap Score: 0.280                                │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Eligibility              Risk                      │  │
│ │ MEDIUM (0.620)           MEDIUM (0.380)            │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ You partially qualify with some access challenges.      │
│                                                          │
│ [View Details ▼]                                         │
└─────────────────────────────────────────────────────────┘
```

**User Insight:** Worth applying, but be prepared for some challenges.

---

## Scenario 4: Low Eligibility, Low Risk

### Data
```json
{
  "scheme_name": "Senior Citizen Savings Scheme",
  "eligibility_score": 0.25,
  "risk_score": 0.10,
  "access_gap": 0.18
}
```

### Display
```
┌─────────────────────────────────────────────────────────┐
│ 1. Senior Citizen Savings Scheme        [not_eligible]  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ✓ Low Access Gap                          [GREEN]  │  │
│ │    Gap Score: 0.180                                │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Eligibility              Risk                      │  │
│ │ LOW (0.250)              LOW (0.100)               │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ You do not meet eligibility criteria, but if you did,   │
│ access would be straightforward.                         │
│                                                          │
│ [View Details ▼]                                         │
└─────────────────────────────────────────────────────────┘
```

**User Insight:** Not eligible, but easy to access if circumstances change.

---

## Scenario 5: No Barriers Identified

### Data
```json
{
  "scheme_name": "Public Distribution System",
  "eligibility_score": 0.92,
  "risk_score": 0.12,
  "access_gap": 0.08,
  "barriers": []
}
```

### Display (Expanded)
```
┌─────────────────────────────────────────────────────────┐
│ 1. Public Distribution System            [fully_eligible]│
│                                                          │
│ ✓ Low Access Gap                                [GREEN] │
│    Gap Score: 0.080                                     │
│                                                          │
│ Eligibility: HIGH (0.920)    Risk: LOW (0.120)          │
│                                                          │
│ [Hide Details ▲]                                         │
│                                                          │
│ Why You Qualify                                          │
│ You meet all income and residency requirements...       │
│                                                          │
│ Potential Barriers                                       │
│ ✓ No major barriers identified                          │
│                                                          │
│ Access Gap Explanation                                   │
│ The scheme is easily accessible with minimal barriers.  │
│                                                          │
│ Recommended Next Steps                                   │
│ 1. Visit your nearest ration shop                       │
│ 2. Bring proof of identity and address                  │
│ 3. Complete simple registration form                    │
└─────────────────────────────────────────────────────────┘
```

**User Insight:** Perfect match - straightforward to access!

---

## Scenario 6: Loading State

### Display
```
┌─────────────────────────────────────────────────────────┐
│ 1. Mahatma Gandhi National Rural...     [fully_eligible]│
│                                                          │
│ ⚠ Moderate Access Gap                         [YELLOW]  │
│    Gap Score: 0.320                                     │
│                                                          │
│ Eligibility: HIGH (0.850)    Risk: MEDIUM (0.450)       │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│ Analyzing eligibility...        (pulsing)               │
│ Evaluating barriers...          (pulsing, delayed)      │
│ Generating insights...          (pulsing, more delayed) │
└─────────────────────────────────────────────────────────┘
```

---

## Scenario 7: Error State

### Display
```
┌─────────────────────────────────────────────────────────┐
│ 1. Ayushman Bharat                       [fully_eligible]│
│                                                          │
│ ✓ Low Access Gap                                [GREEN] │
│    Gap Score: 0.150                                     │
│                                                          │
│ Eligibility: HIGH (0.900)    Risk: LOW (0.200)          │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│ ⚠ Explanation currently unavailable.                    │
└─────────────────────────────────────────────────────────┘
```

---

## Scenario 8: Multiple Schemes Comparison

### Display
```
Recommendations (3)

┌─────────────────────────────────────────────────────────┐
│ 1. PM-KISAN                              [fully_eligible]│
│ ✓ Low Access Gap (0.100)                        [GREEN] │
│ Eligibility: HIGH (0.950)    Risk: LOW (0.150)          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2. PMAY                                  [fully_eligible]│
│ ⚠ High Access Gap (0.550)                         [RED] │
│ Eligibility: HIGH (0.880)    Risk: HIGH (0.720)         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 3. NREGA                                [partially_elig] │
│ ⚠ Moderate Access Gap (0.280)                  [YELLOW] │
│ Eligibility: MEDIUM (0.620)  Risk: MEDIUM (0.380)       │
└─────────────────────────────────────────────────────────┘
```

**User Insight:** At a glance, user can see:
- PM-KISAN: Best option (green, high eligibility, low risk)
- PMAY: Qualified but challenging (red, high barriers)
- NREGA: Moderate option (yellow, some challenges)

---

## Key Visual Patterns

### Color Signals
- **Green** = Go ahead, minimal issues
- **Yellow** = Proceed with caution
- **Red** = Proceed but expect challenges

### Score Labels
- **HIGH** = Strong match (≥70%)
- **MEDIUM** = Moderate match (40-70%)
- **LOW** = Weak match (<40%)

### Icons
- **✓** = Positive indicator
- **⚠** = Warning/caution indicator
- **💡** = Insight/tip
- **▼/▲** = Expand/collapse

### Information Hierarchy
1. Scheme name (most prominent)
2. Access gap (colored, eye-catching)
3. Scores (labeled, clear)
4. Summary (always visible)
5. Details (on-demand)

This design ensures users can quickly scan and identify:
- Which schemes they qualify for
- Which ones are easiest to access
- Where they might need help
