"""Tests for nearby command validation logic."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.nearby import app

pytestmark = pytest.mark.unit


class TestNearbyCoordinateValidation:
    """Test coordinate validation edge cases."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_latitude_without_longitude(self, runner):
        """Test error when only latitude provided."""
        result = runner.invoke(app, ["--lat", "37.7749"])

        assert result.exit_code == 1
        # Via CLI, this gets caught by the first validation check
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_longitude_without_latitude(self, runner):
        """Test error when only longitude provided."""
        result = runner.invoke(app, ["--lon", "-122.4194"])

        assert result.exit_code == 1
        # Via CLI, this gets caught by the first validation check
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_neither_coords_nor_location(self, runner):
        """Test error when neither coordinates nor location provided."""
        result = runner.invoke(app, [])

        assert result.exit_code == 1
        assert "provide either --lat/--lon or --location" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async")
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_valid_coordinates_accepted(self, mock_client_class, mock_run_async, runner):
        """Test that valid coordinate pair is accepted."""

        mock_client = MagicMock()
        mock_client.find_nearby_venues = MagicMock(return_value=([], None))
        mock_client_class.return_value = mock_client

        def _mock_run(coro):
            return [], None

        mock_run_async.side_effect = _mock_run

        result = runner.invoke(app, ["--lat", "37.7749", "--lon", "-122.4194"])

        assert result.exit_code == 0
        # Should not show error messages
        assert "Error:" not in result.stdout

    @patch("fcp_cli.commands.nearby.run_async")
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_valid_location_accepted(self, mock_client_class, mock_run_async, runner):
        """Test that valid location string is accepted."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = MagicMock(return_value=([], "San Francisco, CA"))
        mock_client_class.return_value = mock_client

        def _mock_run(coro):
            return [], "San Francisco, CA"

        mock_run_async.side_effect = _mock_run

        result = runner.invoke(app, ["--location", "San Francisco"])

        assert result.exit_code == 0
        # Should not show error messages
        assert "Error:" not in result.stdout
