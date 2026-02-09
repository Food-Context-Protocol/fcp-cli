"""Tests for FcpPantryMixin."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from fcp_cli.services.fcp import FcpClient
from fcp_cli.services.models import PantryItem

pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestFcpPantryMixin:
    """Test pantry operations."""

    @pytest.mark.asyncio
    async def test_get_user_pantry(self):
        """Test getting user's pantry."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "items": [
                    {"id": "1", "name": "Milk", "quantity": "1L"},
                    {"id": "2", "name": "Eggs", "quantity": "12"},
                ]
            }

            result = await client.get_user_pantry()

            assert len(result) == 2
            assert result[0]["name"] == "Milk"
            mock_request.assert_called_once_with(
                "GET",
                "/inventory/pantry",
                params={"user_id": "test-user"},
            )

    @pytest.mark.asyncio
    async def test_get_user_pantry_empty(self):
        """Test getting empty pantry."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"items": []}

            result = await client.get_user_pantry()

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_user_pantry_no_items_key(self):
        """Test getting pantry when response has no items key."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}

            result = await client.get_user_pantry()

            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_add_to_pantry(self):
        """Test adding items to pantry."""
        client = FcpClient(user_id="test-user")
        items = [
            {"name": "Flour", "quantity": "2kg"},
            {"name": "Sugar", "quantity": "1kg"},
        ]

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "success", "added": 2}

            result = await client.add_to_pantry(items)

            assert result["status"] == "success"
            mock_request.assert_called_once_with(
                "POST",
                "/inventory/pantry",
                json={"user_id": "test-user", "items": items},
            )

    @pytest.mark.asyncio
    async def test_add_to_pantry_empty_list(self):
        """Test adding empty list to pantry."""
        client = FcpClient(user_id="test-user")
        items = []

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "success", "added": 0}

            result = await client.add_to_pantry(items)

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_check_pantry_expiry(self):
        """Test checking for expiring items."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "expiring_soon": [
                    {"id": "1", "name": "Milk", "expiry_date": "2026-02-10"},
                ]
            }

            result = await client.check_pantry_expiry()

            assert "expiring_soon" in result
            mock_request.assert_called_once_with(
                "GET",
                "/inventory/pantry/expiring",
                params={"user_id": "test-user"},
            )

    @pytest.mark.asyncio
    async def test_get_pantry_suggestions(self):
        """Test getting meal suggestions from pantry."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "suggestions": [
                    {"name": "Pasta", "ingredients": ["pasta", "tomatoes"]},
                ]
            }

            result = await client.get_pantry_suggestions()

            assert "suggestions" in result
            mock_request.assert_called_once_with(
                "GET",
                "/inventory/pantry/meal-suggestions",
                params={"user_id": "test-user"},
            )

    @pytest.mark.asyncio
    async def test_update_pantry_item_all_fields(self):
        """Test updating pantry item with all fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "item123",
                "name": "Milk",
                "quantity": "2L",
                "category": "Dairy",
                "storage_location": "Fridge",
                "expiration_date": "2026-02-15",
            }

            result = await client.update_pantry_item(
                item_id="item123",
                quantity="2L",
                category="Dairy",
                storage_location="Fridge",
                expiration_date="2026-02-15",
            )

            assert isinstance(result, PantryItem)
            assert result.id == "item123"
            assert result.quantity == "2L"
            mock_request.assert_called_once_with(
                "PATCH",
                "/inventory/pantry/item123",
                json={
                    "user_id": "test-user",
                    "quantity": "2L",
                    "category": "Dairy",
                    "storage_location": "Fridge",
                    "expiration_date": "2026-02-15",
                },
            )

    @pytest.mark.asyncio
    async def test_update_pantry_item_partial_fields(self):
        """Test updating pantry item with only some fields."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "item123",
                "name": "Milk",
                "quantity": "2L",
            }

            result = await client.update_pantry_item(
                item_id="item123",
                quantity="2L",
            )

            assert isinstance(result, PantryItem)
            mock_request.assert_called_once_with(
                "PATCH",
                "/inventory/pantry/item123",
                json={"user_id": "test-user", "quantity": "2L"},
            )

    @pytest.mark.asyncio
    async def test_update_pantry_item_no_fields(self):
        """Test updating pantry item with no fields provided."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "item123",
                "name": "Milk",
            }

            result = await client.update_pantry_item(item_id="item123")

            assert isinstance(result, PantryItem)
            mock_request.assert_called_once_with(
                "PATCH",
                "/inventory/pantry/item123",
                json={"user_id": "test-user"},
            )

    @pytest.mark.asyncio
    async def test_delete_pantry_item(self):
        """Test deleting a pantry item."""
        client = FcpClient(user_id="test-user")
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}

            result = await client.delete_pantry_item("item123")

            assert result is True
            mock_request.assert_called_once_with("DELETE", "/inventory/pantry/item123")

    @pytest.mark.asyncio
    async def test_deduct_from_pantry(self):
        """Test deducting items from pantry."""
        client = FcpClient(user_id="test-user")
        items = [
            {"name": "Flour", "quantity": "500g"},
            {"name": "Eggs", "quantity": "2"},
        ]

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": "success",
                "deducted": 2,
                "warnings": [],
            }

            result = await client.deduct_from_pantry(items)

            assert result["status"] == "success"
            assert result["deducted"] == 2
            mock_request.assert_called_once_with(
                "POST",
                "/inventory/pantry/deduct",
                json={"user_id": "test-user", "items": items},
            )

    @pytest.mark.asyncio
    async def test_deduct_from_pantry_with_warnings(self):
        """Test deducting items with insufficient quantity warnings."""
        client = FcpClient(user_id="test-user")
        items = [{"name": "Flour", "quantity": "5kg"}]

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "status": "partial",
                "deducted": 1,
                "warnings": ["Insufficient Flour: requested 5kg, available 2kg"],
            }

            result = await client.deduct_from_pantry(items)

            assert result["status"] == "partial"
            assert len(result["warnings"]) > 0
