"""Tests for profile commands."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.profile import _format_list, app
from fcp_cli.services.fcp import FcpConnectionError, FcpServerError
from fcp_cli.services.models import TasteProfile

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestFormatList:
    """Test _format_list helper function."""

    def test_format_empty_list(self):
        """Test formatting empty list."""
        result = _format_list([])
        assert result == "[dim]None[/dim]"

    def test_format_list_within_max(self):
        """Test formatting list with fewer items than max."""
        result = _format_list(["Italian", "Japanese", "Mexican"])
        assert result == "Italian, Japanese, Mexican"
        assert "more" not in result

    def test_format_list_at_max(self):
        """Test formatting list with exactly max items."""
        items = ["A", "B", "C", "D", "E"]
        result = _format_list(items, max_items=5)
        assert result == "A, B, C, D, E"
        assert "more" not in result

    def test_format_list_exceeds_max(self):
        """Test formatting list exceeding max items."""
        items = ["A", "B", "C", "D", "E", "F", "G"]
        result = _format_list(items, max_items=5)
        assert "A, B, C, D, E" in result
        assert "(+2 more)" in result

    def test_format_list_custom_max(self):
        """Test formatting with custom max_items parameter."""
        items = ["One", "Two", "Three", "Four"]
        result = _format_list(items, max_items=2)
        assert "One, Two" in result
        assert "(+2 more)" in result

    def test_format_single_item(self):
        """Test formatting list with single item."""
        result = _format_list(["Only"])
        assert result == "Only"


class TestShowCommand:
    """Test profile show command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def sample_profile(self):
        """Sample taste profile data."""
        return TasteProfile(
            user_id="user123",
            favorite_cuisines=["Italian", "Japanese", "Mexican"],
            preferred_ingredients=["garlic", "tomatoes", "basil"],
            disliked_ingredients=["cilantro"],
            dietary_restrictions=["vegetarian"],
            average_calories=2000.0,
            meal_patterns={"breakfast": "light", "dinner": "heavy"},
        )

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_success(self, mock_client_class, runner, sample_profile):
        """Test successful profile display."""
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(return_value=sample_profile)

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 0
        assert "Italian" in result.stdout
        assert "Japanese" in result.stdout
        assert "garlic" in result.stdout
        assert "cilantro" in result.stdout
        assert "vegetarian" in result.stdout
        assert "2000" in result.stdout
        mock_client.get_taste_profile.assert_called_once()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_with_meal_patterns(self, mock_client_class, runner, sample_profile):
        """Test profile display with meal patterns."""
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(return_value=sample_profile)

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 0
        assert "breakfast" in result.stdout.lower()
        assert "dinner" in result.stdout.lower()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_without_meal_patterns(self, mock_client_class, runner):
        """Test profile display without meal patterns."""
        profile = TasteProfile(
            user_id="user123",
            favorite_cuisines=["Italian"],
            preferred_ingredients=["garlic"],
            disliked_ingredients=[],
            dietary_restrictions=[],
            average_calories=None,
            meal_patterns=None,
        )
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(return_value=profile)

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 0
        assert "Italian" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_empty_lists(self, mock_client_class, runner):
        """Test profile display with empty lists."""
        profile = TasteProfile(
            user_id="user123",
            favorite_cuisines=[],
            preferred_ingredients=[],
            disliked_ingredients=[],
            dietary_restrictions=[],
            average_calories=None,
            meal_patterns=None,
        )
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(return_value=profile)

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 0
        # Empty lists should show "None"
        assert "None" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_long_lists(self, mock_client_class, runner):
        """Test profile display with long lists (exceeding max_items)."""
        profile = TasteProfile(
            user_id="user123",
            favorite_cuisines=["A", "B", "C", "D", "E", "F", "G", "H"],
            preferred_ingredients=["1", "2", "3", "4", "5", "6"],
            disliked_ingredients=[],
            dietary_restrictions=[],
        )
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(return_value=profile)

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 0
        assert "more" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_connection_error(self, mock_client_class, runner):
        """Test profile show with connection error."""
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(side_effect=FcpConnectionError("Connection failed"))

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_server_error(self, mock_client_class, runner):
        """Test profile show with server error."""
        mock_client = mock_client_class.return_value
        mock_client.get_taste_profile = AsyncMock(side_effect=FcpServerError("Server error"))

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestStatsCommand:
    """Test profile stats command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_stats_default(self, mock_client_class, runner):
        """Test stats with default parameters."""
        mock_client = mock_client_class.return_value
        mock_client.get_food_stats = AsyncMock(
            return_value={
                "total_meals": 50,
                "by_meal_type": {"breakfast": 15, "lunch": 20, "dinner": 15},
            }
        )

        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "50" in result.stdout
        mock_client.get_food_stats.assert_called_once_with(period="month", group_by="meal_type")

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_stats_custom_period(self, mock_client_class, runner):
        """Test stats with custom period."""
        mock_client = mock_client_class.return_value
        mock_client.get_food_stats = AsyncMock(return_value={"total_meals": 10})

        result = runner.invoke(app, ["stats", "--period", "week"])

        assert result.exit_code == 0
        mock_client.get_food_stats.assert_called_once_with(period="week", group_by="meal_type")

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_stats_custom_group_by(self, mock_client_class, runner):
        """Test stats with custom group_by."""
        mock_client = mock_client_class.return_value
        mock_client.get_food_stats = AsyncMock(return_value={"by_day": {"Mon": 5, "Tue": 7}})

        result = runner.invoke(app, ["stats", "--group-by", "day"])

        assert result.exit_code == 0
        mock_client.get_food_stats.assert_called_once_with(period="month", group_by="day")

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_stats_short_options(self, mock_client_class, runner):
        """Test stats with short option flags."""
        mock_client = mock_client_class.return_value
        mock_client.get_food_stats = AsyncMock(return_value={})

        result = runner.invoke(app, ["stats", "-p", "year", "-g", "cuisine"])

        assert result.exit_code == 0
        mock_client.get_food_stats.assert_called_once_with(period="year", group_by="cuisine")

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_stats_connection_error(self, mock_client_class, runner):
        """Test stats with connection error."""
        mock_client = mock_client_class.return_value
        mock_client.get_food_stats = AsyncMock(side_effect=FcpConnectionError("Connection failed"))

        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_stats_server_error(self, mock_client_class, runner):
        """Test stats with server error."""
        mock_client = mock_client_class.return_value
        mock_client.get_food_stats = AsyncMock(side_effect=FcpServerError("Server error"))

        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestReportCommand:
    """Test profile report command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_default(self, mock_client_class, runner):
        """Test report with default parameters."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(
            return_value={
                "title": "Weekly Nutrition Report",
                "content": "Your nutrition looks great!",
            }
        )

        result = runner.invoke(app, ["report"])

        assert result.exit_code == 0
        assert "Weekly Nutrition Report" in result.stdout
        assert "Your nutrition looks great!" in result.stdout
        mock_client.get_dietitian_report.assert_called_once_with(days=7, focus_area=None)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_custom_days(self, mock_client_class, runner):
        """Test report with custom days."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(return_value={"title": "Report", "content": "Content"})

        result = runner.invoke(app, ["report", "--days", "14"])

        assert result.exit_code == 0
        mock_client.get_dietitian_report.assert_called_once_with(days=14, focus_area=None)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_with_focus(self, mock_client_class, runner):
        """Test report with focus area."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(
            return_value={
                "title": "Protein Focus Report",
                "content": "Protein intake analysis...",
            }
        )

        result = runner.invoke(app, ["report", "--focus", "protein"])

        assert result.exit_code == 0
        assert "Protein" in result.stdout
        mock_client.get_dietitian_report.assert_called_once_with(days=7, focus_area="protein")

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_short_options(self, mock_client_class, runner):
        """Test report with short option flags."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(return_value={"title": "IBS Report", "content": "Analysis"})

        result = runner.invoke(app, ["report", "-d", "30", "-f", "IBS"])

        assert result.exit_code == 0
        mock_client.get_dietitian_report.assert_called_once_with(days=30, focus_area="IBS")

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_fallback_content(self, mock_client_class, runner):
        """Test report with fallback content field."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(return_value={"report": "Fallback report content"})

        result = runner.invoke(app, ["report"])

        assert result.exit_code == 0
        assert "Fallback report content" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_connection_error(self, mock_client_class, runner):
        """Test report with connection error."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(side_effect=FcpConnectionError("Connection failed"))

        result = runner.invoke(app, ["report"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_report_server_error(self, mock_client_class, runner):
        """Test report with server error."""
        mock_client = mock_client_class.return_value
        mock_client.get_dietitian_report = AsyncMock(side_effect=FcpServerError("Server error"))

        result = runner.invoke(app, ["report"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestStreakCommand:
    """Test profile streak command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_default(self, mock_client_class, runner):
        """Test streak with default parameters."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(
            return_value={
                "current_streak": 5,
                "best_streak": 10,
                "last_logged": "2026-02-08",
            }
        )

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "5 days" in result.stdout
        assert "10 days" in result.stdout
        assert "2026-02-08" in result.stdout
        mock_client.get_streak.assert_called_once_with(streak_days=7)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_custom_days(self, mock_client_class, runner):
        """Test streak with custom days."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 15, "best_streak": 20})

        result = runner.invoke(app, ["streak", "--days", "14"])

        assert result.exit_code == 0
        mock_client.get_streak.assert_called_once_with(streak_days=14)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_zero(self, mock_client_class, runner):
        """Test streak display when streak is zero."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 0, "best_streak": 5})

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "0 days" in result.stdout
        assert "Log a meal today to start your streak!" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_short_encouragement(self, mock_client_class, runner):
        """Test encouragement message for short streak."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 4, "best_streak": 10})

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "Great job! Keep the streak going!" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_long_encouragement(self, mock_client_class, runner):
        """Test encouragement message for long streak."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 10, "best_streak": 15})

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "Amazing" in result.stdout
        assert "10 days straight" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_at_threshold(self, mock_client_class, runner):
        """Test streak at threshold boundaries."""
        # Test at 3 days (just at threshold)
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 3, "best_streak": 3})

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "Great job" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_at_seven(self, mock_client_class, runner):
        """Test streak at 7 days threshold."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 7, "best_streak": 7})

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "Amazing" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_fallback_keys(self, mock_client_class, runner):
        """Test streak with fallback response keys."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(
            return_value={
                "streak": 8,  # Fallback key for current_streak
                "longest_streak": 12,  # Fallback key for best_streak
                "last_log_date": "2026-02-07",  # Fallback key for last_logged
            }
        )

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "8 days" in result.stdout
        assert "12 days" in result.stdout
        assert "2026-02-07" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_no_last_logged(self, mock_client_class, runner):
        """Test streak without last_logged field."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 5, "best_streak": 5})

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 0
        assert "5 days" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_connection_error(self, mock_client_class, runner):
        """Test streak with connection error."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(side_effect=FcpConnectionError("Connection failed"))

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_server_error(self, mock_client_class, runner):
        """Test streak with server error."""
        mock_client = mock_client_class.return_value
        mock_client.get_streak = AsyncMock(side_effect=FcpServerError("Server error"))

        result = runner.invoke(app, ["streak"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestLifetimeCommand:
    """Test profile lifetime command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_success(self, mock_client_class, runner):
        """Test lifetime stats display."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(
            return_value={
                "total_meals": 250,
                "unique_dishes": 180,
                "days_logged": 100,
                "first_log": "2025-01-01",
                "favorite_cuisine": "Italian",
                "avg_meals_per_day": 2.5,
            }
        )

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 0
        assert "250" in result.stdout
        assert "180" in result.stdout
        assert "100" in result.stdout
        assert "2025-01-01" in result.stdout
        assert "Italian" in result.stdout
        assert "2.5" in result.stdout
        mock_client.get_lifetime_stats.assert_called_once()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_fallback_keys(self, mock_client_class, runner):
        """Test lifetime stats with fallback response keys."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(
            return_value={
                "meals_logged": 100,  # Fallback for total_meals
                "unique_foods": 75,  # Fallback for unique_dishes
                "active_days": 50,  # Fallback for days_logged
                "member_since": "2024-06-01",  # Fallback for first_log
                "top_cuisine": "Japanese",  # Fallback for favorite_cuisine
                "average_daily_meals": 2.0,  # Fallback for avg_meals_per_day
            }
        )

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 0
        assert "100" in result.stdout
        assert "75" in result.stdout
        assert "50" in result.stdout
        assert "2024-06-01" in result.stdout
        assert "Japanese" in result.stdout
        assert "2.0" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_minimal_data(self, mock_client_class, runner):
        """Test lifetime stats with minimal data."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(
            return_value={
                "total_meals": 5,
                "unique_dishes": 4,
                "days_logged": 3,
            }
        )

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 0
        assert "5" in result.stdout
        assert "4" in result.stdout
        assert "3" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_zero_stats(self, mock_client_class, runner):
        """Test lifetime stats with zero values."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(
            return_value={
                "total_meals": 0,
                "unique_dishes": 0,
                "days_logged": 0,
            }
        )

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 0
        assert "0" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_float_avg_meals(self, mock_client_class, runner):
        """Test lifetime stats with float average meals."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(
            return_value={
                "total_meals": 100,
                "unique_dishes": 80,
                "days_logged": 30,
                "avg_meals_per_day": 3.333333,
            }
        )

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 0
        # Should format to 1 decimal place
        assert "3.3" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_connection_error(self, mock_client_class, runner):
        """Test lifetime stats with connection error."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(side_effect=FcpConnectionError("Connection failed"))

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_lifetime_server_error(self, mock_client_class, runner):
        """Test lifetime stats with server error."""
        mock_client = mock_client_class.return_value
        mock_client.get_lifetime_stats = AsyncMock(side_effect=FcpServerError("Server error"))

        result = runner.invoke(app, ["lifetime"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestNutritionCommand:
    """Test profile nutrition command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_default(self, mock_client_class, runner):
        """Test nutrition with default parameters."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={
                "summary": {
                    "avg_calories": 2000.0,
                    "total_calories": 14000.0,
                    "avg_protein": 80.0,
                    "total_protein": 560.0,
                    "avg_carbs": 250.0,
                    "total_carbs": 1750.0,
                    "avg_fat": 70.0,
                    "total_fat": 490.0,
                }
            }
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        assert "2000" in result.stdout
        assert "14000" in result.stdout
        mock_client.get_nutrition_analytics.assert_called_once_with(days=7)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_custom_days(self, mock_client_class, runner):
        """Test nutrition with custom days."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={"summary": {"avg_calories": 1800.0, "total_calories": 25200.0}}
        )

        result = runner.invoke(app, ["nutrition", "--days", "14"])

        assert result.exit_code == 0
        mock_client.get_nutrition_analytics.assert_called_once_with(days=14)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_short_option(self, mock_client_class, runner):
        """Test nutrition with short option flag."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(return_value={"summary": {"avg_calories": 2100.0}})

        result = runner.invoke(app, ["nutrition", "-d", "30"])

        assert result.exit_code == 0
        mock_client.get_nutrition_analytics.assert_called_once_with(days=30)

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_all_nutrients(self, mock_client_class, runner):
        """Test nutrition with all nutrient fields."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={
                "summary": {
                    "avg_calories": 2000.0,
                    "total_calories": 14000.0,
                    "avg_protein": 80.0,
                    "total_protein": 560.0,
                    "avg_carbs": 250.0,
                    "total_carbs": 1750.0,
                    "avg_fat": 70.0,
                    "total_fat": 490.0,
                    "avg_fiber": 30.0,
                    "total_fiber": 210.0,
                    "avg_sodium": 2000.0,
                    "total_sodium": 14000.0,
                }
            }
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        assert "Calories" in result.stdout
        assert "Protein" in result.stdout
        assert "Carbs" in result.stdout
        assert "Fat" in result.stdout
        assert "Fiber" in result.stdout
        assert "Sodium" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_fallback_keys(self, mock_client_class, runner):
        """Test nutrition with fallback response keys."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={
                "totals": {  # Fallback for summary
                    "calories_avg": 1900.0,  # Fallback for avg_calories
                    "calories": 13300.0,  # Fallback for total_calories
                    "protein_avg": 75.0,
                    "protein": 525.0,
                }
            }
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        assert "1900" in result.stdout
        assert "13300" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_with_breakdown(self, mock_client_class, runner):
        """Test nutrition with daily breakdown."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={
                "summary": {"avg_calories": 2000.0},
                "breakdown": [
                    {"label": "2026-02-08", "calories": 2100},
                    {"label": "2026-02-07", "calories": 1900},
                    {"label": "2026-02-06", "calories": 2000},
                ],
            }
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        assert "Daily Breakdown" in result.stdout
        assert "2026-02-08" in result.stdout
        assert "2100 kcal" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_breakdown_fallback_keys(self, mock_client_class, runner):
        """Test nutrition breakdown with fallback keys."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={
                "summary": {"avg_calories": 2000.0},
                "by_day": [  # Fallback for breakdown
                    {"date": "2026-02-08", "calories": 2200},  # Fallback for label
                    {"date": "2026-02-07", "calories": 1800},
                ],
            }
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        assert "2026-02-08" in result.stdout
        assert "2200 kcal" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_breakdown_limit(self, mock_client_class, runner):
        """Test nutrition breakdown limited to 10 items."""
        breakdown = [{"label": f"Day {i}", "calories": 2000 + i * 10} for i in range(15)]
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={"summary": {"avg_calories": 2000.0}, "breakdown": breakdown}
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        # Should only show first 10
        assert "Day 9" in result.stdout
        # Should not show 11th item
        assert "Day 10" not in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_no_summary(self, mock_client_class, runner):
        """Test nutrition without summary data."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(return_value={})

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_partial_nutrients(self, mock_client_class, runner):
        """Test nutrition with only some nutrients available."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(
            return_value={
                "summary": {
                    "avg_calories": 2000.0,
                    "total_calories": 14000.0,
                    # Missing other nutrients
                }
            }
        )

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 0
        assert "Calories" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_connection_error(self, mock_client_class, runner):
        """Test nutrition with connection error."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(side_effect=FcpConnectionError("Connection failed"))

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_nutrition_server_error(self, mock_client_class, runner):
        """Test nutrition with server error."""
        mock_client = mock_client_class.return_value
        mock_client.get_nutrition_analytics = AsyncMock(side_effect=FcpServerError("Server error"))

        result = runner.invoke(app, ["nutrition"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "command,expected_text",
    [
        ("show", "Taste Profile"),
        ("stats", "Food Stats"),
        ("report", "Dietitian Report"),
        ("streak", "Logging Streak"),
        ("lifetime", "Lifetime Statistics"),
        ("nutrition", "Nutrition Summary"),
    ],
)
@patch("fcp_cli.commands.profile.FcpClient")
def test_all_commands_output_format(mock_client_class, command, expected_text):
    """Test that all commands produce expected output format."""
    mock_client = mock_client_class.return_value

    # Set up appropriate mocks for each command
    if command == "show":
        profile = TasteProfile(
            user_id="user123",
            favorite_cuisines=["Italian"],
            preferred_ingredients=["garlic"],
            disliked_ingredients=[],
            dietary_restrictions=[],
        )
        mock_client.get_taste_profile = AsyncMock(return_value=profile)
    elif command == "stats":
        mock_client.get_food_stats = AsyncMock(return_value={"total": 100})
    elif command == "report":
        mock_client.get_dietitian_report = AsyncMock(return_value={"title": "Dietitian Report", "content": "Content"})
    elif command == "streak":
        mock_client.get_streak = AsyncMock(return_value={"current_streak": 5, "best_streak": 10})
    elif command == "lifetime":
        mock_client.get_lifetime_stats = AsyncMock(
            return_value={
                "total_meals": 100,
                "unique_dishes": 50,
                "days_logged": 30,
            }
        )
    elif command == "nutrition":
        mock_client.get_nutrition_analytics = AsyncMock(return_value={"summary": {"avg_calories": 2000.0}})

    runner = CliRunner()
    result = runner.invoke(app, [command])

    assert result.exit_code == 0
    assert expected_text in result.stdout


@pytest.mark.parametrize(
    "error_class,error_message",
    [
        (FcpConnectionError, "Connection failed"),
        (FcpServerError, "Internal server error"),
    ],
)
@patch("fcp_cli.commands.profile.FcpClient")
def test_error_handling_consistency(mock_client_class, error_class, error_message):
    """Test that all commands handle errors consistently."""
    mock_client = mock_client_class.return_value
    mock_client.get_taste_profile = AsyncMock(side_effect=error_class(error_message))

    runner = CliRunner()
    result = runner.invoke(app, ["show"])

    assert result.exit_code == 1
    assert "error" in result.stdout.lower()
