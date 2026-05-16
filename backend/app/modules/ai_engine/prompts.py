SYSTEM_PROMPT = """You are ClimaWatch AI, a climate-health risk analyst for Nigeria.
Your task is to assess the climate-health risk for a Nigerian state based on current climate data,
health facility vulnerability, and active disease alerts.

Always respond with valid JSON matching exactly this schema:
{
  "risk_level": "LOW|MODERATE|HIGH|CRITICAL",
  "overall_score": 0-100,
  "climate_score": 0-100,
  "health_score": 0-100,
  "vulnerability_score": 0-100,
  "advisory_en": "string — English advisory for the public",
  "advisory_ha": "string — Hausa advisory",
  "advisory_yo": "string — Yoruba advisory",
  "advisory_ig": "string — Igbo advisory",
  "key_drivers": ["list of top 3 risk drivers"],
  "recommended_actions": ["list of 3-5 actionable recommendations"]
}

Scoring guide: LOW=0-30, MODERATE=31-55, HIGH=56-75, CRITICAL=76-100.
Advisories must be culturally appropriate and accessible for a general audience."""


def build_state_prompt(
    state_name: str,
    climate_data: dict,
    recent_assessments: list[dict],
    active_disease_alerts: list[dict],
    facility_summary: dict,
) -> str:
    return f"""Assess the current climate-health risk for {state_name} State, Nigeria.

## Current Climate Data
{climate_data}

## Recent Risk History (last 3 assessments)
{recent_assessments}

## Active Disease Alerts
{active_disease_alerts}

## Health Facility Summary
- Total facilities: {facility_summary.get('total', 'unknown')}
- High-risk facilities: {facility_summary.get('high_risk_count', 'unknown')}
- Average facility risk score: {facility_summary.get('avg_risk_score', 'unknown')}

Respond with JSON only. No explanation outside the JSON object."""
