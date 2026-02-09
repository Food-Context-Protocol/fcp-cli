"""Example tests demonstrating Phase 3 tools: hypothesis property-based testing.

These tests showcase how to use hypothesis for property-based testing.
They serve as examples for finding edge cases automatically.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from fcp_cli.utils import validate_latitude, validate_limit, validate_longitude

pytestmark = pytest.mark.unit


class TestHypothesisExamples:
    """Example tests using hypothesis for property-based testing."""

    @given(st.floats(min_value=-90.0, max_value=90.0))
    @pytest.mark.property
    def test_validate_latitude_accepts_valid_range(self, lat: float):
        """Property: All floats in [-90, 90] should be valid latitudes."""
        # Should not raise an exception
        validate_latitude(lat)

    @given(st.floats().filter(lambda x: x < -90 or x > 90))
    @pytest.mark.property
    def test_validate_latitude_rejects_invalid_range(self, lat: float):
        """Property: All floats outside [-90, 90] should be rejected."""
        with pytest.raises(ValueError):
            validate_latitude(lat)

    @given(st.floats(min_value=-180.0, max_value=180.0))
    @pytest.mark.property
    def test_validate_longitude_accepts_valid_range(self, lon: float):
        """Property: All floats in [-180, 180] should be valid longitudes."""
        # Should not raise an exception
        validate_longitude(lon)

    @given(st.floats().filter(lambda x: x < -180 or x > 180))
    @pytest.mark.property
    def test_validate_longitude_rejects_invalid_range(self, lon: float):
        """Property: All floats outside [-180, 180] should be rejected."""
        with pytest.raises(ValueError):
            validate_longitude(lon)

    @given(st.integers(min_value=1, max_value=1000))
    @pytest.mark.property
    def test_validate_limit_accepts_valid_range(self, limit: int):
        """Property: All integers in [1, 1000] should be valid limits."""
        # Should return the same value
        result = validate_limit(limit)
        assert result == limit

    @given(st.integers(max_value=0))
    @pytest.mark.property
    def test_validate_limit_rejects_too_small(self, limit: int):
        """Property: All integers less than 1 should be rejected."""
        from typer import BadParameter

        with pytest.raises(BadParameter):
            validate_limit(limit)

    @given(st.integers(min_value=1001))
    @pytest.mark.property
    def test_validate_limit_rejects_too_large(self, limit: int):
        """Property: All integers greater than 1000 should be rejected."""
        from typer import BadParameter

        with pytest.raises(BadParameter):
            validate_limit(limit)

    @given(st.text(min_size=1, max_size=200))
    @pytest.mark.property
    def test_string_properties_example(self, text: str):
        """Property: String operations should maintain certain invariants."""
        # Example properties that should hold for any string
        assert len(text) >= 1
        assert len(text) <= 200
        assert text == text  # Identity
        # Reversing twice returns original
        assert text[::-1][::-1] == text

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
    @pytest.mark.property
    def test_list_properties_example(self, items: list[str]):
        """Property: List operations should maintain certain invariants."""
        # Example properties for lists
        assert len(items) >= 0
        assert len(items) <= 10

        # Filtering and length relationships
        filtered = [item for item in items if len(item) > 5]
        assert len(filtered) <= len(items)

        # Reversing twice returns original
        if items:
            assert list(reversed(list(reversed(items)))) == items


class TestAdvancedHypothesisPatterns:
    """Advanced hypothesis patterns for complex scenarios."""

    @given(
        st.tuples(
            st.floats(min_value=-90.0, max_value=90.0),  # latitude
            st.floats(min_value=-180.0, max_value=180.0),  # longitude
        )
    )
    @pytest.mark.property
    def test_coordinate_pair_properties(self, coords: tuple[float, float]):
        """Property: Valid coordinate pairs should validate correctly."""
        lat, lon = coords

        # Both validations should succeed
        validate_latitude(lat)
        validate_longitude(lon)

        # Verify ranges
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180

    @given(st.integers(min_value=1, max_value=1000), st.integers(min_value=1, max_value=1000))
    @pytest.mark.property
    def test_limit_comparison_properties(self, limit1: int, limit2: int):
        """Property: Limit validation should be order-independent."""
        # Both limits should be valid
        result1 = validate_limit(limit1)
        result2 = validate_limit(limit2)

        # Identity property
        assert result1 == limit1
        assert result2 == limit2

        # Comparison property
        if limit1 < limit2:
            assert result1 < result2
        elif limit1 > limit2:
            assert result1 > result2
        else:
            assert result1 == result2


class TestValidatePositiveIntProperties:
    """Property-based tests for validate_positive_int function."""

    @given(st.integers(min_value=1, max_value=10000))
    @pytest.mark.property
    def test_validate_positive_int_identity(self, value: int):
        """Property: Valid positive integers should return unchanged."""
        from fcp_cli.utils import validate_positive_int

        result = validate_positive_int(value, min_val=1)
        assert result == value

    @given(st.integers(min_value=10, max_value=100), st.integers(min_value=1, max_value=9))
    @pytest.mark.property
    def test_validate_positive_int_with_bounds(self, max_val: int, min_val: int):
        """Property: Values between min and max should be valid."""
        from fcp_cli.utils import validate_positive_int

        # Pick a value in the middle
        value = (min_val + max_val) // 2
        result = validate_positive_int(value, min_val=min_val, max_val=max_val)
        assert result == value
        assert min_val <= result <= max_val

    @given(st.integers(max_value=0))
    @pytest.mark.property
    def test_validate_positive_int_rejects_non_positive(self, value: int):
        """Property: Non-positive integers should be rejected."""
        from fcp_cli.utils import validate_positive_int

        with pytest.raises(ValueError, match="must be at least"):
            validate_positive_int(value, min_val=1)


class TestDateParsingProperties:
    """Property-based tests for date parsing functions."""

    @given(st.dates(min_value=pytest.importorskip("datetime").date(2000, 1, 1)))
    @pytest.mark.property
    def test_parse_date_string_iso_format(self, date):
        """Property: ISO format dates should round-trip correctly."""

        from fcp_cli.utils import parse_date_string

        # Format as ISO date string
        date_str = date.strftime("%Y-%m-%d")

        # Parse it back
        parsed = parse_date_string(date_str)

        # Should get the same date at midnight UTC
        assert parsed.year == date.year
        assert parsed.month == date.month
        assert parsed.day == date.day
        assert parsed.hour == 0
        assert parsed.minute == 0
        assert parsed.second == 0
        assert parsed.tzinfo == UTC

    @given(st.integers(min_value=0, max_value=365))
    @pytest.mark.property
    def test_parse_date_string_relative_days(self, days_ago: int):
        """Property: Relative day strings should parse correctly."""
        from datetime import timedelta

        from fcp_cli.utils import parse_date_string

        # Parse relative date
        date_str = f"-{days_ago}"
        parsed = parse_date_string(date_str)

        # Should be days_ago before today at midnight
        expected = (datetime.now(UTC) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Allow 1 second tolerance for test execution time
        diff = abs((parsed - expected).total_seconds())
        assert diff < 1


class TestRelativeTimeProperties:
    """Property-based tests for get_relative_time function."""

    @given(st.integers(min_value=1, max_value=59))
    @pytest.mark.property
    def test_relative_time_minutes(self, seconds: int):
        """Property: Times less than 60 seconds ago should be 'just now'."""
        from datetime import timedelta

        from fcp_cli.utils import get_relative_time

        # Create a time N seconds ago
        dt = datetime.now(UTC) - timedelta(seconds=seconds)
        result = get_relative_time(dt)

        assert result == "just now"

    @given(st.integers(min_value=60, max_value=3599))
    @pytest.mark.property
    def test_relative_time_minutes_format(self, seconds: int):
        """Property: Times less than 60 minutes should show minute count."""
        from datetime import timedelta

        from fcp_cli.utils import get_relative_time

        # Create a time N seconds ago
        dt = datetime.now(UTC) - timedelta(seconds=seconds)
        result = get_relative_time(dt)

        # Should be in minutes
        expected_minutes = seconds // 60
        assert f"{expected_minutes} min" in result

    @given(st.integers(min_value=3600, max_value=86399))
    @pytest.mark.property
    def test_relative_time_hours_format(self, seconds: int):
        """Property: Times less than 24 hours should show hour count."""
        from datetime import timedelta

        from fcp_cli.utils import get_relative_time

        # Create a time N seconds ago
        dt = datetime.now(UTC) - timedelta(seconds=seconds)
        result = get_relative_time(dt)

        # Should be in hours
        expected_hours = seconds // 3600
        assert f"{expected_hours} hour" in result


class TestResolutionValidationProperties:
    """Property-based tests for resolution validation."""

    @given(st.sampled_from(["low", "medium", "high", "LOW", "MEDIUM", "HIGH", " low ", "  HIGH  "]))
    @pytest.mark.property
    def test_validate_resolution_normalizes(self, resolution: str):
        """Property: Valid resolution strings should normalize correctly."""
        from fcp_cli.utils import validate_resolution

        result = validate_resolution(resolution)

        # Should be lowercase and trimmed
        assert result == result.lower().strip()
        assert result in {"low", "medium", "high"}

    @given(st.text(min_size=1, max_size=20).filter(lambda x: x.lower().strip() not in {"low", "medium", "high"}))
    @pytest.mark.property
    def test_validate_resolution_rejects_invalid(self, resolution: str):
        """Property: Invalid resolution strings should be rejected."""
        from fcp_cli.utils import validate_resolution

        with pytest.raises(ValueError, match="Invalid resolution"):
            validate_resolution(resolution)
