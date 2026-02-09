"""Complete edge case tests for 100% branch coverage.

This file consolidates all edge case tests previously spread across multiple files,
organized by module (commands vs services) for clarity.
"""

from __future__ import annotations

from datetime import UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.log import app as log_app
from fcp_cli.commands.profile import app as profile_app
from fcp_cli.commands.recipes import app as recipes_app
from fcp_cli.commands.search import app as search_app
from fcp_cli.services import FCP, Recipe, SearchResult, TasteProfile

pytestmark = pytest.mark.unit


# ============================================================================
# COMMAND TESTS - Edge cases for CLI commands
# ============================================================================


class TestLogCommandEdgeCases:
    """Edge cases for log.py command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch("fcp_cli.commands.log.Path")
    @patch("fcp_cli.commands.log.asyncio.run")
    def test_batch_multiple_failures_loop(self, mock_asyncio_run, mock_path_class, runner, tmp_path):
        """Test batch command with multiple failures to cover loop branch 583->582."""
        # Create actual temp folder with images
        folder = tmp_path / "images"
        folder.mkdir()
        img1 = folder / "img1.jpg"
        img2 = folder / "img2.jpg"
        img3 = folder / "img3.jpg"
        img1.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        img2.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        img3.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        # Mock Path().iterdir() to return our images
        mock_folder = MagicMock()
        mock_folder.exists.return_value = True
        mock_folder.is_dir.return_value = True
        mock_folder.iterdir.return_value = [img1, img2, img3]
        mock_path_class.return_value = mock_folder

        # Mock asyncio.run to return mixed results with multiple failures
        mock_asyncio_run.return_value = [
            {"success": True, "image": "img1.jpg"},
            {"success": False, "image": "img2.jpg", "error": "Error A"},
            {"success": False, "image": "img3.jpg", "error": "Error B"},
        ]

        result = runner.invoke(log_app, ["batch", str(folder)])

        # The loop at 582 iterates, line 583 checks each result
        # When it finds a failure (img2), it prints (584)
        # Then continues to next iteration (583->582 branch)
        # Finds another failure (img3), prints again
        assert result.exit_code == 0
        assert "Error A" in result.stdout
        assert "Error B" in result.stdout


class TestProfileCommandEdgeCases:
    """Edge cases for profile.py command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_3_to_6_days(self, mock_client_class, runner):
        """Test profile streak with 3-6 days - covers line 223->exit (elif branch)."""
        mock_client_instance = MagicMock()
        # Mock get_streak to return dict with current_streak between 3-6
        mock_client_instance.get_streak = AsyncMock(
            return_value={
                "current_streak": 5,  # Triggers elif current_streak >= 3
                "best_streak": 5,
                "last_logged": "2025-01-15",
            }
        )
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(profile_app, ["streak"])

        assert result.exit_code == 0
        assert "Great job" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_profile_show_covers_exit_branch(self, mock_client_class, mock_run_async, runner):
        """Test profile show command covers the exit branch."""
        mock_profile = TasteProfile(
            user_id="test123",
            favorite_cuisines=["Italian", "Japanese"],
            preferred_ingredients=["tomatoes", "basil"],
            disliked_ingredients=["anchovies"],
            dietary_restrictions=["vegetarian"],
        )
        mock_run_async.return_value = mock_profile

        result = runner.invoke(profile_app, ["show"])

        assert result.exit_code == 0
        assert "Italian" in result.stdout


class TestRecipesCommandEdgeCases:
    """Edge cases for recipes.py command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    @patch("fcp_cli.commands.recipes.validate_resolution")
    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_extract_no_ingredients(self, mock_client, mock_run_async, mock_validate, mock_read, runner, tmp_path):
        """Test extract with no ingredients - covers line 168->176."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.return_value = "high"
        mock_read.return_value = "base64data"
        # Empty ingredients list
        mock_recipe_dict = {
            "id": "recipe123",
            "name": "Test Recipe",
            "ingredients": [],  # Empty list
            "instructions": ["step1"],
        }
        mock_run_async.return_value = mock_recipe_dict

        result = runner.invoke(recipes_app, ["extract", str(img_path), "--res", "high"])

        assert result.exit_code == 0
        assert "Test Recipe" in result.stdout

    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    @patch("fcp_cli.commands.recipes.validate_resolution")
    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_extract_no_instructions(self, mock_client, mock_run_async, mock_validate, mock_read, runner, tmp_path):
        """Test extract with no instructions - covers line 176->184."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.return_value = "high"
        mock_read.return_value = "base64data"
        # Empty instructions list
        mock_recipe_dict = {
            "id": "recipe123",
            "name": "Test Recipe",
            "ingredients": ["ing1"],
            "instructions": [],  # Empty list
        }
        mock_run_async.return_value = mock_recipe_dict

        result = runner.invoke(recipes_app, ["extract", str(img_path), "--res", "high"])

        assert result.exit_code == 0
        assert "Test Recipe" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_generate_recipe_no_ingredients(self, mock_client, mock_run_async, runner):
        """Test generate recipe with no ingredients - covers line 542->552."""
        mock_recipe = Recipe(
            id="recipe123",
            name="Test Recipe",
            ingredients=None,  # No ingredients - triggers else at 542
            instructions=["step1"],
        )
        mock_run_async.return_value = mock_recipe

        result = runner.invoke(recipes_app, ["generate"])

        assert result.exit_code == 0
        assert "Test Recipe" in result.stdout

    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.FcpClient")
    def test_generate_recipe_no_instructions(self, mock_client, mock_run_async, runner):
        """Test generate recipe with no instructions - covers line 552->560."""
        mock_recipe = Recipe(
            id="recipe123",
            name="Test Recipe",
            ingredients=["ing1"],
            instructions=None,  # No instructions - triggers else at 552
        )
        mock_run_async.return_value = mock_recipe

        result = runner.invoke(recipes_app, ["generate"])

        assert result.exit_code == 0
        assert "Test Recipe" in result.stdout


class TestSearchCommandEdgeCases:
    """Edge cases for search.py command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch("fcp_cli.commands.search.FcpClient")
    def test_query_no_timestamp(self, mock_client_class, runner):
        """Test search query with log.timestamp=None - covers line 146->149 (else branch)."""
        mock_client_instance = MagicMock()
        # Create log with no timestamp
        log_no_timestamp = FCP(
            id="log1",
            user_id="test",
            dish_name="Pizza",
            meal_type="dinner",
            timestamp=None,  # No timestamp triggers else branch at 146
        )
        mock_result = SearchResult(logs=[log_no_timestamp], total=1, query="test")
        mock_client_instance.search_meals = AsyncMock(return_value=mock_result)
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(search_app, ["query", "test"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout

    @patch("fcp_cli.commands.search.run_async")
    @patch("fcp_cli.commands.search.FcpClient")
    def test_query_with_limit_covers_branch(self, mock_client_class, mock_run_async, runner):
        """Test query command with limit to cover branches."""
        from datetime import datetime

        mock_logs = [
            FCP(
                id="log1",
                user_id="test_user",
                dish_name="Pizza",
                meal_type="dinner",
                timestamp=datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC),
            ),
            FCP(
                id="log2",
                user_id="test_user",
                dish_name="Pasta",
                meal_type="lunch",
                timestamp=datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC),
            ),
        ]
        mock_result = SearchResult(logs=mock_logs, total=2, query="italian")
        mock_run_async.return_value = mock_result

        result = runner.invoke(search_app, ["query", "italian", "--limit", "5"])

        assert result.exit_code == 0
        assert "Pizza" in result.stdout
        assert "Pasta" in result.stdout


# ============================================================================
# SERVICE TESTS - Edge cases for service layer (client mixins)
# ============================================================================


class TestClientCoreEdgeCases:
    """Edge cases for fcp_client_core.py."""

    @pytest.mark.asyncio
    async def test_max_response_size_zero(self):
        """Test with max_response_size=0 - covers line 181->186 (disabled check)."""
        from fcp_cli.services.fcp_client_core import FcpClientCore

        # Create client with max_response_size=0 (disabled)
        client = FcpClientCore(max_response_size=0)

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"data": "test"})
            mock_response.content = b'{"data": "test"}' * 1000  # Large response

            async def mock_request(*args, **kwargs):
                return mock_response

            mock_http_client.request = mock_request

            # Make _get_client properly async-compatible
            async def mock_get_client_impl():
                return mock_http_client

            mock_get_client.side_effect = mock_get_client_impl

            # Should succeed even with large response because max_response_size=0
            result = await client._request("GET", "/test")
            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_auto_close_false(self):
        """Test FcpClientCore with auto_close=False - covers line 218->221 (else branch)."""
        from fcp_cli.services.fcp_client_core import FcpClientCore

        # Create client with auto_close=False
        client = FcpClientCore(auto_close=False)
        assert client._auto_close is False

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={"data": "test"})
            mock_response.content = b'{"data": "test"}'

            async def mock_request(*args, **kwargs):
                return mock_response

            mock_http_client.request = mock_request

            # Make _get_client properly async-compatible
            async def mock_get_client_impl():
                return mock_http_client

            mock_get_client.side_effect = mock_get_client_impl

            # Make request - should not auto-close (line 218->221)
            result = await client._request("GET", "/test")
            assert result == {"data": "test"}
            # Client should NOT auto-close


class TestClientMealsEdgeCases:
    """Edge cases for fcp_client_meals.py."""

    @pytest.mark.asyncio
    async def test_update_food_log_no_dish_name(self):
        """Test update_food_log with dish_name=None - covers line 297->299."""
        from fcp_cli.services.fcp_client_meals import FcpMealsMixin

        class TestClient(FcpMealsMixin):
            def __init__(self):
                self.user_id = "test_user"

            async def _request(self, method, path, **kwargs):
                # Verify dish_name is NOT in the payload
                payload = kwargs.get("json", {})
                assert "dish_name" not in payload
                return {
                    "id": "meal123",
                    "dishName": "Default",
                    "userId": "test_user",
                }

        client = TestClient()
        result = await client.update_food_log(log_id="log123", dish_name=None)
        assert result.id == "meal123"

    @pytest.mark.asyncio
    async def test_get_food_trends_no_params(self):
        """Test get_food_trends with no region/cuisine - covers lines 379->381, 381->384."""
        from fcp_cli.services.fcp_client_meals import FcpMealsMixin

        class TestClient(FcpMealsMixin):
            def __init__(self):
                self.user_id = "test_user"

            async def _request(self, method, path, **kwargs):
                # Verify region and cuisine_focus are NOT in params
                params = kwargs.get("params", {})
                assert "region" not in params
                assert "cuisine_focus" not in params
                return {"trends": []}

        client = TestClient()
        result = await client.get_food_trends()  # No region or cuisine_focus
        assert "trends" in result


class TestClientRecipesEdgeCases:
    """Edge cases for fcp_client_recipes.py."""

    @pytest.mark.asyncio
    async def test_update_draft_no_params(self):
        """Test update_draft with no optional params - covers lines 142->144."""
        from fcp_cli.services.fcp_client_recipes import FcpRecipesMixin

        class TestClient(FcpRecipesMixin):
            def __init__(self):
                self.user_id = "test_user"

            async def _request(self, method, path, **kwargs):
                # Verify title is NOT in the payload
                payload = kwargs.get("json", {})
                assert "title" not in payload
                return {
                    "id": "draft123",
                    "title": "Existing Title",
                    "content": "Existing Content",
                }

        client = TestClient()
        result = await client.update_draft(draft_id="draft123", title=None)
        assert result.id == "draft123"

    @pytest.mark.asyncio
    async def test_generate_recipe_no_params(self):
        """Test generate_recipe with no optional params - covers lines 244-252."""
        from fcp_cli.services.fcp_client_recipes import FcpRecipesMixin

        class TestClient(FcpRecipesMixin):
            def __init__(self):
                self.user_id = "test_user"

            async def _request(self, method, path, **kwargs):
                # Verify all optional params are NOT in the payload
                payload = kwargs.get("json", {})
                assert "ingredients" not in payload
                assert "cuisine" not in payload
                assert "dietary_restrictions" not in payload
                assert "meal_type" not in payload
                assert "difficulty" not in payload
                return {
                    "id": "recipe123",
                    "name": "Generated Recipe",
                    "ingredients": [],
                    "instructions": [],
                }

        client = TestClient()
        # Call with all optional params as None
        result = await client.generate_recipe(
            ingredients=None,
            cuisine=None,
            dietary_restrictions=None,
            meal_type=None,
            difficulty=None,
        )
        assert result.id == "recipe123"
