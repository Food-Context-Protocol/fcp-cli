"""Tests for taste commands."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.taste import app
from fcp_cli.services import FcpConnectionError, FcpServerError, TasteBuddyResult

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCheckCompatibilityCommand:
    """Test taste check command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def safe_compliant_result(self):
        """Safe and compliant taste buddy result."""
        return TasteBuddyResult(
            is_safe=True,
            is_compliant=True,
            detected_allergens=None,
            diet_conflicts=None,
            warnings=None,
            modifications=None,
        )

    @pytest.fixture
    def safe_with_conflicts_result(self):
        """Safe but has diet conflicts result."""
        return TasteBuddyResult(
            is_safe=True,
            is_compliant=False,
            detected_allergens=None,
            diet_conflicts=["Contains dairy", "Not vegan"],
            warnings=["High sodium content"],
            modifications=["Use plant-based cheese", "Reduce salt"],
        )

    @pytest.fixture
    def unsafe_result(self):
        """Unsafe result with allergens."""
        return TasteBuddyResult(
            is_safe=False,
            is_compliant=False,
            detected_allergens=["peanuts", "tree nuts"],
            diet_conflicts=["Contains gluten"],
            warnings=["Severe allergy risk"],
            modifications=None,
        )

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_minimal(self, mock_run_async, mock_client_class, runner, safe_compliant_result):
        """Test check with minimal arguments."""
        mock_run_async.return_value = safe_compliant_result

        result = runner.invoke(app, ["check", "Pizza"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "Safe & Compliant" in result.stdout
        mock_run_async.assert_called_once()

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_with_ingredients(self, mock_run_async, mock_client_class, runner, safe_compliant_result):
        """Test check with specific ingredients."""
        mock_run_async.return_value = safe_compliant_result

        result = runner.invoke(
            app,
            ["check", "Pizza", "--ingredient", "cheese", "--ingredient", "tomato"],
        )

        assert result.exit_code == 0
        assert "Pizza" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_with_allergies(self, mock_run_async, mock_client_class, runner, unsafe_result):
        """Test check with user allergies."""
        mock_run_async.return_value = unsafe_result

        result = runner.invoke(
            app,
            ["check", "Pad Thai", "--allergy", "peanuts", "--allergy", "shellfish"],
        )

        assert result.exit_code == 0
        assert "Not Safe" in result.stdout
        assert "peanuts" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_with_diets(self, mock_run_async, mock_client_class, runner, safe_with_conflicts_result):
        """Test check with dietary restrictions."""
        mock_run_async.return_value = safe_with_conflicts_result

        result = runner.invoke(
            app,
            ["check", "Cheese Pizza", "--diet", "vegan", "--diet", "low-sodium"],
        )

        assert result.exit_code == 0
        assert "diet conflicts" in result.stdout.lower()
        assert "dairy" in result.stdout.lower()

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_all_options(self, mock_run_async, mock_client_class, runner, safe_with_conflicts_result):
        """Test check with all options."""
        mock_run_async.return_value = safe_with_conflicts_result

        result = runner.invoke(
            app,
            [
                "check",
                "Veggie Burger",
                "--ingredient",
                "beans",
                "--ingredient",
                "cheese",
                "--allergy",
                "soy",
                "--diet",
                "vegan",
            ],
        )

        assert result.exit_code == 0
        assert "Veggie Burger" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_with_warnings(self, mock_run_async, mock_client_class, runner, safe_with_conflicts_result):
        """Test check displays warnings."""
        mock_run_async.return_value = safe_with_conflicts_result

        result = runner.invoke(app, ["check", "Salty Soup"])

        assert result.exit_code == 0
        assert "Warnings:" in result.stdout
        assert "High sodium" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_with_modifications(self, mock_run_async, mock_client_class, runner, safe_with_conflicts_result):
        """Test check displays suggested modifications."""
        mock_run_async.return_value = safe_with_conflicts_result

        result = runner.invoke(app, ["check", "Mac and Cheese"])

        assert result.exit_code == 0
        assert "Suggested Modifications:" in result.stdout
        assert "plant-based cheese" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_detected_allergens(self, mock_run_async, mock_client_class, runner, unsafe_result):
        """Test check displays detected allergens."""
        mock_run_async.return_value = unsafe_result

        result = runner.invoke(app, ["check", "Peanut Butter Cookies"])

        assert result.exit_code == 0
        assert "Detected Allergens:" in result.stdout
        assert "peanuts" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test check with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["check", "Pizza"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_check_server_error(self, mock_run_async, mock_client_class, runner):
        """Test check with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["check", "Pizza"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestGetPairingsCommand:
    """Test taste pairings command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def dict_pairings(self):
        """Pairings in dict format."""
        return [
            {
                "name": "Lemon",
                "flavor_profile": "Citrus, Bright",
                "reason": "Complements richness with acidity",
            },
            {
                "name": "Thyme",
                "flavor_profile": "Earthy, Herbal",
                "reason": "Classic aromatic pairing",
            },
            {
                "name": "Garlic",
                "flavor_profile": "Pungent, Savory",
                "reason": "Enhances savory flavors",
            },
        ]

    @pytest.fixture
    def string_pairings(self):
        """Pairings in simple string format."""
        return ["Lemon", "Thyme", "Garlic", "Butter", "White Wine"]

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_dict_format(self, mock_run_async, mock_client_class, runner, dict_pairings):
        """Test pairings with dict format response."""
        mock_run_async.return_value = dict_pairings

        result = runner.invoke(app, ["pairings", "Chicken"])

        assert result.exit_code == 0
        assert "Chicken" in result.stdout
        assert "Lemon" in result.stdout
        assert "Thyme" in result.stdout
        assert "Citrus" in result.stdout
        assert "Complements richness" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_string_format(self, mock_run_async, mock_client_class, runner, string_pairings):
        """Test pairings with string format response."""
        mock_run_async.return_value = string_pairings

        result = runner.invoke(app, ["pairings", "Salmon"])

        assert result.exit_code == 0
        assert "Salmon" in result.stdout
        assert "Lemon" in result.stdout
        assert "Garlic" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_with_count(self, mock_run_async, mock_client_class, runner, dict_pairings):
        """Test pairings with custom count."""
        mock_run_async.return_value = dict_pairings[:3]

        result = runner.invoke(app, ["pairings", "Beef", "--count", "3"])

        assert result.exit_code == 0
        assert "Beef" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_no_results(self, mock_run_async, mock_client_class, runner):
        """Test pairings with no results."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["pairings", "UnknownIngredient"])

        assert result.exit_code == 0
        assert "No pairings found" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_partial_dict_data(self, mock_run_async, mock_client_class, runner):
        """Test pairings with partial dict data (missing some fields)."""
        partial_pairings = [
            {"name": "Lemon"},
            {"name": "Thyme", "flavor_profile": "Earthy"},
            {"name": "Garlic", "reason": "Enhances flavor"},
        ]
        mock_run_async.return_value = partial_pairings

        result = runner.invoke(app, ["pairings", "Fish"])

        assert result.exit_code == 0
        assert "Lemon" in result.stdout
        assert "Thyme" in result.stdout
        assert "Garlic" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test pairings with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["pairings", "Tomato"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.taste.FcpClient")
    @patch("fcp_cli.commands.taste.run_async")
    def test_pairings_server_error(self, mock_run_async, mock_client_class, runner):
        """Test pairings with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["pairings", "Basil"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "dish_name,expected_status",
    [
        ("Gluten-Free Pizza", "Safe"),
        ("Vegan Burger", "Safe"),
        ("Peanut Butter Cookies", "Not Safe"),
    ],
)
@patch("fcp_cli.commands.taste.FcpClient")
@patch("fcp_cli.commands.taste.run_async")
def test_check_various_dishes(mock_run_async, mock_client_class, dish_name, expected_status):
    """Test checking various dishes."""
    is_safe = expected_status == "Safe"
    result = TasteBuddyResult(
        is_safe=is_safe,
        is_compliant=is_safe,
        detected_allergens=["peanuts"] if not is_safe else None,
    )
    mock_run_async.return_value = result

    runner = CliRunner()
    cli_result = runner.invoke(app, ["check", dish_name])

    assert cli_result.exit_code == 0
    assert expected_status in cli_result.stdout


@pytest.mark.parametrize(
    "ingredient,count",
    [
        ("Chicken", 5),
        ("Salmon", 3),
        ("Tomato", 10),
    ],
)
@patch("fcp_cli.commands.taste.FcpClient")
@patch("fcp_cli.commands.taste.run_async")
def test_pairings_various_counts(mock_run_async, mock_client_class, ingredient, count):
    """Test pairings with various counts."""
    pairings = [f"Pairing {i}" for i in range(count)]
    mock_run_async.return_value = pairings

    runner = CliRunner()
    result = runner.invoke(app, ["pairings", ingredient, "--count", str(count)])

    assert result.exit_code == 0
    assert ingredient in result.stdout
