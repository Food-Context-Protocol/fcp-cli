"""Tests for log helper functions."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from fcp_cli.commands.log import _process_image_for_log
from fcp_cli.utils import ImageTooLargeError, InvalidImageError

pytestmark = pytest.mark.unit


class TestProcessImageForLog:
    """Test _process_image_for_log helper function."""

    @patch("fcp_cli.commands.log.read_image_as_base64")
    @patch("fcp_cli.commands.log.validate_resolution")
    def test_with_explicit_resolution(self, mock_validate, mock_read):
        """Test processing image with explicit resolution."""
        mock_validate.return_value = "medium"
        mock_read.return_value = "base64data"

        image_data, resolution = _process_image_for_log("test.jpg", "medium")

        assert image_data == "base64data"
        assert resolution == "medium"
        mock_validate.assert_called_once_with("medium")
        mock_read.assert_called_once_with("test.jpg")

    @patch("fcp_cli.commands.log.read_image_as_base64")
    @patch("fcp_cli.commands.log.auto_select_resolution")
    def test_with_auto_resolution(self, mock_auto, mock_read):
        """Test processing image with auto resolution."""
        mock_auto.return_value = "low"
        mock_read.return_value = "base64data"

        image_data, resolution = _process_image_for_log("test.jpg", None)

        assert image_data == "base64data"
        assert resolution == "low"
        mock_auto.assert_called_once_with("test.jpg")
        mock_read.assert_called_once_with("test.jpg")

    @patch("fcp_cli.commands.log.validate_resolution")
    def test_invalid_resolution_raises_value_error(self, mock_validate):
        """Test that invalid resolution raises ValueError."""
        mock_validate.side_effect = ValueError("Invalid resolution")

        with pytest.raises(ValueError, match="Invalid resolution"):
            _process_image_for_log("test.jpg", "ultra")

    @patch("fcp_cli.commands.log.validate_resolution")
    @patch("fcp_cli.commands.log.read_image_as_base64")
    def test_image_not_found_raises_file_not_found(self, mock_read, mock_validate):
        """Test that missing image raises FileNotFoundError."""
        mock_validate.return_value = "low"
        mock_read.side_effect = FileNotFoundError("Image not found")

        with pytest.raises(FileNotFoundError, match="Image not found"):
            _process_image_for_log("missing.jpg", "low")

    @patch("fcp_cli.commands.log.validate_resolution")
    @patch("fcp_cli.commands.log.read_image_as_base64")
    def test_image_too_large_raises_error(self, mock_read, mock_validate):
        """Test that oversized image raises ImageTooLargeError."""
        mock_validate.return_value = "low"
        mock_read.side_effect = ImageTooLargeError("Image exceeds 50MB limit")

        with pytest.raises(ImageTooLargeError, match="exceeds 50MB"):
            _process_image_for_log("huge.jpg", "low")

    @patch("fcp_cli.commands.log.validate_resolution")
    @patch("fcp_cli.commands.log.read_image_as_base64")
    def test_invalid_image_raises_error(self, mock_read, mock_validate):
        """Test that invalid image format raises InvalidImageError."""
        mock_validate.return_value = "low"
        mock_read.side_effect = InvalidImageError("Invalid image format")

        with pytest.raises(InvalidImageError, match="Invalid image format"):
            _process_image_for_log("corrupt.jpg", "low")
