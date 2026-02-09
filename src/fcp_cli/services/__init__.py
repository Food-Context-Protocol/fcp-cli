"""Services for FCP CLI."""

from fcp_cli.services.fcp import (
    FCP,
    CottageLabel,
    Draft,
    FcpAuthError,
    FcpClient,
    FcpClientError,
    FcpConnectionError,
    FcpNotFoundError,
    FcpRateLimitError,
    FcpServerError,
    MealSuggestion,
    PantryItem,
    Recipe,
    SearchResult,
    TasteBuddyResult,
    TasteProfile,
    Venue,
)
from fcp_cli.services.logfire_service import configure_logfire

__all__ = [
    "CottageLabel",
    "Draft",
    "FcpAuthError",
    "FcpClient",
    "FcpClientError",
    "FcpConnectionError",
    "FcpNotFoundError",
    "FcpRateLimitError",
    "FcpServerError",
    "FCP",
    "MealSuggestion",
    "PantryItem",
    "Recipe",
    "SearchResult",
    "TasteBuddyResult",
    "TasteProfile",
    "Venue",
    "configure_logfire",
]
