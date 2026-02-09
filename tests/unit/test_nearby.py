"""Tests for nearby commands."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.nearby import VenueType, app
from fcp_cli.services import FcpConnectionError, FcpServerError, Venue

pytestmark = [pytest.mark.unit, pytest.mark.cli]


def _mock_run_async(coro):
    """Execute coroutine synchronously for testing."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestFindVenuesCommand:
    """Test nearby venues command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def full_venues(self):
        """Full venue data with all fields."""
        return [
            Venue(
                name="The Italian Kitchen",
                venue_type="restaurant",
                distance="250m",
                rating=4.5,
                address="123 Main St, San Francisco, CA",
                latitude=37.7749,
                longitude=-122.4194,
            ),
            Venue(
                name="Corner Cafe",
                venue_type="cafe",
                distance="450m",
                rating=4.2,
                address="456 Oak Ave, San Francisco, CA",
                latitude=37.7750,
                longitude=-122.4195,
            ),
            Venue(
                name="Fresh Market",
                venue_type="grocery",
                distance="1.2km",
                rating=4.7,
                address="789 Pine St, San Francisco, CA",
                latitude=37.7751,
                longitude=-122.4196,
            ),
        ]

    @pytest.fixture
    def minimal_venues(self):
        """Minimal venue data."""
        return [
            Venue(
                name="Simple Cafe",
                venue_type=None,
                distance=None,
                rating=None,
                address=None,
            ),
        ]

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_with_coordinates(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test finding venues with lat/lon coordinates."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 0
        assert "The Italian Kitchen" in result.stdout
        assert "Corner Cafe" in result.stdout
        assert "Fresh Market" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_with_location(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test finding venues with location string."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, "San Francisco, CA"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--location", "San Francisco, CA"],
        )

        assert result.exit_code == 0
        assert "San Francisco, CA" in result.stdout
        assert "The Italian Kitchen" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_with_type_filter(self, mock_client_class, mock_run_async, runner):
        """Test filtering venues by type."""
        restaurants = [
            Venue(
                name="Pizza Place",
                venue_type="restaurant",
                distance="300m",
                rating=4.3,
            ),
        ]
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(restaurants, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194", "--type", "restaurant"],
        )

        assert result.exit_code == 0
        assert "Pizza Place" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_with_radius(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test specifying custom search radius."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194", "--radius", "5000"],
        )

        assert result.exit_code == 0
        assert "The Italian Kitchen" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_all_options(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test with all options specified."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--lat",
                "37.7749",
                "--lon",
                "-122.4194",
                "--type",
                "cafe",
                "--radius",
                "1000",
            ],
        )

        assert result.exit_code == 0

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_displays_table(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test that venues are displayed in a table format."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 0
        # Table columns
        assert "Name" in result.stdout
        assert "Type" in result.stdout
        assert "Distance" in result.stdout
        assert "Rating" in result.stdout
        assert "Address" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_displays_ratings(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test that ratings are displayed correctly."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 0
        assert "4.5" in result.stdout
        assert "4.2" in result.stdout
        assert "4.7" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_no_rating(self, mock_client_class, mock_run_async, runner):
        """Test venue with no rating displays dash."""
        venues = [
            Venue(name="New Place", rating=None),
        ]
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 0
        assert "New Place" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_minimal_data(self, mock_client_class, mock_run_async, runner, minimal_venues):
        """Test venues with minimal data."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(minimal_venues, None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 0
        assert "Simple Cafe" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_no_results(self, mock_client_class, mock_run_async, runner):
        """Test when no venues are found."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=([], None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 0
        assert "No venues found" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_resolved_location_display(self, mock_client_class, mock_run_async, runner, full_venues):
        """Test resolved location is displayed in title."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(return_value=(full_venues, "San Francisco, CA"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--location", "San Francisco"],
        )

        assert result.exit_code == 0
        assert "San Francisco, CA" in result.stdout

    def test_venues_no_location_provided(self, runner):
        """Test error when neither coordinates nor location provided."""
        result = runner.invoke(app, [])

        assert result.exit_code == 1
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_venues_only_latitude_provided(self, runner):
        """Test error when only latitude is provided."""
        result = runner.invoke(app, ["--lat", "37.7749"])

        assert result.exit_code == 1
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_venues_only_longitude_provided(self, runner):
        """Test error when only longitude is provided."""
        result = runner.invoke(app, ["--lon", "-122.4194"])

        assert result.exit_code == 1
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_venues_invalid_latitude(self, runner):
        """Test error with invalid latitude value."""
        result = runner.invoke(
            app,
            ["--lat", "100", "--lon", "-122.4194"],
        )

        assert result.exit_code != 0

    def test_venues_invalid_longitude(self, runner):
        """Test error with invalid longitude value."""
        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "200"],
        )

        assert result.exit_code != 0

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test venues with connection error."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(side_effect=FcpConnectionError("Connection failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--lat", "37.7749", "--lon", "-122.4194"],
        )

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_venues_server_error(self, mock_client_class, mock_run_async, runner):
        """Test venues with server error."""
        mock_client = MagicMock()
        mock_client.find_nearby_venues = AsyncMock(side_effect=FcpServerError("Server error"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["--location", "San Francisco"],
        )

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "venue_type",
    [
        VenueType.RESTAURANT,
        VenueType.CAFE,
        VenueType.GROCERY,
        VenueType.BAKERY,
        VenueType.FOOD_TRUCK,
    ],
)
@patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
@patch("fcp_cli.commands.nearby.FcpClient")
def test_venues_all_types(mock_client_class, mock_run_async, venue_type):
    """Test finding venues of all supported types."""
    venues = [
        Venue(
            name=f"Test {venue_type.value}",
            venue_type=venue_type.value,
            distance="500m",
            rating=4.0,
        ),
    ]
    mock_client = MagicMock()
    mock_client.find_nearby_venues = AsyncMock(return_value=(venues, None))
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["--lat", "37.7749", "--lon", "-122.4194", "--type", venue_type.value],
    )

    assert result.exit_code == 0
    assert venue_type.value in result.stdout


@pytest.mark.parametrize(
    "distance,expected_display",
    [
        ("250m", "250m"),
        ("1.2km", "1.2km"),
        ("500m", "500m"),
        (None, "-"),
    ],
)
@patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
@patch("fcp_cli.commands.nearby.FcpClient")
def test_venues_distance_display(mock_client_class, mock_run_async, distance, expected_display):
    """Test distance display formatting."""
    venues = [
        Venue(name="Test Place", distance=distance),
    ]
    mock_client = MagicMock()
    mock_client.find_nearby_venues = AsyncMock(return_value=(venues, None))
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["--lat", "37.7749", "--lon", "-122.4194"],
    )

    assert result.exit_code == 0
    assert expected_display in result.stdout


@pytest.mark.parametrize(
    "lat,lon,radius",
    [
        (37.7749, -122.4194, 1000),
        (40.7128, -74.0060, 2000),
        (51.5074, -0.1278, 5000),
        (-33.8688, 151.2093, 3000),
    ],
)
@patch("fcp_cli.commands.nearby.run_async", side_effect=_mock_run_async)
@patch("fcp_cli.commands.nearby.FcpClient")
def test_venues_various_locations(mock_client_class, mock_run_async, lat, lon, radius):
    """Test finding venues at various locations."""
    venues = [Venue(name="Test Venue", distance="500m")]
    mock_client = MagicMock()
    mock_client.find_nearby_venues = AsyncMock(return_value=(venues, None))
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["--lat", str(lat), "--lon", str(lon), "--radius", str(radius)],
    )

    assert result.exit_code == 0


class TestNearbySearchValidation:
    """Test nearby search input validation."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_nearby_mismatched_coords(self, runner):
        """Test nearby with mismatched lat/lon."""
        # To hit line 73-74, we need to trick the has_coords check
        # This is actually a code path that's hard to reach via CLI
        # It would require internal API usage where one coord is explicitly None
        # For CLI coverage, these lines are defensive programming
        # The actual CLI validation catches this earlier
        result = runner.invoke(app, ["--lat", "40.7128"])

        assert result.exit_code == 1
        # The earlier validation catches incomplete coords
        assert (
            "Please provide either --lat/--lon or --location" in result.stdout
            or "Both --lat and --lon" in result.stdout
        )
