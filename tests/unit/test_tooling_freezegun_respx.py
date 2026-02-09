"""Example tests demonstrating Phase 2 tools: freezegun and respx.

These tests showcase how to use the new testing tools added in Phase 2.
They serve as examples for future test development.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest
import respx
from freezegun import freeze_time

pytestmark = pytest.mark.unit


class TestFreezegunExamples:
    """Example tests using freezegun for time mocking."""

    @freeze_time("2026-02-08 12:00:00")
    def test_frozen_time_example(self):
        """Example: Test with frozen time."""
        now = datetime.now(UTC)
        assert now.year == 2026
        assert now.month == 2
        assert now.day == 8
        assert now.hour == 12

    @freeze_time("2026-01-01 00:00:00")
    def test_date_calculation_deterministic(self):
        """Example: Deterministic date calculations."""
        from datetime import timedelta

        today = datetime.now(UTC)
        tomorrow = today + timedelta(days=1)

        assert today.day == 1
        assert tomorrow.day == 2
        assert tomorrow.month == 1


class TestRespxExamples:
    """Example tests using respx for HTTP mocking."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_respx_basic_mock(self):
        """Example: Basic HTTP mocking with respx."""
        # Mock a simple GET request
        respx.get("https://api.example.com/test").mock(return_value=httpx.Response(200, json={"status": "ok"}))

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    @respx.mock
    @pytest.mark.asyncio
    async def test_respx_retry_scenario(self):
        """Example: Test retry logic with respx."""
        # First call fails, second succeeds
        route = respx.get("https://api.example.com/retry").mock(
            side_effect=[
                httpx.Response(500, json={"error": "Internal Server Error"}),
                httpx.Response(200, json={"status": "success"}),
            ]
        )

        async with httpx.AsyncClient() as client:
            # First call - should fail
            response1 = await client.get("https://api.example.com/retry")
            assert response1.status_code == 500

            # Second call - should succeed
            response2 = await client.get("https://api.example.com/retry")
            assert response2.status_code == 200
            assert response2.json() == {"status": "success"}

        # Verify the endpoint was called twice
        assert route.call_count == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_respx_post_with_json(self):
        """Example: Mock POST request with JSON validation."""
        # Mock POST endpoint and capture the request
        route = respx.post("https://api.example.com/create").mock(
            return_value=httpx.Response(201, json={"id": "123", "created": True})
        )

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.example.com/create", json={"name": "Test Item", "value": 42})

            assert response.status_code == 201
            assert response.json()["created"] is True

        # Verify the request was made
        assert route.called


class TestCombinedToolsExample:
    """Example combining freezegun and respx."""

    @freeze_time("2026-02-08 12:00:00")
    @respx.mock
    @pytest.mark.asyncio
    async def test_time_sensitive_api_call(self):
        """Example: Test time-sensitive API call with both tools."""
        # Mock API that returns time-based data
        respx.get("https://api.example.com/timestamp").mock(
            return_value=httpx.Response(200, json={"server_time": "2026-02-08T12:00:00Z", "timezone": "UTC"})
        )

        # Time is frozen at 2026-02-08 12:00:00
        now = datetime.now(UTC)

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/timestamp")
            data = response.json()

            # Both local time and server time should match
            assert data["server_time"] == "2026-02-08T12:00:00Z"
            assert now.isoformat() == "2026-02-08T12:00:00+00:00"
