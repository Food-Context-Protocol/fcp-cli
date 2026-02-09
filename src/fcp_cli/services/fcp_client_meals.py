"""Meal, search, discovery, and analytics methods for the FCP CLI client."""

from __future__ import annotations

from typing import Any

from fcp_cli.services.models import (
    FCP,
    MealSuggestion,
    SearchResult,
    TasteBuddyResult,
    TasteProfile,
    Venue,
)


class FcpMealsMixin:
    """Meal, search, discovery, and analytics operations."""

    async def get_food_logs(self, limit: int = 10) -> list[FCP]:
        response = await self._request(
            "GET",
            "/meals",
            params={"user_id": self.user_id, "limit": limit},
        )
        logs_data = response.get("logs", response.get("meals", []))
        return [FCP.from_dict(log) for log in logs_data]

    async def create_food_log(
        self,
        dish_name: str,
        description: str | None = None,
        meal_type: str | None = None,
        image_base64: str | None = None,
    ) -> FCP:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "dish_name": dish_name,
        }
        if description:
            payload["description"] = description
        if meal_type:
            payload["meal_type"] = meal_type
        if image_base64:
            payload["image_base64"] = image_base64

        response = await self._request("POST", "/meals", json=payload)
        return FCP.from_dict(response)

    async def log_meal(
        self,
        description: str,
        meal_type: str | None = None,
        calories: int | None = None,
        protein: int | None = None,
        carbs: int | None = None,
        fat: int | None = None,
    ) -> FCP:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "dish_name": description,
            "description": description,
        }
        if meal_type:
            payload["meal_type"] = meal_type
        if any(v is not None for v in (calories, protein, carbs, fat)):
            payload["nutrition"] = {
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            }

        response = await self._request("POST", "/meals", json=payload)
        return FCP.from_dict(response)

    async def search_meals(self, query: str, limit: int = 10) -> SearchResult:
        response = await self._request(
            "POST",
            "/search",
            json={"query": query, "user_id": self.user_id, "limit": limit},
        )
        logs_data = response.get("results", [])
        return SearchResult(
            logs=[FCP.from_dict(log) for log in logs_data],
            total=response.get("total", len(logs_data)),
            query=query,
        )

    async def search_meals_by_date(
        self,
        start_date: str,
        end_date: str | None = None,
        limit: int = 50,
    ) -> SearchResult:
        response = await self._request(
            "POST",
            "/search",
            json={
                "user_id": self.user_id,
                "start_date": start_date,
                "end_date": end_date or start_date,
                "limit": limit,
            },
        )
        logs_data = response.get("results", [])
        return SearchResult(
            logs=[FCP.from_dict(log) for log in logs_data],
            total=response.get("total", len(logs_data)),
            query=f"date:{start_date}" + (f" to {end_date}" if end_date else ""),
        )

    async def get_taste_profile(self) -> TasteProfile:
        response = await self._request(
            "GET",
            "/profile",
            params={"user_id": self.user_id},
        )
        return TasteProfile.from_dict(response)

    async def analyze_image(
        self,
        image_base64: str,
        thinking_level: str | None = None,
        media_resolution: str = "medium",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "image_base64": image_base64,
            "media_resolution": media_resolution,
        }
        if thinking_level:
            payload["thinking_level"] = thinking_level

        return await self._request("POST", "/analyze", json=payload)

    async def get_food_stats(
        self,
        period: str = "month",
        group_by: str = "meal_type",
    ) -> dict[str, Any]:
        _ = group_by  # kept for API compatibility
        period_days = {"week": 7, "month": 30, "year": 365}.get(period, 30)
        return await self._request(
            "GET",
            "/analytics/report",
            params={"days": period_days},
        )

    async def get_flavor_pairings(
        self,
        ingredient: str,
        count: int = 5,
    ) -> list[str]:
        response = await self._request(
            "GET",
            "/flavor/pairings",
            params={"subject": ingredient},
        )
        pairings = response.get("pairings", [])
        return pairings[:count] if count else pairings

    async def check_food_recalls(self, food_items: list[str]) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/safety/recalls",
            json={"user_id": self.user_id, "food_items": food_items},
        )

    async def check_drug_interactions(
        self,
        food_items: list[str],
        medications: list[str],
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/safety/drug-interactions",
            json={
                "user_id": self.user_id,
                "food_items": food_items,
                "medications": medications,
            },
        )

    async def check_allergen_alerts(
        self,
        food_items: list[str],
        allergies: list[str],
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/safety/allergens",
            json={
                "user_id": self.user_id,
                "food_items": food_items,
                "allergies": allergies,
            },
        )

    async def get_restaurant_safety_info(
        self,
        restaurant_name: str,
        location: str | None = None,
    ) -> dict[str, Any]:
        from urllib.parse import quote

        params: dict[str, Any] = {}
        if location:
            params["location"] = location
        return await self._request(
            "GET",
            f"/safety/restaurant/{quote(restaurant_name, safe='')}",
            params=params or None,
        )

    async def discover_food(self) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/agents/daily-insight",
            params={"user_id": self.user_id},
        )

    async def discover_restaurants(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        location: str | None = None,
    ) -> tuple[dict[str, Any], str | None]:
        if (latitude is None or longitude is None) and location is None:
            raise ValueError("Either (latitude, longitude) or location must be provided")

        payload: dict[str, Any] = {"user_id": self.user_id}

        if latitude is not None and longitude is not None:
            payload["latitude"] = latitude
            payload["longitude"] = longitude
            payload["location"] = f"{latitude},{longitude}"
        else:
            payload["location"] = location

        response = await self._request("POST", "/agents/discover/restaurants", json=payload)
        resolved_location = response.get("resolved_location")
        return response, resolved_location

    async def discover_recipes(self, ingredients: list[str]) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/agents/discover/recipes",
            json={
                "user_id": self.user_id,
                "available_ingredients": ingredients,
            },
        )

    async def donate_meal(
        self,
        log_id: str,
        organization: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "log_id": log_id,
        }
        if organization:
            payload["organization"] = organization

        return await self._request("POST", "/impact/donate", json=payload)

    async def get_dietitian_report(
        self,
        days: int = 7,
        focus_area: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "user_id": self.user_id,
            "days": days,
        }
        if focus_area:
            params["focus_area"] = focus_area

        return await self._request("GET", "/clinical/report", params=params)

    async def get_food_log(self, log_id: str) -> FCP:
        response = await self._request("GET", f"/meals/{log_id}")
        meal_data = response.get("meal", response)
        return FCP.from_dict(meal_data)

    async def update_food_log(
        self,
        log_id: str,
        dish_name: str | None = None,
        description: str | None = None,
        meal_type: str | None = None,
        venue_name: str | None = None,
    ) -> FCP:
        payload: dict[str, Any] = {}
        if dish_name:
            payload["dish_name"] = dish_name
        if description:
            payload["notes"] = description
        if meal_type:
            payload["meal_type"] = meal_type
        if venue_name:
            payload["venue_name"] = venue_name

        response = await self._request("PATCH", f"/meals/{log_id}", json=payload)
        return FCP.from_dict(response)

    async def delete_food_log(self, log_id: str) -> bool:
        await self._request("DELETE", f"/meals/{log_id}")
        return True

    async def suggest_meals(
        self,
        context: str | None = None,
        exclude_recent_days: int = 3,
    ) -> list[MealSuggestion]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "exclude_recent_days": exclude_recent_days,
        }
        if context:
            payload["context"] = context

        response = await self._request("POST", "/suggest", json=payload)
        suggestions = response.get("suggestions", [])
        return [MealSuggestion.from_dict(s) for s in suggestions]

    async def check_taste_buddy(
        self,
        dish_name: str,
        ingredients: list[str] | None = None,
        user_allergies: list[str] | None = None,
        user_diet: list[str] | None = None,
    ) -> TasteBuddyResult:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "dish_name": dish_name,
            "ingredients": ingredients or [],
            "user_allergies": user_allergies or [],
            "user_diet": user_diet or [],
        }

        response = await self._request("POST", "/taste-buddy/check", json=payload)
        return TasteBuddyResult.from_dict(response)

    async def find_nearby_venues(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        location: str | None = None,
        venue_type: str | None = None,
        radius: int = 2000,
    ) -> tuple[list[Venue], str | None]:
        if (latitude is None or longitude is None) and location is None:
            raise ValueError("Either (latitude, longitude) or location must be provided")

        payload: dict[str, Any] = {"radius": radius}

        if latitude is not None and longitude is not None:
            payload["latitude"] = latitude
            payload["longitude"] = longitude
        else:
            payload["location"] = location
        if venue_type:
            payload["food_type"] = venue_type

        response = await self._request("POST", "/discovery/nearby", json=payload)
        venues = response.get("venues", response.get("results", []))
        resolved_location = response.get("resolved_location")
        return [Venue.from_dict(v) for v in venues], resolved_location

    async def get_food_trends(
        self,
        region: str | None = None,
        cuisine_focus: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"user_id": self.user_id}
        if region:
            params["region"] = region
        if cuisine_focus:
            params["cuisine_focus"] = cuisine_focus

        return await self._request("GET", "/trends/identify", params=params)

    async def get_random_tip(self) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/agents/food-tip",
            params={"user_id": self.user_id},
        )

    async def get_streak(self, streak_days: int = 7) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/agents/streak/{streak_days}",
            params={"user_id": self.user_id},
        )

    async def get_lifetime_stats(self) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/profile/lifetime",
            params={"user_id": self.user_id},
        )

    async def get_nutrition_analytics(
        self,
        days: int = 7,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/analytics/nutrition",
            json={"days": days},
        )
