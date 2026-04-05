"""
AccessLens v2 — AI Explanation Service
========================================
Calls Groq LLM to generate structured explanations for deterministic
pipeline outputs.

RULES:
  - AI MUST NOT compute eligibility or risk
  - AI MUST NOT invent new facts
  - AI MUST ONLY explain given structured data
  - AI output must be structured JSON
"""

import asyncio
import json
import logging
import os
import re

import httpx

# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------

groq_semaphore = asyncio.Semaphore(2)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("accesslens.explanation")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

# ---------------------------------------------------------------------------
# Required keys — must all be present in LLM output
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {
    "summary",
    "eligibility_explanation",
    "risk_explanation",
    "access_gap_explanation",
    "key_barriers",
    "improvement_suggestions",
}

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are an explanation engine for a deterministic policy system called AccessLens.\n\n"
    "STRICT RULES:\n"
    "- Use ONLY the provided data\n"
    "- DO NOT assume anything not present\n"
    "- DO NOT add new reasons\n"
    "- DO NOT generalize\n"
    "- If a factor is not listed, DO NOT mention it\n"
    "- Be precise and grounded in numbers and factors\n\n"
    "TASK:\n"
    "Convert structured system output into a clear, human explanation.\n\n"
    "OUTPUT FORMAT (STRICT JSON — no markdown, no extra text):\n"
    "{\n"
    '  "summary": "",\n'
    '  "eligibility_explanation": "",\n'
    '  "risk_explanation": "",\n'
    '  "access_gap_explanation": "",\n'
    '  "key_barriers": [],\n'
    '  "improvement_suggestions": []\n'
    "}\n\n"
    "GUIDELINES:\n"
    "1. SUMMARY: Mention scheme name, eligibility_score, risk_score, access_gap.\n"
    "2. ELIGIBILITY: Use ONLY eligibility_factors. Tie to input_snapshot values.\n"
    "3. RISK: Use ONLY risk_factors. Explain why risk is high/low using inputs.\n"
    "4. ACCESS GAP: Explain relationship between eligibility and risk.\n"
    "5. KEY BARRIERS: Directly derived from risk_factors. "
    "If risk_factors is empty, set to [\"No major barriers detected\"].\n"
    "6. IMPROVEMENTS: Suggest fixes ONLY based on risk_factors. "
    "If risk_factors is empty, set to [\"No improvements required\"].\n\n"
    "STYLE: Direct, simple, no fluff. No words like 'may', 'could', 'generally'.\n"
    "CRITICAL: Return ONLY the JSON object. No markdown. No explanation outside JSON."
)

USER_PROMPT_TEMPLATE = (
    "INPUT DATA:\n{data_json}\n\n"
    "Return ONLY a strict JSON object with these exact keys: "
    "summary, eligibility_explanation, risk_explanation, "
    "access_gap_explanation, key_barriers, improvement_suggestions."
)

# ---------------------------------------------------------------------------
# Fallback — guaranteed complete structure
# ---------------------------------------------------------------------------

FALLBACK_EXPLANATION = {
    "summary": "Explanation unavailable",
    "eligibility_explanation": "Could not generate explanation",
    "risk_explanation": "Risk details unavailable",
    "access_gap_explanation": "Access gap could not be computed",
    "key_barriers": [],
    "improvement_suggestions": [],
}

# ---------------------------------------------------------------------------
# JSON extraction + validation
# ---------------------------------------------------------------------------

def extract_json(content: str) -> dict:
    """Extract the first valid JSON object from an LLM response string."""
    # 1. Direct parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Grab first {...} block
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("No valid JSON object found in LLM response.")


def validate_structure(data: dict) -> bool:
    """Return True only if all required keys are present."""
    return REQUIRED_KEYS.issubset(data.keys())


def normalise_explanation(data: dict) -> dict:
    """Ensure list fields are never empty — insert default messages."""
    if not data.get("key_barriers"):
        data["key_barriers"] = ["No major barriers detected"]
    if not data.get("improvement_suggestions"):
        data["improvement_suggestions"] = ["No improvements required"]
    return data

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

async def generate_explanation(input_data: dict) -> dict:
    """Generate a structured AI explanation for a single recommendation.

    Parameters
    ----------
    input_data : dict
        Must contain: persona_summary, scheme, eligibility, risk, access_gap.

    Returns
    -------
    dict
        Structured explanation with all REQUIRED_KEYS guaranteed.
    """
    print("[EXPLAIN INPUT]:", json.dumps(input_data, indent=2, default=str))

    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — returning fallback")
        return normalise_explanation(dict(FALLBACK_EXPLANATION))

    data_json = json.dumps(input_data, indent=2, default=str)
    user_prompt = USER_PROMPT_TEMPLATE.format(data_json=data_json)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 512,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("Calling Groq API (model=%s) …", GROQ_MODEL)

    # Two attempts: initial + 1 retry on bad JSON or invalid structure
    for attempt in range(2):
        try:
            async with groq_semaphore:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        GROQ_API_URL,
                        json=payload,
                        headers=headers,
                    )
            response.raise_for_status()

            body = response.json()
            raw_content = body["choices"][0]["message"]["content"]

            print(f"[LLM RAW OUTPUT] (attempt {attempt + 1}):", raw_content)
            logger.info("LLM raw output (attempt %d):\n%s", attempt + 1, raw_content)

            # Extract JSON
            try:
                parsed = extract_json(raw_content)
            except ValueError as exc:
                logger.warning("JSON extraction failed (attempt %d): %s", attempt + 1, exc)
                if attempt < 1:
                    continue
                break

            # Validate structure
            if not validate_structure(parsed):
                missing = REQUIRED_KEYS - parsed.keys()
                logger.warning(
                    "Missing keys in LLM response (attempt %d): %s",
                    attempt + 1,
                    missing,
                )
                if attempt < 1:
                    continue
                break

            # All good — normalise and return
            logger.info("Explanation generated successfully on attempt %d", attempt + 1)
            return normalise_explanation(parsed)

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Groq API HTTP error: %s — %s",
                exc.response.status_code,
                exc.response.text,
            )
            if exc.response.status_code == 429 and attempt < 1:
                logger.warning("Rate limit hit — waiting 8 s before retry")
                await asyncio.sleep(8)
                continue
            if attempt < 1:
                continue
            break

        except Exception as exc:
            logger.error("Groq API call failed (attempt %d): %s", attempt + 1, exc)
            if attempt < 1:
                continue
            break

    logger.warning("All attempts exhausted — returning fallback")
    return normalise_explanation(dict(FALLBACK_EXPLANATION))


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

async def check_groq_health() -> bool:
    """Run a simple health check against the Groq API on startup."""
    if not GROQ_API_KEY:
        return False

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "temperature": 0.1,
        "max_tokens": 5,
    }

    for attempt in range(2):
        logger.info("Running AI health check (model=%s, attempt %d) …", GROQ_MODEL, attempt + 1)
        try:
            async with groq_semaphore:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(GROQ_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("AI health check passed (model=%s)", GROQ_MODEL)
            return True
        except httpx.HTTPStatusError as exc:
            logger.error(
                "AI health check HTTP error (model=%s): %s — %s",
                GROQ_MODEL,
                exc.response.status_code,
                exc.response.text,
            )
            if exc.response.status_code == 429 and attempt < 1:
                await asyncio.sleep(8)
                continue
        except Exception as exc:
            logger.error("AI health check failed (model=%s): %s", GROQ_MODEL, exc)

        if attempt < 1:
            logger.warning("Retrying health check…")

    return False
