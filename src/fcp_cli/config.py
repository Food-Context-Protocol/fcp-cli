"""Type-safe CLI configuration using pydantic-settings."""

from __future__ import annotations

import logging
from typing import Annotated
from urllib.parse import urlparse

from pydantic import AfterValidator, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def warn_if_insecure_url(url: str) -> str:
    """Warn if using HTTP for non-localhost URLs.

    Args:
        url: The URL to validate

    Returns:
        The validated URL
    """
    parsed = urlparse(url)
    if parsed.scheme == "http":
        host = parsed.hostname or ""
        # Allow HTTP for localhost/127.0.0.1/[::1]
        if host not in ("localhost", "127.0.0.1", "::1"):
            logger.warning(f"Using insecure HTTP connection to {host}. Consider using HTTPS for non-localhost URLs.")
    return url


# Type alias for validated URL
SecureUrl = Annotated[str, AfterValidator(warn_if_insecure_url)]


class CliSettings(BaseSettings):
    """CLI configuration with automatic validation from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    # ==========================================================================
    # Server Configuration
    # ==========================================================================
    fcp_server_url: SecureUrl = Field(
        default="http://localhost:8080",
        description="FCP server URL (supports http/https)",
    )

    # ==========================================================================
    # Authentication
    # ==========================================================================
    fcp_user_id: str = Field(
        default="demo",
        description="User ID for server requests",
    )

    fcp_auth_token: str | None = Field(
        default=None,
        description="Optional JWT token for authenticated requests (enables write operations)",
    )

    @field_validator("fcp_user_id")
    @classmethod
    def warn_demo_user(cls, v: str) -> str:
        """Warn if using the default demo user."""
        if v == "demo":
            logger.warning("FCP_USER_ID not set, using 'demo' user")
        return v


# Global settings instance - loaded once at import time
settings = CliSettings()
