"""Pantry-related methods for the FCP CLI client."""

from __future__ import annotations

from typing import Any

from fcp_cli.services.models import PantryItem


class FcpPantryMixin:
    """Pantry operations."""

    async def get_user_pantry(self) -> list[dict[str, Any]]:
        response = await self._request(
            "GET",
            "/inventory/pantry",
            params={"user_id": self.user_id},
        )
        return response.get("items", [])

    async def add_to_pantry(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/inventory/pantry",
            json={"user_id": self.user_id, "items": items},
        )

    async def check_pantry_expiry(self) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/inventory/pantry/expiring",
            params={"user_id": self.user_id},
        )

    async def get_pantry_suggestions(self) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/inventory/pantry/meal-suggestions",
            params={"user_id": self.user_id},
        )

    async def update_pantry_item(
        self,
        item_id: str,
        quantity: str | None = None,
        category: str | None = None,
        storage_location: str | None = None,
        expiration_date: str | None = None,
    ) -> PantryItem:
        payload: dict[str, Any] = {"user_id": self.user_id}
        if quantity:
            payload["quantity"] = quantity
        if category:
            payload["category"] = category
        if storage_location:
            payload["storage_location"] = storage_location
        if expiration_date:
            payload["expiration_date"] = expiration_date

        response = await self._request("PATCH", f"/inventory/pantry/{item_id}", json=payload)
        return PantryItem.from_dict(response)

    async def delete_pantry_item(self, item_id: str) -> bool:
        await self._request("DELETE", f"/inventory/pantry/{item_id}")
        return True

    async def deduct_from_pantry(
        self,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/inventory/pantry/deduct",
            json={"user_id": self.user_id, "items": items},
        )
