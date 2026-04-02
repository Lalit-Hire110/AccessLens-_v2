"""
Persona Mapping Function (PMF) — AccessLens v2, Phase 3
========================================================
Deterministic persona-matching module that maps a user profile to the
most relevant persona from a pre-defined persona dataset.

Pipeline:
    1. Normalize & validate user input
    2. Load personas from CSV
    3. Hard-filter personas by structural rules
    4. Compute weighted similarity scores (with optional debug breakdown)
    5. Return the best-matching persona with confidence level
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WEIGHTS = {
    "age": 0.18,
    "income_level": 0.18,
    "occupation": 0.15,
    "education_level": 0.15,
    "rural_urban": 0.10,
    "digital_access": 0.10,
    "document_completeness": 0.05,
    "institutional_dependency": 0.05,
    "gender": 0.04,
}

INCOME_ORDER = ["low", "middle", "high"]
EDUCATION_ORDER = ["none", "primary", "secondary", "graduate"]
DIGITAL_ORDER = ["none", "limited", "full"]
INSTITUTIONAL_ORDER = ["low", "medium", "high"]

OCCUPATION_RELATED_PAIRS = {
    frozenset({"worker", "self-employed"}),
    frozenset({"unemployed", "student"}),
    frozenset({"farmer", "worker"}),
}

# Variant mappings used by the input normalisation layer.
# Maps common alternative spellings / phrasings to canonical values.
VARIANT_MAP = {
    # income_level
    "low income": "low",
    "middle income": "middle",
    "high income": "high",
    "lower": "low",
    "upper": "high",
    # rural_urban
    "village": "rural",
    "city": "urban",
    "town": "urban",
    # education_level
    "no education": "none",
    "no schooling": "none",
    "uneducated": "none",
    "elementary": "primary",
    "high school": "secondary",
    "college": "graduate",
    "university": "graduate",
    "postgraduate": "graduate",
    # digital_access
    "no access": "none",
    "partial": "limited",
    "complete": "full",
    # institutional_dependency
    "moderate": "medium",
    # gender
    "m": "male",
    "f": "female",
    "man": "male",
    "woman": "female",
    # disability_status
    "disabled": "yes",
    "not disabled": "no",
    # student_status / farmer_status
    "true": "yes",
    "false": "no",
}

# ---------------------------------------------------------------------------
# 1. Data Loading
# ---------------------------------------------------------------------------


def load_personas(filepath: str) -> pd.DataFrame:
    """Load the personas CSV into a pandas DataFrame.

    Parameters
    ----------
    filepath : str
        Path to the ``personas_v1.csv`` file.

    Returns
    -------
    pd.DataFrame
        DataFrame with all persona records.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Personas file not found: {filepath}")
    df = pd.read_csv(filepath)
    # Normalise string columns to lowercase / stripped
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip().str.lower()
    return df


# ---------------------------------------------------------------------------
# 2. Input Normalization & Validation
# ---------------------------------------------------------------------------


def normalize_input(user_input: dict) -> dict:
    """Normalise and validate raw user input before scoring.

    Processing steps
    ----------------
    1. Strip whitespace and lowercase all string values.
    2. Map common variant spellings to canonical values via ``VARIANT_MAP``.
    3. Coerce ``document_completeness`` to float and clip to [0, 1].

    Parameters
    ----------
    user_input : dict
        Raw user profile dictionary.

    Returns
    -------
    dict
        Cleaned, validated copy of the user profile.
    """
    normalised: dict = {}

    for key, value in user_input.items():
        if value is None:
            normalised[key] = None
            continue

        if isinstance(value, str):
            clean = value.strip().lower()
            # Attempt variant mapping
            clean = VARIANT_MAP.get(clean, clean)
            normalised[key] = clean
        else:
            normalised[key] = value

    # --- Numeric validation for document_completeness ---
    if "document_completeness" in normalised and normalised["document_completeness"] is not None:
        try:
            doc_val = float(normalised["document_completeness"])
        except (ValueError, TypeError):
            doc_val = 0.0
        normalised["document_completeness"] = max(0.0, min(1.0, doc_val))

    return normalised


# ---------------------------------------------------------------------------
# 3. Hard Filtering (relaxed — rural_urban no longer a hard filter)
# ---------------------------------------------------------------------------


def filter_personas(df: pd.DataFrame, user_input: dict) -> pd.DataFrame:
    """Apply hard-filtering rules to narrow the candidate persona set.

    Rules
    -----
    * If user occupation is ``student`` → persona ``student_status`` must be
      ``yes``.
    * If user occupation is ``farmer`` → persona ``farmer_status`` must be
      ``yes``.
    * Personas with an age difference > 40 from the user are removed.

    .. note::
       ``rural_urban`` is **no longer** a hard filter (Enhancement #6).
       It still participates in the similarity scoring.

    Parameters
    ----------
    df : pd.DataFrame
        Full personas DataFrame.
    user_input : dict
        User profile dictionary.

    Returns
    -------
    pd.DataFrame
        Filtered subset of personas.
    """
    filtered = df.copy()

    # --- occupation-based status filters ---
    if "occupation" in user_input and user_input["occupation"] is not None:
        user_occ = str(user_input["occupation"]).strip().lower()
        if user_occ == "student":
            filtered = filtered[filtered["student_status"] == "yes"]
        elif user_occ == "farmer":
            filtered = filtered[filtered["farmer_status"] == "yes"]

    # --- age difference must be ≤ 40 ---
    if "age" in user_input and user_input["age"] is not None:
        user_age = float(user_input["age"])
        filtered = filtered[abs(filtered["age"] - user_age) <= 40]

    return filtered.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Similarity Functions
# ---------------------------------------------------------------------------


def age_similarity(user_age: float, persona_age: float) -> float:
    """Compute age similarity.

    Formula: ``S = max(0, 1 − |user_age − persona_age| / 50)``
    """
    return max(0.0, 1.0 - abs(user_age - persona_age) / 50.0)


def categorical_similarity(
    value1: str,
    value2: str,
    ordered_list: list | None = None,
) -> float:
    """Compute similarity between two categorical values.

    * Exact match → 1.0
    * Adjacent in *ordered_list* → 0.5
    * Otherwise → 0.0
    """
    v1 = str(value1).strip().lower()
    v2 = str(value2).strip().lower()

    if v1 == v2:
        return 1.0

    if ordered_list is not None:
        ordered_lower = [str(x).strip().lower() for x in ordered_list]
        if v1 in ordered_lower and v2 in ordered_lower:
            idx1 = ordered_lower.index(v1)
            idx2 = ordered_lower.index(v2)
            if abs(idx1 - idx2) == 1:
                return 0.5

    return 0.0


def gender_similarity(user_gender: str, persona_gender: str) -> float:
    """Compute gender similarity.

    * Exact match → 1.0
    * Otherwise → 0.0
    """
    u = str(user_gender).strip().lower()
    p = str(persona_gender).strip().lower()
    return 1.0 if u == p else 0.0


def income_similarity(user_income: str, persona_income: str) -> float:
    """Compute income-level similarity using ordered scale low/middle/high.

    * Exact → 1.0
    * Adjacent → 0.5
    * Else → 0.0
    """
    return categorical_similarity(user_income, persona_income, INCOME_ORDER)


def occupation_similarity(user_occ: str, persona_occ: str) -> float:
    """Compute occupation similarity.

    * Exact → 1.0
    * Related pair → 0.5  (worker↔self-employed, unemployed↔student,
      farmer↔worker)
    * Else → 0.0
    """
    u = str(user_occ).strip().lower()
    p = str(persona_occ).strip().lower()

    if u == p:
        return 1.0

    if frozenset({u, p}) in OCCUPATION_RELATED_PAIRS:
        return 0.5

    return 0.0


def education_similarity(user_edu: str, persona_edu: str) -> float:
    """Compute education-level similarity using ordered scale
    none < primary < secondary < graduate.
    """
    return categorical_similarity(user_edu, persona_edu, EDUCATION_ORDER)


def digital_similarity(user_digital: str, persona_digital: str) -> float:
    """Compute digital-access similarity using ordered scale
    none < limited < full.
    """
    return categorical_similarity(user_digital, persona_digital, DIGITAL_ORDER)


def institutional_similarity(user_inst: str, persona_inst: str) -> float:
    """Compute institutional-dependency similarity using ordered scale
    low < medium < high.
    """
    return categorical_similarity(user_inst, persona_inst, INSTITUTIONAL_ORDER)


def document_similarity(user_doc: float, persona_doc: float) -> float:
    """Compute document-completeness similarity.

    Formula: ``S = max(0, 1 − |user_doc − persona_doc|)``
    """
    return max(0.0, 1.0 - abs(float(user_doc) - float(persona_doc)))


# ---------------------------------------------------------------------------
# Similarity dispatcher — maps field names to their similarity functions
# ---------------------------------------------------------------------------

SIMILARITY_FUNCTIONS = {
    "age": lambda u, p: age_similarity(u, p),
    "income_level": lambda u, p: income_similarity(u, p),
    "occupation": lambda u, p: occupation_similarity(u, p),
    "education_level": lambda u, p: education_similarity(u, p),
    "rural_urban": lambda u, p: categorical_similarity(u, p),
    "digital_access": lambda u, p: digital_similarity(u, p),
    "document_completeness": lambda u, p: document_similarity(u, p),
    "institutional_dependency": lambda u, p: institutional_similarity(u, p),
    "gender": lambda u, p: gender_similarity(u, p),
}

# ---------------------------------------------------------------------------
# 5. Scoring
# ---------------------------------------------------------------------------


def compute_score(
    user_input: dict,
    persona_row: pd.Series,
    return_breakdown: bool = False,
) -> float | dict:
    """Compute the weighted similarity score between a user and a persona.

    * Skips any scoring dimension whose key is missing from *user_input* or
      whose value is ``None``.
    * Dynamically re-normalises the remaining weights so they still sum to 1.

    Parameters
    ----------
    user_input : dict
        User profile dictionary.
    persona_row : pd.Series
        A single persona record.
    return_breakdown : bool, default False
        If ``True``, return a debug dict with per-component scores instead
        of a single float.

    Returns
    -------
    float
        Weighted similarity score in [0, 1] when *return_breakdown* is False.
    dict
        ``{"total_score": float, "components": {field: float, ...}}``
        when *return_breakdown* is True.
    """
    active_weights: dict[str, float] = {}

    for field, weight in WEIGHTS.items():
        # Skip if user field is missing or None
        if field not in user_input or user_input[field] is None:
            continue
        active_weights[field] = weight

    # If no active fields, return 0
    total_weight = sum(active_weights.values())
    if total_weight == 0:
        if return_breakdown:
            return {"total_score": 0.0, "components": {}}
        return 0.0

    score = 0.0
    components: dict[str, float] = {}

    for field, weight in active_weights.items():
        sim_fn = SIMILARITY_FUNCTIONS[field]
        sim = sim_fn(user_input[field], persona_row[field])
        normalised_weight = weight / total_weight
        weighted_sim = sim * normalised_weight
        score += weighted_sim
        components[field] = round(weighted_sim, 6)

    score = round(score, 6)

    if return_breakdown:
        return {"total_score": score, "components": components}

    return score


# ---------------------------------------------------------------------------
# 6. Confidence Classification
# ---------------------------------------------------------------------------


def classify_confidence(score: float) -> str:
    """Classify a similarity score into a confidence level.

    * score > 0.8 → ``"high"``
    * 0.6 ≤ score ≤ 0.8 → ``"medium"``
    * score < 0.6 → ``"low"``

    Parameters
    ----------
    score : float
        Weighted similarity score in [0, 1].

    Returns
    -------
    str
        One of ``"high"``, ``"medium"``, or ``"low"``.
    """
    if score > 0.8:
        return "high"
    elif score >= 0.6:
        return "medium"
    else:
        return "low"


# ---------------------------------------------------------------------------
# 7. Persona Mapping (main entry point)
# ---------------------------------------------------------------------------


def map_persona(user_input: dict, personas_df: pd.DataFrame) -> dict:
    """Map a user profile to the best-matching persona.

    Steps
    -----
    1. Normalise and validate user input via ``normalize_input``.
    2. Apply ``filter_personas`` to narrow candidates.
    3. If the filtered set is empty, fall back to the full dataset.
    4. Compute a weighted similarity score for every candidate.
    5. Select the persona with the **highest** score.
    6. Break ties by **smallest age difference**; if still tied, choose the
       **first occurrence**.
    7. Classify a ``confidence`` level based on the final score.

    Parameters
    ----------
    user_input : dict
        User profile dictionary (raw — will be normalised internally).
    personas_df : pd.DataFrame
        Full personas DataFrame (as loaded by ``load_personas``).

    Returns
    -------
    dict
        ``{"persona_id": ..., "score": ..., "confidence": ...,
          "matched_persona": {...}}``
    """
    # Step 1 — normalise & validate
    normalised_input = normalize_input(user_input)

    # Step 2 — filter
    candidates = filter_personas(personas_df, normalised_input)

    # Step 3 — fallback
    if candidates.empty:
        candidates = personas_df.copy()

    # Step 4 — compute scores
    scores = candidates.apply(
        lambda row: compute_score(normalised_input, row), axis=1
    )
    candidates = candidates.copy()
    candidates["_score"] = scores

    # Step 5 & 6 — select best persona (highest score → smallest age diff → first)
    user_age = normalised_input.get("age")
    if user_age is not None:
        candidates["_age_diff"] = abs(candidates["age"] - float(user_age))
    else:
        candidates["_age_diff"] = 0

    # Sort: score descending, then age_diff ascending, then original order
    candidates = candidates.sort_values(
        by=["_score", "_age_diff"],
        ascending=[False, True],
    ).reset_index(drop=True)

    best = candidates.iloc[0]

    # Build result
    final_score = round(float(best["_score"]), 6)
    matched_persona = best.drop(labels=["_score", "_age_diff"]).to_dict()
    result = {
        "persona_id": best["persona_id"],
        "score": final_score,
        "confidence": classify_confidence(final_score),
        "matched_persona": matched_persona,
    }
    return result


# ---------------------------------------------------------------------------
# 8. CLI Test Block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Resolve path relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    personas_path = os.path.join(project_root, "data", "personas", "personas_v1.csv")

    print("=" * 65)
    print("  AccessLens v2 — Persona Mapping Function (PMF) Test Run")
    print("=" * 65)
    print(f"\nLoading personas from: {personas_path}")

    personas_df = load_personas(personas_path)
    print(f"Total personas loaded: {len(personas_df)}\n")

    # ---- Standard test with clean input ----
    sample_user = {
        "age": 26,
        "gender": "male",
        "rural_urban": "urban",
        "income_level": "middle",
        "occupation": "worker",
        "education_level": "graduate",
        "digital_access": "full",
        "document_completeness": 0.75,
        "institutional_dependency": "low",
    }

    print("User Input:")
    for key, value in sample_user.items():
        print(f"  {key:30s}: {value}")

    print("\nRunning persona mapping...\n")
    result = map_persona(sample_user, personas_df)

    print("-" * 65)
    print(f"  Matched Persona ID : {result['persona_id']}")
    print(f"  Similarity Score   : {result['score']}")
    print(f"  Confidence         : {result['confidence']}")
    print("-" * 65)
    print("\n  Full Matched Persona Details:")
    for key, value in result["matched_persona"].items():
        print(f"    {key:30s}: {value}")

    # ---- Debug breakdown for matched persona ----
    print("\n" + "-" * 65)
    print("  Score Breakdown (debug mode):")
    print("-" * 65)
    normalised = normalize_input(sample_user)
    matched_row = personas_df[personas_df["persona_id"] == result["persona_id"]].iloc[0]
    breakdown = compute_score(normalised, matched_row, return_breakdown=True)
    for field, weighted_score in breakdown["components"].items():
        print(f"    {field:30s}: {weighted_score:.6f}")
    print(f"    {'TOTAL':30s}: {breakdown['total_score']:.6f}")

    # ---- Variant-input normalization demo ----
    print("\n" + "=" * 65)
    print("  Input Normalization Demo")
    print("=" * 65)
    messy_input = {
        "age": 26,
        "gender": "  Male ",
        "rural_urban": "City",
        "income_level": "LOW INCOME",
        "occupation": "worker",
        "education_level": "College",
        "digital_access": "FULL",
        "document_completeness": 1.5,  # out-of-range → clipped to 1.0
        "institutional_dependency": "Moderate",
    }
    print("\n  Raw input:")
    for k, v in messy_input.items():
        print(f"    {k:30s}: {v!r}")

    clean = normalize_input(messy_input)
    print("\n  Normalised input:")
    for k, v in clean.items():
        print(f"    {k:30s}: {v!r}")

    print("\n" + "=" * 65)
