"""Tests for FcpRecipesMixin."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from fcp_cli.services.fcp import FcpClient
from fcp_cli.services.models import CottageLabel, Draft, Recipe

pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestRecipeOperations:
    """Test recipe CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_recipes(self):
        """Test getting all recipes."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "recipes": [
                    {"id": "1", "name": "Pizza", "servings": 4},
                    {"id": "2", "name": "Pasta", "servings": 2},
                ]
            }

            result = await client.get_recipes()

            assert len(result) == 2
            assert result[0]["name"] == "Pizza"
            mock_request.assert_called_once_with("GET", "/recipes", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_get_recipes_empty(self):
        """Test getting recipes when none exist."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"recipes": []}

            result = await client.get_recipes()

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_recipe(self):
        """Test getting a single recipe."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Spaghetti",
                "servings": 4,
                "ingredients": ["pasta", "tomatoes", "basil"],
            }

            result = await client.get_recipe("recipe123")

            assert isinstance(result, Recipe)
            assert result.id == "recipe123"
            assert result.name == "Spaghetti"
            mock_request.assert_called_once_with("GET", "/recipes/recipe123")

    @pytest.mark.asyncio
    async def test_get_recipes_filtered(self):
        """Test getting filtered recipes."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "recipes": [
                    {"id": "1", "name": "Pizza", "is_favorite": True},
                ]
            }

            result = await client.get_recipes_filtered(filter_type="favorites")

            assert len(result) == 1
            assert isinstance(result[0], Recipe)
            mock_request.assert_called_once_with(
                "GET",
                "/recipes",
                params={"user_id": "test-user", "filter": "favorites"},
            )

    @pytest.mark.asyncio
    async def test_create_recipe_minimal(self):
        """Test creating recipe with minimal fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "New Recipe",
            }

            result = await client.create_recipe(name="New Recipe")

            assert isinstance(result, Recipe)
            assert result.name == "New Recipe"
            mock_request.assert_called_once_with(
                "POST",
                "/recipes",
                json={"user_id": "test-user", "recipe_name": "New Recipe"},
            )

    @pytest.mark.asyncio
    async def test_create_recipe_full(self):
        """Test creating recipe with all fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Complete Recipe",
            }

            result = await client.create_recipe(
                name="Complete Recipe",
                ingredients=["flour", "eggs", "milk"],
                instructions=["Mix", "Bake"],
                servings=4,
                source="Family cookbook",
            )

            assert isinstance(result, Recipe)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["recipe_name"] == "Complete Recipe"
            assert call_json["ingredients"] == ["flour", "eggs", "milk"]
            assert call_json["instructions"] == ["Mix", "Bake"]
            assert call_json["servings"] == 4
            assert call_json["source"] == "Family cookbook"

    @pytest.mark.asyncio
    async def test_update_recipe_favorite(self):
        """Test updating recipe favorite status."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Pizza",
                "is_favorite": True,
            }

            result = await client.update_recipe("recipe123", is_favorite=True)

            assert isinstance(result, Recipe)
            assert result.is_favorite is True
            mock_request.assert_called_once_with(
                "PATCH",
                "/recipes/recipe123",
                json={"user_id": "test-user", "is_favorite": True},
            )

    @pytest.mark.asyncio
    async def test_update_recipe_archived(self):
        """Test updating recipe archived status."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Old Recipe",
                "is_archived": True,
            }

            result = await client.update_recipe("recipe123", is_archived=True)

            assert isinstance(result, Recipe)
            mock_request.assert_called_once_with(
                "PATCH",
                "/recipes/recipe123",
                json={"user_id": "test-user", "is_archived": True},
            )

    @pytest.mark.asyncio
    async def test_update_recipe_multiple_fields(self):
        """Test updating multiple recipe fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Recipe",
                "is_favorite": True,
                "is_archived": False,
            }

            result = await client.update_recipe("recipe123", is_favorite=True, is_archived=False)

            assert isinstance(result, Recipe)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["is_favorite"] is True
            assert call_json["is_archived"] is False

    @pytest.mark.asyncio
    async def test_delete_recipe(self):
        """Test deleting a recipe."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}

            result = await client.delete_recipe("recipe123")

            assert result is True
            mock_request.assert_called_once_with("DELETE", "/recipes/recipe123")


class TestRecipeScalingAndStandardization:
    """Test recipe scaling and standardization."""

    @pytest.mark.asyncio
    async def test_scale_recipe(self):
        """Test scaling a recipe."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Scaled Recipe",
                "servings": 8,
            }

            result = await client.scale_recipe("recipe123", target_servings=8)

            assert isinstance(result, Recipe)
            assert result.servings == 8
            mock_request.assert_called_once_with(
                "POST",
                "/scaling/scale-recipe",
                json={
                    "user_id": "test-user",
                    "recipe_id": "recipe123",
                    "target_servings": 8,
                },
            )

    @pytest.mark.asyncio
    async def test_standardize_recipe(self):
        """Test standardizing a recipe from raw text."""
        client = FcpClient(user_id="test-user")
        raw_text = "Mix 2 cups flour with 1 egg. Bake at 350F for 30 minutes."

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Standardized Recipe",
                "ingredients": ["2 cups flour", "1 egg"],
                "instructions": ["Mix ingredients", "Bake at 350F for 30 minutes"],
            }

            result = await client.standardize_recipe(raw_text)

            assert isinstance(result, Recipe)
            mock_request.assert_called_once_with(
                "POST",
                "/standardize-recipe",
                json={"user_id": "test-user", "raw_text": raw_text},
            )

    @pytest.mark.asyncio
    async def test_extract_recipe_from_image(self):
        """Test extracting recipe from image with default resolution."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_encoded_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "recipe": {
                    "name": "Extracted Recipe",
                    "ingredients": ["ingredient1", "ingredient2"],
                }
            }

            result = await client.extract_recipe_from_image(image_data)

            assert "recipe" in result
            call_json = mock_request.call_args[1]["json"]
            assert call_json["user_id"] == "test-user"
            assert call_json["image_base64"] == image_data
            assert call_json["media_resolution"] == "medium"

    @pytest.mark.asyncio
    async def test_extract_recipe_from_image_with_resolution(self):
        """Test extracting recipe from image with custom resolution."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_encoded_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"recipe": {"name": "Extracted Recipe"}}

            await client.extract_recipe_from_image(image_data, media_resolution="high")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["media_resolution"] == "high"

    @pytest.mark.asyncio
    async def test_parse_menu_with_resolution(self):
        """Test parsing menu with custom resolution."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_encoded_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": [{"name": "Pizza"}]}

            await client.parse_menu(image_data, restaurant_name="Test Restaurant", media_resolution="low")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["media_resolution"] == "low"
            assert call_json["restaurant_name"] == "Test Restaurant"

    @pytest.mark.asyncio
    async def test_parse_menu_default_resolution(self):
        """Test that parse_menu uses default medium resolution."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_encoded_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": []}

            await client.parse_menu(image_data)

            call_json = mock_request.call_args[1]["json"]
            assert call_json["media_resolution"] == "medium"

    @pytest.mark.asyncio
    async def test_generate_recipe(self):
        """Test generating a recipe."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "recipe123",
                "name": "Generated Recipe",
            }

            result = await client.generate_recipe(
                ingredients=["chicken", "rice"],
                cuisine="Asian",
                dietary_restrictions=["gluten-free"],
                meal_type="dinner",
                difficulty="easy",
            )

            assert isinstance(result, Recipe)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["ingredients"] == ["chicken", "rice"]
            assert call_json["cuisine"] == "Asian"
            assert call_json["dietary_restrictions"] == ["gluten-free"]


class TestDraftOperations:
    """Test content draft operations."""

    @pytest.mark.asyncio
    async def test_get_drafts(self):
        """Test getting all drafts."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "drafts": [
                    {"id": "1", "title": "Draft 1"},
                    {"id": "2", "title": "Draft 2"},
                ]
            }

            result = await client.get_drafts()

            assert len(result) == 2
            assert result[0]["title"] == "Draft 1"
            mock_request.assert_called_once_with("GET", "/publish/drafts", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_get_draft(self):
        """Test getting a single draft."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "draft123",
                "title": "My Draft",
                "content": "Draft content here",
            }

            result = await client.get_draft("draft123")

            assert isinstance(result, Draft)
            assert result.id == "draft123"
            assert result.title == "My Draft"
            mock_request.assert_called_once_with("GET", "/publish/drafts/draft123")

    @pytest.mark.asyncio
    async def test_update_draft_all_fields(self):
        """Test updating draft with all fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "draft123",
                "title": "Updated Title",
                "content": "Updated content",
                "status": "published",
            }

            result = await client.update_draft(
                "draft123",
                title="Updated Title",
                content="Updated content",
                status="published",
            )

            assert isinstance(result, Draft)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["title"] == "Updated Title"
            assert call_json["content"] == "Updated content"
            assert call_json["status"] == "published"

    @pytest.mark.asyncio
    async def test_update_draft_partial(self):
        """Test updating draft with only some fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "draft123",
                "title": "New Title",
            }

            result = await client.update_draft("draft123", title="New Title")

            assert isinstance(result, Draft)
            call_json = mock_request.call_args[1]["json"]
            assert "title" in call_json
            assert "content" not in call_json

    @pytest.mark.asyncio
    async def test_delete_draft(self):
        """Test deleting a draft."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}

            result = await client.delete_draft("draft123")

            assert result is True
            mock_request.assert_called_once_with("DELETE", "/publish/drafts/draft123")

    @pytest.mark.asyncio
    async def test_publish_draft(self):
        """Test publishing a draft."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": "published",
                "platforms": ["twitter", "instagram"],
            }

            result = await client.publish_draft(
                "draft123", platforms=["twitter", "instagram"], publish_immediately=True
            )

            assert result["status"] == "published"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["platforms"] == ["twitter", "instagram"]
            assert call_json["publish_immediately"] is True

    @pytest.mark.asyncio
    async def test_publish_draft_defaults(self):
        """Test publishing draft with default parameters."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "published"}

            await client.publish_draft("draft123")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["publish_immediately"] is True


class TestContentGeneration:
    """Test content generation operations."""

    @pytest.mark.asyncio
    async def test_generate_content_minimal(self):
        """Test generating content with minimal parameters."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "draft_id": "draft123",
                "content": "Generated content",
            }

            result = await client.generate_content(content_type="blog")

            assert "draft_id" in result
            call_json = mock_request.call_args[1]["json"]
            assert call_json["content_type"] == "blog"

    @pytest.mark.asyncio
    async def test_generate_content_with_logs(self):
        """Test generating content with specific log IDs."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"draft_id": "draft123"}

            await client.generate_content(content_type="social", log_ids=["log1", "log2"])

            call_json = mock_request.call_args[1]["json"]
            assert call_json["log_ids"] == ["log1", "log2"]

    @pytest.mark.asyncio
    async def test_get_published_content(self):
        """Test getting published content."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "content": [
                    {"id": "1", "title": "Post 1"},
                    {"id": "2", "title": "Post 2"},
                ]
            }

            result = await client.get_published_content()

            assert len(result) == 2
            mock_request.assert_called_once_with("GET", "/publish/published", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_get_published_content_alternate_key(self):
        """Test getting published content with alternate response key."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"published": [{"id": "1", "title": "Post 1"}]}

            result = await client.get_published_content()

            assert len(result) == 1


class TestParsingOperations:
    """Test parsing operations."""

    @pytest.mark.asyncio
    async def test_parse_receipt(self):
        """Test parsing a receipt."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "items": [
                    {"name": "Milk", "price": 3.99},
                    {"name": "Bread", "price": 2.50},
                ],
                "total": 6.49,
            }

            result = await client.parse_receipt(image_data)

            assert "items" in result
            assert result["total"] == 6.49
            mock_request.assert_called_once_with(
                "POST",
                "/parser/receipt",
                json={"user_id": "test-user", "image_base64": image_data},
            )

    @pytest.mark.asyncio
    async def test_parse_menu_without_restaurant(self):
        """Test parsing a menu without restaurant name."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": [{"name": "Burger", "price": 12.99}]}

            result = await client.parse_menu(image_data)

            assert "items" in result
            call_json = mock_request.call_args[1]["json"]
            assert "restaurant_name" not in call_json

    @pytest.mark.asyncio
    async def test_parse_menu_with_restaurant(self):
        """Test parsing a menu with restaurant name."""
        client = FcpClient(user_id="test-user")
        image_data = "base64_image_data"

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": []}

            await client.parse_menu(image_data, restaurant_name="Joe's Diner")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["restaurant_name"] == "Joe's Diner"


class TestCottageLabel:
    """Test cottage label generation."""

    @pytest.mark.asyncio
    async def test_generate_cottage_label_minimal(self):
        """Test generating cottage label with minimal fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "product_name": "Homemade Jam",
                "ingredients": ["strawberries", "sugar"],
                "allergen_warnings": [],
            }

            result = await client.generate_cottage_label(
                product_name="Homemade Jam",
                ingredients=["strawberries", "sugar"],
            )

            assert isinstance(result, CottageLabel)
            assert result.product_name == "Homemade Jam"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["is_refrigerated"] is False

    @pytest.mark.asyncio
    async def test_generate_cottage_label_full(self):
        """Test generating cottage label with all fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "product_name": "Homemade Jam",
                "ingredients": ["strawberries", "sugar"],
                "allergen_warnings": [],
                "net_weight": "8oz",
                "producer_info": "John's Kitchen",
            }

            result = await client.generate_cottage_label(
                product_name="Homemade Jam",
                ingredients=["strawberries", "sugar"],
                net_weight="8oz",
                business_name="John's Kitchen",
                business_address="123 Main St",
                is_refrigerated=True,
            )

            assert isinstance(result, CottageLabel)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["is_refrigerated"] is True
            assert call_json["net_weight"] == "8oz"
            assert call_json["business_name"] == "John's Kitchen"


class TestProductLookup:
    """Test product lookup operations."""

    @pytest.mark.asyncio
    async def test_lookup_product_by_barcode(self):
        """Test looking up product by barcode."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "name": "Test Product",
                "brand": "Test Brand",
                "barcode": "123456789",
            }

            result = await client.lookup_product_by_barcode("123456789")

            assert result["name"] == "Test Product"
            # Check that the barcode was URL-encoded in the path
            call_args = mock_request.call_args
            assert "/external/lookup-product/123456789" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_lookup_product_by_barcode_with_special_chars(self):
        """Test looking up product with special characters in barcode."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"name": "Test Product"}

            await client.lookup_product_by_barcode("ABC-123/456")

            # Verify URL encoding was applied
            call_args = mock_request.call_args
            path = call_args[0][1]
            assert "ABC-123/456" not in path  # Should be encoded
