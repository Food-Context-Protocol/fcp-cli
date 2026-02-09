"""Tests for FcpMealsMixin."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from fcp_cli.services.fcp import FcpClient
from fcp_cli.services.models import (
    FCP,
    MealSuggestion,
    SearchResult,
    TasteBuddyResult,
    TasteProfile,
    Venue,
)

pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestFoodLogOperations:
    """Test food log CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_food_logs(self):
        """Test getting food logs."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "logs": [
                    {"id": "1", "dish_name": "Pizza", "user_id": "test-user"},
                    {"id": "2", "dish_name": "Pasta", "user_id": "test-user"},
                ]
            }

            result = await client.get_food_logs(limit=10)

            assert len(result) == 2
            assert isinstance(result[0], FCP)
            assert result[0].dish_name == "Pizza"
            mock_request.assert_called_once_with("GET", "/meals", params={"user_id": "test-user", "limit": 10})

    @pytest.mark.asyncio
    async def test_get_food_logs_alternate_key(self):
        """Test getting food logs with alternate response key."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"meals": [{"id": "1", "dish_name": "Pizza", "user_id": "test-user"}]}

            result = await client.get_food_logs(limit=5)

            assert len(result) == 1
            assert isinstance(result[0], FCP)

    @pytest.mark.asyncio
    async def test_create_food_log_minimal(self):
        """Test creating food log with minimal fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Burger",
                "user_id": "test-user",
            }

            result = await client.create_food_log("Burger")

            assert isinstance(result, FCP)
            assert result.dish_name == "Burger"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["dish_name"] == "Burger"

    @pytest.mark.asyncio
    async def test_create_food_log_full(self):
        """Test creating food log with all fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Burger",
                "description": "Delicious burger",
                "meal_type": "lunch",
                "user_id": "test-user",
            }

            result = await client.create_food_log(
                "Burger",
                description="Delicious burger",
                meal_type="lunch",
                image_base64="image_data",
            )

            assert isinstance(result, FCP)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["description"] == "Delicious burger"
            assert call_json["meal_type"] == "lunch"
            assert call_json["image_base64"] == "image_data"

    @pytest.mark.asyncio
    async def test_log_meal_minimal(self):
        """Test logging meal with minimal fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Salad",
                "user_id": "test-user",
            }

            result = await client.log_meal("Salad")

            assert isinstance(result, FCP)
            call_json = mock_request.call_args[1]["json"]
            assert "nutrition" not in call_json

    @pytest.mark.asyncio
    async def test_log_meal_with_nutrition(self):
        """Test logging meal with nutrition information."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Salad",
                "user_id": "test-user",
            }

            result = await client.log_meal("Salad", calories=300, protein=20, carbs=30, fat=10)

            assert isinstance(result, FCP)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["nutrition"]["calories"] == 300
            assert call_json["nutrition"]["protein"] == 20

    @pytest.mark.asyncio
    async def test_log_meal_with_partial_nutrition(self):
        """Test logging meal with partial nutrition info."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Salad",
                "user_id": "test-user",
            }

            await client.log_meal("Salad", calories=300)

            call_json = mock_request.call_args[1]["json"]
            assert "nutrition" in call_json
            assert call_json["nutrition"]["calories"] == 300

    @pytest.mark.asyncio
    async def test_log_meal_with_meal_type_only(self):
        """Test logging meal with only meal_type and no nutrition."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Salad",
                "user_id": "test-user",
            }

            await client.log_meal("Salad", meal_type="lunch")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["meal_type"] == "lunch"
            # Nutrition should not be included when all values are None
            assert "nutrition" not in call_json

    @pytest.mark.asyncio
    async def test_get_food_log(self):
        """Test getting a single food log."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"meal": {"id": "log123", "dish_name": "Pizza", "user_id": "test-user"}}

            result = await client.get_food_log("log123")

            assert isinstance(result, FCP)
            assert result.id == "log123"
            mock_request.assert_called_once_with("GET", "/meals/log123")

    @pytest.mark.asyncio
    async def test_get_food_log_no_meal_key(self):
        """Test getting food log when response has no meal key."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Pizza",
                "user_id": "test-user",
            }

            result = await client.get_food_log("log123")

            assert isinstance(result, FCP)
            assert result.id == "log123"

    @pytest.mark.asyncio
    async def test_update_food_log_all_fields(self):
        """Test updating food log with all fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Updated Pizza",
                "user_id": "test-user",
            }

            result = await client.update_food_log(
                "log123",
                dish_name="Updated Pizza",
                description="Very tasty",
                meal_type="dinner",
                venue_name="Pizza Place",
            )

            assert isinstance(result, FCP)
            call_json = mock_request.call_args[1]["json"]
            assert call_json["dish_name"] == "Updated Pizza"
            assert call_json["notes"] == "Very tasty"
            assert call_json["meal_type"] == "dinner"
            assert call_json["venue_name"] == "Pizza Place"

    @pytest.mark.asyncio
    async def test_update_food_log_partial(self):
        """Test updating food log with only some fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "log123",
                "dish_name": "Pizza",
                "user_id": "test-user",
            }

            await client.update_food_log("log123", dish_name="Pizza")

            call_json = mock_request.call_args[1]["json"]
            assert "dish_name" in call_json
            assert "notes" not in call_json

    @pytest.mark.asyncio
    async def test_delete_food_log(self):
        """Test deleting a food log."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}

            result = await client.delete_food_log("log123")

            assert result is True
            mock_request.assert_called_once_with("DELETE", "/meals/log123")


class TestSearchOperations:
    """Test search operations."""

    @pytest.mark.asyncio
    async def test_search_meals(self):
        """Test searching meals by query."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "results": [
                    {"id": "1", "dish_name": "Pizza", "user_id": "test-user"},
                    {"id": "2", "dish_name": "Pasta", "user_id": "test-user"},
                ],
                "total": 2,
            }

            result = await client.search_meals("pizza", limit=10)

            assert isinstance(result, SearchResult)
            assert len(result.logs) == 2
            assert result.total == 2
            assert result.query == "pizza"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["query"] == "pizza"
            assert call_json["limit"] == 10

    @pytest.mark.asyncio
    async def test_search_meals_no_total(self):
        """Test searching meals when response has no total."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"results": [{"id": "1", "dish_name": "Pizza", "user_id": "test-user"}]}

            result = await client.search_meals("pizza")

            assert result.total == 1  # Falls back to length

    @pytest.mark.asyncio
    async def test_search_meals_by_date_single_date(self):
        """Test searching meals by single date."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "results": [{"id": "1", "dish_name": "Pizza", "user_id": "test-user"}],
                "total": 1,
            }

            result = await client.search_meals_by_date("2026-02-08")

            assert isinstance(result, SearchResult)
            assert "date:2026-02-08" in result.query
            call_json = mock_request.call_args[1]["json"]
            assert call_json["start_date"] == "2026-02-08"
            assert call_json["end_date"] == "2026-02-08"

    @pytest.mark.asyncio
    async def test_search_meals_by_date_range(self):
        """Test searching meals by date range."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"results": [], "total": 0}

            result = await client.search_meals_by_date("2026-02-01", end_date="2026-02-08")

            assert "to 2026-02-08" in result.query
            call_json = mock_request.call_args[1]["json"]
            assert call_json["start_date"] == "2026-02-01"
            assert call_json["end_date"] == "2026-02-08"


class TestProfileAndAnalytics:
    """Test profile and analytics operations."""

    @pytest.mark.asyncio
    async def test_get_taste_profile(self):
        """Test getting taste profile."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "userId": "test-user",
                "favoriteCuisines": ["Italian", "Japanese"],
                "preferredIngredients": ["pasta", "rice"],
                "dislikedIngredients": ["olives"],
                "dietaryRestrictions": ["vegetarian"],
                "averageCalories": 2000.0,
            }

            result = await client.get_taste_profile()

            assert isinstance(result, TasteProfile)
            assert "Italian" in result.favorite_cuisines
            assert "vegetarian" in result.dietary_restrictions
            mock_request.assert_called_once_with("GET", "/profile", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_analyze_image(self):
        """Test analyzing an image."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "dish_name": "Pizza",
                "ingredients": ["cheese", "tomato", "dough"],
            }

            result = await client.analyze_image("image_data")

            assert result["dish_name"] == "Pizza"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["image_base64"] == "image_data"
            assert "thinking_level" not in call_json

    @pytest.mark.asyncio
    async def test_analyze_image_with_thinking_level(self):
        """Test analyzing image with thinking level."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"dish_name": "Pizza"}

            await client.analyze_image("image_data", thinking_level="deep")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["thinking_level"] == "deep"

    @pytest.mark.asyncio
    async def test_analyze_image_with_media_resolution(self):
        """Test analyzing image with custom media resolution."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"dish_name": "Pizza"}

            await client.analyze_image("image_data", media_resolution="high")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["media_resolution"] == "high"

    @pytest.mark.asyncio
    async def test_analyze_image_default_resolution(self):
        """Test that analyze_image uses default medium resolution."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"dish_name": "Pizza"}

            await client.analyze_image("image_data")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["media_resolution"] == "medium"

    @pytest.mark.asyncio
    async def test_get_food_stats_default(self):
        """Test getting food stats with defaults."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"stats": {"total_meals": 100}}

            result = await client.get_food_stats()

            assert result["stats"]["total_meals"] == 100
            call_params = mock_request.call_args[1]["params"]
            assert call_params["days"] == 30

    @pytest.mark.asyncio
    async def test_get_food_stats_week(self):
        """Test getting food stats for week."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"stats": {}}

            await client.get_food_stats(period="week", group_by="cuisine")

            call_params = mock_request.call_args[1]["params"]
            assert call_params["days"] == 7

    @pytest.mark.asyncio
    async def test_get_food_stats_year(self):
        """Test getting food stats for year."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"stats": {}}

            await client.get_food_stats(period="year")

            call_params = mock_request.call_args[1]["params"]
            assert call_params["days"] == 365

    @pytest.mark.asyncio
    async def test_get_lifetime_stats(self):
        """Test getting lifetime stats."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "total_meals": 500,
                "favorite_dish": "Pizza",
            }

            result = await client.get_lifetime_stats()

            assert result["total_meals"] == 500
            mock_request.assert_called_once_with("GET", "/profile/lifetime", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_get_nutrition_analytics(self):
        """Test getting nutrition analytics."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"avg_calories": 2000, "avg_protein": 80}

            result = await client.get_nutrition_analytics(days=14)

            assert result["avg_calories"] == 2000
            call_json = mock_request.call_args[1]["json"]
            assert call_json["days"] == 14


class TestFlavorAndSafety:
    """Test flavor and safety operations."""

    @pytest.mark.asyncio
    async def test_get_flavor_pairings(self):
        """Test getting flavor pairings."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"pairings": ["basil", "garlic", "tomato", "olive oil", "mozzarella"]}

            result = await client.get_flavor_pairings("tomato", count=5)

            assert len(result) == 5
            assert "basil" in result
            call_params = mock_request.call_args[1]["params"]
            assert call_params["subject"] == "tomato"

    @pytest.mark.asyncio
    async def test_get_flavor_pairings_no_limit(self):
        """Test getting flavor pairings without count limit."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"pairings": ["basil", "garlic", "tomato", "olive oil", "mozzarella"]}

            result = await client.get_flavor_pairings("tomato", count=0)

            assert len(result) == 5  # All pairings returned

    @pytest.mark.asyncio
    async def test_check_food_recalls(self):
        """Test checking food recalls."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"recalls": [{"item": "Spinach", "reason": "Contamination"}]}

            result = await client.check_food_recalls(["spinach", "lettuce"])

            assert len(result["recalls"]) == 1
            call_json = mock_request.call_args[1]["json"]
            assert call_json["food_items"] == ["spinach", "lettuce"]

    @pytest.mark.asyncio
    async def test_check_drug_interactions(self):
        """Test checking drug interactions."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"interactions": []}

            result = await client.check_drug_interactions(["grapefruit"], ["statins"])

            assert "interactions" in result
            call_json = mock_request.call_args[1]["json"]
            assert call_json["food_items"] == ["grapefruit"]
            assert call_json["medications"] == ["statins"]

    @pytest.mark.asyncio
    async def test_check_allergen_alerts(self):
        """Test checking allergen alerts."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"alerts": [{"food": "Peanut Butter", "allergen": "peanuts"}]}

            result = await client.check_allergen_alerts(["peanut butter", "bread"], ["peanuts"])

            assert len(result["alerts"]) == 1
            call_json = mock_request.call_args[1]["json"]
            assert call_json["allergies"] == ["peanuts"]

    @pytest.mark.asyncio
    async def test_get_restaurant_safety_info(self):
        """Test getting restaurant safety info."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"safety_score": "A", "violations": []}

            result = await client.get_restaurant_safety_info("Joe's Diner", location="New York")

            assert result["safety_score"] == "A"
            call_params = mock_request.call_args[1]["params"]
            assert call_params["location"] == "New York"

    @pytest.mark.asyncio
    async def test_get_restaurant_safety_info_no_location(self):
        """Test getting restaurant safety info without location."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"safety_score": "A"}

            await client.get_restaurant_safety_info("Joe's Diner")

            # Verify params is None when no location
            call_args = mock_request.call_args[1]
            assert call_args["params"] is None


class TestDiscoveryOperations:
    """Test discovery operations."""

    @pytest.mark.asyncio
    async def test_discover_food(self):
        """Test discovering food."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"insight": "Try quinoa salad today!"}

            result = await client.discover_food()

            assert "insight" in result
            mock_request.assert_called_once_with("GET", "/agents/daily-insight", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_discover_restaurants_with_coords(self):
        """Test discovering restaurants with coordinates."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "restaurants": [{"name": "Joe's Diner"}],
                "resolved_location": "123 Main St",
            }

            result, location = await client.discover_restaurants(latitude=40.7128, longitude=-74.0060)

            assert "restaurants" in result
            assert location == "123 Main St"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["latitude"] == 40.7128
            assert call_json["longitude"] == -74.0060

    @pytest.mark.asyncio
    async def test_discover_restaurants_with_location_string(self):
        """Test discovering restaurants with location string."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"restaurants": [], "resolved_location": None}

            result, location = await client.discover_restaurants(location="New York, NY")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["location"] == "New York, NY"
            assert "latitude" not in call_json

    @pytest.mark.asyncio
    async def test_discover_restaurants_no_location(self):
        """Test discovering restaurants without location raises error."""
        client = FcpClient(user_id="test-user")

        with pytest.raises(ValueError, match="Either \\(latitude, longitude\\) or location must be provided"):
            await client.discover_restaurants()

    @pytest.mark.asyncio
    async def test_discover_recipes(self):
        """Test discovering recipes."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"recipes": [{"name": "Pasta Primavera"}]}

            result = await client.discover_recipes(["pasta", "vegetables"])

            assert "recipes" in result
            call_json = mock_request.call_args[1]["json"]
            assert call_json["available_ingredients"] == ["pasta", "vegetables"]


class TestMealSuggestions:
    """Test meal suggestion operations."""

    @pytest.mark.asyncio
    async def test_suggest_meals(self):
        """Test getting meal suggestions."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "suggestions": [
                    {"name": "Pizza", "reason": "You loved it last week"},
                    {"name": "Salad", "reason": "Healthy option"},
                ]
            }

            result = await client.suggest_meals()

            assert len(result) == 2
            assert isinstance(result[0], MealSuggestion)
            assert result[0].name == "Pizza"

    @pytest.mark.asyncio
    async def test_suggest_meals_with_context(self):
        """Test suggesting meals with context."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"suggestions": []}

            await client.suggest_meals(context="dinner", exclude_recent_days=7)

            call_json = mock_request.call_args[1]["json"]
            assert call_json["context"] == "dinner"
            assert call_json["exclude_recent_days"] == 7

    @pytest.mark.asyncio
    async def test_check_taste_buddy(self):
        """Test checking taste buddy compatibility."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "is_safe": True,
                "is_compliant": True,
                "detected_allergens": [],
                "diet_conflicts": [],
            }

            result = await client.check_taste_buddy(
                "Pizza",
                ingredients=["cheese", "tomato"],
                user_allergies=["peanuts"],
                user_diet=["vegetarian"],
            )

            assert isinstance(result, TasteBuddyResult)
            assert result.is_safe is True
            call_json = mock_request.call_args[1]["json"]
            assert call_json["dish_name"] == "Pizza"
            assert call_json["user_allergies"] == ["peanuts"]

    @pytest.mark.asyncio
    async def test_check_taste_buddy_minimal(self):
        """Test taste buddy with minimal parameters."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"is_safe": True, "is_compliant": True}

            await client.check_taste_buddy("Pizza")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["ingredients"] == []
            assert call_json["user_allergies"] == []


class TestVenueOperations:
    """Test venue operations."""

    @pytest.mark.asyncio
    async def test_find_nearby_venues_with_coords(self):
        """Test finding nearby venues with coordinates."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "venues": [
                    {"name": "Joe's Diner", "distance": 500, "rating": 4.5},
                    {"name": "Pizza Place", "distance": 1000, "rating": 4.0},
                ],
                "resolved_location": "123 Main St",
            }

            venues, location = await client.find_nearby_venues(latitude=40.7128, longitude=-74.0060)

            assert len(venues) == 2
            assert isinstance(venues[0], Venue)
            assert venues[0].name == "Joe's Diner"
            assert location == "123 Main St"

    @pytest.mark.asyncio
    async def test_find_nearby_venues_with_location(self):
        """Test finding nearby venues with location string."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"venues": [], "resolved_location": None}

            venues, location = await client.find_nearby_venues(location="New York")

            call_json = mock_request.call_args[1]["json"]
            assert call_json["location"] == "New York"

    @pytest.mark.asyncio
    async def test_find_nearby_venues_with_type(self):
        """Test finding nearby venues with specific type."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"venues": []}

            await client.find_nearby_venues(
                latitude=40.7128,
                longitude=-74.0060,
                venue_type="pizza",
                radius=5000,
            )

            call_json = mock_request.call_args[1]["json"]
            assert call_json["food_type"] == "pizza"
            assert call_json["radius"] == 5000

    @pytest.mark.asyncio
    async def test_find_nearby_venues_no_location(self):
        """Test finding venues without location raises error."""
        client = FcpClient(user_id="test-user")

        with pytest.raises(ValueError, match="Either \\(latitude, longitude\\) or location must be provided"):
            await client.find_nearby_venues()

    @pytest.mark.asyncio
    async def test_find_nearby_venues_results_key(self):
        """Test finding venues with alternate response key."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"results": [{"name": "Joe's Diner", "distance": 500}]}

            venues, _ = await client.find_nearby_venues(location="New York")

            assert len(venues) == 1


class TestMiscellaneous:
    """Test miscellaneous operations."""

    @pytest.mark.asyncio
    async def test_donate_meal(self):
        """Test donating a meal."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "donated", "impact": "1 meal"}

            result = await client.donate_meal("log123", organization="Food Bank")

            assert result["status"] == "donated"
            call_json = mock_request.call_args[1]["json"]
            assert call_json["log_id"] == "log123"
            assert call_json["organization"] == "Food Bank"

    @pytest.mark.asyncio
    async def test_donate_meal_no_organization(self):
        """Test donating meal without specifying organization."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "donated"}

            await client.donate_meal("log123")

            call_json = mock_request.call_args[1]["json"]
            assert "organization" not in call_json

    @pytest.mark.asyncio
    async def test_get_dietitian_report(self):
        """Test getting dietitian report."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"report": "Your diet is balanced"}

            result = await client.get_dietitian_report(days=14, focus_area="protein")

            assert "report" in result
            call_params = mock_request.call_args[1]["params"]
            assert call_params["days"] == 14
            assert call_params["focus_area"] == "protein"

    @pytest.mark.asyncio
    async def test_get_dietitian_report_defaults(self):
        """Test getting dietitian report with defaults."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"report": "Good"}

            await client.get_dietitian_report()

            call_params = mock_request.call_args[1]["params"]
            assert call_params["days"] == 7
            assert "focus_area" not in call_params

    @pytest.mark.asyncio
    async def test_get_food_trends(self):
        """Test getting food trends."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"trends": ["plant-based", "fermented"]}

            result = await client.get_food_trends(region="US", cuisine_focus="Asian")

            assert "trends" in result
            call_params = mock_request.call_args[1]["params"]
            assert call_params["region"] == "US"
            assert call_params["cuisine_focus"] == "Asian"

    @pytest.mark.asyncio
    async def test_get_random_tip(self):
        """Test getting random food tip."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"tip": "Drink more water"}

            result = await client.get_random_tip()

            assert result["tip"] == "Drink more water"
            mock_request.assert_called_once_with("GET", "/agents/food-tip", params={"user_id": "test-user"})

    @pytest.mark.asyncio
    async def test_get_streak(self):
        """Test getting logging streak."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"streak": 7, "active": True}

            result = await client.get_streak(streak_days=7)

            assert result["streak"] == 7
            mock_request.assert_called_once_with("GET", "/agents/streak/7", params={"user_id": "test-user"})
