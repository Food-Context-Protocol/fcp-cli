"""Tests for async log functions."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fcp_cli.commands.log import _process_single_image
from fcp_cli.services import FCP

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
class TestProcessSingleImage:
    """Test _process_single_image async function."""

    @patch("fcp_cli.commands.log.read_image_as_base64")
    async def test_success_with_custom_client(self, mock_read):
        """Test successful image processing with custom client."""
        mock_read.return_value = "base64data"
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(
            return_value=FCP(
                id="log123",
                dish_name="test",
                description="Logged from test.jpg",
                user_id="user123",
            )
        )

        image_path = Path("test.jpg")
        result = await _process_single_image(image_path, "lunch", mock_client)

        assert result["success"] is True
        assert result["image"] == "test.jpg"
        mock_client.create_food_log.assert_called_once_with(
            dish_name="test",
            description="Logged from test.jpg",
            meal_type="lunch",
            image_base64="base64data",
        )

    @patch("fcp_cli.commands.log.FcpClient")
    @patch("fcp_cli.commands.log.read_image_as_base64")
    async def test_success_creates_default_client(self, mock_read, mock_client_class):
        """Test that default client is created when none provided."""
        mock_read.return_value = "base64data"
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(
            return_value=FCP(
                id="log123",
                dish_name="photo",
                description="Logged from photo.png",
                user_id="user123",
            )
        )
        mock_client_class.return_value = mock_client

        image_path = Path("photo.png")
        result = await _process_single_image(image_path, None)

        assert result["success"] is True
        assert result["image"] == "photo.png"
        mock_client_class.assert_called_once()

    @patch("fcp_cli.commands.log.read_image_as_base64")
    async def test_failure_with_exception(self, mock_read):
        """Test that exceptions are caught and returned as failure."""
        mock_read.side_effect = Exception("Read failed")

        image_path = Path("bad.jpg")
        result = await _process_single_image(image_path, "dinner", None)

        assert result["success"] is False
        assert result["image"] == "bad.jpg"
        assert "Read failed" in result["error"]

    @patch("fcp_cli.commands.log.read_image_as_base64")
    async def test_failure_with_api_error(self, mock_read):
        """Test that API errors are caught and returned."""
        mock_read.return_value = "base64data"
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(side_effect=Exception("API connection failed"))

        image_path = Path("meal.jpg")
        result = await _process_single_image(image_path, None, mock_client)

        assert result["success"] is False
        assert result["image"] == "meal.jpg"
        assert "API connection failed" in result["error"]

    @patch("fcp_cli.commands.log.read_image_as_base64")
    async def test_uses_stem_as_dish_name(self, mock_read):
        """Test that image stem (filename without extension) is used as dish name."""
        mock_read.return_value = "base64data"
        mock_client = MagicMock()
        mock_client.create_food_log = AsyncMock(
            return_value=FCP(
                id="log123",
                dish_name="my_delicious_meal",
                description="Logged from my_delicious_meal.jpg",
                user_id="user123",
            )
        )

        image_path = Path("my_delicious_meal.jpg")
        result = await _process_single_image(image_path, "breakfast", mock_client)

        assert result["success"] is True
        mock_client.create_food_log.assert_called_once()
        call_args = mock_client.create_food_log.call_args
        assert call_args[1]["dish_name"] == "my_delicious_meal"
        assert call_args[1]["description"] == "Logged from my_delicious_meal.jpg"
