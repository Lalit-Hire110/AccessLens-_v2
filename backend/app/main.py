"""
AccessLens v2 — FastAPI Application Entry Point
"""

import logging
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import predict, health, explain, simulate

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="  [%(levelname)s] %(name)s — %(message)s",
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AccessLens v2 API",
    description="REST API for the AccessLens policy-access simulation pipeline",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins for development
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, tags=["Prediction"])
app.include_router(explain.router, tags=["Explanation"])
app.include_router(simulate.router, tags=["Simulation"])

# ---------------------------------------------------------------------------
# Startup Validation
# ---------------------------------------------------------------------------

from app.services.explanation_service import check_groq_health

@app.on_event("startup")
async def startup_event():
    logging.getLogger("accesslens").info("Running startup AI validation...")
    ai_ok = await check_groq_health()
    if ai_ok:
        logging.getLogger("accesslens").info("AI OK")
    else:
        logging.getLogger("accesslens").warning("AI FALLBACK MODE")
