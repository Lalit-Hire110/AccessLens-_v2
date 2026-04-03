"""
AccessLens v2 — /simulate endpoint
===================================
What-if simulator: allows users to modify certain inputs and see how
outcomes change.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.schemas import UserInput, PredictionResponse
from app.services.pipeline_service import get_prediction

logger = logging.getLogger("accesslens.api.simulate")

router = APIRouter()


# ---------------------------------------------------------------------------
# Request Schema
# ---------------------------------------------------------------------------


class SimulationChanges(BaseModel):
    """Changes to apply to the base input for simulation."""

    document_completeness: Optional[float] = None
    digital_access: Optional[str] = None


class SimulateRequest(BaseModel):
    """Request body for /simulate endpoint."""

    base_input: UserInput
    changes: SimulationChanges


# ---------------------------------------------------------------------------
# Response Schema
# ---------------------------------------------------------------------------


class SimulateResponse(BaseModel):
    """Response containing baseline and simulated results."""

    baseline: PredictionResponse
    simulated: PredictionResponse


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(request: SimulateRequest):
    """Run what-if simulation by comparing baseline vs modified inputs.

    This endpoint:
    1. Runs the pipeline on the original input (baseline)
    2. Applies the requested changes to create a modified input
    3. Runs the pipeline again on the modified input (simulated)
    4. Returns both results for comparison

    The pipeline logic is NOT duplicated — we simply call it twice.
    """
    logger.info("Simulation requested with changes: %s", request.changes.model_dump())

    # Extract base input and top_k
    base_dict = request.base_input.model_dump(exclude={"top_k"})
    top_k = request.base_input.top_k or 5

    # ---------------------------------------------------------------------------
    # Step 1: Run baseline (original input)
    # ---------------------------------------------------------------------------

    try:
        baseline_result = get_prediction(base_dict, top_k=top_k)
    except Exception as exc:
        logger.exception("Baseline pipeline execution failed")
        raise HTTPException(
            status_code=500,
            detail=f"Baseline pipeline execution failed: {str(exc)}",
        ) from exc

    # ---------------------------------------------------------------------------
    # Step 2: Apply changes to create modified input
    # ---------------------------------------------------------------------------

    modified_dict = base_dict.copy()

    if request.changes.document_completeness is not None:
        modified_dict["document_completeness"] = request.changes.document_completeness
        logger.info(
            "Applied change: document_completeness = %s",
            request.changes.document_completeness,
        )

    if request.changes.digital_access is not None:
        modified_dict["digital_access"] = request.changes.digital_access
        logger.info(
            "Applied change: digital_access = %s",
            request.changes.digital_access,
        )

    # ---------------------------------------------------------------------------
    # Step 3: Run simulated (modified input)
    # ---------------------------------------------------------------------------

    try:
        simulated_result = get_prediction(modified_dict, top_k=top_k)
    except Exception as exc:
        logger.exception("Simulated pipeline execution failed")
        raise HTTPException(
            status_code=500,
            detail=f"Simulated pipeline execution failed: {str(exc)}",
        ) from exc

    logger.info("Simulation completed successfully")

    return SimulateResponse(
        baseline=baseline_result,
        simulated=simulated_result,
    )
