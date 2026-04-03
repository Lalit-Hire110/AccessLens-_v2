"""
AccessLens v2 — /predict endpoint
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import UserInput, PredictionResponse
from app.services.pipeline_service import get_prediction

logger = logging.getLogger("accesslens.api.predict")

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(user_input: UserInput):
    """Accept a user profile and return scheme recommendations.

    Wraps the existing AccessLens pipeline with error handling.
    """
    # Build the dict the pipeline expects (exclude top_k)
    input_dict = user_input.model_dump(exclude={"top_k"})
    top_k = user_input.top_k or 5

    try:
        result = get_prediction(input_dict, top_k=top_k)
    except Exception as exc:
        logger.exception("Pipeline execution failed")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(exc)}",
        ) from exc

    return result
