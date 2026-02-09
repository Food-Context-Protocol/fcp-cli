"""Tests for pantry commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.pantry import (
    PantryCategory,
    StorageLocation,
    app,
)
from fcp_cli.services import (
    FcpConnectionError,
    FcpServerError,
    PantryItem,
)
from fcp_cli.utils import ImageTooLargeError, InvalidImageError

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestPantryEnums:
    """Test pantry enums."""

    def test_pantry_category_values(self):
        """Test PantryCategory enum values."""
        assert PantryCategory.PRODUCE == "produce"
        assert PantryCategory.DAIRY == "dairy"
        assert PantryCategory.PROTEINS == "proteins"
        assert PantryCategory.GRAINS == "grains"
        assert PantryCategory.FROZEN == "frozen"
        assert PantryCategory.CANNED == "canned"
        assert PantryCategory.CONDIMENTS == "condiments"
        assert PantryCategory.BEVERAGES == "beverages"
        assert PantryCategory.SNACKS == "snacks"
        assert PantryCategory.OTHER == "other"

    def test_storage_location_values(self):
        """Test StorageLocation enum values."""
        assert StorageLocation.FRIDGE == "fridge"
        assert StorageLocation.FREEZER == "freezer"
        assert StorageLocation.PANTRY == "pantry"


class TestPantryListCommand:
    """Test pantry list command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_list_pantry_success(self, mock_run_async, mock_client_class, runner):
        """Test listing pantry items successfully."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = [
            {"name": "Eggs", "quantity": "12", "expiry_date": "2026-02-15"},
            {"item_name": "Milk", "quantity": "1", "expiration": "2026-02-10"},
        ]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Eggs" in result.stdout
        assert "Milk" in result.stdout
        assert "12" in result.stdout
        mock_run_async.assert_called_once()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_list_pantry_empty(self, mock_run_async, mock_client_class, runner):
        """Test listing empty pantry."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = []

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "empty" in result.stdout.lower()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_list_pantry_missing_fields(self, mock_run_async, mock_client_class, runner):
        """Test listing pantry with missing item fields."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = [
            {"name": "Bread"},  # Missing quantity and expiry
            {"quantity": "2"},  # Missing name
        ]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Bread" in result.stdout or "Unknown" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_list_pantry_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test list pantry with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_list_pantry_server_error(self, mock_run_async, mock_client_class, runner):
        """Test list pantry with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPantryAddCommand:
    """Test pantry add command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_add_single_item(self, mock_run_async, mock_client_class, runner):
        """Test adding a single item."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"status": "success"}

        result = runner.invoke(app, ["add", "eggs"])

        assert result.exit_code == 0
        assert "Added 1 item(s)" in result.stdout
        mock_run_async.assert_called_once()
        # Verify the payload structure
        call_args = mock_run_async.call_args
        assert call_args is not None

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_add_multiple_items(self, mock_run_async, mock_client_class, runner):
        """Test adding multiple items."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"status": "success"}

        result = runner.invoke(app, ["add", "eggs", "milk", "bread"])

        assert result.exit_code == 0
        assert "Added 3 item(s)" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_add_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test add with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["add", "eggs"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_add_server_error(self, mock_run_async, mock_client_class, runner):
        """Test add with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["add", "eggs"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPantryExpiringCommand:
    """Test pantry expiring command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_check_expiring_with_items(self, mock_run_async, mock_client_class, runner):
        """Test checking expiring items with results."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "expiring": [
                {"name": "Milk", "expiry_date": "2026-02-09"},
                {"item_name": "Yogurt", "expiration": "2026-02-10"},
            ]
        }

        result = runner.invoke(app, ["expiring"])

        assert result.exit_code == 0
        assert "Milk" in result.stdout
        assert "Yogurt" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_check_expiring_alternative_key(self, mock_run_async, mock_client_class, runner):
        """Test checking expiring with alternative 'items' key."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "items": [
                {"name": "Cheese", "expiry_date": "2026-02-11"},
            ]
        }

        result = runner.invoke(app, ["expiring"])

        assert result.exit_code == 0
        assert "Cheese" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_check_expiring_none(self, mock_run_async, mock_client_class, runner):
        """Test checking expiring with no items."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"expiring": []}

        result = runner.invoke(app, ["expiring"])

        assert result.exit_code == 0
        assert "No items expiring soon" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_check_expiring_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test expiring with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["expiring"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_check_expiring_server_error(self, mock_run_async, mock_client_class, runner):
        """Test expiring with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["expiring"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPantrySuggestCommand:
    """Test pantry suggest command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_suggest_meals_with_suggestions(self, mock_run_async, mock_client_class, runner):
        """Test meal suggestions with results."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "suggestions": [
                {"name": "Egg Fried Rice", "description": "Quick and easy meal"},
                {"title": "Milk Smoothie", "description": "Healthy breakfast"},
            ]
        }

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 0
        assert "Egg Fried Rice" in result.stdout
        assert "Milk Smoothie" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_suggest_meals_no_suggestions(self, mock_run_async, mock_client_class, runner):
        """Test meal suggestions with no results."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"suggestions": []}

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 0
        assert "No suggestions available" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_suggest_meals_missing_fields(self, mock_run_async, mock_client_class, runner):
        """Test meal suggestions with missing fields."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "suggestions": [
                {"description": "Only description"},
                {},
            ]
        }

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 0

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_suggest_meals_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test suggest with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_suggest_meals_server_error(self, mock_run_async, mock_client_class, runner):
        """Test suggest with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPantryUpdateCommand:
    """Test pantry update command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_quantity(self, mock_run_async, mock_client_class, runner):
        """Test updating item quantity."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_item = PantryItem(id="item123", name="Eggs", quantity="6")
        mock_run_async.return_value = mock_item

        result = runner.invoke(app, ["update", "item123", "--qty", "6"])

        assert result.exit_code == 0
        assert "Eggs" in result.stdout
        assert "item123" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_category(self, mock_run_async, mock_client_class, runner):
        """Test updating item category."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_item = PantryItem(id="item123", name="Milk", category="dairy")
        mock_run_async.return_value = mock_item

        result = runner.invoke(app, ["update", "item123", "--category", "dairy"])

        assert result.exit_code == 0
        assert "Milk" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_location(self, mock_run_async, mock_client_class, runner):
        """Test updating storage location."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_item = PantryItem(id="item123", name="Ice Cream", storage_location="freezer")
        mock_run_async.return_value = mock_item

        result = runner.invoke(app, ["update", "item123", "--location", "freezer"])

        assert result.exit_code == 0
        assert "Ice Cream" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_expiration(self, mock_run_async, mock_client_class, runner):
        """Test updating expiration date."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_item = PantryItem(id="item123", name="Yogurt", expiration_date="2026-02-20")
        mock_run_async.return_value = mock_item

        result = runner.invoke(app, ["update", "item123", "--expires", "2026-02-20"])

        assert result.exit_code == 0
        assert "Yogurt" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_multiple_fields(self, mock_run_async, mock_client_class, runner):
        """Test updating multiple fields at once."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_item = PantryItem(id="item123", name="Cheese", quantity="2", category="dairy", storage_location="fridge")
        mock_run_async.return_value = mock_item

        result = runner.invoke(app, ["update", "item123", "--qty", "2", "--category", "dairy", "--location", "fridge"])

        assert result.exit_code == 0
        assert "Cheese" in result.stdout

    def test_update_no_changes(self, runner):
        """Test update with no changes specified."""
        result = runner.invoke(app, ["update", "item123"])

        assert result.exit_code == 0
        assert "No changes specified" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test update with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["update", "item123", "--qty", "5"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_update_server_error(self, mock_run_async, mock_client_class, runner):
        """Test update with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["update", "item123", "--qty", "5"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPantryDeleteCommand:
    """Test pantry delete command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_delete_with_yes_flag(self, mock_run_async, mock_client_class, runner):
        """Test deleting item with --yes flag."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "item123", "--yes"])

        assert result.exit_code == 0
        assert "Deleted pantry item item123" in result.stdout
        mock_run_async.assert_called_once()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_delete_with_confirmation(self, mock_run_async, mock_client_class, runner):
        """Test deleting item with confirmation."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "item123"], input="y\n")

        assert result.exit_code == 0
        assert "Deleted pantry item item123" in result.stdout

    def test_delete_cancelled(self, runner):
        """Test cancelling deletion."""
        result = runner.invoke(app, ["delete", "item123"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_delete_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test delete with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["delete", "item123", "--yes"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_delete_server_error(self, mock_run_async, mock_client_class, runner):
        """Test delete with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["delete", "item123", "--yes"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPantryReceiptCommand:
    """Test pantry receipt command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_image(self, tmp_path):
        """Create a temporary test image."""
        img_path = tmp_path / "receipt.png"
        # PNG magic number
        img_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        return img_path

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_success(
        self,
        mock_read_image,
        mock_run_async,
        mock_client_class,
        runner,
        temp_image,
    ):
        """Test parsing receipt successfully."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_read_image.return_value = "base64encodedimage"
        mock_run_async.return_value = {
            "items": [
                {"name": "Eggs", "quantity": 12, "price": "3.99"},
                {"description": "Milk", "quantity": 1, "price": "2.99"},
            ]
        }

        result = runner.invoke(app, ["receipt", str(temp_image)], input="y\n")

        assert result.exit_code == 0
        assert "Eggs" in result.stdout
        assert "Milk" in result.stdout
        assert "Added 2 items" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_no_items(
        self,
        mock_read_image,
        mock_run_async,
        mock_client_class,
        runner,
        temp_image,
    ):
        """Test parsing receipt with no items found."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_read_image.return_value = "base64encodedimage"
        mock_run_async.return_value = {"items": []}

        result = runner.invoke(app, ["receipt", str(temp_image)])

        assert result.exit_code == 0
        assert "No items found" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_decline_add(
        self,
        mock_read_image,
        mock_run_async,
        mock_client_class,
        runner,
        temp_image,
    ):
        """Test parsing receipt but declining to add items."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_read_image.return_value = "base64encodedimage"
        mock_run_async.return_value = {
            "items": [
                {"name": "Bread", "quantity": 1, "price": "1.99"},
            ]
        }

        result = runner.invoke(app, ["receipt", str(temp_image)], input="n\n")

        assert result.exit_code == 0
        assert "Bread" in result.stdout
        # Verify add_to_pantry was not called
        assert mock_run_async.call_count == 1

    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_file_not_found(self, mock_read_image, runner):
        """Test parsing receipt with missing file."""
        mock_read_image.side_effect = FileNotFoundError("File not found")

        result = runner.invoke(app, ["receipt", "nonexistent.png"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_image_too_large(self, mock_read_image, runner):
        """Test parsing receipt with too large image."""
        mock_read_image.side_effect = ImageTooLargeError("Image too large")

        result = runner.invoke(app, ["receipt", "large.png"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_invalid_image(self, mock_read_image, runner):
        """Test parsing receipt with invalid image."""
        mock_read_image.side_effect = InvalidImageError("Invalid image")

        result = runner.invoke(app, ["receipt", "invalid.png"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_connection_error(
        self,
        mock_read_image,
        mock_run_async,
        mock_client_class,
        runner,
        temp_image,
    ):
        """Test parsing receipt with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_read_image.return_value = "base64encodedimage"
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["receipt", str(temp_image)])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_server_error(
        self,
        mock_read_image,
        mock_run_async,
        mock_client_class,
        runner,
        temp_image,
    ):
        """Test parsing receipt with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_read_image.return_value = "base64encodedimage"
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["receipt", str(temp_image)])

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_missing_price(
        self,
        mock_read_image,
        mock_run_async,
        mock_client_class,
        runner,
        temp_image,
    ):
        """Test parsing receipt with items missing price."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_read_image.return_value = "base64encodedimage"
        mock_run_async.return_value = {
            "items": [
                {"name": "Apples", "quantity": 3},  # Missing price
            ]
        }

        result = runner.invoke(app, ["receipt", str(temp_image)], input="n\n")

        assert result.exit_code == 0
        assert "Apples" in result.stdout


class TestPantryUseCommand:
    """Test pantry use command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_single_item(self, mock_run_async, mock_client_class, runner):
        """Test using a single item."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "deducted": [{"name": "Eggs", "remaining": 10, "quantity_remaining": 10}],
            "not_found": [],
        }

        result = runner.invoke(app, ["use", "Eggs"])

        assert result.exit_code == 0
        assert "Used 1 item(s)" in result.stdout
        assert "Eggs" in result.stdout
        assert "10 remaining" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_multiple_items(self, mock_run_async, mock_client_class, runner):
        """Test using multiple items."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "deducted": [
                {"name": "Eggs", "remaining": 10},
                {"name": "Milk", "remaining": 0},
            ],
            "not_found": [],
        }

        result = runner.invoke(app, ["use", "Eggs", "Milk"])

        assert result.exit_code == 0
        assert "Used 2 item(s)" in result.stdout
        assert "Eggs" in result.stdout
        assert "Milk" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_with_quantity(self, mock_run_async, mock_client_class, runner):
        """Test using items with specified quantity."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"deducted": [{"name": "Eggs", "remaining": 9}], "not_found": []}

        result = runner.invoke(app, ["use", "Eggs", "--qty", "3"])

        assert result.exit_code == 0
        assert "Used 1 item(s)" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_item_not_found(self, mock_run_async, mock_client_class, runner):
        """Test using items not in pantry."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"deducted": [], "not_found": ["Bananas", "Oranges"]}

        result = runner.invoke(app, ["use", "Bananas", "Oranges"])

        assert result.exit_code == 0
        assert "Not found in pantry" in result.stdout
        assert "Bananas" in result.stdout
        assert "Oranges" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_mixed_found_not_found(self, mock_run_async, mock_client_class, runner):
        """Test using items with some found and some not found."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"deducted": [{"name": "Eggs", "remaining": 11}], "not_found": ["Chocolate"]}

        result = runner.invoke(app, ["use", "Eggs", "Chocolate"])

        assert result.exit_code == 0
        assert "Used 1 item(s)" in result.stdout
        assert "Eggs" in result.stdout
        assert "Not found in pantry" in result.stdout
        assert "Chocolate" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_alternative_keys(self, mock_run_async, mock_client_class, runner):
        """Test using items with alternative response keys."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {
            "items": [
                {"name": "Bread"}  # No remaining field
            ],
        }

        result = runner.invoke(app, ["use", "Bread"])

        assert result.exit_code == 0
        assert "Used 1 item(s)" in result.stdout
        assert "Bread" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_not_found_dict(self, mock_run_async, mock_client_class, runner):
        """Test not found items as dict objects."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.return_value = {"deducted": [], "not_found": [{"name": "Rice"}]}

        result = runner.invoke(app, ["use", "Rice"])

        assert result.exit_code == 0
        assert "Not found in pantry" in result.stdout
        assert "Rice" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test use with connection error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["use", "Eggs"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.run_async")
    def test_use_server_error(self, mock_run_async, mock_client_class, runner):
        """Test use with server error."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["use", "Eggs"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "category",
    [
        PantryCategory.PRODUCE,
        PantryCategory.DAIRY,
        PantryCategory.PROTEINS,
        PantryCategory.GRAINS,
        PantryCategory.FROZEN,
        PantryCategory.CANNED,
        PantryCategory.CONDIMENTS,
        PantryCategory.BEVERAGES,
        PantryCategory.SNACKS,
        PantryCategory.OTHER,
    ],
)
@patch("fcp_cli.commands.pantry.FcpClient")
@patch("fcp_cli.commands.pantry.run_async")
def test_update_all_categories(mock_run_async, mock_client_class, category):
    """Test updating items with all category values."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_item = PantryItem(id="item123", name="Test", category=category.value)
    mock_run_async.return_value = mock_item

    runner = CliRunner()
    result = runner.invoke(app, ["update", "item123", "--category", category.value])

    assert result.exit_code == 0
    assert "Test" in result.stdout


@pytest.mark.parametrize(
    "location",
    [
        StorageLocation.FRIDGE,
        StorageLocation.FREEZER,
        StorageLocation.PANTRY,
    ],
)
@patch("fcp_cli.commands.pantry.FcpClient")
@patch("fcp_cli.commands.pantry.run_async")
def test_update_all_locations(mock_run_async, mock_client_class, location):
    """Test updating items with all storage location values."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_item = PantryItem(id="item123", name="Test", storage_location=location.value)
    mock_run_async.return_value = mock_item

    runner = CliRunner()
    result = runner.invoke(app, ["update", "item123", "--location", location.value])

    assert result.exit_code == 0
    assert "Test" in result.stdout
