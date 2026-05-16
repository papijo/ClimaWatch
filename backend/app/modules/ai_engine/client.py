import json

from openai import AsyncOpenAI

from app.config import settings
from app.modules.ai_engine.prompts import SYSTEM_PROMPT, build_state_prompt
from app.modules.ai_engine.schemas import RiskAssessmentResponse

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

MODEL = "gpt-4o"


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
    )
    raw_json = json.loads(response.choices[0].message.content)
    return RiskAssessmentResponse.model_validate(raw_json)
