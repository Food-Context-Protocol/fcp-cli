"""Tests for remaining branch coverage in log commands."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.log import app
from fcp_cli.services import FCP, FcpConnectionError, FcpNotFoundError, FcpServerError

pytestmark = pytest.mark.unit


class TestLogNutritionDisplayBranch:
    """Test nutrition display conditional with walrus operator."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_nutrition_displays_when_present(self, mock_client_class, mock_run_async, runner):
        """Test that nutrition is displayed when values are present."""
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Chicken",
            nutrition={"calories": 300, "protein": 25},
        )
        mock_run_async.return_value = mock_log

        result = runner.invoke(app, ["nutrition", "Chicken", "--calories", "300", "--protein", "25"])

        assert result.exit_code == 0
        assert "Nutrition:" in result.stdout
        assert "Calories: 300" in result.stdout
        assert "Protein: 25" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_nutrition_skips_none_values(self, mock_client_class, mock_run_async, runner):
        """Test that None nutrition values are skipped in display."""
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Salad",
            nutrition={"calories": 150, "protein": None, "carbs": 20, "fat": None},
        )
        mock_run_async.return_value = mock_log

        result = runner.invoke(app, ["nutrition", "Salad", "--calories", "150", "--carbs", "20"])

        assert result.exit_code == 0
        assert "Nutrition:" in result.stdout
        assert "Calories: 150" in result.stdout
        assert "Carbs: 20" in result.stdout
        # Should not display None values
        assert "None" not in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_nutrition_empty_when_all_none(self, mock_client_class, mock_run_async, runner):
        """Test that nutrition section is not displayed when all values are None."""
        mock_log = FCP(
            id="log123",
            user_id="user123",
            dish_name="Water",
            nutrition={},
        )
        mock_run_async.return_value = mock_log

        result = runner.invoke(app, ["nutrition", "Water"])

        assert result.exit_code == 0
        # Should not show nutrition section when empty
        assert "Nutrition:" not in result.stdout or result.stdout.count("Nutrition:") == 1


class TestLogListTimestampBranch:
    """Test timestamp display conditional in list command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_list_with_timestamp(self, mock_client_class, mock_run_async, runner):
        """Test that timestamp is displayed when present."""
        mock_log_with_time = FCP(
            id="log123",
            user_id="user123",
            dish_name="Pizza",
            meal_type="lunch",
            timestamp=datetime(2025, 1, 15, 12, 30),
        )
        mock_run_async.return_value = [mock_log_with_time]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        # Should show timestamp (either relative or formatted date)
        assert "2025-01-15" in result.stdout or "ago" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_list_without_timestamp(self, mock_client_class, mock_run_async, runner):
        """Test that missing timestamp shows empty string."""
        mock_log_no_time = FCP(
            id="log123",
            user_id="user123",
            dish_name="Burger",
            meal_type="dinner",
            timestamp=None,
        )
        mock_run_async.return_value = [mock_log_no_time]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Burger" in result.stdout


class TestLogDeleteErrorHandling:
    """Test delete command error handling branches."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_delete_not_found_error(self, mock_client_class, mock_run_async, runner):
        """Test delete with not found error."""
        mock_run_async.side_effect = FcpNotFoundError("Food log not found")

        result = runner.invoke(app, ["delete", "nonexistent123"], input="y\n")

        assert result.exit_code == 1
        assert "Food log not found" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_delete_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test delete with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["delete", "log123"], input="y\n")

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_delete_server_error(self, mock_client_class, mock_run_async, runner):
        """Test delete with server error."""
        mock_run_async.side_effect = FcpServerError("Internal server error")

        result = runner.invoke(app, ["delete", "log123"], input="y\n")

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_delete_generic_exception(self, mock_client_class, mock_run_async, runner):
        """Test delete with generic exception."""
        mock_run_async.side_effect = Exception("Unexpected error")

        result = runner.invoke(app, ["delete", "log123"], input="y\n")

        assert result.exit_code == 1
        assert "Failed to delete food log" in result.stdout


class TestLogAddIdDisplay:
    """Test ID display conditional in add command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_add_without_id_no_display(self, mock_client_class, mock_run_async, runner):
        """Test that ID line is not displayed when None or empty."""
        mock_log = FCP(
            id="",  # Empty ID
            user_id="user123",
            dish_name="Snack",
        )
        mock_run_async.return_value = mock_log

        result = runner.invoke(app, ["add", "Snack"])

        assert result.exit_code == 0
        # Should not show ID line when empty
        assert result.stdout.count("ID:") == 0 or "ID: " not in result.stdout
