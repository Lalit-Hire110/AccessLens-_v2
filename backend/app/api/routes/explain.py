"""
AccessLens v2 — /explain endpoint
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import ExplanationInput, ExplanationResponse
from app.services.explanation_service import generate_explanation

logger = logging.getLogger("accesslens.api.explain")

router = APIRouter()


@router.post("/explain", response_model=ExplanationResponse)
async def explain(data: ExplanationInput):
    """Generate an AI explanation for a single scheme recommendation.

    The AI does NOT compute scores — it only interprets the structured
    data provided by the deterministic pipeline.
    """
    try:
        explanation = await generate_explanation(data.model_dump())
    except Exception as exc:
        logger.exception("Explanation generation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Explanation generation failed: {str(exc)}",
        ) from exc

    return explanation
