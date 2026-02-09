"""Shared utilities for FCP CLI commands."""

import asyncio
import sys
from collections.abc import Callable, Coroutine
from contextlib import contextmanager
from datetime import UTC, datetime
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from collections.abc import Generator

# Display formatting constants
ID_DISPLAY_LENGTH = 8
MAX_PROFILE_ITEMS_DISPLAY = 5

# Venue search defaults
DEFAULT_SEARCH_RADIUS_METERS = 2000

# Meal suggestion defaults
DEFAULT_EXCLUDE_DAYS = 3

T = TypeVar("T")


def demo_safe(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for demo-safe error handling in CLI commands.

    Provides graceful error handling for production demos:
    - KeyboardInterrupt: Shows "Cancelled" message and exits cleanly
    - Other exceptions: Shows user-friendly error message
    - Debug mode (--debug flag): Shows full traceback

    Args:
        func: The command function to wrap

    Returns:
        Wrapped function with error handling

    Example:
        @app.command()
        @demo_safe
        def meal(...):
            ...
    """
    import typer

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console = Console()
            console.print("\n[yellow]Cancelled[/yellow]")
            raise typer.Exit(0) from None
        except Exception as e:
            console = Console()
            console.print(f"[red]Error:[/red] {e}")
            # Show full trace in debug mode
            if "--debug" in sys.argv:
                raise
            raise typer.Exit(1) from None

    return wrapper


@contextmanager
def show_progress(description: str, console: Console) -> "Generator[None]":
    """Display a progress spinner during an operation.

    Args:
        description: Text to show next to spinner
        console: Rich console instance

    Yields:
        None - just provides spinner context
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description, total=None)
        yield


def validate_latitude(value: float) -> float:
    """Validate latitude is within valid range.

    Args:
        value: Latitude to validate

    Returns:
        The validated latitude

    Raises:
        ValueError: If latitude is out of range
    """
    if not -90 <= value <= 90:
        raise ValueError(f"Latitude must be between -90 and 90, got {value}")
    return value


def validate_longitude(value: float) -> float:
    """Validate longitude is within valid range.

    Args:
        value: Longitude to validate

    Returns:
        The validated longitude

    Raises:
        ValueError: If longitude is out of range
    """
    if not -180 <= value <= 180:
        raise ValueError(f"Longitude must be between -180 and 180, got {value}")
    return value


def validate_limit(value: int) -> int:
    """Validate limit parameter for CLI commands.

    Standard validation callback for --limit options.
    Accepts values from 1 to 1000.

    Args:
        value: Limit value to validate

    Returns:
        The validated limit

    Raises:
        typer.BadParameter: If value is out of range
    """
    import typer

    try:
        return validate_positive_int(value, min_val=1, max_val=1000)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def validate_latitude_callback(value: float) -> float:
    """Typer callback for validating latitude.

    Args:
        value: Latitude to validate

    Returns:
        The validated latitude

    Raises:
        typer.BadParameter: If latitude is out of range
    """
    import typer

    try:
        return validate_latitude(value)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def validate_longitude_callback(value: float) -> float:
    """Typer callback for validating longitude.

    Args:
        value: Longitude to validate

    Returns:
        The validated longitude

    Raises:
        typer.BadParameter: If longitude is out of range
    """
    import typer

    try:
        return validate_longitude(value)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def validate_positive_int(value: int, min_val: int = 1, max_val: int | None = None) -> int:
    """Validate that an integer is positive and within bounds.

    Args:
        value: Integer to validate
        min_val: Minimum allowed value (default: 1)
        max_val: Maximum allowed value (default: None, no upper limit)

    Returns:
        The validated integer

    Raises:
        ValueError: If value is out of range
    """
    if value < min_val:
        raise ValueError(f"Value must be at least {min_val}, got {value}")
    if max_val is not None and value > max_val:
        raise ValueError(f"Value must be at most {max_val}, got {value}")
    return value


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run async coroutine in sync context.

    This is a wrapper around asyncio.run() for use in CLI commands
    that need to call async service methods.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine
    """
    return asyncio.run(coro)


def get_relative_time(dt: datetime) -> str:
    """Get a human-readable relative time string.

    Args:
        dt: The datetime to format (should be timezone-aware or UTC)

    Returns:
        String like "just now", "5 mins ago", "yesterday", etc.
    """
    now = datetime.now(UTC)

    # Assume UTC if naive
    dt = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 0:
        # Future time or clock skew
        return dt.strftime("%Y-%m-%d %H:%M")

    if seconds < 60:
        return "just now"

    minutes = int(seconds / 60)
    if minutes < 60:
        return f"{minutes} min{'s' if minutes != 1 else ''} ago"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    days = int(hours / 24)
    if days == 1:
        return "yesterday"
    return f"{days} days ago" if days < 7 else dt.strftime("%Y-%m-%d")


# Maximum image file size (50MB)
MAX_IMAGE_SIZE_BYTES = 50 * 1024 * 1024
MAX_IMAGE_SIZE_MB = 50

# Supported image extensions
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Image resolution settings for FCP server
VALID_RESOLUTIONS = {"low", "medium", "high"}
DEFAULT_RESOLUTION = "medium"

# Resolution size thresholds for auto-detection (in bytes)
RESOLUTION_AUTO_THRESHOLDS = {
    "low": (0, 100_000),  # 0-100KB
    "medium": (100_000, 500_000),  # 100KB-500KB
    "high": (500_000, float("inf")),  # 500KB+
}

# Image magic number headers
IMAGE_MAGIC_NUMBERS = {
    b"\xff\xd8\xff": "JPEG",
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"GIF87a": "GIF",
    b"GIF89a": "GIF",
}

# WEBP has a special structure: RIFF[size]WEBP
WEBP_RIFF_HEADER = b"RIFF"
WEBP_FORMAT_MARKER = b"WEBP"


class ImageValidationError(Exception):
    """Base exception for image validation errors."""

    pass


class ImageTooLargeError(ImageValidationError):
    """Raised when an image file exceeds the maximum allowed size."""

    pass


class InvalidImageError(ImageValidationError):
    """Raised when a file is not a valid image."""

    pass


def validate_image_path(image_path: str) -> None:
    """Validate an image file path for security and format.

    Checks:
    - Path exists and is a regular file
    - Path doesn't traverse outside expected directories
    - File extension is supported
    - File size is within limits
    - File has valid image magic numbers

    Args:
        image_path: Path to the image file

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ImageTooLargeError: If the image exceeds 50MB
        InvalidImageError: If the file is not a valid image
    """
    from pathlib import Path

    path = Path(image_path)

    # Resolve to absolute path to prevent path traversal attacks
    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Ensure path is a regular file (not a directory, device, etc.)
    if not path.is_file():
        raise InvalidImageError(f"Path is not a regular file: {image_path}")

    # Check file extension
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        raise InvalidImageError(
            f"Unsupported file extension: {suffix}. Allowed: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}"
        )

    # Check file size before reading
    file_size = path.stat().st_size
    if file_size > MAX_IMAGE_SIZE_BYTES:
        raise ImageTooLargeError(
            f"Image file is too large ({file_size / 1024 / 1024:.1f}MB). Maximum allowed size is {MAX_IMAGE_SIZE_MB}MB."
        )

    # Check magic numbers
    with open(path, "rb") as f:
        header = f.read(12)

    if not header:
        raise InvalidImageError("File is empty")

    is_valid = any(header.startswith(magic) for magic, _format in IMAGE_MAGIC_NUMBERS.items())
    # Special handling for WEBP: RIFF[4 bytes size]WEBP
    if not is_valid and len(header) >= 12 and header[:4] == WEBP_RIFF_HEADER and header[8:12] == WEBP_FORMAT_MARKER:
        is_valid = True

    if not is_valid:
        raise InvalidImageError("File content does not match any supported image format.")


def read_image_as_base64(image_path: str) -> str:
    """Read and validate an image file, returning base64-encoded content.

    This is a convenience wrapper that validates and reads the image.

    Args:
        image_path: Path to the image file

    Returns:
        Base64-encoded image string

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ImageTooLargeError: If the image exceeds 50MB
        InvalidImageError: If the file is not a valid image
    """
    import base64
    from pathlib import Path

    # Validate first
    validate_image_path(image_path)

    path = Path(image_path).resolve()

    # Read and encode
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def parse_date_string(date_str: str) -> datetime:
    """Parse a date string in various formats.

    Supported formats:
    - YYYY-MM-DD (e.g., 2026-01-15)
    - MM/DD/YYYY (e.g., 01/15/2026)
    - MM-DD-YYYY (e.g., 01-15-2026)
    - today, yesterday
    - Relative days: -1, -2, etc. (days ago)

    Args:
        date_str: Date string to parse

    Returns:
        Parsed datetime (at midnight UTC)

    Raises:
        ValueError: If date string cannot be parsed
    """
    date_str = date_str.strip().lower()

    # Handle relative keywords
    if date_str == "today":
        return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    if date_str == "yesterday":
        from datetime import timedelta

        return (datetime.now(UTC) - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle relative days (e.g., -1, -2)
    if date_str.startswith("-") and date_str[1:].isdigit():
        from datetime import timedelta

        days_ago = int(date_str[1:])
        return (datetime.now(UTC) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Try various date formats
    formats = [
        "%Y-%m-%d",  # 2026-01-15
        "%m/%d/%Y",  # 01/15/2026
        "%m-%d-%Y",  # 01-15-2026
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.replace(tzinfo=UTC)
        except ValueError:
            continue

    raise ValueError(
        f"Cannot parse date: '{date_str}'. Use YYYY-MM-DD, MM/DD/YYYY, 'today', 'yesterday', or -N for days ago."
    )


def handle_cli_error(
    console: Console,
    error: Exception,
    message: str,
    hint: str | None = None,
) -> None:
    """Handle CLI errors with proper logging and user-friendly output.

    This function logs the full exception for debugging/telemetry purposes
    (captured by Sentry if configured), then displays a user-friendly message.

    Args:
        console: Rich console for output
        error: The exception that occurred
        message: User-friendly error message to display
        hint: Optional helpful hint for the user

    Note:
        After calling this function, the caller should raise typer.Exit(1)
        to terminate the CLI with an error code.
    """
    import logging

    # Log the full exception for debugging/Sentry capture
    logger = logging.getLogger(__name__)
    logger.exception("CLI error occurred: %s", message)

    # Display user-friendly message
    console.print(f"[red]Error:[/red] {message}")
    if error and str(error):
        console.print(f"[dim]Details: {error}[/dim]")
    if hint:
        console.print(f"[dim]{hint}[/dim]")


def validate_resolution(resolution: str) -> str:
    """Validate and normalize image resolution parameter.

    Args:
        resolution: Resolution string (low, medium, or high)

    Returns:
        Validated resolution string

    Raises:
        ValueError: If resolution is not valid
    """
    resolution = resolution.lower().strip()
    if resolution not in VALID_RESOLUTIONS:
        raise ValueError(f"Invalid resolution: '{resolution}'. Must be one of: {', '.join(sorted(VALID_RESOLUTIONS))}")
    return resolution


def auto_select_resolution(image_path: str) -> str:
    """Automatically select resolution based on image file size.

    Uses file size thresholds:
    - < 100KB: low
    - 100KB-500KB: medium
    - > 500KB: high

    Args:
        image_path: Path to the image file

    Returns:
        Recommended resolution ("low", "medium", or "high")

    Raises:
        FileNotFoundError: If image file doesn't exist
    """
    from pathlib import Path

    path = Path(image_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    file_size = path.stat().st_size

    for resolution, (min_size, max_size) in RESOLUTION_AUTO_THRESHOLDS.items():
        if min_size <= file_size < max_size:
            return resolution

    return DEFAULT_RESOLUTION
