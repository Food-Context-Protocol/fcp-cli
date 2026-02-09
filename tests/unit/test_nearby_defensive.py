"""Direct tests for nearby command defensive validation."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import typer

from fcp_cli.commands.nearby import find_venues

pytestmark = pytest.mark.unit


class TestNearbyDefensiveValidation:
    """Test defensive XOR validation in nearby command."""

    @pytest.fixture
    def mock_console(self):
        """Mock console."""
        with patch("fcp_cli.commands.nearby.console") as mock:
            yield mock

    def test_latitude_without_longitude_defensive_check(self, mock_console):
        """Test the defensive XOR check when latitude is provided without longitude."""
        # To hit the XOR check, we need to provide location (to pass first check)
        # and then have mismatched lat/lon (to hit the XOR check)
        with pytest.raises(typer.Exit) as exc_info:
            find_venues(
                latitude=37.7749,  # Latitude provided
                longitude=None,  # Longitude not provided
                location="San Francisco",  # Location provided to pass first check
                venue_type=None,
                radius=1000,
            )

        assert exc_info.value.exit_code == 1
        # Verify the defensive error message was shown
        mock_console.print.assert_called()
        call_args = str(mock_console.print.call_args)
        assert "Both --lat and --lon must be provided together" in call_args

    def test_longitude_without_latitude_defensive_check(self, mock_console):
        """Test the defensive XOR check when longitude is provided without latitude."""
        # Same pattern: provide location to pass first check, then mismatched coords
        with pytest.raises(typer.Exit) as exc_info:
            find_venues(
                latitude=None,  # Latitude not provided
                longitude=-122.4194,  # Longitude provided
                location="San Francisco",  # Location provided to pass first check
                venue_type=None,
                radius=1000,
            )

        assert exc_info.value.exit_code == 1
        # Verify the defensive error message was shown
        mock_console.print.assert_called()
        call_args = str(mock_console.print.call_args)
        assert "Both --lat and --lon must be provided together" in call_args

    @patch("fcp_cli.commands.nearby.run_async")
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_both_coordinates_provided(self, mock_client_class, mock_run_async, mock_console):
        """Test that both coordinates together pass defensive validation."""
        mock_run_async.return_value = ([], None)

        # This should NOT raise an error
        try:
            find_venues(
                latitude=37.7749,
                longitude=-122.4194,
                location=None,
                venue_type=None,
                radius=1000,
            )
        except typer.Exit:
            pytest.fail("Should not raise Exit when both coords provided")

        # Should get past validation and call the client
        assert mock_run_async.called
