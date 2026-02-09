"""Tests for safety commands."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.safety import app
from fcp_cli.services.fcp import FcpConnectionError, FcpServerError

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCheckRecallsCommand:
    """Test recalls command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_no_recalls_found(self, mock_client_class, runner):
        """Test recalls with no recalls found."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {"recalls": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "apple", "banana"])

        assert result.exit_code == 0
        assert "No recalls found" in result.stdout
        mock_client.check_food_recalls.assert_called_once_with(["apple", "banana"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_with_results(self, mock_client_class, runner):
        """Test recalls with results found."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {
            "recalls": [
                {
                    "title": "Romaine Lettuce Recall",
                    "reason": "E. coli contamination",
                    "date": "2026-02-01",
                },
                {
                    "product": "Organic Spinach",
                    "description": "Listeria concerns",
                    "recall_date": "2026-01-28",
                },
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "lettuce", "spinach"])

        assert result.exit_code == 0
        assert "Romaine Lettuce Recall" in result.stdout
        assert "E. coli contamination" in result.stdout
        assert "2026-02-01" in result.stdout
        assert "Organic Spinach" in result.stdout
        assert "Listeria concerns" in result.stdout
        assert "2026-01-28" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_with_minimal_data(self, mock_client_class, runner):
        """Test recalls with minimal recall data."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {
            "recalls": [
                {
                    # Missing title/product, reason/description, date
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "test"])

        assert result.exit_code == 0
        assert "Unknown" in result.stdout
        assert "No details" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_connection_error(self, mock_client_class, runner):
        """Test recalls with connection error."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.side_effect = FcpConnectionError("Connection failed")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "apple"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "Is the FCP server running?" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_server_error(self, mock_client_class, runner):
        """Test recalls with server error."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.side_effect = FcpServerError("Server error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "apple"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_generic_error(self, mock_client_class, runner):
        """Test recalls with generic error."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.side_effect = Exception("Unexpected error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "apple"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_single_item(self, mock_client_class, runner):
        """Test recalls with single food item."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {"recalls": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "milk"])

        assert result.exit_code == 0
        mock_client.check_food_recalls.assert_called_once_with(["milk"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_multiple_items(self, mock_client_class, runner):
        """Test recalls with multiple food items."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {"recalls": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "milk", "eggs", "cheese"])

        assert result.exit_code == 0
        mock_client.check_food_recalls.assert_called_once_with(["milk", "eggs", "cheese"])


class TestCheckInteractionsCommand:
    """Test interactions command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_no_interactions_found(self, mock_client_class, runner):
        """Test interactions with no interactions found."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {"interactions": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "grapefruit", "--medication", "statins"],
        )

        assert result.exit_code == 0
        assert "No interactions found" in result.stdout
        mock_client.check_drug_interactions.assert_called_once_with(["grapefruit"], ["statins"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_with_results(self, mock_client_class, runner):
        """Test interactions with results found."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {
            "interactions": [
                {
                    "food": "Grapefruit",
                    "medication": "Atorvastatin",
                    "severity": "High",
                    "description": "Increases drug concentration",
                },
                {
                    "food": "Spinach",
                    "medication": "Warfarin",
                    "severity": "Moderate",
                    "details": "May reduce effectiveness",
                },
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "interactions",
                "grapefruit",
                "spinach",
                "--medication",
                "atorvastatin",
                "--medication",
                "warfarin",
            ],
        )

        assert result.exit_code == 0
        assert "Grapefruit" in result.stdout
        assert "Atorvastatin" in result.stdout
        assert "High" in result.stdout
        assert "Increases drug concentration" in result.stdout
        assert "Spinach" in result.stdout
        assert "Warfarin" in result.stdout
        assert "Moderate" in result.stdout
        assert "May reduce effectiveness" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_with_minimal_data(self, mock_client_class, runner):
        """Test interactions with minimal interaction data."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {
            "interactions": [
                {
                    # Missing all optional fields
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "test", "--medication", "test"],
        )

        assert result.exit_code == 0
        # Should display default values (dashes)
        assert result.stdout.count("-") > 0

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_connection_error(self, mock_client_class, runner):
        """Test interactions with connection error."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.side_effect = FcpConnectionError("Connection failed")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "grapefruit", "--medication", "statins"],
        )

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "Is the FCP server running?" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_server_error(self, mock_client_class, runner):
        """Test interactions with server error."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.side_effect = FcpServerError("Server error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "grapefruit", "--medication", "statins"],
        )

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_generic_error(self, mock_client_class, runner):
        """Test interactions with generic error."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.side_effect = Exception("Unexpected error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "grapefruit", "--medication", "statins"],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_single_medication(self, mock_client_class, runner):
        """Test interactions with single medication."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {"interactions": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "grapefruit", "-m", "statins"],
        )

        assert result.exit_code == 0
        mock_client.check_drug_interactions.assert_called_once_with(["grapefruit"], ["statins"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_multiple_medications(self, mock_client_class, runner):
        """Test interactions with multiple medications."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {"interactions": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "interactions",
                "grapefruit",
                "spinach",
                "-m",
                "warfarin",
                "-m",
                "aspirin",
            ],
        )

        assert result.exit_code == 0
        mock_client.check_drug_interactions.assert_called_once_with(["grapefruit", "spinach"], ["warfarin", "aspirin"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_description_fallback(self, mock_client_class, runner):
        """Test interactions using 'details' field when 'description' is missing."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {
            "interactions": [
                {
                    "food": "Test",
                    "medication": "Test Med",
                    "severity": "Low",
                    "details": "Detail text without description",
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["interactions", "test", "-m", "test"],
        )

        assert result.exit_code == 0
        assert "Detail text without description" in result.stdout


class TestCheckAllergensCommand:
    """Test allergens command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_no_alerts_found(self, mock_client_class, runner):
        """Test allergens with no alerts found."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.return_value = {"alerts": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["allergens", "bread", "--allergy", "peanuts"],
        )

        assert result.exit_code == 0
        assert "No allergen alerts found" in result.stdout
        mock_client.check_allergen_alerts.assert_called_once_with(["bread"], ["peanuts"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_with_results(self, mock_client_class, runner):
        """Test allergens with results found."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.return_value = {
            "alerts": [
                {
                    "food": "Peanut Butter",
                    "allergen": "Peanuts",
                    "confidence": "High",
                },
                {
                    "food": "Bread",
                    "allergen": "Gluten",
                    "confidence": "Confirmed",
                },
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "allergens",
                "peanut-butter",
                "bread",
                "--allergy",
                "peanuts",
                "--allergy",
                "gluten",
            ],
        )

        assert result.exit_code == 0
        assert "Peanut Butter" in result.stdout
        assert "Peanuts" in result.stdout
        assert "High" in result.stdout
        assert "Bread" in result.stdout
        assert "Gluten" in result.stdout
        assert "Confirmed" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_with_minimal_data(self, mock_client_class, runner):
        """Test allergens with minimal alert data."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.return_value = {
            "alerts": [
                {
                    # Missing all optional fields
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["allergens", "test", "--allergy", "test"],
        )

        assert result.exit_code == 0
        assert "Unknown" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_connection_error(self, mock_client_class, runner):
        """Test allergens with connection error."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.side_effect = FcpConnectionError("Connection failed")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["allergens", "bread", "--allergy", "peanuts"],
        )

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "Is the FCP server running?" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_server_error(self, mock_client_class, runner):
        """Test allergens with server error."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.side_effect = FcpServerError("Server error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["allergens", "bread", "--allergy", "peanuts"],
        )

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_generic_error(self, mock_client_class, runner):
        """Test allergens with generic error."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.side_effect = Exception("Unexpected error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["allergens", "bread", "--allergy", "peanuts"],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_single_allergy(self, mock_client_class, runner):
        """Test allergens with single allergy."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.return_value = {"alerts": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["allergens", "bread", "-a", "gluten"],
        )

        assert result.exit_code == 0
        mock_client.check_allergen_alerts.assert_called_once_with(["bread"], ["gluten"])

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_multiple_allergies(self, mock_client_class, runner):
        """Test allergens with multiple allergies."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.return_value = {"alerts": []}
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "allergens",
                "sandwich",
                "cookies",
                "-a",
                "peanuts",
                "-a",
                "dairy",
                "-a",
                "gluten",
            ],
        )

        assert result.exit_code == 0
        mock_client.check_allergen_alerts.assert_called_once_with(
            ["sandwich", "cookies"], ["peanuts", "dairy", "gluten"]
        )


class TestCheckRestaurantCommand:
    """Test restaurant command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_basic_info(self, mock_client_class, runner):
        """Test restaurant with basic information."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": "Joe's Diner",
            "status": "Pass",
            "last_inspection_date": "2026-01-15",
            "inspection_score": "95",
            "violations": [],
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Joe's Diner", "New York"])

        assert result.exit_code == 0
        assert "Joe's Diner" in result.stdout
        assert "Pass" in result.stdout
        assert "2026-01-15" in result.stdout
        assert "95" in result.stdout
        mock_client.get_restaurant_safety_info.assert_called_once_with("Joe's Diner", "New York")

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_with_violations(self, mock_client_class, runner):
        """Test restaurant with violations."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": "Risky Restaurant",
            "status": "Conditional Pass",
            "last_inspection_date": "2026-02-01",
            "inspection_score": "78",
            "violations": [
                {
                    "description": "Food not properly stored",
                    "is_critical": True,
                },
                {
                    "description": "Minor cleaning issue",
                    "is_critical": False,
                },
            ],
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Risky Restaurant", "Boston"])

        assert result.exit_code == 0
        assert "Risky Restaurant" in result.stdout
        assert "Conditional Pass" in result.stdout
        assert "78" in result.stdout
        assert "Food not properly stored" in result.stdout
        assert "CRITICAL" in result.stdout
        assert "Minor cleaning issue" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_with_string_violations(self, mock_client_class, runner):
        """Test restaurant with violations as strings."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": "Simple Cafe",
            "status": "Pass",
            "last_inspection_date": "2026-01-20",
            "inspection_score": "88",
            "violations": [
                "Temperature violation",
                "Handwashing station issue",
            ],
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Simple Cafe", "Chicago"])

        assert result.exit_code == 0
        assert "Simple Cafe" in result.stdout
        assert "Temperature violation" in result.stdout
        assert "Handwashing station issue" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_minimal_data(self, mock_client_class, runner):
        """Test restaurant with minimal data."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Mystery Place", "Unknown"])

        assert result.exit_code == 0
        assert "Mystery Place" in result.stdout
        assert "Unknown" in result.stdout
        assert "N/A" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_no_violations(self, mock_client_class, runner):
        """Test restaurant with no violations."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": "Clean Kitchen",
            "status": "Pass",
            "last_inspection_date": "2026-02-05",
            "inspection_score": "100",
            "violations": [],
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Clean Kitchen", "Seattle"])

        assert result.exit_code == 0
        assert "Clean Kitchen" in result.stdout
        assert "100" in result.stdout
        # Should not have violations section
        assert "Violations:" not in result.stdout or result.stdout.count("Violations:") == 0

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_connection_error(self, mock_client_class, runner):
        """Test restaurant with connection error."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.side_effect = FcpConnectionError("Connection failed")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Test", "Location"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "Is the FCP server running?" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_server_error(self, mock_client_class, runner):
        """Test restaurant with server error."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.side_effect = FcpServerError("Server error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Test", "Location"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_generic_error(self, mock_client_class, runner):
        """Test restaurant with generic error."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.side_effect = Exception("Unexpected error")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Test", "Location"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_name_with_spaces(self, mock_client_class, runner):
        """Test restaurant with spaces in name."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": "The Grand Palace Restaurant",
            "status": "Pass",
            "last_inspection_date": "2026-01-10",
            "inspection_score": "92",
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "The Grand Palace Restaurant", "Los Angeles"])

        assert result.exit_code == 0
        assert "The Grand Palace Restaurant" in result.stdout
        mock_client.get_restaurant_safety_info.assert_called_once_with("The Grand Palace Restaurant", "Los Angeles")

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_violation_with_dict_no_description(self, mock_client_class, runner):
        """Test restaurant with violation dict but no description field."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": "Test Restaurant",
            "status": "Pass",
            "last_inspection_date": "2026-02-01",
            "inspection_score": "85",
            "violations": [
                {
                    "code": "V123",
                    "is_critical": False,
                    # No description field
                }
            ],
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Test Restaurant", "Test City"])

        assert result.exit_code == 0
        # Should convert dict to string when no description available
        assert "code" in result.stdout or "V123" in result.stdout


class TestSafetyEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_empty_result_dict(self, mock_client_class, runner):
        """Test recalls with empty result dictionary."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "apple"])

        assert result.exit_code == 0
        assert "No recalls found" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_interactions_empty_result_dict(self, mock_client_class, runner):
        """Test interactions with empty result dictionary."""
        mock_client = AsyncMock()
        mock_client.check_drug_interactions.return_value = {}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["interactions", "food", "--medication", "drug"])

        assert result.exit_code == 0
        assert "No interactions found" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_allergens_empty_result_dict(self, mock_client_class, runner):
        """Test allergens with empty result dictionary."""
        mock_client = AsyncMock()
        mock_client.check_allergen_alerts.return_value = {}
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["allergens", "food", "--allergy", "peanuts"])

        assert result.exit_code == 0
        assert "No allergen alerts found" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_recalls_with_special_characters(self, mock_client_class, runner):
        """Test recalls with special characters in food names."""
        mock_client = AsyncMock()
        mock_client.check_food_recalls.return_value = {
            "recalls": [
                {
                    "title": "Café's Special Bread",
                    "reason": "Contains nuts & dairy",
                    "date": "2026-02-01",
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["recalls", "Café's Bread"])

        assert result.exit_code == 0
        assert "Café's Special Bread" in result.stdout
        assert "nuts & dairy" in result.stdout

    @patch("fcp_cli.commands.safety.FcpClient")
    def test_restaurant_with_none_values(self, mock_client_class, runner):
        """Test restaurant with None values in response."""
        mock_client = AsyncMock()
        mock_client.get_restaurant_safety_info.return_value = {
            "restaurant_name": None,
            "status": None,
            "last_inspection_date": None,
            "inspection_score": None,
            "violations": None,
        }
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["restaurant", "Test", "Location"])

        # Should handle None values gracefully
        assert result.exit_code == 0


@pytest.mark.parametrize(
    "food_items,expected_count",
    [
        (["apple"], 1),
        (["apple", "banana"], 2),
        (["apple", "banana", "orange", "grape"], 4),
    ],
)
@patch("fcp_cli.commands.safety.FcpClient")
def test_recalls_various_food_counts(mock_client_class, food_items, expected_count):
    """Test recalls with various numbers of food items."""
    mock_client = AsyncMock()
    mock_client.check_food_recalls.return_value = {"recalls": []}
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(app, ["recalls"] + food_items)

    assert result.exit_code == 0
    call_args = mock_client.check_food_recalls.call_args[0][0]
    assert len(call_args) == expected_count
    assert call_args == food_items


@pytest.mark.parametrize(
    "severity",
    ["Low", "Moderate", "High", "Severe", "Critical"],
)
@patch("fcp_cli.commands.safety.FcpClient")
def test_interactions_severity_levels(mock_client_class, severity):
    """Test interactions with different severity levels."""
    mock_client = AsyncMock()
    mock_client.check_drug_interactions.return_value = {
        "interactions": [
            {
                "food": "Test Food",
                "medication": "Test Med",
                "severity": severity,
                "description": "Test interaction",
            }
        ]
    }
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(app, ["interactions", "food", "-m", "med"])

    assert result.exit_code == 0
    assert severity in result.stdout


@pytest.mark.parametrize(
    "confidence",
    ["Low", "Medium", "High", "Confirmed", "Unknown"],
)
@patch("fcp_cli.commands.safety.FcpClient")
def test_allergens_confidence_levels(mock_client_class, confidence):
    """Test allergens with different confidence levels."""
    mock_client = AsyncMock()
    mock_client.check_allergen_alerts.return_value = {
        "alerts": [
            {
                "food": "Test Food",
                "allergen": "Test Allergen",
                "confidence": confidence,
            }
        ]
    }
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(app, ["allergens", "food", "-a", "allergen"])

    assert result.exit_code == 0
    assert confidence in result.stdout
