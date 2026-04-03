"""
AccessLens v2 — Pipeline Service
=================================
Thin wrapper around the existing ``run_accesslens_pipeline`` function.
Adds sys.path entries so the Phase-2 and Phase-3 modules can be imported,
then delegates entirely to the original pipeline code.

NO existing logic is modified.
"""

import logging
import sys

from app.core.config import PHASE2_DIR, PHASE3_DIR, DEFAULT_TOP_K

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("accesslens.service")

# ---------------------------------------------------------------------------
# Path setup — make Phase 2 & Phase 3 importable
# ---------------------------------------------------------------------------

for _dir in (PHASE3_DIR, PHASE2_DIR):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

# Import AFTER sys.path is patched
from pipeline_v1 import run_accesslens_pipeline  # noqa: E402

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_prediction(user_input: dict, top_k: int = DEFAULT_TOP_K) -> dict:
    """Run the full AccessLens pipeline and return structured output.

    Parameters
    ----------
    user_input : dict
        Raw user profile dictionary (matches pipeline expectations).
    top_k : int
        Number of top-ranked schemes to include.

    Returns
    -------
    dict
        ``{"persona": {...}, "recommendations": [...]}``
    """
    logger.info("Pipeline invoked — input: %s", user_input)
    logger.info("top_k = %d", top_k)

    result = run_accesslens_pipeline(user_input, top_k=top_k)

    logger.info(
        "Pipeline completed — %d recommendation(s) returned",
        len(result.get("recommendations", [])),
    )
    return result
