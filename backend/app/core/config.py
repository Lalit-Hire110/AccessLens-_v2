"""
AccessLens v2 — Backend Configuration
"""

import os

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

# backend/app/core/config.py  →  backend/app/core/
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))

# backend/app/core  →  backend/app  →  backend  →  Access_Lens_v2 (project root)
PROJECT_ROOT = os.path.abspath(os.path.join(_CORE_DIR, "..", "..", ".."))

PHASE2_DIR = os.path.join(PROJECT_ROOT, "phase 2 - Access Risk Model v1")
PHASE3_DIR = os.path.join(PROJECT_ROOT, "phase 3 - Interface Layer")

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_TOP_K = 5
