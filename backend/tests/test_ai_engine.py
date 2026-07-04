"""Unit tests for the AI engine — schema validation, JSON extraction, prompt building."""

import asyncio
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

# Stub openai so the module can be imported even without the installed package.
# The real openai client is patched out in every test that touches it.
if "openai" not in sys.modules:
    _openai_stub = MagicMock()
    sys.modules["openai"] = _openai_stub

from app.modules.ai_engine.client import assess_state, extract_json  # noqa: E402
from app.modules.ai_engine.prompts import SYSTEM_PROMPT, build_state_prompt  # noqa: E402
from app.modules.ai_engine.schemas import RiskAssessmentResponse  # noqa: E402

VALID_PAYLOAD = {
    "risk_level": "MODERATE",
    "overall_score": 45.0,
    "climate_score": 50.0,
    "health_score": 40.0,
    "vulnerability_score": 35.0,
    "advisory_en": "Exercise caution in exposed areas.",
    "advisory_ha": "Ku yi hankali a wuraren budewa.",
    "advisory_yo": "Ṣọra ní àwọn àgbègbè tí a fihàn.",
    "advisory_ig": "Dị njikere n'ebe ọnọdụ dị.",
    "key_drivers": ["heat", "rainfall"],
    "recommended_actions": ["stay hydrated", "avoid flooding"],
}


class TestExtractJson:
    def test_plain_json_string(self):
        raw = json.dumps(VALID_PAYLOAD)
        result = extract_json(raw)
        assert result["risk_level"] == "MODERATE"
        assert result["overall_score"] == 45.0

    def test_strips_json_code_fence(self):
        raw = f"```json\n{json.dumps(VALID_PAYLOAD)}\n```"
        result = extract_json(raw)
        assert result["risk_level"] == "MODERATE"

    def test_strips_bare_code_fence(self):
        raw = f"```\n{json.dumps(VALID_PAYLOAD)}\n```"
        result = extract_json(raw)
        assert result["overall_score"] == 45.0

    def test_whitespace_around_json(self):
        raw = f"\n  {json.dumps(VALID_PAYLOAD)}\n  "
        result = extract_json(raw)
        assert result["climate_score"] == 50.0

    def test_invalid_json_raises_json_decode_error(self):
        with pytest.raises(json.JSONDecodeError):
            extract_json("this is not JSON")

    def test_empty_string_raises(self):
        with pytest.raises(json.JSONDecodeError):
            extract_json("")


class TestRiskAssessmentResponseSchema:
    def test_valid_payload_validates(self):
        model = RiskAssessmentResponse.model_validate(VALID_PAYLOAD)
        assert model.risk_level == "MODERATE"
        assert model.overall_score == 45.0

    def test_all_four_risk_levels_accepted(self):
        for level in ("LOW", "MODERATE", "HIGH", "CRITICAL"):
            m = RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "risk_level": level})
            assert m.risk_level == level

    def test_invalid_risk_level_rejected(self):
        with pytest.raises(ValidationError):
            RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "risk_level": "EXTREME"})

    def test_risk_level_lowercase_rejected(self):
        with pytest.raises(ValidationError):
            RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "risk_level": "moderate"})

    def test_score_above_100_rejected(self):
        with pytest.raises(ValidationError):
            RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "overall_score": 100.1})

    def test_score_below_0_rejected(self):
        with pytest.raises(ValidationError):
            RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "climate_score": -0.1})

    def test_score_at_boundary_0_accepted(self):
        m = RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "overall_score": 0.0})
        assert m.overall_score == 0.0

    def test_score_at_boundary_100_accepted(self):
        m = RiskAssessmentResponse.model_validate({**VALID_PAYLOAD, "overall_score": 100.0})
        assert m.overall_score == 100.0

    def test_key_drivers_defaults_to_empty_list(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "key_drivers"}
        m = RiskAssessmentResponse.model_validate(payload)
        assert m.key_drivers == []

    def test_recommended_actions_defaults_to_empty_list(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "recommended_actions"}
        m = RiskAssessmentResponse.model_validate(payload)
        assert m.recommended_actions == []

    def test_all_advisory_fields_required(self):
        for field in ("advisory_en", "advisory_ha", "advisory_yo", "advisory_ig"):
            payload = {k: v for k, v in VALID_PAYLOAD.items() if k != field}
            with pytest.raises(ValidationError):
                RiskAssessmentResponse.model_validate(payload)


class TestBuildStatePrompt:
    def test_contains_state_name(self):
        prompt = build_state_prompt("Lagos", {}, [], [], {})
        assert "Lagos" in prompt

    def test_climate_data_serialised_into_prompt(self):
        prompt = build_state_prompt("Kano", {"temperature_max": 38.5}, [], [], {})
        assert "temperature_max" in prompt
        assert "38.5" in prompt

    def test_no_history_includes_first_assessment_note(self):
        prompt = build_state_prompt("Abuja", {}, [], [], {})
        assert "first assessment" in prompt.lower()

    def test_recent_history_included(self):
        history = [{"risk_level": "HIGH", "overall_score": 70.0}]
        prompt = build_state_prompt("Lagos", {}, history, [], {})
        assert "Risk History" in prompt
        assert "HIGH" in prompt

    def test_disease_alerts_included(self):
        alerts = [{"disease_name": "Cholera", "alert_level": "warning"}]
        prompt = build_state_prompt("Lagos", {}, [], alerts, {})
        assert "Cholera" in prompt

    def test_no_disease_alerts_message_shown(self):
        prompt = build_state_prompt("Lagos", {}, [], [], {})
        assert "No active disease alerts" in prompt

    def test_facility_summary_included(self):
        summary = {"total_facilities": 12, "avg_risk_score": 55.0}
        prompt = build_state_prompt("Lagos", {}, [], [], summary)
        assert "total_facilities" in prompt

    def test_prompt_ends_with_json_instruction(self):
        prompt = build_state_prompt("Lagos", {}, [], [], {})
        assert "JSON" in prompt

    def test_system_prompt_defines_output_format(self):
        assert "risk_level" in SYSTEM_PROMPT
        assert "overall_score" in SYSTEM_PROMPT
        assert "advisory_en" in SYSTEM_PROMPT


class TestAssessState:
    def test_returns_validated_model_on_valid_response(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(VALID_PAYLOAD)

        with patch(
            "app.modules.ai_engine.client._client.chat.completions.create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = asyncio.run(assess_state("Lagos", {}, [], [], {}))

        assert isinstance(result, RiskAssessmentResponse)
        assert result.risk_level == "MODERATE"
        assert result.overall_score == 45.0

    def test_invalid_json_from_api_raises(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "not valid json"

        with patch(
            "app.modules.ai_engine.client._client.chat.completions.create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(json.JSONDecodeError):
                asyncio.run(assess_state("Lagos", {}, [], [], {}))

    def test_invalid_schema_raises_validation_error(self):
        bad_payload = {**VALID_PAYLOAD, "risk_level": "NOT_VALID"}
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(bad_payload)

        with patch(
            "app.modules.ai_engine.client._client.chat.completions.create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ValidationError):
                asyncio.run(assess_state("Lagos", {}, [], [], {}))

    def test_code_fenced_json_from_api_parses_correctly(self):
        fenced = f"```json\n{json.dumps(VALID_PAYLOAD)}\n```"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = fenced

        with patch(
            "app.modules.ai_engine.client._client.chat.completions.create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = asyncio.run(assess_state("Lagos", {}, [], [], {}))

        assert result.risk_level == "MODERATE"
