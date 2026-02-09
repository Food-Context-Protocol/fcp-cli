"""FCP client service for CLI commands."""

from __future__ import annotations

import asyncio  # noqa: F401 - re-exported for test patching

from fcp_cli.services.fcp_client_core import FcpClientCore
from fcp_cli.services.fcp_client_meals import FcpMealsMixin
from fcp_cli.services.fcp_client_pantry import FcpPantryMixin
from fcp_cli.services.fcp_client_recipes import FcpRecipesMixin
from fcp_cli.services.fcp_errors import (
    FcpAuthError,
    FcpClientError,
    FcpConnectionError,
    FcpNotFoundError,
    FcpRateLimitError,
    FcpResponseTooLargeError,
    FcpServerError,
)

# Re-export models for backward compatibility
from fcp_cli.services.models import (  # noqa: F401
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

__all__ = [
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


class FcpClient(
    FcpClientCore,
    FcpMealsMixin,
    FcpPantryMixin,
    FcpRecipesMixin,
):
    """HTTP client for the FCP server with retry logic and connection pooling."""
