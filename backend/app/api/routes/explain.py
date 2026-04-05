"""
AccessLens v2 — /explain endpoint
"""

import logging

from fastapi import APIRouter

from app.models.schemas import ExplanationInput, ExplanationResponse
from app.services.explanation_service import (
    FALLBACK_EXPLANATION,
    REQUIRED_KEYS,
    generate_explanation,
    normalise_explanation,
)

logger = logging.getLogger("accesslens.api.explain")

router = APIRouter()


@router.post("/explain", response_model=ExplanationResponse)
async def explain(data: ExplanationInput):
    """Generate an AI explanation for a single scheme recommendation.

    Always returns a valid ExplanationResponse — never raises 500.
    Falls back to a structured default if the LLM fails or returns bad JSON.
    """
    try:
        result = await generate_explanation(data.model_dump())
    except Exception as exc:
        logger.exception("Unexpected error in generate_explanation: %s", exc)
        result = {}

    # Final safety net: ensure all required keys exist before Pydantic validates
    if not REQUIRED_KEYS.issubset(result.keys()):
        missing = REQUIRED_KEYS - result.keys()
        logger.warning("Explanation missing keys %s — patching with fallback values", missing)
        for key in missing:
            result[key] = FALLBACK_EXPLANATION[key]

    result = normalise_explanation(result)

    return ExplanationResponse(**result)
