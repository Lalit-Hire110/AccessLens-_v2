"""
Eligibility Discovery Module (EDM) — AccessLens v2, Phase 3
=============================================================
Deterministic scheme-eligibility engine that takes a persona profile
(output of the Persona Mapping Function) and ranks all government
schemes by weighted eligibility score.

Pipeline:
    1. Load schemes from CSV (with xlsx fallback)
    2. For each scheme, compute per-dimension match scores
    3. Apply hard-rejection rules (instant disqualification)
    4. Enforce minimum-active-fields threshold
    5. Compute weighted eligibility score with dynamic re-normalisation
    6. Apply data-quality penalty
    7. Rank, label, and attach confidence to all schemes
"""

import logging
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("accesslens.edm")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WEIGHTS = {
    "age": 0.20,
    "gender": 0.10,
    "income_category": 0.20,
    "occupation_required": 0.15,
    "rural_urban": 0.10,
    "student_required": 0.10,
    "farmer_required": 0.10,
    "disability_required": 0.05,
}

TOTAL_POSSIBLE_FIELDS = len(WEIGHTS)  # 8

MIN_ACTIVE_FIELDS = 3

NOT_SPECIFIED = "not specified"

INCOME_ORDER = ["low", "middle", "high"]

# ---------------------------------------------------------------------------
# 1. Data Loading
# ---------------------------------------------------------------------------


def load_schemes(
    project_root: str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Load the schemes dataset from CSV, with fallback paths.

    Resolution order
    ----------------
    1. ``data/schemes/schemes_v1.csv``
    2. ``data/schemes/schemes_v1_sample.csv``
    3. ``data/schemes/schemes_v1_sample.csv.xlsx`` (Excel fallback)

    All string columns are normalised to stripped lowercase.

    Parameters
    ----------
    project_root : str or None
        Absolute path to the project root.  When *None*, the root is
        inferred as the parent of the directory containing this script.
    verbose : bool, default True
        If *True*, emit informational log messages.

    Returns
    -------
    pd.DataFrame
        DataFrame with all scheme records.

    Raises
    ------
    FileNotFoundError
        If none of the candidate paths exist.
    """
    if project_root is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

    candidates = [
        os.path.join(project_root, "data", "schemes", "schemes_v1.csv"),
        os.path.join(project_root, "data", "schemes", "schemes_v1_sample.csv"),
        os.path.join(project_root, "data", "schemes", "schemes_v1_sample.csv.xlsx"),
    ]

    df = None
    loaded_path = None

    for path in candidates:
        if os.path.isfile(path):
            if path.endswith(".xlsx"):
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)
            loaded_path = path
            break

    if df is None:
        raise FileNotFoundError(
            f"Schemes file not found.  Searched:\n"
            + "\n".join(f"  • {p}" for p in candidates)
        )

    # Normalise string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip().str.lower()

    msg = f"[EDM] Loaded {len(df)} schemes from: {loaded_path}"
    logger.info(msg)
    if verbose:
        print(f"  {msg}")

    return df


# ---------------------------------------------------------------------------
# 2. Matching Functions
# ---------------------------------------------------------------------------


def _safe_str(value) -> str:
    """Convert a value to stripped lowercase string, treating NaN as ''."""
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _is_specified(value) -> bool:
    """Return False if the value is missing, NaN, or 'not specified'."""
    v = _safe_str(value)
    return v != "" and v != NOT_SPECIFIED


def age_match(persona_age: float, min_age, max_age) -> float | None:
    """Check whether the persona's age falls within the scheme's range.

    Returns
    -------
    1.0 if within range, 0.0 if outside, or *None* if both bounds are
    unspecified (meaning the dimension should be skipped).
    """
    min_specified = _is_specified(min_age)
    max_specified = _is_specified(max_age)

    if not min_specified and not max_specified:
        return None  # ignore — not specified

    p_age = float(persona_age)

    if min_specified and max_specified:
        return 1.0 if float(min_age) <= p_age <= float(max_age) else 0.0
    elif min_specified:
        return 1.0 if p_age >= float(min_age) else 0.0
    else:  # only max specified
        return 1.0 if p_age <= float(max_age) else 0.0


def gender_match(persona_gender: str, target_gender) -> float | None:
    """Check gender eligibility.

    * ``"all"`` → 1.0  (any gender qualifies)
    * exact match → 1.0
    * else → 0.0
    * not specified → None (skip)
    """
    tg = _safe_str(target_gender)
    if not tg or tg == NOT_SPECIFIED:
        return None
    if tg == "all":
        return 1.0
    pg = _safe_str(persona_gender)
    return 1.0 if pg == tg else 0.0


def income_match(persona_income: str, scheme_income) -> float | None:
    """Check income-category eligibility using ordered proximity.

    Ordered scale: ``low < middle < high``

    * ``"not specified"`` → None (skip)
    * exact match → 1.0
    * adjacent (one step apart) → 0.5
    * else → 0.0

    Parameters
    ----------
    persona_income : str
        Persona's income level.
    scheme_income : str or any
        Scheme's required income category.

    Returns
    -------
    float or None
    """
    si = _safe_str(scheme_income)
    if not si or si == NOT_SPECIFIED:
        return None

    pi = _safe_str(persona_income)

    if pi == si:
        return 1.0

    # Ordered adjacency check
    if pi in INCOME_ORDER and si in INCOME_ORDER:
        idx_p = INCOME_ORDER.index(pi)
        idx_s = INCOME_ORDER.index(si)
        if abs(idx_p - idx_s) == 1:
            return 0.5

    return 0.0


def occupation_match(persona_occ: str, scheme_occ) -> float | None:
    """Check occupation eligibility.

    * ``"none"`` → 1.0  (no occupation requirement)
    * ``"not specified"`` → None (skip)
    * exact match → 1.0
    * else → 0.0
    """
    so = _safe_str(scheme_occ)
    if not so or so == NOT_SPECIFIED:
        return None
    if so == "none":
        return 1.0
    po = _safe_str(persona_occ)
    return 1.0 if po == so else 0.0


def rural_urban_match(
    persona_ru: str, rural_eligible, urban_eligible
) -> float | None:
    """Check rural/urban eligibility.

    * If **either** ``rural_eligible`` or ``urban_eligible`` is ``"both"``
      → always return 1.0 regardless of persona area.
    * persona is rural → checks ``rural_eligible``
    * persona is urban → checks ``urban_eligible``
    * Not specified → None (skip)

    Returns
    -------
    1.0 if eligible, 0.0 if not, None if not determinable.
    """
    re_ = _safe_str(rural_eligible)
    ue_ = _safe_str(urban_eligible)
    pru = _safe_str(persona_ru)

    # Enhancement #5 — if either field is "both", always eligible
    if re_ == "both" or ue_ == "both":
        return 1.0

    if not pru:
        return None

    if pru == "rural":
        if not re_ or re_ == NOT_SPECIFIED:
            return None
        return 1.0 if re_ == "yes" else 0.0
    elif pru == "urban":
        if not ue_ or ue_ == NOT_SPECIFIED:
            return None
        return 1.0 if ue_ == "yes" else 0.0
    else:
        return None


def student_match(persona_student: str, scheme_student) -> float:
    """Check student requirement.

    * required = ``"no"`` → 1.0
    * required = ``"yes"`` AND persona is student → 1.0
    * else → 0.0
    """
    ss = _safe_str(scheme_student)
    if ss != "yes":
        return 1.0
    ps = _safe_str(persona_student)
    return 1.0 if ps == "yes" else 0.0


def farmer_match(persona_farmer: str, scheme_farmer) -> float:
    """Check farmer requirement.

    * required = ``"no"`` → 1.0
    * required = ``"yes"`` AND persona is farmer → 1.0
    * else → 0.0
    """
    sf = _safe_str(scheme_farmer)
    if sf != "yes":
        return 1.0
    pf = _safe_str(persona_farmer)
    return 1.0 if pf == "yes" else 0.0


def disability_match(persona_disability: str, scheme_disability) -> float:
    """Check disability requirement.

    * required = ``"no"`` → 1.0
    * required = ``"yes"`` AND persona has disability → 1.0
    * else → 0.0
    """
    sd = _safe_str(scheme_disability)
    if sd != "yes":
        return 1.0
    pd_ = _safe_str(persona_disability)
    return 1.0 if pd_ == "yes" else 0.0


# ---------------------------------------------------------------------------
# 3. Eligibility Scoring
# ---------------------------------------------------------------------------


def compute_eligibility_score(
    persona: dict,
    scheme: pd.Series,
    return_breakdown: bool = False,
) -> float | dict:
    """Compute the weighted eligibility score for a single persona–scheme pair.

    Hard-rejection
    ~~~~~~~~~~~~~~
    If **age** (when specified), **gender** (when specified), or
    **occupation** (when strict / not 'none') yields 0 → score is
    immediately 0.

    Minimum-active-fields guard
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    If fewer than ``MIN_ACTIVE_FIELDS`` (3) dimensions are active after
    skipping unspecified fields → score is 0.

    Data-quality penalty
    ~~~~~~~~~~~~~~~~~~~~
    The raw weighted score is multiplied by a data-quality factor:
    ``active_fields / TOTAL_POSSIBLE_FIELDS``.

    Parameters
    ----------
    persona : dict
        Persona profile dictionary (from PMF output).
    scheme : pd.Series
        A single scheme record.
    return_breakdown : bool, default False
        If ``True``, return a debug dict with per-component scores and
        metadata instead of a single float.

    Returns
    -------
    float
        Weighted eligibility score in [0, 1] when *return_breakdown* is
        False.
    dict
        ``{"score": float, "components": {field: float, ...}}`` when
        *return_breakdown* is True.
    """
    # --- Compute all match scores ---
    match_results: dict[str, float | None] = {}

    match_results["age"] = age_match(
        persona.get("age", 0), scheme.get("min_age"), scheme.get("max_age")
    )
    match_results["gender"] = gender_match(
        persona.get("gender", ""), scheme.get("target_gender")
    )
    match_results["income_category"] = income_match(
        persona.get("income_level", ""), scheme.get("income_category")
    )
    match_results["occupation_required"] = occupation_match(
        persona.get("occupation", ""), scheme.get("occupation_required")
    )
    match_results["rural_urban"] = rural_urban_match(
        persona.get("rural_urban", ""),
        scheme.get("rural_eligible"),
        scheme.get("urban_eligible"),
    )
    match_results["student_required"] = student_match(
        persona.get("student_status", "no"), scheme.get("student_required")
    )
    match_results["farmer_required"] = farmer_match(
        persona.get("farmer_status", "no"), scheme.get("farmer_required")
    )
    match_results["disability_required"] = disability_match(
        persona.get("disability_status", "no"), scheme.get("disability_required")
    )

    _zero_result = (
        {"score": 0.0, "components": {}} if return_breakdown else 0.0
    )

    # --- Hard-rejection rule ---
    # Age: reject if specified and failed
    age_score = match_results.get("age")
    if age_score is not None and age_score == 0.0:
        logger.debug(
            "Hard reject (age) for scheme %s", scheme.get("scheme_id")
        )
        return _zero_result

    # Gender: reject if specified and failed
    gender_score = match_results.get("gender")
    if gender_score is not None and gender_score == 0.0:
        logger.debug(
            "Hard reject (gender) for scheme %s", scheme.get("scheme_id")
        )
        return _zero_result

    # Occupation: reject if strict (not 'none' and not skipped) and failed
    occ_score = match_results.get("occupation_required")
    scheme_occ_raw = _safe_str(scheme.get("occupation_required"))
    if (
        occ_score is not None
        and occ_score == 0.0
        and scheme_occ_raw != "none"
        and _is_specified(scheme_occ_raw)
    ):
        logger.debug(
            "Hard reject (occupation) for scheme %s", scheme.get("scheme_id")
        )
        return _zero_result

    # --- Collect active dimensions ---
    active_weights: dict[str, float] = {}
    active_scores: dict[str, float] = {}

    for field, weight in WEIGHTS.items():
        score_val = match_results.get(field)
        if score_val is None:
            continue  # skip unspecified dimensions
        active_weights[field] = weight
        active_scores[field] = score_val

    active_field_count = len(active_weights)

    # --- Enhancement #1: minimum active fields check ---
    if active_field_count < MIN_ACTIVE_FIELDS:
        logger.debug(
            "Too few active fields (%d < %d) for scheme %s",
            active_field_count,
            MIN_ACTIVE_FIELDS,
            scheme.get("scheme_id"),
        )
        return _zero_result

    # --- Weighted scoring with dynamic re-normalisation ---
    total_weight = sum(active_weights.values())
    if total_weight == 0:
        return _zero_result

    raw_score = 0.0
    components: dict[str, float] = {}

    for field, weight in active_weights.items():
        normalised_weight = weight / total_weight
        weighted_sim = active_scores[field] * normalised_weight
        raw_score += weighted_sim
        components[field] = round(weighted_sim, 6)

    # --- Enhancement #2: data-quality penalty ---
    data_quality_factor = active_field_count / TOTAL_POSSIBLE_FIELDS
    final_score = round(raw_score * data_quality_factor, 6)

    if return_breakdown:
        return {
            "score": final_score,
            "raw_score": round(raw_score, 6),
            "data_quality_factor": round(data_quality_factor, 4),
            "active_fields": active_field_count,
            "components": components,
        }

    return final_score


# ---------------------------------------------------------------------------
# 4. Eligibility Labelling
# ---------------------------------------------------------------------------


def classify_eligibility(score: float) -> str:
    """Classify a score into an eligibility label.

    * ≥ 0.85 → ``"high"``
    * 0.60 – 0.85 → ``"medium"``
    * 0.40 – 0.60 → ``"low"``
    * < 0.40 → ``"not recommended"``

    Parameters
    ----------
    score : float
        Eligibility score in [0, 1].

    Returns
    -------
    str
        Human-readable eligibility label.
    """
    if score >= 0.85:
        return "high"
    elif score >= 0.60:
        return "medium"
    elif score >= 0.40:
        return "low"
    else:
        return "not recommended"


# ---------------------------------------------------------------------------
# 5. Scheme Ranking
# ---------------------------------------------------------------------------


def rank_schemes(
    persona: dict,
    schemes_df: pd.DataFrame,
    verbose: bool = True,
) -> list[dict]:
    """Rank all schemes by eligibility score for a given persona.

    Steps
    -----
    1. Compute eligibility score for every scheme.
    2. Attach an eligibility label and a confidence field.
    3. Sort descending by score.

    Parameters
    ----------
    persona : dict
        Persona profile dictionary (from PMF output).
    schemes_df : pd.DataFrame
        Full schemes DataFrame (as loaded by ``load_schemes``).
    verbose : bool, default True
        If *True*, emit informational log messages to stdout.

    Returns
    -------
    list[dict]
        Sorted list of ``{"scheme_id", "scheme_name", "score",
        "eligibility", "confidence"}`` dictionaries, highest score first.
    """
    results: list[dict] = []

    for _, scheme_row in schemes_df.iterrows():
        score = compute_eligibility_score(persona, scheme_row)
        eligibility = classify_eligibility(score)
        results.append(
            {
                "scheme_id": scheme_row["scheme_id"],
                "scheme_name": scheme_row["scheme_name"],
                "score": score,
                "eligibility": eligibility,
                "confidence": eligibility,  # mirrors eligibility label
            }
        )

    # Sort descending by score, stable (preserves original order for ties)
    results.sort(key=lambda r: r["score"], reverse=True)

    logger.info("Ranked %d schemes for persona", len(results))
    if verbose:
        high = sum(1 for r in results if r["eligibility"] == "high")
        logger.info("  high=%d, total=%d", high, len(results))

    return results


# ---------------------------------------------------------------------------
# 6. CLI Test Block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Configure logging for CLI runs
    logging.basicConfig(
        level=logging.DEBUG,
        format="  [%(levelname)s] %(name)s — %(message)s",
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    print("=" * 72)
    print("  AccessLens v2 — Eligibility Discovery Module (EDM) Test Run")
    print("=" * 72)

    # Load schemes
    schemes_df = load_schemes(project_root, verbose=True)
    print(f"  [EDM] Total schemes available: {len(schemes_df)}\n")

    # Sample persona (as would be returned by PMF)
    sample_persona = {
        "age": 26,
        "gender": "male",
        "rural_urban": "urban",
        "income_level": "middle",
        "occupation": "worker",
        "education_level": "graduate",
        "student_status": "no",
        "farmer_status": "no",
        "disability_status": "no",
    }

    print("  Persona Input:")
    for key, value in sample_persona.items():
        print(f"    {key:30s}: {value}")

    print("\n  Running eligibility ranking...\n")
    ranked = rank_schemes(sample_persona, schemes_df, verbose=False)

    # Display top 5
    top_n = 5
    print("-" * 72)
    print(f"  Top {top_n} Eligible Schemes")
    print("-" * 72)
    print(
        f"  {'Rank':<6}{'ID':<10}{'Score':<10}{'Eligibility':<18}"
        f"{'Scheme Name'}"
    )
    print("  " + "-" * 68)

    for i, entry in enumerate(ranked[:top_n], start=1):
        print(
            f"  {i:<6}{entry['scheme_id']:<10}"
            f"{entry['score']:<10.4f}{entry['eligibility']:<18}"
            f"{entry['scheme_name']}"
        )

    # Full summary
    print("\n" + "-" * 72)
    print("  Full Ranking Summary")
    print("-" * 72)
    labels = {"high": 0, "medium": 0, "low": 0, "not recommended": 0}
    for entry in ranked:
        labels[entry["eligibility"]] += 1

    for label, count in labels.items():
        print(f"    {label:20s}: {count} scheme(s)")

    # Debug breakdown for top scheme
    if ranked:
        top = ranked[0]
        top_row = schemes_df[schemes_df["scheme_id"] == top["scheme_id"]].iloc[0]
        breakdown = compute_eligibility_score(
            sample_persona, top_row, return_breakdown=True
        )
        print("\n" + "-" * 72)
        print(f"  Score Breakdown — {top['scheme_id']} ({top['scheme_name']})")
        print("-" * 72)
        for field, wscore in breakdown["components"].items():
            print(f"    {field:30s}: {wscore:.6f}")
        print(f"    {'RAW SCORE':30s}: {breakdown['raw_score']:.6f}")
        print(f"    {'DATA QUALITY FACTOR':30s}: {breakdown['data_quality_factor']:.4f}")
        print(
            f"    {'ACTIVE FIELDS':30s}: "
            f"{breakdown['active_fields']} / {TOTAL_POSSIBLE_FIELDS}"
        )
        print(f"    {'FINAL SCORE':30s}: {breakdown['score']:.6f}")

    print("\n" + "=" * 72)
