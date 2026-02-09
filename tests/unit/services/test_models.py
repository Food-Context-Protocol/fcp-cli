"""Tests for data models."""

from __future__ import annotations

from datetime import datetime

import pytest

from fcp_cli.services.models import (
    FCP,
    CottageLabel,
    Draft,
    MealSuggestion,
    PantryItem,
    Recipe,
    SearchResult,
    TasteBuddyResult,
    TasteProfile,
    Venue,
)

pytestmark = pytest.mark.unit


class TestFCPModel:
    """Test FCP (food log) model."""

    def test_from_dict_minimal(self):
        """Test creating FCP from minimal dict."""
        data = {"id": "log123", "userId": "user456", "dishName": "Pizza"}
        fcp = FCP.from_dict(data)

        assert fcp.id == "log123"
        assert fcp.user_id == "user456"
        assert fcp.dish_name == "Pizza"
        assert fcp.description is None
        assert fcp.meal_type is None

    def test_from_dict_full(self):
        """Test creating FCP from full dict."""
        data = {
            "id": "log123",
            "userId": "user456",
            "dishName": "Pizza",
            "description": "Delicious",
            "mealType": "dinner",
            "ingredients": ["cheese", "tomato"],
            "nutrition": {"calories": 800},
            "timestamp": "2026-02-08T12:00:00Z",
            "imageUrl": "https://example.com/image.jpg",
        }
        fcp = FCP.from_dict(data)

        assert fcp.description == "Delicious"
        assert fcp.meal_type == "dinner"
        assert fcp.ingredients == ["cheese", "tomato"]
        assert fcp.nutrition == {"calories": 800}
        assert isinstance(fcp.timestamp, datetime)
        assert fcp.image_url == "https://example.com/image.jpg"

    def test_from_dict_snake_case(self):
        """Test creating FCP from snake_case dict."""
        data = {
            "id": "log123",
            "user_id": "user456",
            "dish_name": "Pizza",
            "meal_type": "dinner",
            "image_url": "https://example.com/image.jpg",
        }
        fcp = FCP.from_dict(data)

        assert fcp.user_id == "user456"
        assert fcp.dish_name == "Pizza"
        assert fcp.meal_type == "dinner"
        assert fcp.image_url == "https://example.com/image.jpg"

    def test_from_dict_invalid_timestamp(self):
        """Test creating FCP with invalid timestamp."""
        data = {
            "id": "log123",
            "userId": "user456",
            "dishName": "Pizza",
            "timestamp": "invalid-date",
        }
        fcp = FCP.from_dict(data)

        assert fcp.timestamp is None

    def test_from_dict_empty_fields(self):
        """Test creating FCP with empty required fields."""
        data = {}
        fcp = FCP.from_dict(data)

        assert fcp.id == ""
        assert fcp.user_id == ""
        assert fcp.dish_name == ""


class TestTasteProfileModel:
    """Test TasteProfile model."""

    def test_from_dict_camelcase(self):
        """Test creating TasteProfile from camelCase dict."""
        data = {
            "userId": "user123",
            "favoriteCuisines": ["Italian", "Japanese"],
            "preferredIngredients": ["pasta", "rice"],
            "dislikedIngredients": ["olives"],
            "dietaryRestrictions": ["vegetarian"],
            "averageCalories": 2000.5,
            "mealPatterns": {"breakfast": "light"},
        }
        profile = TasteProfile.from_dict(data)

        assert profile.user_id == "user123"
        assert profile.favorite_cuisines == ["Italian", "Japanese"]
        assert profile.preferred_ingredients == ["pasta", "rice"]
        assert profile.disliked_ingredients == ["olives"]
        assert profile.dietary_restrictions == ["vegetarian"]
        assert profile.average_calories == 2000.5
        assert profile.meal_patterns == {"breakfast": "light"}

    def test_from_dict_snake_case(self):
        """Test creating TasteProfile from snake_case dict."""
        data = {
            "user_id": "user123",
            "favorite_cuisines": ["Italian"],
            "preferred_ingredients": ["pasta"],
            "disliked_ingredients": ["olives"],
            "dietary_restrictions": ["vegetarian"],
            "average_calories": 2000.0,
            "meal_patterns": {},
        }
        profile = TasteProfile.from_dict(data)

        assert profile.user_id == "user123"
        assert profile.favorite_cuisines == ["Italian"]

    def test_from_dict_empty_lists(self):
        """Test creating TasteProfile with empty lists."""
        data = {}
        profile = TasteProfile.from_dict(data)

        assert profile.user_id == ""
        assert profile.favorite_cuisines == []
        assert profile.preferred_ingredients == []
        assert profile.disliked_ingredients == []
        assert profile.dietary_restrictions == []


class TestSearchResultModel:
    """Test SearchResult model."""

    def test_search_result_creation(self):
        """Test creating SearchResult."""
        logs = [
            FCP(id="1", user_id="user", dish_name="Pizza"),
            FCP(id="2", user_id="user", dish_name="Pasta"),
        ]
        result = SearchResult(logs=logs, total=2, query="italian")

        assert len(result.logs) == 2
        assert result.total == 2
        assert result.query == "italian"


class TestPantryItemModel:
    """Test PantryItem model."""

    def test_from_dict_full(self):
        """Test creating PantryItem from full dict."""
        data = {
            "id": "item123",
            "name": "Milk",
            "quantity": "1L",
            "category": "Dairy",
            "storageLocation": "Fridge",
            "expirationDate": "2026-02-15",
            "userId": "user123",
        }
        item = PantryItem.from_dict(data)

        assert item.id == "item123"
        assert item.name == "Milk"
        assert item.quantity == "1L"
        assert item.category == "Dairy"
        assert item.storage_location == "Fridge"
        assert item.expiration_date == "2026-02-15"
        assert item.user_id == "user123"

    def test_from_dict_snake_case(self):
        """Test creating PantryItem from snake_case dict."""
        data = {
            "id": "item123",
            "item_name": "Eggs",
            "storage_location": "Fridge",
            "expiry_date": "2026-02-20",
            "user_id": "user123",
        }
        item = PantryItem.from_dict(data)

        assert item.name == "Eggs"
        assert item.storage_location == "Fridge"
        assert item.expiration_date == "2026-02-20"

    def test_from_dict_minimal(self):
        """Test creating PantryItem with minimal data."""
        data = {"id": "item123", "name": "Flour"}
        item = PantryItem.from_dict(data)

        assert item.id == "item123"
        assert item.name == "Flour"
        assert item.quantity is None
        assert item.category is None


class TestRecipeModel:
    """Test Recipe model."""

    def test_from_dict_camelcase(self):
        """Test creating Recipe from camelCase dict."""
        data = {
            "id": "recipe123",
            "recipeName": "Spaghetti",
            "description": "Italian classic",
            "ingredients": ["pasta", "tomatoes"],
            "instructions": ["Boil water", "Cook pasta"],
            "servings": 4,
            "source": "Family recipe",
            "prepTime": "10min",
            "cookTime": "20min",
            "isFavorite": True,
            "isArchived": False,
            "userId": "user123",
        }
        recipe = Recipe.from_dict(data)

        assert recipe.id == "recipe123"
        assert recipe.name == "Spaghetti"
        assert recipe.description == "Italian classic"
        assert recipe.servings == 4
        assert recipe.prep_time == "10min"
        assert recipe.cook_time == "20min"
        assert recipe.is_favorite is True
        assert recipe.is_archived is False

    def test_from_dict_alternate_keys(self):
        """Test creating Recipe with alternate field names."""
        data = {
            "id": "recipe123",
            "name": "Pizza",
            "ingredientsList": ["dough", "cheese"],
            "steps": ["Make dough", "Add toppings"],
            "prep_time": "15min",
            "cook_time": "25min",
            "is_favorite": True,
            "is_archived": True,
            "user_id": "user123",
        }
        recipe = Recipe.from_dict(data)

        assert recipe.name == "Pizza"
        assert recipe.ingredients == ["dough", "cheese"]
        assert recipe.instructions == ["Make dough", "Add toppings"]
        assert recipe.is_favorite is True
        assert recipe.is_archived is True

    def test_from_dict_default_booleans(self):
        """Test Recipe default boolean values."""
        data = {"id": "recipe123", "name": "Soup"}
        recipe = Recipe.from_dict(data)

        assert recipe.is_favorite is False
        assert recipe.is_archived is False


class TestDraftModel:
    """Test Draft model."""

    def test_from_dict_camelcase(self):
        """Test creating Draft from camelCase dict."""
        data = {
            "id": "draft123",
            "title": "My Post",
            "content": "Content here",
            "contentType": "blog",
            "status": "draft",
            "platforms": ["twitter", "instagram"],
            "userId": "user123",
        }
        draft = Draft.from_dict(data)

        assert draft.id == "draft123"
        assert draft.title == "My Post"
        assert draft.content == "Content here"
        assert draft.content_type == "blog"
        assert draft.status == "draft"
        assert draft.platforms == ["twitter", "instagram"]

    def test_from_dict_alternate_keys(self):
        """Test creating Draft with alternate keys."""
        data = {
            "id": "draft123",
            "title": "Post",
            "body": "Body content",
            "type": "social",
            "user_id": "user123",
        }
        draft = Draft.from_dict(data)

        assert draft.content == "Body content"
        assert draft.content_type == "social"


class TestMealSuggestionModel:
    """Test MealSuggestion model."""

    def test_from_dict_camelcase(self):
        """Test creating MealSuggestion from camelCase dict."""
        data = {
            "name": "Pizza",
            "description": "Classic Italian",
            "mealType": "dinner",
            "venue": "Joe's Pizza",
            "reason": "You loved it",
            "ingredientsNeeded": ["cheese", "dough"],
            "prepTime": "30min",
            "matchScore": 0.95,
        }
        suggestion = MealSuggestion.from_dict(data)

        assert suggestion.name == "Pizza"
        assert suggestion.description == "Classic Italian"
        assert suggestion.meal_type == "dinner"
        assert suggestion.venue == "Joe's Pizza"
        assert suggestion.reason == "You loved it"
        assert suggestion.prep_time == "30min"
        assert suggestion.match_score == 0.95

    def test_from_dict_alternate_keys(self):
        """Test creating MealSuggestion with alternate keys."""
        data = {
            "title": "Salad",
            "type": "lunch",
            "ingredients_needed": ["lettuce", "tomatoes"],
            "prep_time": "10min",
            "match_score": 0.8,
        }
        suggestion = MealSuggestion.from_dict(data)

        assert suggestion.name == "Salad"
        assert suggestion.meal_type == "lunch"
        assert suggestion.ingredients_needed == ["lettuce", "tomatoes"]


class TestTasteBuddyResultModel:
    """Test TasteBuddyResult model."""

    def test_from_dict_camelcase(self):
        """Test creating TasteBuddyResult from camelCase dict."""
        data = {
            "isSafe": True,
            "isCompliant": False,
            "detectedAllergens": ["peanuts"],
            "dietConflicts": ["vegetarian"],
            "warnings": ["Contains nuts"],
            "modifications": ["Remove peanuts"],
        }
        result = TasteBuddyResult.from_dict(data)

        assert result.is_safe is True
        assert result.is_compliant is False
        assert result.detected_allergens == ["peanuts"]
        assert result.diet_conflicts == ["vegetarian"]
        assert result.warnings == ["Contains nuts"]
        assert result.modifications == ["Remove peanuts"]

    def test_from_dict_snake_case(self):
        """Test creating TasteBuddyResult from snake_case dict."""
        data = {
            "is_safe": False,
            "is_compliant": True,
            "detected_allergens": ["shellfish"],
            "diet_conflicts": [],
            "warnings": [],
            "suggestions": ["Use alternative"],
        }
        result = TasteBuddyResult.from_dict(data)

        assert result.is_safe is False
        assert result.is_compliant is True
        assert result.modifications == ["Use alternative"]

    def test_from_dict_defaults(self):
        """Test TasteBuddyResult defaults."""
        data = {}
        result = TasteBuddyResult.from_dict(data)

        assert result.is_safe is True
        assert result.is_compliant is True
        assert result.detected_allergens == []


class TestVenueModel:
    """Test Venue model."""

    def test_from_dict_camelcase(self):
        """Test creating Venue from camelCase dict."""
        data = {
            "name": "Joe's Diner",
            "venueType": "restaurant",
            "distance": 500,
            "rating": 4.5,
            "address": "123 Main St",
            "lat": 40.7128,
            "lng": -74.0060,
        }
        venue = Venue.from_dict(data)

        assert venue.name == "Joe's Diner"
        assert venue.venue_type == "restaurant"
        assert venue.distance == "500m"
        assert venue.rating == 4.5
        assert venue.address == "123 Main St"
        assert venue.latitude == 40.7128
        assert venue.longitude == -74.0060

    def test_from_dict_distance_conversion_meters(self):
        """Test distance conversion for meters."""
        data = {"name": "Venue", "distance": 800}
        venue = Venue.from_dict(data)

        assert venue.distance == "800m"

    def test_from_dict_distance_conversion_kilometers(self):
        """Test distance conversion for kilometers."""
        data = {"name": "Venue", "distance": 2500}
        venue = Venue.from_dict(data)

        assert venue.distance == "2.5km"

    def test_from_dict_distance_string(self):
        """Test distance as string."""
        data = {"name": "Venue", "distance": "1km"}
        venue = Venue.from_dict(data)

        assert venue.distance == "1km"

    def test_from_dict_alternate_keys(self):
        """Test creating Venue with alternate keys."""
        data = {
            "name": "Pizza Place",
            "type": "pizzeria",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        venue = Venue.from_dict(data)

        assert venue.venue_type == "pizzeria"
        assert venue.latitude == 40.7128


class TestCottageLabelModel:
    """Test CottageLabel model."""

    def test_from_dict_camelcase(self):
        """Test creating CottageLabel from camelCase dict."""
        data = {
            "productName": "Homemade Jam",
            "ingredients": ["strawberries", "sugar"],
            "allergenWarnings": ["may contain traces of nuts"],
            "warnings": ["Keep refrigerated"],
            "regulatoryNotes": ["Made in cottage kitchen"],
            "netWeight": "8oz",
            "producerInfo": "John's Kitchen, 123 Main St",
            "labelText": "Full label text",
        }
        label = CottageLabel.from_dict(data)

        assert label.product_name == "Homemade Jam"
        assert label.ingredients == ["strawberries", "sugar"]
        assert label.allergen_warnings == ["may contain traces of nuts"]
        assert label.warnings == ["Keep refrigerated"]
        assert label.regulatory_notes == ["Made in cottage kitchen"]
        assert label.weight == "8oz"
        assert label.producer_info == "John's Kitchen, 123 Main St"
        assert label.label_text == "Full label text"

    def test_from_dict_snake_case(self):
        """Test creating CottageLabel from snake_case dict."""
        data = {
            "product_name": "Jam",
            "ingredients": ["berries"],
            "allergen_warnings": [],
            "net_weight": "10oz",
            "producer_info": "Kitchen",
            "label_text": "Label",
        }
        label = CottageLabel.from_dict(data)

        assert label.product_name == "Jam"
        assert label.weight == "10oz"

    def test_from_dict_weight_key_priority(self):
        """Test weight key priority."""
        # Test that 'weight' is preferred over 'netWeight' over 'net_weight'
        data = {
            "product_name": "Jam",
            "ingredients": [],
            "weight": "12oz",
            "netWeight": "10oz",
            "net_weight": "8oz",
        }
        label = CottageLabel.from_dict(data)

        assert label.weight == "12oz"

    def test_from_dict_defaults(self):
        """Test CottageLabel defaults."""
        data = {"product_name": "Jam", "ingredients": ["berries"]}
        label = CottageLabel.from_dict(data)

        assert label.allergen_warnings == []
        assert label.warnings == []
        assert label.regulatory_notes == []
