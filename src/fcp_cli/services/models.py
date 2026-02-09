"""Data models for FCP API responses."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class FCP:
    """Food log entry from the FCP server."""

    id: str
    user_id: str
    dish_name: str
    description: str | None = None
    meal_type: str | None = None
    ingredients: list[str] | None = None
    nutrition: dict[str, Any] | None = None
    timestamp: datetime | None = None
    image_url: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FCP":
        """Create a FCP from a dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                timestamp = None

        return cls(
            id=data.get("id", ""),
            user_id=data.get("userId", data.get("user_id", "")),
            dish_name=data.get("dishName", data.get("dish_name", "")),
            description=data.get("description"),
            meal_type=data.get("mealType", data.get("meal_type")),
            ingredients=data.get("ingredients"),
            nutrition=data.get("nutrition"),
            timestamp=timestamp,
            image_url=data.get("imageUrl", data.get("image_url")),
        )


@dataclass
class TasteProfile:
    """User taste profile from the FCP server."""

    user_id: str
    favorite_cuisines: list[str]
    preferred_ingredients: list[str]
    disliked_ingredients: list[str]
    dietary_restrictions: list[str]
    average_calories: float | None = None
    meal_patterns: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TasteProfile":
        """Create a TasteProfile from a dictionary."""
        return cls(
            user_id=data.get("userId", data.get("user_id", "")),
            favorite_cuisines=data.get("favoriteCuisines", data.get("favorite_cuisines", [])),
            preferred_ingredients=data.get("preferredIngredients", data.get("preferred_ingredients", [])),
            disliked_ingredients=data.get("dislikedIngredients", data.get("disliked_ingredients", [])),
            dietary_restrictions=data.get("dietaryRestrictions", data.get("dietary_restrictions", [])),
            average_calories=data.get("averageCalories", data.get("average_calories")),
            meal_patterns=data.get("mealPatterns", data.get("meal_patterns")),
        )


@dataclass
class SearchResult:
    """Search result from the FCP server."""

    logs: list[FCP]
    total: int
    query: str


@dataclass
class PantryItem:
    """Pantry item from the FCP server."""

    id: str
    name: str
    quantity: str | None = None
    category: str | None = None
    storage_location: str | None = None
    expiration_date: str | None = None
    user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PantryItem":
        """Create a PantryItem from a dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", data.get("item_name", "")),
            quantity=data.get("quantity"),
            category=data.get("category"),
            storage_location=data.get("storageLocation", data.get("storage_location")),
            expiration_date=data.get("expirationDate", data.get("expiration_date", data.get("expiry_date"))),
            user_id=data.get("userId", data.get("user_id")),
        )


@dataclass
class Recipe:
    """Recipe from the FCP server."""

    id: str
    name: str
    description: str | None = None
    ingredients: list[str | dict[str, Any]] | None = None
    instructions: list[str | dict[str, Any]] | None = None
    servings: int | None = None
    source: str | None = None
    prep_time: str | None = None
    cook_time: str | None = None
    is_favorite: bool = False
    is_archived: bool = False
    user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recipe":
        """Create a Recipe from a dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", data.get("recipe_name", data.get("recipeName", ""))),
            description=data.get("description"),
            ingredients=data.get("ingredients", data.get("ingredientsList")),
            instructions=data.get("instructions", data.get("steps")),
            servings=data.get("servings"),
            source=data.get("source"),
            prep_time=data.get("prepTime", data.get("prep_time")),
            cook_time=data.get("cookTime", data.get("cook_time")),
            is_favorite=data.get("isFavorite", data.get("is_favorite", False)),
            is_archived=data.get("isArchived", data.get("is_archived", False)),
            user_id=data.get("userId", data.get("user_id")),
        )


@dataclass
class Draft:
    """Content draft from the FCP server."""

    id: str
    title: str
    content: str | None = None
    content_type: str | None = None
    status: str | None = None
    platforms: list[str] | None = None
    user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Draft":
        """Create a Draft from a dictionary."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            content=data.get("content", data.get("body")),
            content_type=data.get("contentType", data.get("content_type", data.get("type"))),
            status=data.get("status"),
            platforms=data.get("platforms"),
            user_id=data.get("userId", data.get("user_id")),
        )


@dataclass
class MealSuggestion:
    """Meal suggestion from the FCP server."""

    name: str
    description: str | None = None
    meal_type: str | None = None
    venue: str | None = None
    reason: str | None = None
    ingredients_needed: list[str] | None = None
    prep_time: str | None = None
    match_score: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MealSuggestion":
        """Create a MealSuggestion from a dictionary."""
        return cls(
            name=data.get("name", data.get("title", "")),
            description=data.get("description"),
            meal_type=data.get("mealType", data.get("meal_type", data.get("type"))),
            venue=data.get("venue"),
            reason=data.get("reason"),
            ingredients_needed=data.get("ingredientsNeeded", data.get("ingredients_needed")),
            prep_time=data.get("prepTime", data.get("prep_time")),
            match_score=data.get("matchScore", data.get("match_score")),
        )


@dataclass
class TasteBuddyResult:
    """Taste Buddy compatibility result from the FCP server."""

    is_safe: bool
    is_compliant: bool
    detected_allergens: list[str] | None = None
    diet_conflicts: list[str] | None = None
    warnings: list[str] | None = None
    modifications: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TasteBuddyResult":
        """Create a TasteBuddyResult from a dictionary."""
        return cls(
            is_safe=data.get("isSafe", data.get("is_safe", True)),
            is_compliant=data.get("isCompliant", data.get("is_compliant", True)),
            detected_allergens=data.get("detectedAllergens", data.get("detected_allergens", [])),
            diet_conflicts=data.get("dietConflicts", data.get("diet_conflicts", [])),
            warnings=data.get("warnings", []),
            modifications=data.get("modifications", data.get("suggestions", [])),
        )


@dataclass
class Venue:
    """Nearby venue from the FCP server."""

    name: str
    venue_type: str | None = None
    distance: str | None = None
    rating: float | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Venue":
        """Create a Venue from a dictionary."""
        # Convert distance from meters (int) to readable string
        distance_raw = data.get("distance")
        if isinstance(distance_raw, int | float):
            distance = f"{int(distance_raw)}m" if distance_raw < 1000 else f"{distance_raw / 1000:.1f}km"
        else:
            distance = distance_raw  # Already a string or None

        return cls(
            name=data.get("name", ""),
            venue_type=data.get("venueType", data.get("venue_type", data.get("type"))),
            distance=distance,
            rating=data.get("rating"),
            address=data.get("address"),
            latitude=data.get("lat", data.get("latitude")),
            longitude=data.get("lng", data.get("longitude")),
        )


@dataclass
class CottageLabel:
    """Cottage food label from the FCP server."""

    product_name: str
    ingredients: list[str]
    allergen_warnings: list[str] | None = None
    warnings: list[str] | None = None
    regulatory_notes: list[str] | None = None
    weight: str | None = None
    producer_info: str | None = None
    label_text: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CottageLabel":
        """Create a CottageLabel from a dictionary."""
        return cls(
            product_name=data.get("productName", data.get("product_name", "")),
            ingredients=data.get("ingredients", []),
            allergen_warnings=data.get("allergenWarnings", data.get("allergen_warnings", [])),
            warnings=data.get("warnings", []),
            regulatory_notes=data.get("regulatoryNotes", data.get("regulatory_notes", [])),
            weight=data.get("weight", data.get("netWeight", data.get("net_weight"))),
            producer_info=data.get("producerInfo", data.get("producer_info")),
            label_text=data.get("labelText", data.get("label_text")),
        )
