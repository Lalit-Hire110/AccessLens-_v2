"""
AccessLens v2 — Pydantic Schemas
"""

from typing import Optional, Union

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------


class UserInput(BaseModel):
    """Schema for user profile input sent to the /predict endpoint."""

    age: int = Field(..., ge=0, le=150, description="User's age")
    gender: str = Field(..., description="male / female")
    rural_urban: str = Field(..., description="rural / urban")
    income_level: str = Field(..., description="low / middle / high")
    occupation: str = Field(..., description="worker / farmer / student / …")
    education_level: str = Field(..., description="none / primary / secondary / graduate")
    digital_access: str = Field(..., description="none / limited / full")
    document_completeness: Union[float, str] = Field(
        ...,
        description="Document completeness — float 0-1 or descriptive string",
    )
    institutional_dependency: str = Field(..., description="low / medium / high")
    top_k: Optional[int] = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of top schemes to return (default 5)",
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class SchemeResult(BaseModel):
    """A single scheme recommendation."""

    scheme_id: str
    scheme_name: str
    eligibility_score: float
    eligibility: str
    risk_score: float
    access_gap: float
    insight: Optional[str] = None


class PredictionResponse(BaseModel):
    """Full pipeline response returned by /predict."""

    persona: dict
    recommendations: list[SchemeResult]


# ---------------------------------------------------------------------------
# Explanation — /explain
# ---------------------------------------------------------------------------


class PersonaSummary(BaseModel):
    """Condensed persona fields relevant for explanation."""

    age: int
    occupation: str
    income_level: str
    digital_access: str
    document_completeness: Union[float, str]


class SchemeSummary(BaseModel):
    scheme_name: str


class EligibilitySummary(BaseModel):
    score: float
    label: str


class RiskSummary(BaseModel):
    score: float
    label: str


class ExplanationInput(BaseModel):
    """Input for the /explain endpoint."""

    persona_summary: PersonaSummary
    scheme: SchemeSummary
    eligibility: EligibilitySummary
    risk: RiskSummary
    access_gap: float


class ExplanationResponse(BaseModel):
    """Structured AI-generated explanation."""

    summary: str
    barriers: list[str] = []
    next_steps: list[str] = []

