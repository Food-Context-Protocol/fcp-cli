"""Recipe, publishing, parsing, and misc methods for the FCP CLI client."""

from __future__ import annotations

from typing import Any

from fcp_cli.services.models import CottageLabel, Draft, Recipe


class FcpRecipesMixin:
    """Recipe, publishing, and parsing operations."""

    async def scale_recipe(self, recipe_id: str, target_servings: int) -> Recipe:
        response = await self._request(
            "POST",
            "/scaling/scale-recipe",
            json={"user_id": self.user_id, "recipe_id": recipe_id, "target_servings": target_servings},
        )
        return Recipe.from_dict(response)

    async def standardize_recipe(self, raw_text: str) -> Recipe:
        response = await self._request(
            "POST",
            "/standardize-recipe",
            json={"user_id": self.user_id, "raw_text": raw_text},
        )
        return Recipe.from_dict(response)

    async def extract_recipe_from_image(
        self,
        image_base64: str,
        media_resolution: str = "medium",
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/recipes/extract",
            json={
                "user_id": self.user_id,
                "image_base64": image_base64,
                "media_resolution": media_resolution,
            },
        )

    async def get_recipes(self) -> list[dict[str, Any]]:
        response = await self._request(
            "GET",
            "/recipes",
            params={"user_id": self.user_id},
        )
        return response.get("recipes", [])

    async def get_recipe(self, recipe_id: str) -> Recipe:
        response = await self._request("GET", f"/recipes/{recipe_id}")
        return Recipe.from_dict(response)

    async def get_recipes_filtered(self, filter_type: str = "all") -> list[Recipe]:
        response = await self._request(
            "GET",
            "/recipes",
            params={"user_id": self.user_id, "filter": filter_type},
        )
        recipes_data = response.get("recipes", [])
        return [Recipe.from_dict(r) for r in recipes_data]

    async def create_recipe(
        self,
        name: str,
        ingredients: list[str] | None = None,
        instructions: list[str] | None = None,
        servings: int | None = None,
        source: str | None = None,
    ) -> Recipe:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "recipe_name": name,
        }
        if ingredients:
            payload["ingredients"] = ingredients
        if instructions:
            payload["instructions"] = instructions
        if servings:
            payload["servings"] = servings
        if source:
            payload["source"] = source

        response = await self._request("POST", "/recipes", json=payload)
        return Recipe.from_dict(response)

    async def update_recipe(
        self,
        recipe_id: str,
        is_favorite: bool | None = None,
        is_archived: bool | None = None,
    ) -> Recipe:
        payload: dict[str, Any] = {"user_id": self.user_id}
        if is_favorite is not None:
            payload["is_favorite"] = is_favorite
        if is_archived is not None:
            payload["is_archived"] = is_archived

        response = await self._request("PATCH", f"/recipes/{recipe_id}", json=payload)
        return Recipe.from_dict(response)

    async def delete_recipe(self, recipe_id: str) -> bool:
        await self._request("DELETE", f"/recipes/{recipe_id}")
        return True

    async def generate_content(
        self,
        content_type: str,
        log_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "content_type": content_type,
        }
        if log_ids:
            payload["log_ids"] = log_ids

        return await self._request("POST", "/publish/generate", json=payload)

    async def get_drafts(self) -> list[dict[str, Any]]:
        response = await self._request(
            "GET",
            "/publish/drafts",
            params={"user_id": self.user_id},
        )
        return response.get("drafts", [])

    async def get_draft(self, draft_id: str) -> Draft:
        response = await self._request("GET", f"/publish/drafts/{draft_id}")
        return Draft.from_dict(response)

    async def update_draft(
        self,
        draft_id: str,
        title: str | None = None,
        content: str | None = None,
        status: str | None = None,
    ) -> Draft:
        payload: dict[str, Any] = {"user_id": self.user_id}
        if title:
            payload["title"] = title
        if content:
            payload["content"] = content
        if status:
            payload["status"] = status

        response = await self._request("PATCH", f"/publish/drafts/{draft_id}", json=payload)
        return Draft.from_dict(response)

    async def delete_draft(self, draft_id: str) -> bool:
        await self._request("DELETE", f"/publish/drafts/{draft_id}")
        return True

    async def publish_draft(
        self,
        draft_id: str,
        platforms: list[str] | None = None,
        publish_immediately: bool = True,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "publish_immediately": publish_immediately,
        }
        if platforms:
            payload["platforms"] = platforms

        return await self._request("POST", f"/publish/drafts/{draft_id}/publish", json=payload)

    async def get_published_content(self) -> list[dict[str, Any]]:
        response = await self._request(
            "GET",
            "/publish/published",
            params={"user_id": self.user_id},
        )
        return response.get("content", response.get("published", []))

    async def parse_receipt(self, image_base64: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/parser/receipt",
            json={"user_id": self.user_id, "image_base64": image_base64},
        )

    async def parse_menu(
        self,
        image_base64: str,
        restaurant_name: str | None = None,
        media_resolution: str = "medium",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "image_base64": image_base64,
            "media_resolution": media_resolution,
        }
        if restaurant_name:
            payload["restaurant_name"] = restaurant_name

        return await self._request("POST", "/parser/menu", json=payload)

    async def generate_cottage_label(
        self,
        product_name: str,
        ingredients: list[str],
        net_weight: str | None = None,
        business_name: str | None = None,
        business_address: str | None = None,
        is_refrigerated: bool = False,
    ) -> CottageLabel:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "product_name": product_name,
            "ingredients": ingredients,
            "is_refrigerated": is_refrigerated,
        }
        if net_weight:
            payload["net_weight"] = net_weight
        if business_name:
            payload["business_name"] = business_name
        if business_address:
            payload["business_address"] = business_address

        response = await self._request("POST", "/cottage/label", json=payload)
        return CottageLabel.from_dict(response)

    async def lookup_product_by_barcode(self, barcode: str) -> dict[str, Any]:
        from urllib.parse import quote

        return await self._request(
            "GET",
            f"/external/lookup-product/{quote(barcode, safe='')}",
        )

    async def generate_recipe(
        self,
        ingredients: list[str] | None = None,
        cuisine: str | None = None,
        dietary_restrictions: list[str] | None = None,
        meal_type: str | None = None,
        difficulty: str | None = None,
    ) -> Recipe:
        payload: dict[str, Any] = {"user_id": self.user_id}
        if ingredients:
            payload["ingredients"] = ingredients
        if cuisine:
            payload["cuisine"] = cuisine
        if dietary_restrictions:
            payload["dietary_restrictions"] = dietary_restrictions
        if meal_type:
            payload["meal_type"] = meal_type
        if difficulty:
            payload["difficulty"] = difficulty

        response = await self._request("POST", "/recipes/generate", json=payload)
        return Recipe.from_dict(response)
