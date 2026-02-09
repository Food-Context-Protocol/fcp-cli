"""Tests for FcpClient composite class."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from fcp_cli.services.fcp import FcpClient
from fcp_cli.services.fcp_client_core import FcpClientCore
from fcp_cli.services.fcp_client_meals import FcpMealsMixin
from fcp_cli.services.fcp_client_pantry import FcpPantryMixin
from fcp_cli.services.fcp_client_recipes import FcpRecipesMixin

pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestFcpClientInheritance:
    """Test FcpClient class composition and inheritance."""

    def test_inherits_from_core(self):
        """Test FcpClient inherits from FcpClientCore."""
        assert issubclass(FcpClient, FcpClientCore)

    def test_inherits_from_meals_mixin(self):
        """Test FcpClient inherits from FcpMealsMixin."""
        assert issubclass(FcpClient, FcpMealsMixin)

    def test_inherits_from_pantry_mixin(self):
        """Test FcpClient inherits from FcpPantryMixin."""
        assert issubclass(FcpClient, FcpPantryMixin)

    def test_inherits_from_recipes_mixin(self):
        """Test FcpClient inherits from FcpRecipesMixin."""
        assert issubclass(FcpClient, FcpRecipesMixin)

    def test_has_core_methods(self):
        """Test FcpClient has core HTTP methods."""
        client = FcpClient()
        assert hasattr(client, "_request")
        assert hasattr(client, "health_check")
        assert hasattr(client, "close")

    def test_has_meals_methods(self):
        """Test FcpClient has meals methods."""
        client = FcpClient()
        assert hasattr(client, "get_food_logs")
        assert hasattr(client, "create_food_log")
        assert hasattr(client, "search_meals")
        assert hasattr(client, "get_taste_profile")

    def test_has_pantry_methods(self):
        """Test FcpClient has pantry methods."""
        client = FcpClient()
        assert hasattr(client, "get_user_pantry")
        assert hasattr(client, "add_to_pantry")
        assert hasattr(client, "update_pantry_item")

    def test_has_recipes_methods(self):
        """Test FcpClient has recipes methods."""
        client = FcpClient()
        assert hasattr(client, "get_recipes")
        assert hasattr(client, "create_recipe")
        assert hasattr(client, "scale_recipe")
        assert hasattr(client, "generate_recipe")


class TestFcpClientIntegration:
    """Test FcpClient integration scenarios."""

    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test FcpClient can be used as context manager."""
        async with FcpClient() as client:
            assert isinstance(client, FcpClient)
            assert client._auto_close is False

    @pytest.mark.asyncio
    async def test_multiple_operations_same_client(self):
        """Test multiple operations with same client instance."""
        client = FcpClient(user_id="test-user")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            # Mock different responses for different calls
            mock_request.side_effect = [
                {"logs": []},  # get_food_logs
                {"items": []},  # get_user_pantry
                {"recipes": []},  # get_recipes
            ]

            async with client:
                await client.get_food_logs()
                await client.get_user_pantry()
                await client.get_recipes()

            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_shared_user_id(self):
        """Test user_id is shared across all operations."""
        client = FcpClient(user_id="shared-user")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"logs": []}

            await client.get_food_logs()

            # Verify user_id was used
            call_params = mock_request.call_args[1]["params"]
            assert call_params["user_id"] == "shared-user"

    @pytest.mark.asyncio
    async def test_error_handling_across_mixins(self):
        """Test error handling works across all mixins."""
        client = FcpClient()

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("Network error")

            with pytest.raises(Exception, match="Network error"):
                await client.get_food_logs()

            with pytest.raises(Exception, match="Network error"):
                await client.get_user_pantry()

            with pytest.raises(Exception, match="Network error"):
                await client.get_recipes()


class TestFcpClientExports:
    """Test FcpClient module exports."""

    def test_fcp_client_exported(self):
        """Test FcpClient is exported from fcp module."""
        from fcp_cli.services.fcp import FcpClient as ExportedClient

        assert ExportedClient is FcpClient

    def test_models_exported(self):
        """Test models are exported from fcp module."""
        from fcp_cli.services.fcp import (
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

        # Just verify they can be imported
        assert FCP is not None
        assert Recipe is not None
        assert PantryItem is not None
        assert Draft is not None
        assert TasteProfile is not None
        assert SearchResult is not None
        assert MealSuggestion is not None
        assert TasteBuddyResult is not None
        assert Venue is not None
        assert CottageLabel is not None

    def test_errors_exported(self):
        """Test error classes are exported from fcp module."""
        from fcp_cli.services.fcp import (
            FcpAuthError,
            FcpClientError,
            FcpConnectionError,
            FcpNotFoundError,
            FcpRateLimitError,
            FcpResponseTooLargeError,
            FcpServerError,
        )

        # Just verify they can be imported
        assert FcpClientError is not None
        assert FcpConnectionError is not None
        assert FcpServerError is not None
        assert FcpNotFoundError is not None
        assert FcpAuthError is not None
        assert FcpRateLimitError is not None
        assert FcpResponseTooLargeError is not None

    def test_all_exports(self):
        """Test __all__ contains expected exports."""
        from fcp_cli.services import fcp

        expected_exports = [
            "FcpClient",
            "FcpClientError",
            "FcpConnectionError",
            "FcpServerError",
            "FcpNotFoundError",
            "FcpAuthError",
            "FcpRateLimitError",
            "FcpResponseTooLargeError",
            "FCP",
            "TasteProfile",
            "SearchResult",
            "PantryItem",
            "Recipe",
            "Draft",
            "MealSuggestion",
            "TasteBuddyResult",
            "Venue",
            "CottageLabel",
        ]

        for export in expected_exports:
            assert export in fcp.__all__, f"{export} not in __all__"


class TestFcpClientConfiguration:
    """Test FcpClient configuration options."""

    def test_custom_base_url(self):
        """Test FcpClient with custom base URL."""
        client = FcpClient(base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"

    def test_custom_timeout(self):
        """Test FcpClient with custom timeout."""
        client = FcpClient(timeout=60.0)
        assert client.timeout == 60.0

    def test_custom_max_retries(self):
        """Test FcpClient with custom max retries."""
        client = FcpClient(max_retries=5)
        assert client.max_retries == 5

    def test_custom_auth_token(self):
        """Test FcpClient with custom auth token."""
        client = FcpClient(auth_token="custom-token")
        assert client.auth_token == "custom-token"
        assert client.is_authenticated is True

    def test_auto_close_configuration(self):
        """Test FcpClient with auto_close disabled."""
        client = FcpClient(auto_close=False)
        assert client._auto_close is False

    def test_all_custom_options(self):
        """Test FcpClient with all custom options."""
        client = FcpClient(
            base_url="https://custom.example.com",
            user_id="custom-user",
            timeout=120.0,
            max_retries=10,
            retry_delay=2.5,
            auth_token="token-123",
            max_response_size=5 * 1024 * 1024,
            auto_close=False,
        )

        assert client.base_url == "https://custom.example.com"
        assert client.user_id == "custom-user"
        assert client.timeout == 120.0
        assert client.max_retries == 10
        assert client.retry_delay == 2.5
        assert client.auth_token == "token-123"
        assert client.max_response_size == 5 * 1024 * 1024
        assert client._auto_close is False


class TestFcpClientMethodResolutionOrder:
    """Test method resolution order in FcpClient."""

    def test_mro_order(self):
        """Test method resolution order is correct."""
        mro = FcpClient.__mro__

        # Should be: FcpClient, Core, Meals, Pantry, Recipes, object
        assert mro[0] == FcpClient
        assert FcpClientCore in mro
        assert FcpMealsMixin in mro
        assert FcpPantryMixin in mro
        assert FcpRecipesMixin in mro

    def test_no_method_conflicts(self):
        """Test there are no method name conflicts between mixins."""
        client = FcpClient()

        # Get all methods from each mixin
        meals_methods = {
            name for name in dir(FcpMealsMixin) if callable(getattr(FcpMealsMixin, name)) and not name.startswith("_")
        }
        pantry_methods = {
            name for name in dir(FcpPantryMixin) if callable(getattr(FcpPantryMixin, name)) and not name.startswith("_")
        }
        recipes_methods = {
            name
            for name in dir(FcpRecipesMixin)
            if callable(getattr(FcpRecipesMixin, name)) and not name.startswith("_")
        }

        # Check for overlaps (excluding methods from object)
        all_methods = meals_methods | pantry_methods | recipes_methods
        assert len(meals_methods & pantry_methods) == 0, "Meals and Pantry have method conflicts"
        assert len(meals_methods & recipes_methods) == 0, "Meals and Recipes have method conflicts"
        assert len(pantry_methods & recipes_methods) == 0, "Pantry and Recipes have method conflicts"

        # Verify all methods are accessible from FcpClient
        for method in all_methods:
            assert hasattr(client, method), f"Method {method} not accessible from FcpClient"
