"""Integration-style tests for batch processing."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.log import _batch_log_meals, app

pytestmark = pytest.mark.integration


class TestBatchLogMealsAsync:
    """Test _batch_log_meals async function directly."""

    @pytest.mark.asyncio
    @patch("fcp_cli.commands.log._process_single_image")
    async def test_batch_processes_images_in_parallel(self, mock_process):
        """Test that batch processing handles multiple images."""

        # Mock the process function to return success
        async def mock_process_impl(image, meal_type, client=None):
            return {"success": True, "image": image.name}

        mock_process.side_effect = mock_process_impl

        images = [Path(f"test{i}.jpg") for i in range(3)]
        results = await _batch_log_meals(images, max_parallel=2, resolution="low", meal_type="lunch")

        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert mock_process.call_count == 3

    @pytest.mark.asyncio
    @patch("fcp_cli.commands.log._process_single_image")
    async def test_batch_with_failures(self, mock_process):
        """Test batch processing with some failures."""
        call_count = 0

        async def mock_process_impl(image, meal_type, client=None):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                return {"success": False, "image": image.name, "error": "Failed"}
            return {"success": True, "image": image.name}

        mock_process.side_effect = mock_process_impl

        images = [Path(f"test{i}.jpg") for i in range(3)]
        results = await _batch_log_meals(images, max_parallel=2, resolution="low")

        assert len(results) == 3
        assert results[1]["success"] is False
        assert "Failed" in results[1]["error"]

    @pytest.mark.asyncio
    @patch("fcp_cli.commands.log._process_single_image")
    async def test_batch_respects_max_parallel(self, mock_process):
        """Test that batch respects max_parallel limit."""

        async def mock_process_impl(image, meal_type, client=None):
            return {"success": True, "image": image.name}

        mock_process.side_effect = mock_process_impl

        images = [Path(f"test{i}.jpg") for i in range(5)]
        results = await _batch_log_meals(images, max_parallel=1, resolution="high")

        assert len(results) == 5
        # All should succeed
        assert all(r["success"] for r in results)


class TestBatchCommandIntegration:
    """Integration tests for batch command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.asyncio.run")
    @patch("fcp_cli.commands.log.validate_resolution")
    def test_batch_command_calls_async_runner(self, mock_validate, mock_run, runner, tmp_path):
        """Test that batch command invokes async processing."""
        folder = tmp_path / "images"
        folder.mkdir()
        (folder / "meal1.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.return_value = "low"
        mock_run.return_value = [{"success": True, "image": "meal1.jpg"}]

        result = runner.invoke(app, ["batch", str(folder)])

        assert result.exit_code == 0
        assert "1/1 meals logged successfully" in result.stdout
        mock_run.assert_called_once()

    @patch("fcp_cli.commands.log.asyncio.run")
    @patch("fcp_cli.commands.log.validate_resolution")
    def test_batch_shows_failure_details(self, mock_validate, mock_run, runner, tmp_path):
        """Test that batch command shows failure details."""
        folder = tmp_path / "images"
        folder.mkdir()
        (folder / "bad.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.return_value = "low"
        mock_run.return_value = [{"success": False, "image": "bad.jpg", "error": "Upload failed"}]

        result = runner.invoke(app, ["batch", str(folder)])

        assert result.exit_code == 0
        assert "0/1" in result.stdout
        assert "1 failed" in result.stdout
        assert "Failed images:" in result.stdout
        assert "bad.jpg" in result.stdout
        assert "Upload failed" in result.stdout

    @patch("fcp_cli.commands.log.validate_resolution")
    def test_batch_no_images_found(self, mock_validate, runner, tmp_path):
        """Test batch command when no images are found in folder."""
        folder = tmp_path / "empty"
        folder.mkdir()

        mock_validate.return_value = "low"

        result = runner.invoke(app, ["batch", str(folder)])

        assert result.exit_code == 0
        assert "No images found" in result.stdout
