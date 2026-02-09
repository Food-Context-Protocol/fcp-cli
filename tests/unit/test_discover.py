"""Tests for discover commands.

Coverage Note:
- Lines 86-87 in discover.py are defensive programming code that is currently
  unreachable due to the validation logic on line 81. The XOR check on line 85
  can never be True because if only one coordinate is provided, the has_coords
  check on line 78 will be False, causing line 81 to trigger first.
- Current coverage: 99% (158/160 lines)
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.discover import (
    _validate_optional_latitude,
    _validate_optional_longitude,
    app,
)
from fcp_cli.services import FcpConnectionError, FcpServerError

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestValidationHelpers:
    """Test latitude and longitude validation helpers."""

    def test_validate_optional_latitude_none(self):
        """Test latitude validation with None."""
        assert _validate_optional_latitude(None) is None

    def test_validate_optional_latitude_valid(self):
        """Test latitude validation with valid value."""
        assert _validate_optional_latitude(40.7128) == 40.7128
        assert _validate_optional_latitude(0.0) == 0.0
        assert _validate_optional_latitude(-90.0) == -90.0
        assert _validate_optional_latitude(90.0) == 90.0

    def test_validate_optional_latitude_invalid(self):
        """Test latitude validation with invalid value."""
        with pytest.raises(Exception):
            _validate_optional_latitude(91.0)
        with pytest.raises(Exception):
            _validate_optional_latitude(-91.0)

    def test_validate_optional_longitude_none(self):
        """Test longitude validation with None."""
        assert _validate_optional_longitude(None) is None

    def test_validate_optional_longitude_valid(self):
        """Test longitude validation with valid value."""
        assert _validate_optional_longitude(-74.0060) == -74.0060
        assert _validate_optional_longitude(0.0) == 0.0
        assert _validate_optional_longitude(-180.0) == -180.0
        assert _validate_optional_longitude(180.0) == 180.0

    def test_validate_optional_longitude_invalid(self):
        """Test longitude validation with invalid value."""
        with pytest.raises(Exception):
            _validate_optional_longitude(181.0)
        with pytest.raises(Exception):
            _validate_optional_longitude(-181.0)


class TestDiscoverFoodCommand:
    """Test discover food command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_with_insight_and_discoveries(self, mock_run_async, mock_client_class, runner):
        """Test discover food with insight and discoveries."""
        mock_run_async.return_value = {
            "insight": "Try Mediterranean cuisine this week!",
            "discoveries": [
                {
                    "name": "Shakshuka",
                    "description": "Middle Eastern egg dish",
                    "category": "Breakfast",
                },
                {
                    "name": "Falafel",
                    "description": "Crispy chickpea fritters",
                    "category": "Appetizer",
                },
            ],
        }

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 0
        assert "Mediterranean cuisine" in result.stdout
        assert "Shakshuka" in result.stdout
        assert "Falafel" in result.stdout
        assert "Breakfast" in result.stdout
        mock_run_async.assert_called_once()

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_with_items_key(self, mock_run_async, mock_client_class, runner):
        """Test discover food with 'items' key instead of 'discoveries'."""
        mock_run_async.return_value = {
            "items": [
                {
                    "title": "Pad Thai",
                    "description": "Thai stir-fried noodles",
                },
            ],
        }

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 0
        assert "Pad Thai" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_insight_only(self, mock_run_async, mock_client_class, runner):
        """Test discover food with only insight."""
        mock_run_async.return_value = {
            "insight": "Explore seasonal vegetables!",
            "discoveries": [],
        }

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 0
        assert "seasonal vegetables" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_discoveries_without_category(self, mock_run_async, mock_client_class, runner):
        """Test discover food with discoveries lacking category."""
        mock_run_async.return_value = {
            "discoveries": [
                {
                    "name": "Sushi",
                    "description": "Japanese delicacy",
                },
            ],
        }

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 0
        assert "Sushi" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_no_data(self, mock_run_async, mock_client_class, runner):
        """Test discover food with no discoveries available."""
        mock_run_async.return_value = {
            "discoveries": [],
        }

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 0
        assert "No discoveries available" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test discover food with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_food_server_error(self, mock_run_async, mock_client_class, runner):
        """Test discover food with server error."""
        mock_run_async.side_effect = FcpServerError("Internal server error")

        result = runner.invoke(app, ["food"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestDiscoverRestaurantsCommand:
    """Test discover restaurants command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_with_coordinates(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with latitude and longitude."""
        mock_run_async.return_value = (
            {
                "restaurants": [
                    {
                        "name": "The Italian Place",
                        "cuisine": "Italian",
                        "rating": "4.5",
                        "distance": "0.5 mi",
                    },
                    {
                        "name": "Sushi Bar",
                        "type": "Japanese",
                        "rating": "4.8",
                        "distance": "0.3 mi",
                    },
                ],
            },
            None,
        )

        result = runner.invoke(app, ["restaurants", "--lat", "40.7128", "--lon", "-74.0060"])

        assert result.exit_code == 0
        assert "The Italian Place" in result.stdout
        assert "Sushi Bar" in result.stdout
        assert "4.5" in result.stdout
        assert "Japanese" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_with_location(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with location string."""
        mock_run_async.return_value = (
            {
                "restaurants": [
                    {
                        "name": "Local Cafe",
                        "cuisine": "American",
                        "rating": "4.2",
                        "distance": "1.0 mi",
                    },
                ],
            },
            "San Francisco, CA",
        )

        result = runner.invoke(app, ["restaurants", "--location", "San Francisco, CA"])

        assert result.exit_code == 0
        assert "Local Cafe" in result.stdout
        # Note: resolved location is shown in table title (may have formatting/newlines)
        assert "San Francisco" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_results_key(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with 'results' key instead of 'restaurants'."""
        mock_run_async.return_value = (
            {
                "results": [
                    {
                        "name": "Pizza Shop",
                        "cuisine": "Italian",
                        "rating": "4.0",
                        "distance": "0.2 mi",
                    },
                ],
            },
            None,
        )

        result = runner.invoke(app, ["restaurants", "--lat", "40.0", "--lon", "-74.0"])

        assert result.exit_code == 0
        assert "Pizza Shop" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_no_results(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with no results."""
        mock_run_async.return_value = ({"restaurants": []}, None)

        result = runner.invoke(app, ["restaurants", "--lat", "40.0", "--lon", "-74.0"])

        assert result.exit_code == 0
        assert "No restaurant recommendations" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_missing_fields(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with missing optional fields."""
        mock_run_async.return_value = (
            {
                "restaurants": [
                    {
                        # Missing cuisine, rating, distance
                        "name": "Mystery Restaurant",
                    },
                ],
            },
            None,
        )

        result = runner.invoke(app, ["restaurants", "--lat", "40.0", "--lon", "-74.0"])

        assert result.exit_code == 0
        assert "Mystery Restaurant" in result.stdout

    def test_discover_restaurants_no_location_provided(self, runner):
        """Test discover restaurants without any location."""
        result = runner.invoke(app, ["restaurants"])

        assert result.exit_code == 1
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_discover_restaurants_only_latitude(self, runner):
        """Test discover restaurants with only latitude."""
        result = runner.invoke(app, ["restaurants", "--lat", "40.0"])

        assert result.exit_code == 1
        # The first validation check catches this case
        assert "provide either --lat/--lon or --location" in result.stdout

    def test_discover_restaurants_only_longitude(self, runner):
        """Test discover restaurants with only longitude."""
        result = runner.invoke(app, ["restaurants", "--lon", "-74.0"])

        assert result.exit_code == 1
        # The first validation check catches this case
        assert "provide either --lat/--lon or --location" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_coordinates_precedence(self, mock_run_async, mock_client_class, runner):
        """Test that coordinates take precedence over location."""
        mock_run_async.return_value = (
            {
                "restaurants": [
                    {
                        "name": "Nearby Spot",
                        "cuisine": "Mexican",
                        "rating": "4.3",
                        "distance": "0.4 mi",
                    },
                ],
            },
            None,
        )

        result = runner.invoke(
            app,
            ["restaurants", "--lat", "40.7128", "--lon", "-74.0060", "--location", "Boston, MA"],
        )

        assert result.exit_code == 0
        assert "Nearby Spot" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["restaurants", "--lat", "40.0", "--lon", "-74.0"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_restaurants_server_error(self, mock_run_async, mock_client_class, runner):
        """Test discover restaurants with server error."""
        mock_run_async.side_effect = FcpServerError("Internal server error")

        result = runner.invoke(app, ["restaurants", "--location", "NYC"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestDiscoverRecipesCommand:
    """Test discover recipes command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_with_full_details(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with complete recipe data."""
        mock_run_async.return_value = {
            "recipes": [
                {
                    "name": "Chicken Stir Fry",
                    "description": "Quick and healthy dinner",
                    "cook_time": "25 minutes",
                    "difficulty": "Medium",
                },
                {
                    "name": "Pasta Primavera",
                    "description": "Light vegetable pasta",
                    "cook_time": "20 minutes",
                    "difficulty": "Easy",
                },
            ],
        }

        result = runner.invoke(app, ["recipes", "chicken", "vegetables"])

        assert result.exit_code == 0
        assert "Chicken Stir Fry" in result.stdout
        assert "Pasta Primavera" in result.stdout
        assert "25 minutes" in result.stdout
        assert "Medium" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_suggestions_key(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with 'suggestions' key instead of 'recipes'."""
        mock_run_async.return_value = {
            "suggestions": [
                {
                    "title": "Tomato Soup",
                    "description": "Classic comfort food",
                },
            ],
        }

        result = runner.invoke(app, ["recipes", "tomatoes", "onions"])

        assert result.exit_code == 0
        assert "Tomato Soup" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_minimal_data(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with minimal recipe data."""
        mock_run_async.return_value = {
            "recipes": [
                {
                    "name": "Simple Salad",
                    "description": "Fresh and healthy",
                },
            ],
        }

        result = runner.invoke(app, ["recipes", "lettuce"])

        assert result.exit_code == 0
        assert "Simple Salad" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_with_time_field(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes using 'time' field instead of 'cook_time'."""
        mock_run_async.return_value = {
            "recipes": [
                {
                    "name": "Quick Eggs",
                    "description": "Fast breakfast",
                    "time": "5 minutes",
                },
            ],
        }

        result = runner.invoke(app, ["recipes", "eggs"])

        assert result.exit_code == 0
        assert "5 minutes" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_no_results(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with no results."""
        mock_run_async.return_value = {"recipes": []}

        result = runner.invoke(app, ["recipes", "unicorn", "rainbow"])

        assert result.exit_code == 0
        assert "No recipe suggestions" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_single_ingredient(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with single ingredient."""
        mock_run_async.return_value = {
            "recipes": [
                {
                    "name": "Baked Potato",
                    "description": "Classic side dish",
                    "cook_time": "60 minutes",
                    "difficulty": "Easy",
                },
            ],
        }

        result = runner.invoke(app, ["recipes", "potato"])

        assert result.exit_code == 0
        assert "Baked Potato" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_multiple_ingredients(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with multiple ingredients."""
        mock_run_async.return_value = {
            "recipes": [
                {
                    "name": "Veggie Bowl",
                    "description": "Nutritious meal",
                },
            ],
        }

        result = runner.invoke(app, ["recipes", "rice", "beans", "avocado", "salsa"])

        assert result.exit_code == 0
        assert "Veggie Bowl" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["recipes", "flour", "eggs"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_discover_recipes_server_error(self, mock_run_async, mock_client_class, runner):
        """Test discover recipes with server error."""
        mock_run_async.side_effect = FcpServerError("Internal server error")

        result = runner.invoke(app, ["recipes", "fish"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestShowTrendsCommand:
    """Test show trends command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_default(self, mock_run_async, mock_client_class, runner):
        """Test show trends with default parameters."""
        mock_run_async.return_value = {
            "trends": [
                {
                    "name": "Plant-based proteins",
                    "description": "Growing popularity of plant proteins",
                    "popularity": "High",
                },
                {
                    "name": "Fermented foods",
                    "description": "Gut health focus",
                    "score": "85",
                },
            ],
        }

        result = runner.invoke(app, ["trends"])

        assert result.exit_code == 0
        assert "Plant-based proteins" in result.stdout
        assert "Fermented foods" in result.stdout
        assert "High" in result.stdout
        assert "85" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_with_region(self, mock_run_async, mock_client_class, runner):
        """Test show trends with region filter."""
        mock_run_async.return_value = {
            "trends": [
                {
                    "name": "Regional specialty",
                    "description": "Local favorite",
                    "popularity": "Medium",
                },
            ],
        }

        result = runner.invoke(app, ["trends", "--region", "West Coast"])

        assert result.exit_code == 0
        assert "Regional specialty" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_with_cuisine(self, mock_run_async, mock_client_class, runner):
        """Test show trends with cuisine focus."""
        mock_run_async.return_value = {
            "trends": [
                {
                    "name": "Ramen varieties",
                    "description": "New ramen styles",
                    "popularity": "Very High",
                },
            ],
        }

        result = runner.invoke(app, ["trends", "--cuisine", "Japanese"])

        assert result.exit_code == 0
        assert "Ramen varieties" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_with_both_filters(self, mock_run_async, mock_client_class, runner):
        """Test show trends with both region and cuisine."""
        mock_run_async.return_value = {
            "trends": [
                {
                    "name": "Fusion cuisine",
                    "description": "Asian-Mexican fusion",
                    "popularity": "Growing",
                },
            ],
        }

        result = runner.invoke(app, ["trends", "--region", "California", "--cuisine", "Fusion"])

        assert result.exit_code == 0
        assert "Fusion cuisine" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_with_sources(self, mock_run_async, mock_client_class, runner):
        """Test show trends with sources."""
        mock_run_async.return_value = {
            "trends": [
                {
                    "name": "AI-powered cooking",
                    "description": "Tech meets kitchen",
                    "popularity": "Emerging",
                },
            ],
            "sources": [
                {
                    "title": "Food Tech Magazine",
                    "url": "https://example.com/article",
                },
                {
                    "title": "Culinary Trends Report",
                    "url": "https://example.com/report",
                },
            ],
        }

        result = runner.invoke(app, ["trends"])

        assert result.exit_code == 0
        assert "AI-powered cooking" in result.stdout
        assert "Sources:" in result.stdout
        assert "Food Tech Magazine" in result.stdout
        assert "https://example.com/article" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_missing_fields(self, mock_run_async, mock_client_class, runner):
        """Test show trends with missing optional fields."""
        mock_run_async.return_value = {
            "trends": [
                {
                    # Missing name, description, popularity
                },
            ],
        }

        result = runner.invoke(app, ["trends"])

        assert result.exit_code == 0

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_no_data(self, mock_run_async, mock_client_class, runner):
        """Test show trends with no trends available."""
        mock_run_async.return_value = {"trends": []}

        result = runner.invoke(app, ["trends"])

        assert result.exit_code == 0
        assert "No trends available" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test show trends with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["trends"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_trends_server_error(self, mock_run_async, mock_client_class, runner):
        """Test show trends with server error."""
        mock_run_async.side_effect = FcpServerError("Internal server error")

        result = runner.invoke(app, ["trends", "--region", "Europe"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestShowTipCommand:
    """Test show tip command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_full_data(self, mock_run_async, mock_client_class, runner):
        """Test show tip with complete data."""
        mock_run_async.return_value = {
            "tip": "Store tomatoes at room temperature for better flavor",
            "tip_title": "Tomato Storage",
            "category": "Storage Tips",
            "source": "The Kitchen Science Journal",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "tomatoes at room temperature" in result.stdout
        assert "Tomato Storage" in result.stdout
        assert "Storage Tips" in result.stdout
        assert "The Kitchen Science Journal" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_text_key(self, mock_run_async, mock_client_class, runner):
        """Test show tip with 'text' key instead of 'tip'."""
        mock_run_async.return_value = {
            "text": "Always preheat your oven",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "preheat your oven" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_content_key(self, mock_run_async, mock_client_class, runner):
        """Test show tip with 'content' key."""
        mock_run_async.return_value = {
            "content": "Salt pasta water generously",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "Salt pasta water" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_minimal_data(self, mock_run_async, mock_client_class, runner):
        """Test show tip with minimal data."""
        mock_run_async.return_value = {
            "tip": "Let meat rest before cutting",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "meat rest before cutting" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_with_title_no_category(self, mock_run_async, mock_client_class, runner):
        """Test show tip with title but no category."""
        mock_run_async.return_value = {
            "tip": "Use a kitchen scale for baking",
            "tip_title": "Baking Accuracy",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "kitchen scale" in result.stdout
        assert "Baking Accuracy" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_with_category_no_title(self, mock_run_async, mock_client_class, runner):
        """Test show tip with category but no custom title."""
        mock_run_async.return_value = {
            "tip": "Keep knives sharp for safety",
            "category": "Kitchen Safety",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "knives sharp" in result.stdout
        assert "Kitchen Safety" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_with_source_no_title(self, mock_run_async, mock_client_class, runner):
        """Test show tip with source but no title."""
        mock_run_async.return_value = {
            "tip": "Taste as you cook",
            "source": "Chef's Wisdom",
        }

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "Taste as you cook" in result.stdout
        assert "Chef's Wisdom" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_empty_tip(self, mock_run_async, mock_client_class, runner):
        """Test show tip with empty tip text."""
        mock_run_async.return_value = {}

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 0
        assert "No tip available" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test show tip with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.discover.FcpClient")
    @patch("fcp_cli.commands.discover.run_async")
    def test_show_tip_server_error(self, mock_run_async, mock_client_class, runner):
        """Test show tip with server error."""
        mock_run_async.side_effect = FcpServerError("Internal server error")

        result = runner.invoke(app, ["tip"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "command,args,expected_in_output",
    [
        ("food", [], "Test insight"),
        ("restaurants", ["--lat", "40.7128", "--lon", "-74.0060"], "Restaurant"),
        ("restaurants", ["--location", "New York"], "Restaurant"),
        ("recipes", ["eggs", "cheese"], "recipe"),
        ("trends", [], "Trends"),
        ("trends", ["--region", "Asia"], "Trends"),
        ("trends", ["--cuisine", "Italian"], "Trends"),
        ("tip", [], "Tip"),
    ],
)
@patch("fcp_cli.commands.discover.FcpClient")
@patch("fcp_cli.commands.discover.run_async")
def test_all_commands_parametrized(mock_run_async, mock_client_class, command, args, expected_in_output):
    """Test all discover commands with various inputs."""

    # Set up appropriate mock responses
    if command == "food":
        mock_run_async.return_value = {
            "insight": "Test insight",
            "discoveries": [{"name": "Test", "description": "Test desc"}],
        }
    elif command == "restaurants":
        mock_run_async.return_value = (
            {"restaurants": [{"name": "Test Restaurant", "cuisine": "Test", "rating": "5", "distance": "1 mi"}]},
            "Test Location",
        )
    elif command == "recipes":
        mock_run_async.return_value = {"recipes": [{"name": "Test Recipe", "description": "Test desc"}]}
    elif command == "trends":
        mock_run_async.return_value = {
            "trends": [{"name": "Test Trend", "description": "Test desc", "popularity": "High"}]
        }
    elif command == "tip":
        mock_run_async.return_value = {"tip": "Test tip"}

    runner = CliRunner()
    result = runner.invoke(app, [command] + args)

    assert result.exit_code == 0
    assert expected_in_output in result.stdout or expected_in_output.lower() in result.stdout.lower()


class TestDiscoverRestaurantsValidation:
    """Test discover restaurants input validation."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_discover_restaurants_only_latitude(self, runner):
        """Test discover restaurants with only latitude."""
        result = runner.invoke(app, ["restaurants", "--lat", "40.7128", "--location", "NYC"])

        assert result.exit_code == 1
        assert "Both --lat and --lon must be provided together" in result.stdout

    def test_discover_restaurants_only_longitude(self, runner):
        """Test discover restaurants with only longitude."""
        result = runner.invoke(app, ["restaurants", "--lon", "-74.0060", "--location", "NYC"])

        assert result.exit_code == 1
        assert "Both --lat and --lon must be provided together" in result.stdout
