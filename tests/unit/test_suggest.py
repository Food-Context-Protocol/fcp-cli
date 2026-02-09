"""Tests for suggest commands."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.suggest import app
from fcp_cli.services import FcpConnectionError, FcpServerError, MealSuggestion

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestSuggestMealsCommand:
    """Test suggest meals command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def full_suggestions(self):
        """Full meal suggestions with all fields."""
        return [
            MealSuggestion(
                name="Grilled Salmon with Asparagus",
                description="Light and healthy dinner option",
                meal_type="dinner",
                venue="Home",
                reason="You haven't had fish in a week",
                ingredients_needed=["salmon", "asparagus", "lemon"],
                prep_time="25 minutes",
                match_score=0.95,
            ),
            MealSuggestion(
                name="Buddha Bowl",
                description="Nutritious vegetarian bowl",
                meal_type="lunch",
                venue="Home",
                reason="Based on your preference for healthy meals",
                ingredients_needed=["quinoa", "chickpeas", "vegetables"],
                prep_time="30 minutes",
                match_score=0.88,
            ),
        ]

    @pytest.fixture
    def minimal_suggestions(self):
        """Minimal meal suggestions with only required fields."""
        return [
            MealSuggestion(
                name="Pizza",
                description=None,
                meal_type=None,
                venue=None,
                reason=None,
                ingredients_needed=None,
                prep_time=None,
                match_score=None,
            ),
            MealSuggestion(
                name="Salad",
                description="Fresh greens",
                meal_type="lunch",
            ),
        ]

    @pytest.fixture
    def restaurant_suggestions(self):
        """Restaurant-based suggestions."""
        return [
            MealSuggestion(
                name="Ramen",
                description="Tonkotsu ramen bowl",
                meal_type="dinner",
                venue="Ippudo",
                reason="You love ramen and haven't been there recently",
                match_score=0.92,
            ),
        ]

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_default(self, mock_run_async, mock_client_class, runner, full_suggestions):
        """Test suggest meals with default options."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = full_suggestions

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Grilled Salmon" in result.stdout
        assert "Buddha Bowl" in result.stdout
        assert "haven't had fish" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_with_context(self, mock_run_async, mock_client_class, runner, full_suggestions):
        """Test suggest meals with context."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = full_suggestions

        result = runner.invoke(app, ["--context", "date night"])

        assert result.exit_code == 0
        assert "Grilled Salmon" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_with_exclude_days(self, mock_run_async, mock_client_class, runner, full_suggestions):
        """Test suggest meals with custom exclude days."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = full_suggestions

        result = runner.invoke(app, ["--exclude-days", "7"])

        assert result.exit_code == 0
        assert "Grilled Salmon" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_all_options(self, mock_run_async, mock_client_class, runner, full_suggestions):
        """Test suggest meals with all options."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = full_suggestions

        result = runner.invoke(
            app,
            ["--context", "healthy lunch", "--exclude-days", "5"],
        )

        assert result.exit_code == 0
        assert "Buddha Bowl" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_displays_all_fields(self, mock_run_async, mock_client_class, runner, full_suggestions):
        """Test that all suggestion fields are displayed."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = full_suggestions[:1]

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Grilled Salmon" in result.stdout
        assert "Light and healthy" in result.stdout
        assert "dinner" in result.stdout
        assert "Home" in result.stdout
        assert "haven't had fish" in result.stdout
        assert "salmon" in result.stdout
        assert "25 minutes" in result.stdout
        assert "95%" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_minimal_data(self, mock_run_async, mock_client_class, runner, minimal_suggestions):
        """Test suggestions with minimal data."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = minimal_suggestions

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "Salad" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_restaurant_venue(self, mock_run_async, mock_client_class, runner, restaurant_suggestions):
        """Test suggestions with restaurant venues."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = restaurant_suggestions

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Ramen" in result.stdout
        assert "Ippudo" in result.stdout
        assert "92%" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_no_suggestions(self, mock_run_async, mock_client_class, runner):
        """Test when no suggestions are available."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = []

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "No suggestions available" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_empty_list(self, mock_run_async, mock_client_class, runner):
        """Test with empty suggestions list."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = []

        result = runner.invoke(app, ["--context", "breakfast"])

        assert result.exit_code == 0
        assert "No suggestions" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_match_score_formatting(self, mock_run_async, mock_client_class, runner):
        """Test match score percentage formatting."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        suggestions = [
            MealSuggestion(name="Test Meal", match_score=0.856),
        ]
        mock_run_async.return_value = suggestions

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "86%" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_ingredients_list(self, mock_run_async, mock_client_class, runner):
        """Test ingredients list formatting."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        suggestions = [
            MealSuggestion(
                name="Stir Fry",
                ingredients_needed=["chicken", "broccoli", "soy sauce", "rice"],
            ),
        ]
        mock_run_async.return_value = suggestions

        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "chicken" in result.stdout
        assert "broccoli" in result.stdout
        assert "soy sauce" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test suggest meals with connection error."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, [])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.suggest.FcpClient")
    @patch("fcp_cli.commands.suggest.run_async")
    def test_suggest_meals_server_error(self, mock_run_async, mock_client_class, runner):
        """Test suggest meals with server error."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, [])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "context,exclude_days",
    [
        ("breakfast", 1),
        ("quick lunch", 3),
        ("date night", 7),
        ("healthy dinner", 5),
        (None, 3),
    ],
)
@patch("fcp_cli.commands.suggest.FcpClient")
@patch("fcp_cli.commands.suggest.run_async")
def test_suggest_meals_various_contexts(mock_run_async, mock_client_class, context, exclude_days):
    """Test suggesting meals with various contexts."""
    mock_client = AsyncMock()
    mock_client_class.return_value = mock_client
    suggestions = [
        MealSuggestion(
            name="Test Meal",
            description="Test description",
            match_score=0.85,
        ),
    ]
    mock_run_async.return_value = suggestions

    runner = CliRunner()
    cmd = ["--exclude-days", str(exclude_days)]
    if context:
        cmd.extend(["--context", context])

    result = runner.invoke(app, cmd)

    assert result.exit_code == 0
    assert "Test Meal" in result.stdout


@pytest.mark.parametrize(
    "match_score,expected_display",
    [
        (0.95, "95%"),
        (0.5, "50%"),
        (0.123, "12%"),
        (1.0, "100%"),
        (None, None),
    ],
)
@patch("fcp_cli.commands.suggest.FcpClient")
@patch("fcp_cli.commands.suggest.run_async")
def test_suggest_meals_score_display(mock_run_async, mock_client_class, match_score, expected_display):
    """Test match score display formatting."""
    mock_client = AsyncMock()
    mock_client_class.return_value = mock_client
    suggestions = [
        MealSuggestion(name="Test Meal", match_score=match_score),
    ]
    mock_run_async.return_value = suggestions

    runner = CliRunner()
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    if expected_display:
        assert expected_display in result.stdout
    else:
        # If score is None, "Match score:" should not appear
        assert "Match score:" not in result.stdout or "None" not in result.stdout
