# AccessLens v2

A deterministic policy access simulation engine that computes normalised **Access Risk Scores** for (scheme, persona) pairs and surfaces actionable scheme recommendations through a full-stack web interface.

---

## What it does

AccessLens v2 models the non-financial barriers an individual faces when applying for government welfare schemes — across three stages of the beneficiary journey:

| Stage | Description |
|---|---|
| **Discovery** | Awareness of a scheme and clarity on eligibility |
| **Application** | Document gathering, portal interaction |
| **Verification** | Approvals, processing delays, final confirmation |

The model produces an **Access Risk Score** from `0.0` (minimal friction) to `1.0` (very high friction) for any (scheme, persona) combination, without using machine learning, real enrollment data, or personal information.

---

## Architecture

```
AccessLens v2
├── phase 2 - Access Risk Model v1/   # Core risk model + batch/counterfactual simulation
├── phase 3 - Interface Layer/        # Persona mapping, eligibility engine, pipeline
├── backend/                          # FastAPI REST API
│   └── app/
│       ├── api/routes/               # /predict  /explain  /simulate  /health
│       ├── services/                 # Pipeline orchestration + Groq AI explanation
│       └── models/schemas.py         # Pydantic request/response models
├── frontend/                         # Next.js 13 App Router UI
│   ├── app/                          # / (home)  /input  /results
│   ├── components/                   # Navbar, SchemeCarousel, ErrorBoundary, etc.
│   └── lib/                          # API client, global state, motion presets
└── data/                             # Schemes, personas, barriers datasets
```

---

## Modelled Barriers

Four categories of access friction:

- **Awareness** — lack of scheme knowledge or eligibility clarity
- **Documentation** — missing or hard-to-obtain documents
- **Digital** — no device, connectivity, or digital literacy
- **Institutional** — intermediary dependence, processing delays, inconsistency

> All severity values and barrier mappings are structured assumptions for simulation and counterfactual analysis. No real outcome data is used.

---

## Project Phases

### Phase 2 — Access Risk Model

| File | Purpose |
|---|---|
| `access_risk_model_v1.py` | Core risk score computation |
| `batch_simulation_v1.py` | Population-level analytics across thousands of persona-scheme pairs |
| `counterfactual_simulation_v1.py` | What-if engine — tests interventions and shows delta risk changes |
| `plots_v1.py` | Matplotlib/seaborn visualisations for batch results |

### Phase 3 — Interface Layer

| File | Purpose |
|---|---|
| `persona_mapping_v1.py` | Maps raw demographic inputs to standardised Persona IDs |
| `eligibility_engine_v1.py` | Deterministic weighted scoring to rank schemes by eligibility |
| `pipeline_v1.py` | End-to-end orchestration: input → persona → eligibility → risk → JSON |

### Phase 4 — Full-Stack Web Application (current)

A production-deployed web interface built on top of the Phase 3 pipeline.

**Backend (FastAPI)**

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/predict` | POST | Run full pipeline — returns persona match + ranked scheme recommendations |
| `/explain` | POST | Generate AI explanation for a single scheme result (Groq LLM) |
| `/simulate` | POST | What-if simulation — compare baseline vs modified inputs |

**Frontend (Next.js 13)**

| Page | Route | Description |
|---|---|---|
| Home | `/` | Landing page with hero, featured scheme carousel, explore cards |
| Input | `/input` | User profile form with quick-fill demo, tips, loading states |
| Results | `/results` | Scheme cards with access gap badges, progress bars, AI explanations, visualisations |

**Frontend features added in this phase:**
- Multi-page App Router structure with React Context global state
- Scheme cards with dominant access gap badge, animated progress bars, skeleton loaders
- Per-card on-demand AI explanation (Groq, cached in-memory)
- What-If Simulator panel (adjust document completeness / digital access)
- Recharts bar chart visualisation of eligibility, risk, and access gap scores
- Framer Motion animation system (`lib/motion.ts`) — consistent presets across all pages
- Design token system (Tailwind config + CSS custom properties)
- Global `ErrorBoundary` component — catches unhandled render errors
- `NetworkBanner` — detects offline state and warns the user
- API client with retry logic, per-endpoint timeouts, and production-safe logging

---

## Running locally

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # add your GROQ_API_KEY
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

The UI will be available at `http://localhost:3000`.

### Phase 2 / Phase 3 scripts (standalone)

```bash
# Phase 3 pipeline
cd "phase 3 - Interface Layer"
python pipeline_v1.py

# Phase 2 risk model
cd "phase 2 - Access Risk Model v1"
python access_risk_model_v1.py

# Counterfactual simulation
python counterfactual_simulation_v1.py
```

To change the simulation target, edit the bottom of `access_risk_model_v1.py`:

```python
TARGET_SCHEME_ID  = "pmmvy"   # e.g. pmjay, jsy, kasp
TARGET_PERSONA_ID = "p05"     # p01 – p12
```

---

## Environment variables

### Backend

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key for AI-powered explanations |
| `GROQ_MODEL` | No | Model override (default: `llama-3.1-8b-instant`) |

### Frontend

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Public URL of the deployed backend |

---

## Deployment

### Backend — Render / Railway

1. Set `GROQ_API_KEY` in environment variables.
2. Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. Health check path: `GET /health`

### Frontend — Vercel

1. Connect the repository to Vercel.
2. Set `NEXT_PUBLIC_API_URL` to your deployed backend URL (e.g. `https://accesslens-api.onrender.com`).
3. Framework preset: **Next.js**
4. Build command: `npm run build`
5. Output directory: `.next`

---

## Tech stack

| Layer | Technology |
|---|---|
| Risk model | Python, pandas |
| Backend | FastAPI, Pydantic, httpx, python-dotenv |
| AI explanations | Groq (llama-3.1-8b-instant) |
| Frontend | Next.js 13 (App Router), React 18, TypeScript |
| Styling | Tailwind CSS v3, CSS custom properties |
| Animations | Framer Motion |
| Visualisations | Recharts |
| State management | React Context |
| Deployment | Vercel (frontend), Render (backend) |

---

## Documentation

| File | Description |
|---|---|
| `docs/MODEL_SPEC.md` | Mathematical and logical specification of the risk algorithm |
| `docs/USAGE.md` | Full guide — all scheme and persona IDs |
| `docs/BARRIERS_JUSTIFICATION.txt` | Barrier taxonomy breakdown |
| `docs/ASSUMPTIONS.txt` | Data gaps, limitations, and modelling assumptions |
| `docs/DATA_POLICY.txt` | Data handling and privacy policy |
