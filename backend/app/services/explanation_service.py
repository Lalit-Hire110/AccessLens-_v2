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
    "OUTPUT FORMAT (STRICT JSON):\n"
    "{\n"
    '  "summary": "",\n'
    '  "eligibility_explanation": "",\n'
    '  "risk_explanation": "",\n'
    '  "access_gap_explanation": "",\n'
    '  "key_barriers": [],\n'
    '  "improvement_suggestions": []\n'
    "}\n\n"
    "GUIDELINES:\n"
    "1. SUMMARY:\n"
    "- Mention scheme name\n"
    "- Mention eligibility_score, risk_score, access_gap\n\n"
    "2. ELIGIBILITY:\n"
    "- ONLY use eligibility_factors (these are provided as structured objects)\n"
    "- Tie to input_snapshot values\n\n"
    "3. RISK:\n"
    "- ONLY use risk_factors (these are provided as structured objects)\n"
    "- Explain why risk is high/low using inputs\n\n"
    "4. ACCESS GAP:\n"
    "- Explain relationship between eligibility and risk\n\n"
    "5. KEY BARRIERS:\n"
    "- Directly derived from risk_factors\n\n"
    "6. IMPROVEMENTS:\n"
    "- Suggest fixes ONLY based on risk_factors\n"
    '- Example: "missing_documents" -> "Complete required documents"\n\n'
    "STYLE:\n"
    "- Direct, simple, no fluff\n"
    '- No words like "may", "could", "generally"\n'
    'CRITICAL REQUIREMENT: You MUST return ONLY a strict JSON object. Do not format with markdown.'
)

USER_PROMPT_TEMPLATE = (
    "INPUT DATA:\n{data_json}\n\n"
    "Output in STRICT JSON format."
)

# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

FALLBACK_EXPLANATION = {
    "summary": "Based on your numeric profile, you appear eligible for this scheme, but face potential access barriers.",
    "eligibility_explanation": "You meet the basic demographic criteria for this scheme.",
    "risk_explanation": "Some application dimensions require additional effort to fulfill.",
    "access_gap_explanation": "Your high eligibility is somewhat offset by actionable application risks.",
    "key_barriers": ["Unverified barriers"],
    "improvement_suggestions": ["Review scheme requirements manually"],
}

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def extract_json(content: str) -> dict:
    """Extract and parse JSON from a string that might contain text around it."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    cleaned = content.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("\n", 1)
        if len(parts) > 1:
            cleaned = parts[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
            
    raise ValueError("Failed to extract valid JSON from response.")



async def generate_explanation(input_data: dict) -> dict:
    """Generate a structured AI explanation for a single recommendation.

    Parameters
    ----------
    input_data : dict
        Must contain: persona_summary, scheme, eligibility, risk, access_gap.

    Returns
    -------
    dict
        Structured explanation with keys: summary, barriers, next_steps.
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
        "temperature": 0.1,
        "max_tokens": 200,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("Calling Groq API (model=%s) …", GROQ_MODEL)

    # Try up to 2 times (initial + 1 retry)
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
            content = body["choices"][0]["message"]["content"]
            
            logger.info("RAW LLM OUTPUT:\n%s", content)

            explanation = extract_json(content)
            logger.info("Explanation generated successfully")
            return explanation

        except (json.JSONDecodeError, ValueError):
            logger.warning("JSON parse/extraction failed (attempt %d/2) — retrying", attempt + 1)
            continue

        except httpx.HTTPStatusError as exc:
            logger.error("Groq API HTTP error: %s - response: %s", exc.response.status_code, exc.response.text)
            if exc.response.status_code == 429 and attempt < 1:
                logger.warning("Rate limit hit, waiting 8 seconds before retry...")
                await asyncio.sleep(8)
                continue
            if attempt < 1:
                logger.warning("Retrying after HTTP error (attempt %d/2)", attempt + 1)
                continue
            break

        except Exception as exc:
            logger.error("Groq API call failed: %s", exc)
            if attempt < 1:
                logger.warning("Retrying after Exception (attempt %d/2)", attempt + 1)
                continue
            break

    logger.warning("All attempts failed — returning fallback")
    return FALLBACK_EXPLANATION

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
        current_model = payload["model"]
        logger.info("Running AI health check (model=%s) ...", current_model)
        try:
            async with groq_semaphore:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(GROQ_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("AI health check passed (model=%s)", current_model)
            return True
        except httpx.HTTPStatusError as exc:
            logger.error("AI health check HTTP error (model=%s): %s - %s", current_model, exc.response.status_code, exc.response.text)
            if exc.response.status_code == 429 and attempt < 1:
                logger.warning("Rate limit hit, waiting 8 seconds before retry...")
                await asyncio.sleep(8)
                continue
        except Exception as exc:
            logger.error("AI health check failed (model=%s): %s", current_model, exc)

        if attempt < 1:
            logger.warning("Retrying health check...")

    return False
