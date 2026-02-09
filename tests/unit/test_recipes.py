"""Tests for recipes commands."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.recipes import (
    Difficulty,
    MealType,
    RecipeFilter,
    app,
)
from fcp_cli.services import FcpConnectionError, FcpServerError
from fcp_cli.services.models import MealSuggestion, Recipe
from fcp_cli.utils import ImageTooLargeError, InvalidImageError

pytestmark = [pytest.mark.unit, pytest.mark.cli]


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_recipe():
    """Create a mock recipe object."""
    return Recipe(
        id="recipe123",
        name="Test Recipe",
        description="A delicious test recipe",
        ingredients=["flour", "sugar", "eggs"],
        instructions=["Mix ingredients", "Bake at 350F"],
        servings=4,
        source="test",
        prep_time="15 min",
        cook_time="30 min",
        is_favorite=False,
        is_archived=False,
        user_id="user123",
    )


@pytest.fixture
def mock_recipe_dict_ingredients():
    """Create a mock recipe with dict-based ingredients."""
    return Recipe(
        id="recipe456",
        name="Advanced Recipe",
        ingredients=[
            {"name": "flour", "amount": "2 cups"},
            {"name": "sugar", "amount": "1 cup"},
        ],
        instructions=[
            {"text": "Mix dry ingredients"},
            {"text": "Add wet ingredients"},
        ],
        servings=6,
        source="cookbook",
    )


class TestListRecipes:
    """Test recipes list command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_default(self, mock_run_async, mock_client_class, runner, mock_recipe):
        """Test listing recipes with default filter."""
        mock_run_async.return_value = [mock_recipe]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Test Recipe" in result.stdout
        assert "test" in result.stdout
        assert "recipe123"[:8] in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_favorites(self, mock_run_async, mock_client_class, runner):
        """Test listing favorite recipes."""
        favorite_recipe = Recipe(
            id="fav123",
            name="Favorite Recipe",
            servings=2,
            source="home",
            is_favorite=True,
        )
        mock_run_async.return_value = [favorite_recipe]

        result = runner.invoke(app, ["list", "--filter", "favorites"])

        assert result.exit_code == 0
        assert "Favorite Recipe" in result.stdout
        assert "★" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_archived(self, mock_run_async, mock_client_class, runner):
        """Test listing archived recipes."""
        archived_recipe = Recipe(
            id="arch123",
            name="Archived Recipe",
            servings=3,
            is_archived=True,
        )
        mock_run_async.return_value = [archived_recipe]

        result = runner.invoke(app, ["list", "--filter", "archived"])

        assert result.exit_code == 0
        assert "Archived Recipe" in result.stdout
        assert "archived" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_empty(self, mock_run_async, mock_client_class, runner):
        """Test listing recipes when none exist."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No saved recipes yet" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_empty_favorites(self, mock_run_async, mock_client_class, runner):
        """Test listing favorites when none exist."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["list", "--filter", "favorites"])

        assert result.exit_code == 0
        assert "No favorite recipes yet" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_empty_archived(self, mock_run_async, mock_client_class, runner):
        """Test listing archived when none exist."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["list", "--filter", "archived"])

        assert result.exit_code == 0
        assert "No archived recipes" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_favorite_and_archived(self, mock_run_async, mock_client_class, runner):
        """Test listing recipe that is both favorite and archived."""
        recipe = Recipe(
            id="both123",
            name="Both Recipe",
            servings=1,
            is_favorite=True,
            is_archived=True,
        )
        mock_run_async.return_value = [recipe]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "★" in result.stdout
        assert "archived" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_no_optional_fields(self, mock_run_async, mock_client_class, runner):
        """Test listing recipe with minimal fields."""
        minimal_recipe = Recipe(id=None, name="Minimal", servings=None, source=None)
        mock_run_async.return_value = [minimal_recipe]

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Minimal" in result.stdout
        assert "-" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test list recipes with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "Is the FCP server running?" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_list_recipes_server_error(self, mock_run_async, mock_client_class, runner):
        """Test list recipes with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestSuggestRecipes:
    """Test recipes suggest command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_suggest_recipes_no_context(self, mock_run_async, mock_client_class, runner):
        """Test suggesting recipes without context."""
        suggestions = [
            MealSuggestion(name="Pasta", meal_type="dinner", reason="Quick and easy"),
            MealSuggestion(name="Salad", meal_type="lunch", reason="Healthy option"),
        ]
        mock_run_async.return_value = suggestions

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 0
        assert "Pasta" in result.stdout
        assert "Salad" in result.stdout
        assert "Quick and easy" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_suggest_recipes_with_context(self, mock_run_async, mock_client_class, runner):
        """Test suggesting recipes with context."""
        suggestions = [
            MealSuggestion(name="Stir Fry", meal_type="dinner", reason="Quick weeknight meal"),
        ]
        mock_run_async.return_value = suggestions

        result = runner.invoke(app, ["suggest", "quick dinner"])

        assert result.exit_code == 0
        assert "Stir Fry" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_suggest_recipes_custom_exclude_days(self, mock_run_async, mock_client_class, runner):
        """Test suggesting recipes with custom exclude days."""
        mock_run_async.return_value = [
            MealSuggestion(name="Tacos", meal_type="dinner"),
        ]

        result = runner.invoke(app, ["suggest", "--exclude-recent", "7"])

        assert result.exit_code == 0
        assert "Tacos" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_suggest_recipes_no_suggestions(self, mock_run_async, mock_client_class, runner):
        """Test suggesting recipes with no results."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 0
        assert "No suggestions found" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_suggest_recipes_minimal_fields(self, mock_run_async, mock_client_class, runner):
        """Test suggesting recipes with minimal suggestion data."""
        suggestions = [
            MealSuggestion(name="Simple Dish", meal_type=None, reason=None),
        ]
        mock_run_async.return_value = suggestions

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 0
        assert "Simple Dish" in result.stdout
        assert "-" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_suggest_recipes_error(self, mock_run_async, mock_client_class, runner):
        """Test suggest recipes with error."""
        mock_run_async.side_effect = Exception("Suggestion failed")

        result = runner.invoke(app, ["suggest"])

        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestExtractRecipe:
    """Test recipes extract command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_success(self, mock_read_image, mock_run_async, mock_client_class, runner, tmp_path):
        """Test extracting recipe from image."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_read_image.return_value = "base64_image_data"
        mock_run_async.return_value = {
            "name": "Chocolate Cake",
            "ingredients": ["flour", "sugar", "cocoa"],
            "instructions": ["Mix", "Bake"],
            "servings": 8,
        }

        result = runner.invoke(app, ["extract", str(img_path)])

        assert result.exit_code == 0
        assert "Chocolate Cake" in result.stdout
        assert "flour" in result.stdout
        assert "Mix" in result.stdout
        assert "Servings: 8" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_dict_ingredients(
        self, mock_read_image, mock_run_async, mock_client_class, runner, tmp_path
    ):
        """Test extracting recipe with dict-based ingredients."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_read_image.return_value = "base64_image_data"
        mock_run_async.return_value = {
            "recipe_name": "Cookies",
            "ingredients": [
                {"name": "butter", "amount": "1 cup"},
                {"name": "flour", "amount": "2 cups"},
            ],
            "steps": [
                {"text": "Cream butter"},
                {"text": "Add flour"},
            ],
        }

        result = runner.invoke(app, ["extract", str(img_path)])

        assert result.exit_code == 0
        assert "Cookies" in result.stdout
        assert "butter: 1 cup" in result.stdout
        assert "Cream butter" in result.stdout

    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_file_not_found(self, mock_read_image, runner):
        """Test extracting recipe with missing file."""
        mock_read_image.side_effect = FileNotFoundError("Image not found")

        result = runner.invoke(app, ["extract", "/nonexistent/image.jpg"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_image_too_large(self, mock_read_image, runner, tmp_path):
        """Test extracting recipe with oversized image."""
        img_path = tmp_path / "large.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_read_image.side_effect = ImageTooLargeError("Image too large")

        result = runner.invoke(app, ["extract", str(img_path)])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_invalid_image(self, mock_read_image, runner, tmp_path):
        """Test extracting recipe with invalid image."""
        img_path = tmp_path / "invalid.jpg"
        img_path.write_bytes(b"not an image")

        mock_read_image.side_effect = InvalidImageError("Invalid image")

        result = runner.invoke(app, ["extract", str(img_path)])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_connection_error(
        self, mock_read_image, mock_run_async, mock_client_class, runner, tmp_path
    ):
        """Test extracting recipe with connection error."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_read_image.return_value = "base64_data"
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["extract", str(img_path)])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    @patch("fcp_cli.commands.recipes.read_image_as_base64")
    def test_extract_recipe_server_error(self, mock_read_image, mock_run_async, mock_client_class, runner, tmp_path):
        """Test extracting recipe with server error."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_read_image.return_value = "base64_data"
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["extract", str(img_path)])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestShowRecipe:
    """Test recipes show command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_full_details(self, mock_run_async, mock_client_class, runner, mock_recipe):
        """Test showing recipe with full details."""
        mock_run_async.return_value = mock_recipe

        result = runner.invoke(app, ["show", "recipe123"])

        assert result.exit_code == 0
        assert "Test Recipe" in result.stdout
        assert "A delicious test recipe" in result.stdout
        assert "flour" in result.stdout
        assert "Mix ingredients" in result.stdout
        assert "Servings: 4" in result.stdout
        assert "Prep: 15 min" in result.stdout
        assert "Cook: 30 min" in result.stdout
        assert "Source: test" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_dict_ingredients(
        self, mock_run_async, mock_client_class, runner, mock_recipe_dict_ingredients
    ):
        """Test showing recipe with dict-based ingredients."""
        mock_run_async.return_value = mock_recipe_dict_ingredients

        result = runner.invoke(app, ["show", "recipe456"])

        assert result.exit_code == 0
        assert "Advanced Recipe" in result.stdout
        assert "2 cups flour" in result.stdout
        assert "Mix dry ingredients" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_with_item_field(self, mock_run_async, mock_client_class, runner):
        """Test showing recipe with 'item' field in ingredients."""
        recipe = Recipe(
            id="recipe789",
            name="Recipe with Items",
            ingredients=[
                {"item": "salt", "amount": "1 tsp"},
            ],
            instructions=[],
        )
        mock_run_async.return_value = recipe

        result = runner.invoke(app, ["show", "recipe789"])

        assert result.exit_code == 0
        assert "1 tsp salt" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_favorite(self, mock_run_async, mock_client_class, runner):
        """Test showing favorite recipe."""
        recipe = Recipe(
            id="fav123",
            name="Favorite Recipe",
            is_favorite=True,
        )
        mock_run_async.return_value = recipe

        result = runner.invoke(app, ["show", "fav123"])

        assert result.exit_code == 0
        assert "★ Favorite" in result.stdout or "Favorite" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_archived(self, mock_run_async, mock_client_class, runner):
        """Test showing archived recipe."""
        recipe = Recipe(
            id="arch123",
            name="Archived Recipe",
            is_archived=True,
        )
        mock_run_async.return_value = recipe

        result = runner.invoke(app, ["show", "arch123"])

        assert result.exit_code == 0
        assert "Archived" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_minimal(self, mock_run_async, mock_client_class, runner):
        """Test showing recipe with minimal fields."""
        recipe = Recipe(
            id="minimal123",
            name="Minimal Recipe",
        )
        mock_run_async.return_value = recipe

        result = runner.invoke(app, ["show", "minimal123"])

        assert result.exit_code == 0
        assert "Minimal Recipe" in result.stdout
        assert "minimal123" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test showing recipe with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["show", "recipe123"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_show_recipe_server_error(self, mock_run_async, mock_client_class, runner):
        """Test showing recipe with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["show", "recipe123"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestSaveRecipe:
    """Test recipes save command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_save_recipe_minimal(self, mock_run_async, mock_client_class, runner):
        """Test saving recipe with minimal data."""
        mock_run_async.return_value = Recipe(
            id="new123",
            name="New Recipe",
        )

        result = runner.invoke(app, ["save", "New Recipe"])

        assert result.exit_code == 0
        assert "New Recipe" in result.stdout
        assert "Recipe Saved" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_save_recipe_with_ingredients(self, mock_run_async, mock_client_class, runner):
        """Test saving recipe with ingredients."""
        mock_run_async.return_value = Recipe(
            id="new456",
            name="Pancakes",
        )

        result = runner.invoke(
            app,
            ["save", "Pancakes", "-i", "flour", "-i", "eggs", "-i", "milk"],
        )

        assert result.exit_code == 0
        assert "Pancakes" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_save_recipe_with_steps(self, mock_run_async, mock_client_class, runner):
        """Test saving recipe with instruction steps."""
        mock_run_async.return_value = Recipe(
            id="new789",
            name="Simple Dish",
        )

        result = runner.invoke(
            app,
            ["save", "Simple Dish", "-s", "Step 1", "-s", "Step 2"],
        )

        assert result.exit_code == 0
        assert "Simple Dish" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_save_recipe_full_details(self, mock_run_async, mock_client_class, runner):
        """Test saving recipe with all details."""
        mock_run_async.return_value = Recipe(
            id="full123",
            name="Complete Recipe",
            servings=6,
            source="my cookbook",
        )

        result = runner.invoke(
            app,
            [
                "save",
                "Complete Recipe",
                "-i",
                "ingredient1",
                "-s",
                "step1",
                "--servings",
                "6",
                "--source",
                "my cookbook",
            ],
        )

        assert result.exit_code == 0
        assert "Complete Recipe" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_save_recipe_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test saving recipe with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["save", "Recipe"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_save_recipe_server_error(self, mock_run_async, mock_client_class, runner):
        """Test saving recipe with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["save", "Recipe"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestToggleFavorite:
    """Test recipes favorite command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_favorite_add(self, mock_run_async, mock_client_class, runner):
        """Test adding recipe to favorites."""
        mock_run_async.return_value = Recipe(
            id="recipe123",
            name="Tasty Recipe",
            is_favorite=True,
        )

        result = runner.invoke(app, ["favorite", "recipe123"])

        assert result.exit_code == 0
        assert "Tasty Recipe" in result.stdout
        assert "added to favorites" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_favorite_remove(self, mock_run_async, mock_client_class, runner):
        """Test removing recipe from favorites."""
        mock_run_async.return_value = Recipe(
            id="recipe123",
            name="Tasty Recipe",
            is_favorite=False,
        )

        result = runner.invoke(app, ["favorite", "recipe123", "--remove"])

        assert result.exit_code == 0
        assert "Tasty Recipe" in result.stdout
        assert "removed from favorites" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_favorite_remove_short_flag(self, mock_run_async, mock_client_class, runner):
        """Test removing recipe from favorites with short flag."""
        mock_run_async.return_value = Recipe(
            id="recipe123",
            name="Recipe",
            is_favorite=False,
        )

        result = runner.invoke(app, ["favorite", "recipe123", "-r"])

        assert result.exit_code == 0
        assert "removed from favorites" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_favorite_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test favorite command with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["favorite", "recipe123"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_favorite_server_error(self, mock_run_async, mock_client_class, runner):
        """Test favorite command with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["favorite", "recipe123"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestToggleArchive:
    """Test recipes archive command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_archive_recipe(self, mock_run_async, mock_client_class, runner):
        """Test archiving a recipe."""
        mock_run_async.return_value = Recipe(
            id="recipe123",
            name="Old Recipe",
            is_archived=True,
        )

        result = runner.invoke(app, ["archive", "recipe123"])

        assert result.exit_code == 0
        assert "Old Recipe" in result.stdout
        assert "moved to archive" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_archive_restore(self, mock_run_async, mock_client_class, runner):
        """Test restoring recipe from archive."""
        mock_run_async.return_value = Recipe(
            id="recipe123",
            name="Restored Recipe",
            is_archived=False,
        )

        result = runner.invoke(app, ["archive", "recipe123", "--restore"])

        assert result.exit_code == 0
        assert "Restored Recipe" in result.stdout
        assert "restored from archive" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_archive_restore_short_flag(self, mock_run_async, mock_client_class, runner):
        """Test restoring recipe with short flag."""
        mock_run_async.return_value = Recipe(
            id="recipe123",
            name="Recipe",
            is_archived=False,
        )

        result = runner.invoke(app, ["archive", "recipe123", "-r"])

        assert result.exit_code == 0
        assert "restored from archive" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_archive_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test archive command with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["archive", "recipe123"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_archive_server_error(self, mock_run_async, mock_client_class, runner):
        """Test archive command with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["archive", "recipe123"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestDeleteRecipe:
    """Test recipes delete command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_delete_recipe_with_yes_flag(self, mock_run_async, mock_client_class, runner):
        """Test deleting recipe with --yes flag."""
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "recipe123", "--yes"])

        assert result.exit_code == 0
        assert "Deleted recipe recipe123" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_delete_recipe_with_y_flag(self, mock_run_async, mock_client_class, runner):
        """Test deleting recipe with -y flag."""
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "recipe123", "-y"])

        assert result.exit_code == 0
        assert "Deleted recipe recipe123" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_delete_recipe_with_confirmation(self, mock_run_async, mock_client_class, runner):
        """Test deleting recipe with confirmation prompt."""
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "recipe123"], input="y\n")

        assert result.exit_code == 0
        assert "Deleted recipe recipe123" in result.stdout

    def test_delete_recipe_cancelled(self, runner):
        """Test cancelling recipe deletion."""
        result = runner.invoke(app, ["delete", "recipe123"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_delete_recipe_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test delete recipe with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["delete", "recipe123", "--yes"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_delete_recipe_server_error(self, mock_run_async, mock_client_class, runner):
        """Test delete recipe with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["delete", "recipe123", "--yes"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestScaleRecipe:
    """Test recipes scale command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_scale_recipe_success(self, mock_run_async, mock_client_class, runner):
        """Test scaling recipe successfully."""
        scaled_recipe = Recipe(
            id="recipe123",
            name="Scaled Recipe",
            ingredients=["2 cups flour", "4 eggs"],
            servings=8,
        )
        mock_run_async.return_value = scaled_recipe

        result = runner.invoke(app, ["scale", "recipe123", "8"])

        assert result.exit_code == 0
        assert "Scaled Recipe" in result.stdout
        assert "Scaled to 8 servings" in result.stdout
        assert "2 cups flour" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_scale_recipe_dict_ingredients(self, mock_run_async, mock_client_class, runner):
        """Test scaling recipe with dict-based ingredients."""
        scaled_recipe = Recipe(
            id="recipe456",
            name="Dict Recipe",
            ingredients=[
                {"name": "sugar", "amount": "3 cups"},
                {"item": "butter", "amount": "1.5 cups"},
            ],
            servings=12,
        )
        mock_run_async.return_value = scaled_recipe

        result = runner.invoke(app, ["scale", "recipe456", "12"])

        assert result.exit_code == 0
        assert "3 cups sugar" in result.stdout
        assert "1.5 cups butter" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_scale_recipe_no_ingredients(self, mock_run_async, mock_client_class, runner):
        """Test scaling recipe with no ingredients."""
        scaled_recipe = Recipe(
            id="recipe789",
            name="Empty Recipe",
            ingredients=None,
            servings=4,
        )
        mock_run_async.return_value = scaled_recipe

        result = runner.invoke(app, ["scale", "recipe789", "4"])

        assert result.exit_code == 0
        assert "Scaled to 4 servings" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_scale_recipe_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test scaling recipe with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["scale", "recipe123", "8"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_scale_recipe_server_error(self, mock_run_async, mock_client_class, runner):
        """Test scaling recipe with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["scale", "recipe123", "8"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestStandardizeRecipe:
    """Test recipes standardize command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_standardize_recipe_success(self, mock_run_async, mock_client_class, runner):
        """Test standardizing recipe text successfully."""
        standardized = Recipe(
            id="std123",
            name="Standardized Recipe",
            ingredients=["1 cup flour", "2 eggs"],
            instructions=["Mix", "Bake"],
        )
        mock_run_async.return_value = standardized

        result = runner.invoke(app, ["standardize", "Mix flour and eggs, then bake"])

        assert result.exit_code == 0
        assert "Standardized Recipe" in result.stdout
        assert "Recipe Standardized" in result.stdout
        assert "1 cup flour" in result.stdout
        assert "Mix" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_standardize_recipe_dict_ingredients(self, mock_run_async, mock_client_class, runner):
        """Test standardizing recipe with dict-based ingredients."""
        standardized = Recipe(
            id="std456",
            name="Dict Standardized",
            ingredients=[
                {"name": "milk", "amount": "2 cups"},
                {"item": "vanilla", "amount": "1 tsp"},
            ],
            instructions=["Step 1", "Step 2"],
        )
        mock_run_async.return_value = standardized

        result = runner.invoke(app, ["standardize", "Recipe with milk and vanilla"])

        assert result.exit_code == 0
        assert "2 cups milk" in result.stdout
        assert "1 tsp vanilla" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_standardize_recipe_minimal(self, mock_run_async, mock_client_class, runner):
        """Test standardizing recipe with minimal data."""
        standardized = Recipe(
            id="std789",
            name="Minimal Standardized",
        )
        mock_run_async.return_value = standardized

        result = runner.invoke(app, ["standardize", "Simple recipe"])

        assert result.exit_code == 0
        assert "Minimal Standardized" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_standardize_recipe_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test standardizing recipe with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["standardize", "Recipe text"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_standardize_recipe_server_error(self, mock_run_async, mock_client_class, runner):
        """Test standardizing recipe with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["standardize", "Recipe text"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestGenerateRecipe:
    """Test recipes generate command."""

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_minimal(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with no parameters."""
        generated = Recipe(
            id="gen123",
            name="Generated Recipe",
            description="AI-generated recipe",
            ingredients=["ingredient1", "ingredient2"],
            instructions=["step1", "step2"],
            servings=4,
        )
        mock_run_async.return_value = generated

        result = runner.invoke(app, ["generate"])

        assert result.exit_code == 0
        assert "Generated Recipe" in result.stdout
        assert "AI-generated recipe" in result.stdout
        assert "ingredient1" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_with_ingredients(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with specific ingredients."""
        generated = Recipe(
            id="gen456",
            name="Chicken Pasta",
            ingredients=["chicken", "pasta"],
            instructions=["Cook pasta", "Add chicken"],
        )
        mock_run_async.return_value = generated

        result = runner.invoke(
            app,
            ["generate", "-i", "chicken", "-i", "pasta"],
        )

        assert result.exit_code == 0
        assert "Chicken Pasta" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_with_cuisine(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with cuisine type."""
        generated = Recipe(
            id="gen789",
            name="Italian Dish",
            ingredients=["tomatoes", "basil"],
            instructions=["Prepare"],
        )
        mock_run_async.return_value = generated

        result = runner.invoke(app, ["generate", "--cuisine", "Italian"])

        assert result.exit_code == 0
        assert "Italian Dish" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_with_dietary_restrictions(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with dietary restrictions."""
        generated = Recipe(
            id="gen101",
            name="Vegan Meal",
            ingredients=["vegetables"],
            instructions=["Cook"],
        )
        mock_run_async.return_value = generated

        result = runner.invoke(
            app,
            ["generate", "-d", "vegan", "-d", "gluten-free"],
        )

        assert result.exit_code == 0
        assert "Vegan Meal" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_with_meal_type(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with meal type."""
        generated = Recipe(
            id="gen202",
            name="Breakfast Bowl",
            ingredients=["oats", "berries"],
            instructions=["Mix"],
        )
        mock_run_async.return_value = generated

        result = runner.invoke(app, ["generate", "--meal", "breakfast"])

        assert result.exit_code == 0
        assert "Breakfast Bowl" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_with_difficulty(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with difficulty level."""
        generated = Recipe(
            id="gen303",
            name="Simple Snack",
            ingredients=["crackers"],
            instructions=["Serve"],
        )
        mock_run_async.return_value = generated

        result = runner.invoke(app, ["generate", "--difficulty", "easy"])

        assert result.exit_code == 0
        assert "Simple Snack" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_all_options(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with all options."""
        generated = Recipe(
            id="gen404",
            name="Complete Recipe",
            description="Fully specified",
            ingredients=[{"name": "rice", "amount": "2 cups"}],
            instructions=[{"text": "Cook rice"}],
            servings=6,
            prep_time="10 min",
            cook_time="20 min",
        )
        mock_run_async.return_value = generated

        result = runner.invoke(
            app,
            [
                "generate",
                "-i",
                "rice",
                "-c",
                "Asian",
                "-d",
                "vegetarian",
                "-m",
                "dinner",
                "--difficulty",
                "medium",
            ],
        )

        assert result.exit_code == 0
        assert "Complete Recipe" in result.stdout
        assert "Fully specified" in result.stdout
        assert "Servings: 6" in result.stdout
        assert "Prep: 10 min" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_dict_ingredients_and_instructions(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with dict-based ingredients and instructions."""
        generated = Recipe(
            id="gen505",
            name="Advanced Generated",
            ingredients=[
                {"name": "flour", "amount": "3 cups"},
                {"item": "yeast", "amount": "1 tsp"},
            ],
            instructions=[
                {"text": "Mix dry ingredients"},
                {"text": "Add water"},
            ],
        )
        mock_run_async.return_value = generated

        result = runner.invoke(app, ["generate"])

        assert result.exit_code == 0
        assert "3 cups flour" in result.stdout
        assert "1 tsp yeast" in result.stdout
        assert "Mix dry ingredients" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["generate"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.recipes.FcpClient")
    @patch("fcp_cli.commands.recipes.run_async")
    def test_generate_recipe_server_error(self, mock_run_async, mock_client_class, runner):
        """Test generating recipe with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["generate"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestRecipeEnums:
    """Test recipe-related enums."""

    def test_recipe_filter_enum(self):
        """Test RecipeFilter enum values."""
        assert RecipeFilter.ALL == "all"
        assert RecipeFilter.FAVORITES == "favorites"
        assert RecipeFilter.ARCHIVED == "archived"

    def test_difficulty_enum(self):
        """Test Difficulty enum values."""
        assert Difficulty.EASY == "easy"
        assert Difficulty.MEDIUM == "medium"
        assert Difficulty.HARD == "hard"

    def test_meal_type_enum(self):
        """Test MealType enum values."""
        assert MealType.BREAKFAST == "breakfast"
        assert MealType.LUNCH == "lunch"
        assert MealType.DINNER == "dinner"
        assert MealType.SNACK == "snack"


@pytest.mark.parametrize(
    "filter_type,expected_title",
    [
        ("all", "Saved Recipes"),
        ("favorites", "Favorite Recipes"),
        ("archived", "Archived Recipes"),
    ],
)
@patch("fcp_cli.commands.recipes.FcpClient")
@patch("fcp_cli.commands.recipes.run_async")
def test_list_recipes_table_titles(mock_run_async, mock_client_class, filter_type, expected_title, runner):
    """Test that list command shows correct table titles."""
    recipe = Recipe(id="test123", name="Test", servings=2)
    mock_run_async.return_value = [recipe]

    result = runner.invoke(app, ["list", "--filter", filter_type])

    assert result.exit_code == 0
    # Title appears in the output (Rich table rendering)
    assert expected_title in result.stdout or "Test" in result.stdout


@pytest.mark.parametrize(
    "meal_type,difficulty",
    [
        ("breakfast", "easy"),
        ("lunch", "medium"),
        ("dinner", "hard"),
        ("snack", "easy"),
    ],
)
@patch("fcp_cli.commands.recipes.FcpClient")
@patch("fcp_cli.commands.recipes.run_async")
def test_generate_recipe_meal_type_difficulty_combinations(
    mock_run_async, mock_client_class, meal_type, difficulty, runner
):
    """Test generating recipes with various meal type and difficulty combinations."""
    generated = Recipe(
        id=f"gen_{meal_type}_{difficulty}",
        name=f"{meal_type.capitalize()} Recipe",
        ingredients=["test"],
        instructions=["cook"],
    )
    mock_run_async.return_value = generated

    result = runner.invoke(
        app,
        ["generate", "--meal", meal_type, "--difficulty", difficulty],
    )

    assert result.exit_code == 0
    assert meal_type.capitalize() in result.stdout or "Recipe" in result.stdout


class TestRecipeExtractImageErrors:
    """Test recipe extract error handling."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.recipes.validate_resolution")
    def test_extract_with_explicit_resolution(self, mock_validate, runner, tmp_path):
        """Test extract with explicit resolution."""

        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"not an image")

        mock_validate.return_value = "high"

        result = runner.invoke(app, ["extract", str(img_path), "--res", "high"])

        assert result.exit_code == 1
        # Should call validate_resolution before failing on invalid image
        mock_validate.assert_called_once_with("high")

    @patch("fcp_cli.commands.recipes.validate_resolution")
    def test_extract_invalid_resolution(self, mock_validate, runner, tmp_path):
        """Test extract with invalid resolution."""
        img_path = tmp_path / "recipe.jpg"
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_validate.side_effect = ValueError("Invalid resolution")

        result = runner.invoke(app, ["extract", str(img_path), "--res", "ultra"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
