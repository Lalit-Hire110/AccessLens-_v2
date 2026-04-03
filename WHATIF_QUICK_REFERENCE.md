# What-If Simulator - Quick Reference

## API Endpoint

### POST /simulate

**Request:**
```json
{
  "base_input": {
    "age": 26,
    "gender": "male",
    "rural_urban": "urban",
    "income_level": "middle",
    "occupation": "worker",
    "education_level": "graduate",
    "digital_access": "limited",
    "document_completeness": 0.5,
    "institutional_dependency": "low",
    "top_k": 5
  },
  "changes": {
    "document_completeness": 0.95,
    "digital_access": "full"
  }
}
```

**Response:**
```json
{
  "baseline": {
    "persona": {...},
    "recommendations": [
      {
        "scheme_id": "PM-KISAN",
        "scheme_name": "PM-KISAN Direct Benefit Transfer",
        "eligibility_score": 0.85,
        "risk_score": 0.35,
        "access_gap": 0.50,
        "eligibility": "fully_eligible"
      }
    ]
  },
  "simulated": {
    "persona": {...},
    "recommendations": [
      {
        "scheme_id": "PM-KISAN",
        "scheme_name": "PM-KISAN Direct Benefit Transfer",
        "eligibility_score": 0.90,
        "risk_score": 0.20,
        "access_gap": 0.30,
        "eligibility": "fully_eligible"
      }
    ]
  }
}
```

## Utility Functions

### getAccessGapLevel(score)
```typescript
getAccessGapLevel(0.15) // "low"
getAccessGapLevel(0.30) // "moderate"
getAccessGapLevel(0.55) // "high"
```

### getAccessGapInfo(level)
```typescript
getAccessGapInfo("low")
// Returns: { level: "Low Access Gap", color: "text-green-400", ... }

getAccessGapInfo("moderate")
// Returns: { level: "Moderate Access Gap", color: "text-yellow-400", ... }

getAccessGapInfo("high")
// Returns: { level: "High Access Gap", color: "text-red-400", ... }
```

### getScoreLabel(score)
```typescript
getScoreLabel(0.85) // "HIGH"
getScoreLabel(0.55) // "MEDIUM"
getScoreLabel(0.25) // "LOW"
```

### formatScoreChange(before, after)
```typescript
formatScoreChange(0.50, 0.70)
// Returns: { value: 0.20, formatted: "↑ 0.200", direction: "up", color: "text-green-400" }

formatScoreChange(0.70, 0.50)
// Returns: { value: -0.20, formatted: "↓ 0.200", direction: "down", color: "text-red-400" }

formatScoreChange(0.50, 0.50)
// Returns: { value: 0, formatted: "—", direction: "same", color: "text-gray-400" }
```

## Component Usage

### WhatIfSimulator

```tsx
import WhatIfSimulator from "@/components/WhatIfSimulator";

<WhatIfSimulator
  baseInput={userInput}
  baselineRecommendations={result.recommendations}
/>
```

**Props:**
- `baseInput`: Original UserInput object
- `baselineRecommendations`: Array of SchemeResult from baseline prediction

## State Flow

```
Initial State
├── documentCompleteness: from baseInput
├── digitalAccess: from baseInput
├── simulationResult: null
├── loading: false
├── error: null
└── viewMode: "original"

User Adjusts Parameters
├── documentCompleteness: updated
└── digitalAccess: updated

User Clicks "Simulate"
├── loading: true
├── Call /simulate API
├── simulationResult: API response
├── viewMode: "simulated"
└── loading: false

User Toggles View
└── viewMode: "original" | "simulated"

User Clicks "Reset"
├── Reset to original values
├── simulationResult: null
├── viewMode: "original"
└── error: null
```

## Visual Indicators

### Access Gap Colors
- **Green** (✓): Low access gap (≤0.2) - Good to go!
- **Yellow** (⚠): Moderate access gap (0.2-0.4) - Some challenges
- **Red** (⚠): High access gap (>0.4) - Significant barriers

### Change Indicators
- **↑ Green**: Score improved (eligibility up, risk/gap down)
- **↓ Red**: Score declined (eligibility down, risk/gap up)
- **— Gray**: No significant change (<0.001 difference)

### Score Labels
- **HIGH**: Score ≥ 0.7
- **MEDIUM**: Score 0.4-0.7
- **LOW**: Score < 0.4

## Common Scenarios

### Scenario 1: Complete Documents
```
Before: document_completeness = 0.5
After:  document_completeness = 1.0

Expected Impact:
- Risk scores decrease (↓)
- Access gaps decrease (↓)
- Eligibility may increase slightly (↑)
```

### Scenario 2: Gain Digital Access
```
Before: digital_access = "none"
After:  digital_access = "full"

Expected Impact:
- Risk scores decrease significantly (↓)
- Access gaps decrease (↓)
- More schemes become accessible
```

### Scenario 3: Both Improvements
```
Before: document_completeness = 0.5, digital_access = "limited"
After:  document_completeness = 1.0, digital_access = "full"

Expected Impact:
- Maximum risk reduction (↓↓)
- Significant access gap improvement (↓↓)
- Best possible outcomes
```

## Troubleshooting

### Button Disabled
**Cause:** No changes made to parameters
**Solution:** Adjust slider or dropdown to enable button

### Simulation Failed
**Cause:** Backend error or network issue
**Solution:** Check error message, verify backend is running

### No Changes Visible
**Cause:** Changes too small or parameters already optimal
**Solution:** Try more significant changes (e.g., 0.5 → 1.0)

### Schemes Don't Match
**Cause:** Different schemes returned in baseline vs simulated
**Solution:** This is expected - persona may change, affecting recommendations

## Performance Tips

### Backend
- Each simulation = 2 pipeline runs
- Typical response time: 2-4 seconds
- No caching (each simulation is unique)

### Frontend
- Minimal re-renders (local state)
- Efficient comparison by scheme_id
- Smooth transitions with CSS

## Integration Checklist

- [x] Backend endpoint created (`/simulate`)
- [x] Backend endpoint registered in main.py
- [x] Frontend API client updated
- [x] Utility functions created
- [x] WhatIfSimulator component created
- [x] ResultsDisplay refactored to use utils
- [x] Main page integrated with simulator
- [x] TypeScript types defined
- [x] Error handling implemented
- [x] Loading states implemented
- [x] Documentation created

## Quick Test

### Backend Test
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d @test_simulate.json
```

### Frontend Test
```bash
# Start frontend
cd frontend
npm run dev

# Open browser
# Navigate to http://localhost:3000
# Submit form
# Scroll to "What If You Improve Your Situation?"
# Adjust sliders
# Click "Simulate Changes"
# Toggle between Original/Simulated views
```

## Key Files

### Backend
- `backend/app/api/routes/simulate.py` - Simulate endpoint
- `backend/app/main.py` - Router registration

### Frontend
- `frontend/lib/utils.ts` - Utility functions
- `frontend/lib/api.ts` - API client
- `frontend/components/WhatIfSimulator.tsx` - Main component
- `frontend/components/ResultsDisplay.tsx` - Refactored component
- `frontend/app/page.tsx` - Integration

### Documentation
- `WHATIF_IMPLEMENTATION.md` - Detailed guide
- `WHATIF_QUICK_REFERENCE.md` - This file

## Summary

The What-If Simulator allows users to:
1. Adjust document_completeness (slider 0-1)
2. Change digital_access (dropdown: none/limited/full)
3. See how changes affect scheme recommendations
4. Compare original vs simulated results side-by-side
5. Understand impact with visual indicators (↑/↓)
6. Reset and try different scenarios

All implemented with clean architecture, no breaking changes, and production-ready code.
