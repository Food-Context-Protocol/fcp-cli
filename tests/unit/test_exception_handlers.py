"""Tests for exception handlers marked with pragma: no cover.

This test file provides comprehensive coverage for all 46 exception handlers
across the FCP CLI commands that were previously marked with 'pragma: no cover'.
Each test verifies that unexpected exceptions are properly caught and handled.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands import (
    discover,
    labels,
    log,
    nearby,
    pantry,
    profile,
    publish,
    recipes,
    safety,
    search,
    suggest,
    taste,
)

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestPublishExceptionHandlers:
    """Test exception handlers in publish.py (7 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_generate_content_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test generate command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["generate", "blog"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_list_drafts_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test drafts command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["drafts"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_show_draft_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test show command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["show", "draft123"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_edit_draft_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test edit command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["edit", "draft123", "--title", "New Title"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_delete_draft_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test delete command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["delete", "draft123", "--yes"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_publish_draft_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test publish command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["publish", "draft123"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.publish.run_async")
    @patch("fcp_cli.commands.publish.FcpClient")
    def test_list_published_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test published command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(publish.app, ["published"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestPantryExceptionHandlers:
    """Test exception handlers in pantry.py (8 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_list_pantry_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test list command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["list"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_add_item_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test add command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["add", "eggs", "milk"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_check_expiring_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test expiring command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["expiring"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_suggest_meals_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test suggest command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["suggest"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_update_item_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test update command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["update", "item123", "--qty", "2"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_delete_item_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test delete command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["delete", "item123", "--yes"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    @patch("fcp_cli.commands.pantry.read_image_as_base64")
    def test_parse_receipt_unexpected_exception(self, mock_read_image, mock_client, mock_run_async, runner):
        """Test receipt command handles unexpected exceptions."""
        mock_read_image.return_value = "base64data"
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["receipt", "receipt.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.pantry.run_async")
    @patch("fcp_cli.commands.pantry.FcpClient")
    def test_use_items_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test use command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(pantry.app, ["use", "eggs"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestProfileExceptionHandlers:
    """Test exception handlers in profile.py (6 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_profile_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test show command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(profile.app, ["show"])

        assert result.exit_code == 1
        assert "Failed to fetch profile:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_stats_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test stats command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(profile.app, ["stats"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_generate_report_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test report command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(profile.app, ["report"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_streak_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test streak command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(profile.app, ["streak"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_lifetime_stats_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test lifetime command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(profile.app, ["lifetime"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_show_nutrition_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test nutrition command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(profile.app, ["nutrition"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestRecipesExceptionHandlers:
    """Test exception handlers in recipes.py (9 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_list_recipes_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test list command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["list"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    @patch("fcp_cli.commands.recipes.auto_select_resolution")
    def test_extract_recipe_unexpected_exception(
        self, mock_auto_res, mock_read_image, mock_client, mock_run_async, runner
    ):
        """Test extract command handles unexpected exceptions."""
        mock_auto_res.return_value = "medium"
        mock_read_image.return_value = "base64data"
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["extract", "recipe.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_show_recipe_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test show command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["show", "recipe123"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_save_recipe_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test save command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["save", "Test Recipe"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_toggle_favorite_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test favorite command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["favorite", "recipe123"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_toggle_archive_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test archive command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["archive", "recipe123"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_delete_recipe_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test delete command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["delete", "recipe123", "--yes"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_scale_recipe_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test scale command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["scale", "recipe123", "4"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_standardize_recipe_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test standardize command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["standardize", "Raw recipe text"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_generate_recipe_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test generate command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(recipes.app, ["generate"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestDiscoverExceptionHandlers:
    """Test exception handlers in discover.py (5 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.discover.run_async")
    @patch("fcp_cli.commands.discover.FcpClient")
    def test_discover_food_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test food command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(discover.app, ["food"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.discover.run_async")
    @patch("fcp_cli.commands.discover.FcpClient")
    def test_discover_restaurants_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test restaurants command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(discover.app, ["restaurants", "--location", "San Francisco"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.discover.run_async")
    @patch("fcp_cli.commands.discover.FcpClient")
    def test_discover_recipes_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test recipes command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(discover.app, ["recipes", "eggs", "milk"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.discover.run_async")
    @patch("fcp_cli.commands.discover.FcpClient")
    def test_show_trends_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test trends command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(discover.app, ["trends"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.discover.run_async")
    @patch("fcp_cli.commands.discover.FcpClient")
    def test_show_tip_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test tip command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(discover.app, ["tip"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestSafetyExceptionHandlers:
    """Test exception handlers in safety.py (1 handler)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.safety.run_async")
    @patch("fcp_cli.commands.safety.FcpClient")
    def test_check_restaurant_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test restaurant command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(safety.app, ["restaurant", "Test Restaurant", "San Francisco"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestNearbyExceptionHandlers:
    """Test exception handlers in nearby.py (1 handler)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.nearby.run_async")
    @patch("fcp_cli.commands.nearby.FcpClient")
    def test_find_venues_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test venues command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(nearby.app, ["--location", "San Francisco"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestTasteExceptionHandlers:
    """Test exception handlers in taste.py (2 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.taste.run_async")
    @patch("fcp_cli.commands.taste.FcpClient")
    def test_check_compatibility_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test check command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(taste.app, ["check", "Test Dish"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.taste.run_async")
    @patch("fcp_cli.commands.taste.FcpClient")
    def test_get_pairings_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test pairings command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(taste.app, ["pairings", "tomato"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestLogExceptionHandlers:
    """Test exception handlers in log.py (1 handler)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_log_nutrition_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test nutrition command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(log.app, ["nutrition", "Test Meal"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestSearchExceptionHandlers:
    """Test exception handlers in search.py (3 handlers)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.search.run_async")
    @patch("fcp_cli.commands.search.FcpClient")
    def test_query_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test query command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(search.app, ["query", "test query"])

        assert result.exit_code == 1
        assert "Search failed:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.search.run_async")
    @patch("fcp_cli.commands.search.FcpClient")
    def test_by_date_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test by-date command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(search.app, ["by-date", "2024-01-01"])

        assert result.exit_code == 1
        assert "Search failed:" in result.stdout
        assert "Unexpected error" in result.stdout

    @patch("fcp_cli.commands.search.run_async")
    @patch("fcp_cli.commands.search.FcpClient")
    def test_lookup_barcode_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test barcode command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(search.app, ["barcode", "123456789"])

        assert result.exit_code == 1
        assert "Barcode lookup failed:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestSuggestExceptionHandlers:
    """Test exception handlers in suggest.py (1 handler)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.suggest.run_async")
    @patch("fcp_cli.commands.suggest.FcpClient")
    def test_suggest_meals_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test meals command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(suggest.app, [])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout


class TestLabelsExceptionHandlers:
    """Test exception handlers in labels.py (1 handler)."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.labels.run_async")
    @patch("fcp_cli.commands.labels.FcpClient")
    def test_generate_cottage_label_unexpected_exception(self, mock_client, mock_run_async, runner):
        """Test cottage command handles unexpected exceptions."""
        mock_run_async.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(labels.app, ["cottage", "Test Product", "flour", "sugar"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Unexpected error" in result.stdout
