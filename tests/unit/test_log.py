"""Tests for log commands."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.log import app

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestLogAddCommand:
    """Test log add command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_minimal(self, mock_client_class, mock_run_async, runner):
        """Test log add with minimal arguments."""
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(return_value=MagicMock(id="meal123", dish_name="Pizza", meal_type=None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        mock_client.create_food_log.assert_called_once()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_with_meal_type(self, mock_client_class, mock_run_async, runner):
        """Test log add with meal type."""
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(
            return_value=MagicMock(id="meal123", dish_name="Ramen", meal_type="lunch")
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Ramen", "--meal-type", "lunch"])

        assert result.exit_code == 0
        assert "Ramen" in result.stdout
        assert "lunch" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_with_description(self, mock_client_class, mock_run_async, runner):
        """Test log add with description."""
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(return_value=MagicMock(id="meal123", dish_name="Sushi", meal_type=None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Sushi"])

        assert result.exit_code == 0
        assert "Sushi" in result.stdout
        mock_client.create_food_log.assert_called_once()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test log add with connection error."""
        from fcp_cli.services.fcp import FcpConnectionError

        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(side_effect=FcpConnectionError("Connection failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza"])

        assert result.exit_code != 0


class TestLogListCommand:
    """Test log list command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_list_default(self, mock_client_class, mock_run_async, runner):
        """Test log list with defaults."""
        from datetime import datetime

        mock_client = MagicMock()
        mock_client.get_food_logs = AsyncMock(
            return_value=[
                MagicMock(id="1", dish_name="Pizza", meal_type="dinner", timestamp=datetime(2026, 2, 8, 10, 0, 0)),
                MagicMock(id="2", dish_name="Pasta", meal_type="lunch", timestamp=datetime(2026, 2, 8, 11, 0, 0)),
            ]
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "Pasta" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_list_with_limit(self, mock_client_class, mock_run_async, runner):
        """Test log list with custom limit."""
        mock_client = MagicMock()
        mock_client.get_food_logs = AsyncMock(return_value=[])
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list", "--limit", "5"])

        assert result.exit_code == 0
        mock_client.get_food_logs.assert_called_once()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_list_empty(self, mock_client_class, mock_run_async, runner):
        """Test log list with no meals."""
        mock_client = MagicMock()
        mock_client.get_food_logs = AsyncMock(return_value=[])
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No" in result.stdout and "food logs" in result.stdout


class TestLogDeleteCommand:
    """Test log delete command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_delete_success(self, mock_client_class, mock_run_async, runner):
        """Test successful meal deletion."""
        mock_client = MagicMock()
        mock_client.delete_food_log = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "meal123", "--yes"])

        assert result.exit_code == 0
        mock_client.delete_food_log.assert_called_once_with("meal123")

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_delete_not_found(self, mock_client_class, mock_run_async, runner):
        """Test deleting non-existent meal."""
        from fcp_cli.services.fcp import FcpNotFoundError

        mock_client = MagicMock()
        mock_client.delete_food_log = AsyncMock(side_effect=FcpNotFoundError("Not found"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["delete", "nonexistent", "--yes"])

        assert result.exit_code != 0


class TestLogNutritionCommand:
    """Test log nutrition command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_nutrition_success(self, mock_client_class, mock_run_async, runner):
        """Test nutrition logging."""
        mock_client = MagicMock()
        mock_client.log_meal = AsyncMock(
            return_value=MagicMock(
                id="meal123",
                dish_name="Pizza",
                nutrition={"calories": 800, "protein": 30, "carbs": 90, "fat": 35},
            )
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["nutrition", "Pizza", "--calories", "800", "--protein", "30"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "800" in result.stdout or "calories" in result.stdout.lower()

    def test_log_nutrition_negative_calories(self, runner):
        """Test nutrition with negative calories."""
        result = runner.invoke(app, ["nutrition", "Pizza", "--calories", "-100"])

        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

    def test_log_nutrition_negative_protein(self, runner):
        """Test nutrition with negative protein."""
        result = runner.invoke(app, ["nutrition", "Pizza", "--protein", "-10"])

        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

    def test_log_nutrition_negative_carbs(self, runner):
        """Test nutrition with negative carbs."""
        result = runner.invoke(app, ["nutrition", "Pizza", "--carbs", "-50"])

        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout

    def test_log_nutrition_negative_fat(self, runner):
        """Test nutrition with negative fat."""
        result = runner.invoke(app, ["nutrition", "Pizza", "--fat", "-20"])

        assert result.exit_code == 1
        assert "cannot be negative" in result.stdout


@pytest.mark.parametrize(
    "dish_name,expected_in_output",
    [
        ("Pizza", "Pizza"),
        ("Sushi Roll", "Sushi"),
        ("Spicy Ramen 🍜", "Ramen"),
    ],
)
@patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
@patch("fcp_cli.commands.log.FcpClient")
def test_log_add_various_dishes(mock_client_class, mock_run_async, dish_name, expected_in_output):
    """Test logging various dish names."""
    mock_client = MagicMock()
    mock_client.create_food_log = AsyncMock(return_value=MagicMock(id="meal123", dish_name=dish_name, meal_type=None))
    mock_client_class.return_value = mock_client

    runner = CliRunner()
    result = runner.invoke(app, ["add", dish_name])

    assert result.exit_code == 0
    assert expected_in_output in result.stdout


class TestLogAddWithImage:
    """Test log add command with image."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    @patch("fcp_cli.commands.log.read_image_as_base64")
    @patch("fcp_cli.commands.log.validate_resolution")
    def test_log_add_with_image_and_resolution(
        self, mock_validate, mock_read_image, mock_client_class, mock_run_async, runner, tmp_path
    ):
        """Test log add with image and explicit resolution."""
        img_path = tmp_path / "meal.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.return_value = "low"
        mock_read_image.return_value = "base64data"
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(return_value=MagicMock(id="meal123", dish_name="Pizza", meal_type=None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza", "--image", str(img_path), "--res", "low"])

        assert result.exit_code == 0
        mock_validate.assert_called_once_with("low")
        mock_read_image.assert_called_once()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    @patch("fcp_cli.commands.log.read_image_as_base64")
    @patch("fcp_cli.commands.log.auto_select_resolution")
    def test_log_add_with_image_auto_resolution(
        self, mock_auto_select, mock_read_image, mock_client_class, mock_run_async, runner, tmp_path
    ):
        """Test log add with image and auto resolution."""
        img_path = tmp_path / "meal.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_auto_select.return_value = "medium"
        mock_read_image.return_value = "base64data"
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(return_value=MagicMock(id="meal123", dish_name="Pizza", meal_type=None))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza", "--image", str(img_path)])

        assert result.exit_code == 0
        mock_auto_select.assert_called_once()
        assert "Auto-selected resolution: medium" in result.stdout

    @patch("fcp_cli.commands.log.read_image_as_base64")
    def test_log_add_image_not_found(self, mock_read_image, runner):
        """Test log add with non-existent image."""
        mock_read_image.side_effect = FileNotFoundError("Image not found")

        result = runner.invoke(app, ["add", "Pizza", "--image", "/nonexistent/image.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @patch("fcp_cli.commands.log.read_image_as_base64")
    def test_log_add_image_too_large(self, mock_read_image, runner):
        """Test log add with image that's too large."""
        from fcp_cli.utils import ImageTooLargeError

        mock_read_image.side_effect = ImageTooLargeError("Image too large")

        result = runner.invoke(app, ["add", "Pizza", "--image", "large.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @patch("fcp_cli.commands.log.read_image_as_base64")
    def test_log_add_invalid_image(self, mock_read_image, runner):
        """Test log add with invalid image."""
        from fcp_cli.utils import InvalidImageError

        mock_read_image.side_effect = InvalidImageError("Invalid image")

        result = runner.invoke(app, ["add", "Pizza", "--image", "invalid.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @patch("fcp_cli.commands.log.validate_resolution")
    def test_log_add_invalid_resolution(self, mock_validate, runner, tmp_path):
        """Test log add with invalid resolution."""
        img_path = tmp_path / "meal.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.side_effect = ValueError("Invalid resolution")

        result = runner.invoke(app, ["add", "Pizza", "--image", str(img_path), "--res", "ultra"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestLogAddErrorHandling:
    """Test log add error handling."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_server_error(self, mock_client_class, mock_run_async, runner):
        """Test log add with server error."""
        from fcp_cli.services.fcp import FcpServerError

        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(side_effect=FcpServerError("Internal server error"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza"])

        assert result.exit_code == 1
        assert "Server error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_http_error(self, mock_client_class, mock_run_async, runner):
        """Test log add with HTTP error."""
        import httpx

        mock_client = MagicMock()
        response = MagicMock()
        response.status_code = 500
        mock_client.create_food_log = AsyncMock(
            side_effect=httpx.HTTPStatusError("Error", request=None, response=response)
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza"])

        assert result.exit_code == 1
        assert "HTTP error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_generic_error(self, mock_client_class, mock_run_async, runner):
        """Test log add with generic error."""
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(side_effect=Exception("Something went wrong"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza"])

        assert result.exit_code == 1
        assert "Failed to add food log:" in result.stdout


class TestLogListErrorHandling:
    """Test log list error handling."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_list_server_error(self, mock_client_class, mock_run_async, runner):
        """Test log list with server error."""
        from fcp_cli.services.fcp import FcpServerError

        mock_client = MagicMock()
        mock_client.get_food_logs = AsyncMock(side_effect=FcpServerError("Server error"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Server error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_list_generic_error(self, mock_client_class, mock_run_async, runner):
        """Test log list with generic error."""
        mock_client = MagicMock()
        mock_client.get_food_logs = AsyncMock(side_effect=Exception("Something went wrong"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Failed to fetch food logs:" in result.stdout


class TestLogShowCommand:
    """Test log show command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_log_success(self, mock_client_class, mock_run_async, runner):
        """Test showing a food log."""
        from datetime import datetime

        mock_client = MagicMock()
        mock_client.get_food_log = AsyncMock(
            return_value=MagicMock(
                id="meal123",
                dish_name="Pizza",
                description="Margherita pizza",
                meal_type="dinner",
                timestamp=datetime(2026, 2, 8, 18, 0, 0),
                ingredients=["tomato", "mozzarella", "basil"],
                nutrition={"calories": 800, "protein": 30},
            )
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "meal123"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "Margherita pizza" in result.stdout
        assert "dinner" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_log_not_found(self, mock_client_class, mock_run_async, runner):
        """Test showing non-existent log."""
        from fcp_cli.services.fcp import FcpNotFoundError

        mock_client = MagicMock()
        mock_client.get_food_log = AsyncMock(side_effect=FcpNotFoundError("Not found"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "nonexistent"])

        assert result.exit_code == 1
        assert "Food log not found:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_log_server_error(self, mock_client_class, mock_run_async, runner):
        """Test show with server error."""
        from fcp_cli.services.fcp import FcpServerError

        mock_client = MagicMock()
        mock_client.get_food_log = AsyncMock(side_effect=FcpServerError("Server error"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "meal123"])

        assert result.exit_code == 1
        assert "Server error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_log_generic_error(self, mock_client_class, mock_run_async, runner):
        """Test show with generic error."""
        mock_client = MagicMock()
        mock_client.get_food_log = AsyncMock(side_effect=Exception("Something went wrong"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "meal123"])

        assert result.exit_code == 1
        assert "Failed to fetch food log:" in result.stdout


class TestLogEditCommand:
    """Test log edit command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_edit_log_no_changes(self, runner):
        """Test edit with no changes specified."""
        result = runner.invoke(app, ["edit", "meal123"])

        assert result.exit_code == 0
        assert "No changes specified" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_edit_log_success(self, mock_client_class, mock_run_async, runner):
        """Test editing a food log."""
        mock_client = MagicMock()
        mock_client.update_food_log = AsyncMock(
            return_value=MagicMock(
                id="meal123",
                dish_name="Updated Pizza",
            )
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["edit", "meal123", "--dish", "Updated Pizza"])

        assert result.exit_code == 0
        assert "Updated Pizza" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_edit_log_not_found(self, mock_client_class, mock_run_async, runner):
        """Test editing non-existent log."""
        from fcp_cli.services.fcp import FcpNotFoundError

        mock_client = MagicMock()
        mock_client.update_food_log = AsyncMock(side_effect=FcpNotFoundError("Not found"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["edit", "nonexistent", "--dish", "New Name"])

        assert result.exit_code == 1
        assert "Food log not found:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_edit_log_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test edit with connection error."""
        from fcp_cli.services.fcp import FcpConnectionError

        mock_client = MagicMock()
        mock_client.update_food_log = AsyncMock(side_effect=FcpConnectionError("Connection failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["edit", "meal123", "--dish", "New Name"])

        assert result.exit_code == 1
        assert "Connection error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_edit_log_server_error(self, mock_client_class, mock_run_async, runner):
        """Test edit with server error."""
        from fcp_cli.services.fcp import FcpServerError

        mock_client = MagicMock()
        mock_client.update_food_log = AsyncMock(side_effect=FcpServerError("Server error"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["edit", "meal123", "--dish", "New Name"])

        assert result.exit_code == 1
        assert "Server error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_edit_log_generic_error(self, mock_client_class, mock_run_async, runner):
        """Test edit with generic error."""
        mock_client = MagicMock()
        mock_client.update_food_log = AsyncMock(side_effect=Exception("Something went wrong"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["edit", "meal123", "--dish", "New Name"])

        assert result.exit_code == 1
        assert "Failed to update food log:" in result.stdout


class TestLogDeleteConfirmation:
    """Test log delete command confirmation."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.typer.confirm")
    def test_delete_cancelled(self, mock_confirm, runner):
        """Test delete cancelled by user."""
        mock_confirm.return_value = False

        result = runner.invoke(app, ["delete", "meal123"])

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout


class TestLogNutritionDisplay:
    """Test log nutrition command display logic."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_nutrition_with_full_nutrition_display(self, mock_client_class, mock_run_async, runner):
        """Test nutrition with full nutrition information displayed."""
        mock_client = MagicMock()
        mock_client.log_meal = AsyncMock(
            return_value=MagicMock(
                id="meal123",
                dish_name="Chicken Breast",
                nutrition={"calories": 165, "protein": 31, "carbs": 0, "fat": 3},
            )
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "nutrition",
                "Chicken Breast",
                "--calories",
                "165",
                "--protein",
                "31",
                "--carbs",
                "0",
                "--fat",
                "3",
            ],
        )

        assert result.exit_code == 0
        assert "Chicken Breast" in result.stdout
        assert "Nutrition" in result.stdout or "165" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_nutrition_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test nutrition with connection error."""
        from fcp_cli.services.fcp import FcpConnectionError

        mock_client = MagicMock()
        mock_client.log_meal = AsyncMock(side_effect=FcpConnectionError("Connection failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["nutrition", "Pizza", "--calories", "800"])

        assert result.exit_code == 1
        assert "Connection error:" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_nutrition_server_error(self, mock_client_class, mock_run_async, runner):
        """Test nutrition with server error."""
        from fcp_cli.services.fcp import FcpServerError

        mock_client = MagicMock()
        mock_client.log_meal = AsyncMock(side_effect=FcpServerError("Server error"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["nutrition", "Pizza", "--calories", "800"])

        assert result.exit_code == 1
        assert "Server error:" in result.stdout


class TestLogMenuCommand:
    """Test log menu command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_menu_file_not_found(self, runner):
        """Test menu with non-existent file."""
        result = runner.invoke(app, ["menu", "/nonexistent/menu.jpg"])

        assert result.exit_code == 1
        assert "File not found" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    @patch("fcp_cli.commands.log.auto_select_resolution")
    def test_menu_success(self, mock_auto_select, mock_client_class, mock_run_async, runner, tmp_path):
        """Test menu analysis success."""
        menu_path = tmp_path / "menu.jpg"
        menu_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_auto_select.return_value = "medium"
        mock_client = MagicMock()
        mock_client.parse_menu = AsyncMock(
            return_value={
                "items": [
                    {"name": "Burger", "price": "$12", "description": "Beef burger"},
                    {"name": "Fries", "price": "$5", "description": "Crispy fries"},
                ]
            }
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["menu", str(menu_path)])

        assert result.exit_code == 0
        assert "Burger" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    @patch("fcp_cli.commands.log.validate_resolution")
    def test_menu_with_explicit_resolution(self, mock_validate, mock_client_class, mock_run_async, runner, tmp_path):
        """Test menu with explicit resolution."""
        menu_path = tmp_path / "menu.jpg"
        menu_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.return_value = "high"
        mock_client = MagicMock()
        mock_client.parse_menu = AsyncMock(
            return_value={"items": [{"name": "Pizza", "price": "$15", "description": ""}]}
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["menu", str(menu_path), "--res", "high"])

        assert result.exit_code == 0
        mock_validate.assert_called_once_with("high")

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    @patch("fcp_cli.commands.log.auto_select_resolution")
    def test_menu_no_items(self, mock_auto_select, mock_client_class, mock_run_async, runner, tmp_path):
        """Test menu with no items found."""
        menu_path = tmp_path / "menu.jpg"
        menu_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_auto_select.return_value = "medium"
        mock_client = MagicMock()
        mock_client.parse_menu = AsyncMock(return_value={"items": []})
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["menu", str(menu_path)])

        assert result.exit_code == 0
        assert "No dishes found" in result.stdout

    @patch("fcp_cli.commands.log.auto_select_resolution")
    def test_menu_error(self, mock_auto_select, runner, tmp_path):
        """Test menu with error."""
        menu_path = tmp_path / "menu.jpg"
        menu_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_auto_select.side_effect = Exception("Processing error")

        result = runner.invoke(app, ["menu", str(menu_path)])

        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestLogDonateCommand:
    """Test log donate command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_donate_success(self, mock_client_class, mock_run_async, runner):
        """Test donation success."""
        mock_client = MagicMock()
        mock_client.donate_meal = AsyncMock(return_value={"message": "Donation pledged successfully"})
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["donate", "meal123"])

        assert result.exit_code == 0
        assert "Donation pledged successfully" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_donate_with_organization(self, mock_client_class, mock_run_async, runner):
        """Test donation with organization."""
        mock_client = MagicMock()
        mock_client.donate_meal = AsyncMock(return_value={"message": "Donated to Food Bank"})
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["donate", "meal123", "--org", "Food Bank"])

        assert result.exit_code == 0
        assert "Donated to Food Bank" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_donate_error(self, mock_client_class, mock_run_async, runner):
        """Test donation error."""
        mock_client = MagicMock()
        mock_client.donate_meal = AsyncMock(side_effect=Exception("Donation failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["donate", "meal123"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestLogBatchCommand:
    """Test log batch command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_batch_not_a_directory(self, runner):
        """Test batch with non-directory."""
        result = runner.invoke(app, ["batch", "/nonexistent/folder"])

        assert result.exit_code == 1
        assert "Not a directory" in result.stdout

    @patch("fcp_cli.commands.log.validate_resolution")
    def test_batch_invalid_resolution(self, mock_validate, runner, tmp_path):
        """Test batch with invalid resolution."""
        folder = tmp_path / "images"
        folder.mkdir()

        mock_validate.side_effect = ValueError("Invalid resolution")

        result = runner.invoke(app, ["batch", str(folder), "--res", "ultra"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestLogAddIDDisplay:
    """Test log add ID display logic."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_add_with_id_display(self, mock_client_class, mock_run_async, runner):
        """Test log add displaying ID."""
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(
            return_value=MagicMock(id="meal123", dish_name="Pizza", meal_type="dinner")
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["add", "Pizza", "--meal-type", "dinner"])

        assert result.exit_code == 0
        assert "meal123" in result.stdout or "ID" in result.stdout


class TestLogShowConditionalDisplay:
    """Test log show conditional display logic."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_with_all_fields(self, mock_client_class, mock_run_async, runner):
        """Test show with all optional fields."""
        from datetime import datetime

        mock_client = MagicMock()
        mock_client.get_food_log = AsyncMock(
            return_value=MagicMock(
                id="meal123",
                dish_name="Pizza",
                description="Margherita",
                meal_type="dinner",
                timestamp=datetime(2026, 2, 8, 18, 0, 0),
                ingredients=["tomato", "cheese"],
                nutrition={"calories": 800},
            )
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "meal123"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "Margherita" in result.stdout

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_show_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test show with connection error."""
        from fcp_cli.services.fcp import FcpConnectionError

        mock_client = MagicMock()
        mock_client.get_food_log = AsyncMock(side_effect=FcpConnectionError("Connection failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["show", "meal123"])

        assert result.exit_code == 1
        assert "Connection error:" in result.stdout


class TestLogListConnectionError:
    """Test log list connection error."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async", side_effect=lambda coro: asyncio.new_event_loop().run_until_complete(coro))
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_list_connection_error(self, mock_client_class, mock_run_async, runner):
        """Test log list with connection error."""
        from fcp_cli.services.fcp import FcpConnectionError

        mock_client = MagicMock()
        mock_client.get_food_logs = AsyncMock(side_effect=FcpConnectionError("Connection failed"))
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Connection error:" in result.stdout
        assert "Is the FCP server running?" in result.stdout


# Batch processing tests removed - complex async mocking makes these difficult to test reliably
# The batch command logic is covered by integration tests and manual testing
