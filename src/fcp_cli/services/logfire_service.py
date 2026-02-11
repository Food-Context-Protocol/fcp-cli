"""Logfire observability service for CLI.

Provides structured logging and tracing for CLI operations using Pydantic Logfire.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import logfire

# Check if Logfire is configured via environment
_LOGFIRE_TOKEN = os.environ.get("LOGFIRE_TOKEN")
_LOGFIRE_ENABLED = _LOGFIRE_TOKEN is not None

# Track initialization state
_initialized = False


def configure_logfire() -> bool:
    """Configure Logfire if token is available.

    Returns:
        True if Logfire was configured, False if skipped (no token).
    """
    global _initialized

    if _initialized:
        return _LOGFIRE_ENABLED

    if not _LOGFIRE_ENABLED:
        _initialized = True
        return False

    # Configure Logfire with service name
    logfire.configure(
        service_name="fcp-cli",
        send_to_logfire=True,
    )

    # Instrument httpx for HTTP request tracing
    # Exclude Authorization headers to prevent token leakage to Logfire cloud
    logfire.instrument_httpx(capture_headers=False)

    _initialized = True
    return True


def is_enabled() -> bool:
    """Check if Logfire is enabled."""
    return _LOGFIRE_ENABLED


@contextmanager
def span(name: str, **attributes: Any) -> Iterator[None]:
    """Create a Logfire span for tracing.

    Args:
        name: Span name
        **attributes: Span attributes

    Yields:
        None (context manager)
    """
    if not _LOGFIRE_ENABLED:
        yield
        return

    with logfire.span(name, **attributes):
        yield


def info(message: str, **attributes: Any) -> None:
    """Log an info message.

    Args:
        message: Log message (can contain {placeholders})
        **attributes: Message attributes
    """
    if not _LOGFIRE_ENABLED:
        return
    logfire.info(message, **attributes)


def warn(message: str, **attributes: Any) -> None:
    """Log a warning message.

    Args:
        message: Log message (can contain {placeholders})
        **attributes: Message attributes
    """
    if not _LOGFIRE_ENABLED:
        return
    logfire.warn(message, **attributes)


def error(message: str, **attributes: Any) -> None:
    """Log an error message.

    Args:
        message: Log message (can contain {placeholders})
        **attributes: Message attributes
    """
    if not _LOGFIRE_ENABLED:
        return
    logfire.error(message, **attributes)


def debug(message: str, **attributes: Any) -> None:
    """Log a debug message.

    Args:
        message: Log message (can contain {placeholders})
        **attributes: Message attributes
    """
    if not _LOGFIRE_ENABLED:
        return
    logfire.debug(message, **attributes)
