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

import json
import logging
import os

import httpx

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
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are an explanation engine for a policy access system.\n"
    "You must explain structured results clearly and faithfully.\n\n"
    "Rules:\n"
    "- Do not invent facts\n"
    "- Do not assume missing data\n"
    "- Only use provided input\n"
    "- If something is uncertain, say so\n"
    "- Be simple, clear, and practical\n"
    "- Always respond with valid JSON only, no markdown fences"
)

USER_PROMPT_TEMPLATE = (
    "Explain the following result:\n\n"
    "DATA:\n{data_json}\n\n"
    "Output in JSON with exactly these fields:\n"
    "- summary: one-sentence plain-language summary\n"
    "- eligibility_explanation: why this eligibility score was assigned\n"
    "- barriers: list of access barriers the user may face\n"
    "- access_gap_explanation: what the access gap means practically\n"
    "- next_steps: list of actionable steps the user can take\n\n"
    "Keep language simple and grounded. Return ONLY valid JSON."
)

# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

FALLBACK_EXPLANATION = {
    "summary": "Based on your profile, you appear eligible for this scheme. However, access may depend on factors like documentation, digital access, or institutional support.",
    "eligibility_explanation": "Please refer to the eligibility score directly.",
    "barriers": [],
    "access_gap_explanation": "Please refer to the access gap score directly.",
    "next_steps": ["Review the scheme details manually."],
}

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
        Structured explanation with keys: summary, eligibility_explanation,
        barriers, access_gap_explanation, next_steps.
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — returning fallback")
        return FALLBACK_EXPLANATION

    data_json = json.dumps(input_data, indent=2, default=str)
    user_prompt = USER_PROMPT_TEMPLATE.format(data_json=data_json)

    if not SYSTEM_PROMPT or not user_prompt:
        logger.error("System or User prompt is empty")
        return FALLBACK_EXPLANATION

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    if not messages:
        logger.error("Messages array is empty or invalid")
        return FALLBACK_EXPLANATION

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("Calling Groq API (model=%s) …", GROQ_MODEL)

    # Try up to 2 times (initial + 1 retry)
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    json=payload,
                    headers=headers,
                )
            response.raise_for_status()

            body = response.json()
            content = body["choices"][0]["message"]["content"]

            # Strip markdown fences if the model wraps them
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]  # drop first line
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            content = content.strip()

            explanation = json.loads(content)
            logger.info("Explanation generated successfully")
            return explanation

        except json.JSONDecodeError:
            logger.warning("JSON parse failed (attempt %d/2) — retrying", attempt + 1)
            if attempt < 1:
                payload["model"] = "llama-3.1-70b-versatile"
            continue

        except httpx.HTTPStatusError as exc:
            logger.error("Groq API HTTP error: %s - response: %s", exc.response.status_code, exc.response.text)
            if attempt < 1:
                logger.warning("Retrying after HTTP error with fallback model (attempt %d/2)", attempt + 1)
                payload["model"] = "llama-3.1-70b-versatile"
                continue
            break

        except Exception as exc:
            logger.error("Groq API call failed: %s", exc)
            if attempt < 1:
                logger.warning("Retrying after Exception with fallback model (attempt %d/2)", attempt + 1)
                payload["model"] = "llama-3.1-70b-versatile"
                continue
            break

    logger.warning("All attempts failed — returning fallback")
    return FALLBACK_EXPLANATION
