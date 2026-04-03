# AccessLens v2 - Complete Architecture with What-If Simulator

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Next.js Frontend)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MAIN PAGE                               │
│                      (app/page.tsx)                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  UserForm    │  │ ResultsDisplay│  │ WhatIfSimulator      │ │
│  │              │  │               │  │                      │ │
│  │ • Age        │  │ • Persona     │  │ • Slider (doc)       │ │
│  │ • Gender     │  │ • Schemes     │  │ • Dropdown (digital) │ │
│  │ • Income     │  │ • Scores      │  │ • Simulate Button    │ │
│  │ • ...        │  │ • Explanations│  │ • View Toggle        │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│         │                  │                      │             │
└─────────┼──────────────────┼──────────────────────┼─────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API CLIENT LAYER                           │
│                       (lib/api.ts)                              │
│                                                                 │
│  getPrediction()    fetchAllExplanations()    simulate()        │
└─────────────────────────────────────────────────────────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│                     (app/main.py)                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ /predict     │  │ /explain     │  │ /simulate            │ │
│  │              │  │              │  │                      │ │
│  │ POST         │  │ POST         │  │ POST                 │ │
│  │ UserInput    │  │ Explanation  │  │ SimulateRequest      │ │
│  │ → Prediction │  │ Input        │  │ → SimulateResponse   │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│         │                  │                      │             │
└─────────┼──────────────────┼──────────────────────┼─────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────────────┐   │
│  │ pipeline_service.py  │  │ explanation_service.py       │   │
│  │                      │  │                              │   │
│  │ get_prediction()     │  │ generate_explanation()       │   │
│  │   ↓                  │  │   ↓                          │   │
│  │ Calls pipeline_v1    │  │ Calls Groq AI API            │   │
│  └──────────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────┐    ┌──────────────────────┐
│  DETERMINISTIC PIPELINE │    │     AI LAYER         │
│  (Phase 2 & 3 modules)  │    │   (Groq/LLaMA)       │
│                         │    │                      │
│  • Persona Mapping      │    │  • Explanation Gen   │
│  • Eligibility Engine   │    │  • Barrier Analysis  │
│  • Risk Calculation     │    │  • Next Steps        │
│  • Access Gap Calc      │    │                      │
└─────────────────────────┘    └──────────────────────┘
```

## What-If Simulator Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHAT-IF SIMULATOR FLOW                       │
└─────────────────────────────────────────────────────────────────┘

Step 1: User Submits Form
┌──────────────┐
│  UserInput   │
│  • age: 26   │
│  • doc: 0.5  │
│  • digital:  │
│    limited   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  POST /predict                       │
│  → Pipeline → Baseline Results       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Display Results + What-If Simulator │
└──────────────────────────────────────┘

Step 2: User Adjusts Parameters
┌──────────────────────────────────────┐
│  What-If Controls                    │
│  • doc: 0.5 → 0.95 (slider)         │
│  • digital: limited → full (dropdown)│
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  User Clicks "Simulate Changes"      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  POST /simulate                      │
│  {                                   │
│    base_input: { ...original... },   │
│    changes: {                        │
│      document_completeness: 0.95,    │
│      digital_access: "full"          │
│    }                                 │
│  }                                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Backend Processing                  │
│                                      │
│  1. Run pipeline(base_input)         │
│     → baseline results               │
│                                      │
│  2. Apply changes:                   │
│     modified = base + changes        │
│                                      │
│  3. Run pipeline(modified)           │
│     → simulated results              │
│                                      │
│  4. Return both                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Frontend Receives Response          │
│  {                                   │
│    baseline: { ... },                │
│    simulated: { ... }                │
│  }                                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Display Comparison                  │
│                                      │
│  For each scheme:                    │
│  • Show before/after scores          │
│  • Highlight changes (↑/↓)           │
│  • Color-code improvements           │
│  • Emphasize access gap changes      │
└──────────────────────────────────────┘

Step 3: User Toggles View
┌──────────────────────────────────────┐
│  [Original] [Simulated]              │
│     ↑           ↑                    │
│  Click to switch between views       │
└──────────────────────────────────────┘
```

## Component Hierarchy

```
App (page.tsx)
│
├── UserForm
│   ├── Age Input
│   ├── Gender Select
│   ├── Income Select
│   ├── Document Completeness Input
│   ├── Digital Access Select
│   └── Submit Button
│
├── ResultsDisplay
│   ├── Persona Card
│   │   └── Persona Details
│   │
│   └── Recommendations
│       └── For each scheme:
│           ├── Scheme Header
│           ├── Access Gap Card (prominent)
│           ├── Scores Grid
│           ├── Insight
│           └── ExplanationSection (collapsible)
│               ├── Summary (always visible)
│               ├── Toggle Button
│               └── Details (when expanded)
│                   ├── Why You Qualify
│                   ├── Barriers
│                   ├── Access Gap Explanation
│                   └── Next Steps
│
└── WhatIfSimulator
    ├── Controls Card
    │   ├── Document Completeness Slider
    │   ├── Digital Access Dropdown
    │   ├── Simulate Button
    │   └── Reset Button
    │
    ├── View Toggle
    │   ├── Original Button
    │   └── Simulated Button
    │
    └── Comparison Display
        └── For each scheme:
            ├── Scheme Header
            ├── Access Gap Card (with change indicator)
            └── Scores Grid (with change indicators)
```

## State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                      APP STATE (page.tsx)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  result: PredictionResponse | null                              │
│  userInput: UserInput | null                                    │
│  loading: boolean                                               │
│  error: string | null                                           │
│  explanations: Record<number, ExplanationResponse | null>       │
│  explanationErrors: Record<number, boolean>                     │
│  explanationsLoading: boolean                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              WHATIF SIMULATOR STATE (component)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  documentCompleteness: number                                   │
│  digitalAccess: string                                          │
│  simulationResult: SimulateResponse | null                      │
│  loading: boolean                                               │
│  error: string | null                                           │
│  viewMode: "original" | "simulated"                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Utility Functions (lib/utils.ts)

```
┌─────────────────────────────────────────────────────────────────┐
│                      UTILITY FUNCTIONS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  getAccessGapLevel(score: number)                               │
│    Input: 0.3                                                   │
│    Output: "moderate"                                           │
│    Logic: ≤0.2 → low, ≤0.4 → moderate, >0.4 → high            │
│                                                                 │
│  getAccessGapInfo(level: "low" | "moderate" | "high")           │
│    Input: "moderate"                                            │
│    Output: { level, color, bgColor, borderColor, icon }         │
│                                                                 │
│  getScoreLabel(score: number)                                   │
│    Input: 0.85                                                  │
│    Output: "HIGH"                                               │
│    Logic: ≥0.7 → HIGH, ≥0.4 → MEDIUM, <0.4 → LOW              │
│                                                                 │
│  formatScoreChange(before: number, after: number)               │
│    Input: (0.5, 0.7)                                            │
│    Output: { value: 0.2, formatted: "↑ 0.200",                 │
│              direction: "up", color: "text-green-400" }         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND ENDPOINTS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  POST /predict                                                  │
│    Input: UserInput                                             │
│    Output: PredictionResponse                                   │
│    Purpose: Get scheme recommendations                          │
│                                                                 │
│  POST /explain                                                  │
│    Input: ExplanationInput                                      │
│    Output: ExplanationResponse                                  │
│    Purpose: Generate AI explanation for a scheme                │
│                                                                 │
│  POST /simulate                                                 │
│    Input: SimulateRequest                                       │
│    Output: SimulateResponse                                     │
│    Purpose: Run what-if simulation                              │
│                                                                 │
│  GET /health                                                    │
│    Output: { status: "ok" }                                     │
│    Purpose: Health check                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Models

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA MODELS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  UserInput                                                      │
│    • age: number                                                │
│    • gender: string                                             │
│    • rural_urban: string                                        │
│    • income_level: string                                       │
│    • occupation: string                                         │
│    • education_level: string                                    │
│    • digital_access: string                                     │
│    • document_completeness: number | string                     │
│    • institutional_dependency: string                           │
│    • top_k?: number                                             │
│                                                                 │
│  SchemeResult                                                   │
│    • scheme_id: string                                          │
│    • scheme_name: string                                        │
│    • eligibility_score: number                                  │
│    • eligibility: string                                        │
│    • risk_score: number                                         │
│    • access_gap: number                                         │
│    • insight?: string                                           │
│                                                                 │
│  PredictionResponse                                             │
│    • persona: Record<string, unknown>                           │
│    • recommendations: SchemeResult[]                            │
│                                                                 │
│  SimulateRequest                                                │
│    • base_input: UserInput                                      │
│    • changes: SimulationChanges                                 │
│                                                                 │
│  SimulateResponse                                               │
│    • baseline: PredictionResponse                               │
│    • simulated: PredictionResponse                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frontend                                                       │
│    • Next.js 13+ (App Router)                                   │
│    • React 18+                                                  │
│    • TypeScript 5+                                              │
│    • Tailwind CSS 3+                                            │
│                                                                 │
│  Backend                                                        │
│    • FastAPI                                                    │
│    • Python 3.10+                                               │
│    • Pydantic (validation)                                      │
│    • Uvicorn (ASGI server)                                      │
│                                                                 │
│  AI Layer                                                       │
│    • Groq API                                                   │
│    • LLaMA 3.1 70B                                              │
│                                                                 │
│  Pipeline                                                       │
│    • Custom Python modules                                      │
│    • Pandas (data processing)                                   │
│    • NumPy (calculations)                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │         Load Balancer               │
        └─────────────────────────────────────┘
                      │           │
         ┌────────────┘           └────────────┐
         ▼                                     ▼
┌──────────────────┐                  ┌──────────────────┐
│  Frontend Server │                  │  Backend Server  │
│  (Next.js)       │                  │  (FastAPI)       │
│  Port: 3000      │◄────────────────►│  Port: 8000      │
└──────────────────┘                  └──────────────────┘
         │                                     │
         │                                     ▼
         │                            ┌──────────────────┐
         │                            │   Groq API       │
         │                            │   (External)     │
         │                            └──────────────────┘
         │
         ▼
┌──────────────────┐
│   Static Assets  │
│   (CDN)          │
└──────────────────┘
```

This architecture provides a clean, scalable, and maintainable system for the AccessLens v2 application with the What-If Simulator feature fully integrated.
