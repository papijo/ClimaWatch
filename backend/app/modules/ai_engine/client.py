import json
import logging
import re

from openai import AsyncOpenAI

from app.config import settings
from app.modules.ai_engine.prompts import SYSTEM_PROMPT, build_state_prompt
from app.modules.ai_engine.schemas import RiskAssessmentResponse

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

MODEL = "gpt-4o"


def extract_json(raw: str) -> dict:
    """Strips markdown code fences if the model wraps JSON in ```json ... ```."""
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    return json.loads(cleaned)


async def assess_state(
    state_name: str,
    climate_data: dict,
    recent_assessments: list[dict],
    active_disease_alerts: list[dict],
    facility_summary: dict,
) -> RiskAssessmentResponse:
    prompt = build_state_prompt(
        state_name, climate_data, recent_assessments, active_disease_alerts, facility_summary
    )
    response = await _client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2048,
        temperature=0.2,
        timeout=60,
    )
    raw_content = response.choices[0].message.content
    raw_json = extract_json(raw_content)
    validated = RiskAssessmentResponse.model_validate(raw_json)
    logger.info(
        "AI assessment for %s: %s (score=%.1f)",
        state_name, validated.risk_level, validated.overall_score,
    )
    return validated
