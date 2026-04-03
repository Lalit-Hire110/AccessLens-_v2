# What-If Simulator - Visual Examples

## Example 1: Improving Document Completeness

### Initial State
```
User Profile:
- document_completeness: 0.50 (50%)
- digital_access: full

Original Results:
┌─────────────────────────────────────────────────────────┐
│ 1. PM-KISAN Direct Benefit Transfer                     │
│                                                          │
│ ⚠ High Access Gap                              [RED]    │
│    Gap Score: 0.550                                     │
│                                                          │
│ Eligibility: HIGH (0.850)    Risk: HIGH (0.720)         │
└─────────────────────────────────────────────────────────┘
```

### What-If Simulator
```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [========●==] 0.95               │
│ 0.0 ────────────────────────────────────── 1.0          │
│                                                          │
│ Digital Access: [Full ▼]                                │
│                                                          │
│ [Simulate Changes]  [Reset]                             │
└─────────────────────────────────────────────────────────┘
```

### Simulated Results
```
┌─────────────────────────────────────────────────────────┐
│ [Original] [Simulated] ← Active                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Simulated Results                                        │
│                                                          │
│ 1. PM-KISAN Direct Benefit Transfer                     │
│                                                          │
│ ⚠ Moderate Access Gap                        [YELLOW]   │
│    Gap Score: 0.320  ↓ 0.230                            │
│                                                          │
│ Eligibility: HIGH (0.900)  ↑ 0.050                      │
│ Risk: MEDIUM (0.420)       ↓ 0.300                      │
└─────────────────────────────────────────────────────────┘
```

**Insight:** Completing documents reduced access gap from HIGH to MODERATE!

---

## Example 2: Gaining Digital Access

### Initial State
```
User Profile:
- document_completeness: 0.75
- digital_access: none

Original Results:
┌─────────────────────────────────────────────────────────┐
│ 1. Ayushman Bharat                                       │
│                                                          │
│ ⚠ High Access Gap                              [RED]    │
│    Gap Score: 0.620                                     │
│                                                          │
│ Eligibility: HIGH (0.920)    Risk: HIGH (0.780)         │
└─────────────────────────────────────────────────────────┘
```

### What-If Simulator
```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [=======●===] 0.75               │
│                                                          │
│ Digital Access: [Full ▼] ← Changed from "None"          │
│                                                          │
│ [Simulate Changes]  [Reset]                             │
└─────────────────────────────────────────────────────────┘
```

### Simulated Results
```
┌─────────────────────────────────────────────────────────┐
│ Simulated Results                                        │
│                                                          │
│ 1. Ayushman Bharat                                       │
│                                                          │
│ ✓ Low Access Gap                              [GREEN]   │
│    Gap Score: 0.180  ↓ 0.440                            │
│                                                          │
│ Eligibility: HIGH (0.920)  — (no change)                │
│ Risk: LOW (0.260)          ↓ 0.520                      │
└─────────────────────────────────────────────────────────┘
```

**Insight:** Digital access dramatically reduced risk and access gap!

---

## Example 3: Maximum Improvement

### Initial State
```
User Profile:
- document_completeness: 0.40
- digital_access: limited

Original Results:
┌─────────────────────────────────────────────────────────┐
│ 1. PMAY (Housing)                                        │
│                                                          │
│ ⚠ High Access Gap                              [RED]    │
│    Gap Score: 0.680                                     │
│                                                          │
│ Eligibility: MEDIUM (0.680)  Risk: HIGH (0.820)         │
│                                                          │
│ 2. NREGA (Employment)                                    │
│                                                          │
│ ⚠ High Access Gap                              [RED]    │
│    Gap Score: 0.550                                     │
│                                                          │
│ Eligibility: HIGH (0.750)    Risk: HIGH (0.720)         │
└─────────────────────────────────────────────────────────┘
```

### What-If Simulator
```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [==========●] 1.00               │
│ ← Moved from 0.40 to 1.00                               │
│                                                          │
│ Digital Access: [Full ▼]                                │
│ ← Changed from "Limited" to "Full"                      │
│                                                          │
│ [Simulate Changes]  [Reset]                             │
└─────────────────────────────────────────────────────────┘
```

### Simulated Results
```
┌─────────────────────────────────────────────────────────┐
│ Simulated Results                                        │
│                                                          │
│ 1. PMAY (Housing)                                        │
│                                                          │
│ ✓ Low Access Gap                              [GREEN]   │
│    Gap Score: 0.150  ↓ 0.530                            │
│                                                          │
│ Eligibility: HIGH (0.750)  ↑ 0.070                      │
│ Risk: LOW (0.180)          ↓ 0.640                      │
│                                                          │
│ 2. NREGA (Employment)                                    │
│                                                          │
│ ✓ Low Access Gap                              [GREEN]   │
│    Gap Score: 0.120  ↓ 0.430                            │
│                                                          │
│ Eligibility: HIGH (0.820)  ↑ 0.070                      │
│ Risk: LOW (0.150)          ↓ 0.570                      │
└─────────────────────────────────────────────────────────┘
```

**Insight:** Both improvements together transformed ALL schemes from HIGH to LOW access gap!

---

## Example 4: Minimal Impact Scenario

### Initial State
```
User Profile:
- document_completeness: 0.95 (already high)
- digital_access: full (already optimal)

Original Results:
┌─────────────────────────────────────────────────────────┐
│ 1. PM-KISAN                                              │
│                                                          │
│ ✓ Low Access Gap                              [GREEN]   │
│    Gap Score: 0.120                                     │
│                                                          │
│ Eligibility: HIGH (0.950)    Risk: LOW (0.180)          │
└─────────────────────────────────────────────────────────┘
```

### What-If Simulator
```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [==========●] 1.00               │
│ ← Only 0.05 improvement possible                        │
│                                                          │
│ Digital Access: [Full ▼]                                │
│ ← Already optimal                                       │
│                                                          │
│ [Simulate Changes]  [Reset]                             │
└─────────────────────────────────────────────────────────┘
```

### Simulated Results
```
┌─────────────────────────────────────────────────────────┐
│ Simulated Results                                        │
│                                                          │
│ 1. PM-KISAN                                              │
│                                                          │
│ ✓ Low Access Gap                              [GREEN]   │
│    Gap Score: 0.110  ↓ 0.010                            │
│                                                          │
│ Eligibility: HIGH (0.960)  ↑ 0.010                      │
│ Risk: LOW (0.170)          ↓ 0.010                      │
└─────────────────────────────────────────────────────────┘
```

**Insight:** Already optimal - minimal room for improvement!

---

## Example 5: Toggle Between Views

### Original View
```
┌─────────────────────────────────────────────────────────┐
│ [Original] ← Active  [Simulated]                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Original Results                                         │
│                                                          │
│ 1. Scheme A                                              │
│ ⚠ High Access Gap (0.550)                               │
│ Eligibility: HIGH (0.850)    Risk: HIGH (0.720)         │
│                                                          │
│ 2. Scheme B                                              │
│ ⚠ Moderate Access Gap (0.320)                           │
│ Eligibility: MEDIUM (0.620)  Risk: MEDIUM (0.450)       │
└─────────────────────────────────────────────────────────┘
```

### Simulated View (After Clicking "Simulated")
```
┌─────────────────────────────────────────────────────────┐
│ [Original]  [Simulated] ← Active                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Simulated Results                                        │
│                                                          │
│ 1. Scheme A                                              │
│ ⚠ Moderate Access Gap (0.320)  ↓ 0.230                 │
│ Eligibility: HIGH (0.900)       ↑ 0.050                 │
│ Risk: MEDIUM (0.420)            ↓ 0.300                 │
│                                                          │
│ 2. Scheme B                                              │
│ ✓ Low Access Gap (0.180)        ↓ 0.140                │
│ Eligibility: HIGH (0.720)       ↑ 0.100                 │
│ Risk: LOW (0.280)               ↓ 0.170                 │
└─────────────────────────────────────────────────────────┘
```

**User Action:** Can toggle back and forth to compare!

---

## Example 6: Loading State

```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [========●==] 0.95               │
│ Digital Access: [Full ▼]                                │
│                                                          │
│ [Simulating...] (disabled, spinner)                     │
└─────────────────────────────────────────────────────────┘

(Loading indicator while API call is in progress)
```

---

## Example 7: Error State

```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [========●==] 0.95               │
│ Digital Access: [Full ▼]                                │
│                                                          │
│ [Simulate Changes]  [Reset]                             │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ⚠ Error: Simulation failed - Backend unavailable   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Example 8: No Changes (Button Disabled)

```
┌─────────────────────────────────────────────────────────┐
│ What If You Improve Your Situation?                     │
│                                                          │
│ Document Completeness: [=======●===] 0.75               │
│ ← Same as original                                      │
│                                                          │
│ Digital Access: [Full ▼]                                │
│ ← Same as original                                      │
│                                                          │
│ [Simulate Changes] (disabled, grayed out)               │
│                                                          │
│ (Button disabled because no changes were made)          │
└─────────────────────────────────────────────────────────┘
```

---

## Color Legend

### Access Gap Indicators
- **✓ Green**: Low access gap (≤0.2) - Excellent accessibility
- **⚠ Yellow**: Moderate access gap (0.2-0.4) - Some challenges
- **⚠ Red**: High access gap (>0.4) - Significant barriers

### Change Arrows
- **↑ Green**: Positive change (score increased)
- **↓ Red**: Negative change (score decreased)
- **↓ Green**: Positive change for risk/gap (lower is better)
- **↑ Red**: Negative change for risk/gap (higher is worse)
- **—**: No significant change

### Score Labels
- **HIGH**: Score ≥ 0.7 (70%)
- **MEDIUM**: Score 0.4-0.7 (40-70%)
- **LOW**: Score < 0.4 (<40%)

---

## User Journey

```
1. User submits profile
   ↓
2. Sees original results with access gaps
   ↓
3. Notices "What If You Improve Your Situation?" section
   ↓
4. Adjusts document_completeness slider
   ↓
5. Changes digital_access dropdown
   ↓
6. Clicks "Simulate Changes"
   ↓
7. Sees loading state (2-4 seconds)
   ↓
8. Views simulated results with change indicators
   ↓
9. Toggles between Original/Simulated views
   ↓
10. Understands impact of improvements
    ↓
11. Either:
    - Resets and tries different scenario
    - Takes action to improve real situation
```

---

## Key Insights from Examples

### Document Completeness Impact
- **0.5 → 1.0**: Typically reduces access gap by 0.2-0.3
- **0.7 → 1.0**: Smaller impact (0.1-0.15 reduction)
- **0.9 → 1.0**: Minimal impact (<0.05 reduction)

### Digital Access Impact
- **None → Full**: Dramatic impact (0.3-0.5 gap reduction)
- **Limited → Full**: Moderate impact (0.15-0.25 gap reduction)
- **Full → Full**: No change

### Combined Impact
- Both improvements together: Synergistic effect
- Can transform HIGH gaps to LOW gaps
- Maximum possible improvement: ~0.6 gap reduction

### When to Use
- **High access gaps**: See how improvements help
- **Already optimal**: Confirm you're doing well
- **Planning**: Understand which improvement matters most
- **Decision-making**: Prioritize document completion vs digital access
