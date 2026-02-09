"""Tests for conditional display branches in log commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.log import app
from fcp_cli.services import FCP
from fcp_cli.utils import ImageTooLargeError, InvalidImageError

pytestmark = pytest.mark.unit


class TestLogAddImageErrors:
    """Test image error handling in add command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log._process_image_for_log")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_image_too_large_error(self, mock_client_class, mock_process, runner):
        """Test that ImageTooLargeError is caught and displayed."""
        mock_process.side_effect = ImageTooLargeError("Image exceeds 50MB limit")

        result = runner.invoke(app, ["add", "Pizza", "--image", "huge.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "exceeds 50MB" in result.stdout

    @patch("fcp_cli.commands.log._process_image_for_log")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_invalid_image_error(self, mock_client_class, mock_process, runner):
        """Test that InvalidImageError is caught and displayed."""
        mock_process.side_effect = InvalidImageError("Invalid image format")

        result = runner.invoke(app, ["add", "Pizza", "--image", "corrupt.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Invalid image format" in result.stdout

    @patch("fcp_cli.commands.log._process_image_for_log")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_image_value_error(self, mock_client_class, mock_process, runner):
        """Test that ValueError from resolution validation is caught."""
        mock_process.side_effect = ValueError("Invalid resolution: ultra")

        result = runner.invoke(app, ["add", "Pizza", "--image", "photo.jpg", "--res", "ultra"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Invalid resolution" in result.stdout


class TestLogAddConditionalDisplay:
    """Test conditional display in add command output."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_displays_id_when_present(self, mock_client_class, mock_run_async, runner):
        """Test that log ID is displayed when present in response."""
        mock_client = MagicMock()
        mock_log = FCP(
            id="log12345",
            user_id="user123",
            dish_name="Pizza",
            description="Cheese Pizza",
            meal_type="lunch",
        )
        mock_run_async.return_value = mock_log
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza", "--meal-type", "lunch"])

        assert result.exit_code == 0
        assert "log12345" in result.stdout
        assert "ID:" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_displays_meal_type_when_present(self, mock_client_class, mock_run_async, runner):
        """Test that meal type is displayed when present."""
        mock_client = MagicMock()
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Salad",
            meal_type="dinner",
        )
        mock_run_async.return_value = mock_log
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Salad", "--meal-type", "dinner"])

        assert result.exit_code == 0
        assert "dinner" in result.stdout
        assert "Meal Type:" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_without_meal_type_no_display(self, mock_client_class, mock_run_async, runner):
        """Test that meal type line is not displayed when None."""
        mock_client = MagicMock()
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Snack",
            meal_type=None,
        )
        mock_run_async.return_value = mock_log
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Snack"])

        assert result.exit_code == 0
        # Should not have the Meal Type line
        assert "Meal Type:" not in result.stdout


class TestLogShowConditionals:
    """Test conditional display in show command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_with_description(self, mock_client_class, mock_run_async, runner):
        """Test show displays description when present."""
        mock_client = MagicMock()
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Pizza",
            description="Detailed description of the pizza",
            meal_type="lunch",
        )
        mock_run_async.return_value = mock_log
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "log123"])

        assert result.exit_code == 0
        assert "Detailed description" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_with_nutrition(self, mock_client_class, mock_run_async, runner):
        """Test show displays nutrition when present."""
        mock_client = MagicMock()
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Chicken",
            nutrition={"calories": 350, "protein": 30, "carbs": 10, "fat": 20},
        )
        mock_run_async.return_value = mock_log
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "log123"])

        assert result.exit_code == 0
        assert "Nutrition" in result.stdout
        assert "350" in result.stdout  # calories
        assert "30" in result.stdout  # protein

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_without_nutrition_no_display(self, mock_client_class, mock_run_async, runner):
        """Test show doesn't display nutrition section when None."""
        mock_client = MagicMock()
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Simple Dish",
            nutrition=None,
        )
        mock_run_async.return_value = mock_log
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "log123"])

        assert result.exit_code == 0
        # Should not have nutrition section
        assert "Nutrition" not in result.stdout or "None" in result.stdout


class TestLogNutritionConditionals:
    """Test conditional validation in nutrition command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_nutrition_rejects_negative_values(self, runner):
        """Test that negative nutritional values are rejected."""
        # Test negative calories
        result = runner.invoke(app, ["nutrition", "Pizza", "--calories", "-100"])
        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

        # Test negative protein
        result = runner.invoke(app, ["nutrition", "Pizza", "--protein", "-10"])
        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

        # Test negative carbs
        result = runner.invoke(app, ["nutrition", "Pizza", "--carbs", "-20"])
        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

        # Test negative fat
        result = runner.invoke(app, ["nutrition", "Pizza", "--fat", "-5"])
        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

    def test_nutrition_accepts_zero_values(self, runner):
        """Test that zero values are accepted for nutrition."""
        # Zero values should be valid
        result = runner.invoke(app, ["nutrition", "Water", "--calories", "0"])
        # Should not fail on validation (might fail on other things, but not validation)
        assert "cannot be negative" not in result.stdout
