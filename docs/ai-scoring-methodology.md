# ClimaWatch AI Scoring Methodology

## Overview

ClimaWatch uses OpenAI's GPT-4o model to generate climate-health risk assessments for each of Nigeria's 36 states and FCT. The AI receives structured context about a state's current conditions and returns a validated JSON risk assessment.

## Model Configuration

- **Model:** GPT-4o
- **Temperature:** 0.2 (low variance for consistent scoring)
- **Response format:** `json_object` (guaranteed valid JSON)
- **Max tokens:** 2048
- **Timeout:** 60 seconds

## Input Context

Every assessment prompt includes:

1. **Current Climate Data** — merged from up to 3 sources (Open-Meteo, NASA POWER, NOAA CDO): temperature, humidity, rainfall, wind speed, UV index, air quality.
2. **Recent Risk History** — last 3 assessments for trend awareness. Prevents sudden oscillation and rewards consistent improvement.
3. **Active Disease Alerts** — from NCDC and WHO AFRO bulletins. Active outbreaks and warnings directly increase the health sub-score.
4. **Health Facility Summary** — total facility count, type breakdown, ownership distribution, high-risk facility count, and average facility risk score.

## Scoring Structure

### Sub-scores (0–100 each)

| Sub-score | Weight | Key Drivers |
|-----------|--------|-------------|
| `climate_score` | 40% | Temperature extremes, rainfall (flood/drought), humidity, wind, UV |
| `health_score` | 35% | Active disease outbreaks, alert severity, facility risk levels |
| `vulnerability_score` | 25% | Facility density, infrastructure quality, average facility risk |

### Overall Score

`overall_score = climate_score × 0.40 + health_score × 0.35 + vulnerability_score × 0.25`

### Risk Level Thresholds

| Score Range | Risk Level |
|-------------|------------|
| 0–30 | LOW |
| 31–55 | MODERATE |
| 56–75 | HIGH |
| 76–100 | CRITICAL |

## Climate Score Rubric

| Factor | Low Risk | Moderate Risk | High Risk |
|--------|----------|---------------|-----------|
| Temperature | 25–35°C | 35–40°C or 10–15°C | >40°C or <10°C |
| Rainfall | 5–30mm/day | 30–50mm/day | >50mm/day (flood) or <5mm in rainy season (drought) |
| Humidity | 40–70% | 70–85% | >85% (disease breeding) or <20% (heat amplifier) |
| Wind Speed | <30 km/h | 30–60 km/h | >60 km/h (structural risk) |
| UV Index | <6 | 6–10 | >10 (extreme exposure) |

## Trend Awareness

The AI considers the trajectory from the last 3 assessments:
- **Rising trend:** slight upward bias to anticipate worsening conditions
- **Falling trend (2+ cycles):** slight downward bias to reflect improving conditions
- **First assessment:** relies solely on current data with no trend adjustment

## Advisory Generation

Each assessment produces advisories in 4 languages:
- **English (advisory_en):** standard advisory
- **Hausa (advisory_ha):** culturally adapted for Northern Nigeria
- **Yoruba (advisory_yo):** culturally adapted for South-West Nigeria
- **Igbo (advisory_ig):** culturally adapted for South-East Nigeria

Advisories are 2–3 sentences, written in plain language for a general audience. They are culturally adapted translations, not literal word-for-word translations.

## Validation

Every AI response is validated against the `RiskAssessmentResponse` Pydantic schema before being written to the database:
- `risk_level` must be one of: LOW, MODERATE, HIGH, CRITICAL
- All scores must be floats between 0 and 100
- All 4 advisory fields must be non-empty strings
- Invalid responses raise a `ValueError` and are not stored

## Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `risk_level` | enum | LOW, MODERATE, HIGH, CRITICAL |
| `overall_score` | float | 0–100 weighted composite |
| `climate_score` | float | 0–100 climate sub-score |
| `health_score` | float | 0–100 health sub-score |
| `vulnerability_score` | float | 0–100 vulnerability sub-score |
| `advisory_en` | text | English public advisory |
| `advisory_ha` | text | Hausa public advisory |
| `advisory_yo` | text | Yoruba public advisory |
| `advisory_ig` | text | Igbo public advisory |
| `key_drivers` | list | Top 3 risk drivers |
| `recommended_actions` | list | 3–5 actionable recommendations |
| `raw_response` | JSON | Full AI response stored for audit |
