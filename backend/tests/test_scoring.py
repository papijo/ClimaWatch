"""Unit tests for vulnerability scoring formulas."""

import pytest

from app.modules.vulnerability_scoring.lga_scorer import (
    compute_health_access_score,
    score_lga,
)
from app.modules.vulnerability_scoring.facility_scorer import score_facility


class TestLGAScoring:
    def test_weights_sum_to_100(self):
        score = score_lga(100.0, 100.0, 100.0)
        assert score == 100.0

    def test_all_zeros(self):
        assert score_lga(0.0, 0.0, 0.0) == 0.0

    def test_weighted_average(self):
        result = score_lga(50.0, 50.0, 50.0)
        assert result == 50.0

    def test_population_heavy(self):
        result = score_lga(100.0, 0.0, 0.0)
        assert result == 35.0

    def test_health_heavy(self):
        result = score_lga(0.0, 100.0, 0.0)
        assert result == 40.0

    def test_climate_heavy(self):
        result = score_lga(0.0, 0.0, 100.0)
        assert result == 25.0

    def test_clamped_to_100(self):
        result = score_lga(120.0, 120.0, 120.0)
        assert result == 100.0

    def test_clamped_to_0(self):
        result = score_lga(-10.0, -10.0, -10.0)
        assert result == 0.0

    def test_health_access_no_facilities(self):
        assert compute_health_access_score(0) == 100.0

    def test_health_access_many_facilities(self):
        assert compute_health_access_score(20) == 10.0

    def test_health_access_moderate(self):
        score = compute_health_access_score(10)
        assert 40.0 <= score <= 60.0


class TestFacilityScoring:
    def test_weights_sum_to_100(self):
        score = score_facility(100.0, 100.0, 100.0, 100.0)
        assert score == 100.0

    def test_all_zeros(self):
        assert score_facility(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_weighted_average(self):
        result = score_facility(50.0, 50.0, 50.0, 50.0)
        assert result == 50.0

    def test_flood_heavy(self):
        result = score_facility(100.0, 0.0, 0.0, 0.0)
        assert result == 30.0

    def test_heat_heavy(self):
        result = score_facility(0.0, 100.0, 0.0, 0.0)
        assert result == 25.0

    def test_disease_heavy(self):
        result = score_facility(0.0, 0.0, 100.0, 0.0)
        assert result == 25.0

    def test_infra_heavy(self):
        result = score_facility(0.0, 0.0, 0.0, 100.0)
        assert result == 20.0

    def test_clamped_to_100(self):
        result = score_facility(120.0, 120.0, 120.0, 120.0)
        assert result == 100.0

    def test_clamped_to_0(self):
        result = score_facility(-10.0, -10.0, -10.0, -10.0)
        assert result == 0.0

    def test_boundary_mixed(self):
        result = score_facility(0.0, 100.0, 100.0, 0.0)
        assert result == 50.0
