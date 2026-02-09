"""Tests for utility functions."""

from __future__ import annotations

import asyncio
import base64
from datetime import UTC, datetime, timedelta
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
import typer
from rich.console import Console

from fcp_cli.utils import (
    DEFAULT_EXCLUDE_DAYS,
    DEFAULT_SEARCH_RADIUS_METERS,
    ID_DISPLAY_LENGTH,
    IMAGE_MAGIC_NUMBERS,
    MAX_IMAGE_SIZE_BYTES,
    MAX_IMAGE_SIZE_MB,
    MAX_PROFILE_ITEMS_DISPLAY,
    SUPPORTED_IMAGE_EXTENSIONS,
    WEBP_FORMAT_MARKER,
    WEBP_RIFF_HEADER,
    ImageTooLargeError,
    ImageValidationError,
    InvalidImageError,
    demo_safe,
    get_relative_time,
    handle_cli_error,
    parse_date_string,
    read_image_as_base64,
    run_async,
    show_progress,
    validate_image_path,
    validate_latitude,
    validate_latitude_callback,
    validate_limit,
    validate_longitude,
    validate_longitude_callback,
    validate_positive_int,
)

pytestmark = pytest.mark.unit


class TestConstants:
    """Test module constants."""

    def test_id_display_length(self):
        """Test ID_DISPLAY_LENGTH constant."""
        assert ID_DISPLAY_LENGTH == 8

    def test_max_profile_items_display(self):
        """Test MAX_PROFILE_ITEMS_DISPLAY constant."""
        assert MAX_PROFILE_ITEMS_DISPLAY == 5

    def test_default_search_radius_meters(self):
        """Test DEFAULT_SEARCH_RADIUS_METERS constant."""
        assert DEFAULT_SEARCH_RADIUS_METERS == 2000

    def test_default_exclude_days(self):
        """Test DEFAULT_EXCLUDE_DAYS constant."""
        assert DEFAULT_EXCLUDE_DAYS == 3

    def test_max_image_size(self):
        """Test image size constants."""
        assert MAX_IMAGE_SIZE_BYTES == 50 * 1024 * 1024
        assert MAX_IMAGE_SIZE_MB == 50

    def test_supported_image_extensions(self):
        """Test supported image extensions."""
        assert SUPPORTED_IMAGE_EXTENSIONS == {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    def test_image_magic_numbers(self):
        """Test image magic number headers."""
        assert b"\xff\xd8\xff" in IMAGE_MAGIC_NUMBERS
        assert IMAGE_MAGIC_NUMBERS[b"\xff\xd8\xff"] == "JPEG"
        assert IMAGE_MAGIC_NUMBERS[b"\x89PNG\r\n\x1a\n"] == "PNG"
        assert IMAGE_MAGIC_NUMBERS[b"GIF87a"] == "GIF"
        assert IMAGE_MAGIC_NUMBERS[b"GIF89a"] == "GIF"

    def test_webp_constants(self):
        """Test WEBP format constants."""
        assert WEBP_RIFF_HEADER == b"RIFF"
        assert WEBP_FORMAT_MARKER == b"WEBP"


class TestShowProgress:
    """Test show_progress context manager."""

    def test_show_progress_basic(self):
        """Test basic progress spinner."""
        console = Console(file=StringIO())

        with show_progress("Loading...", console):
            pass

        # Should not raise and completes successfully

    def test_show_progress_with_operation(self):
        """Test progress with actual operation."""
        console = Console(file=StringIO())
        executed = []

        with show_progress("Processing...", console):
            executed.append(True)

        assert executed == [True]

    def test_show_progress_with_exception(self):
        """Test progress when operation raises exception."""
        console = Console(file=StringIO())

        with pytest.raises(ValueError, match="Test error"):
            with show_progress("Failing...", console):
                raise ValueError("Test error")


class TestValidateLatitude:
    """Test latitude validation."""

    def test_validate_latitude_valid_positive(self):
        """Test valid positive latitude."""
        assert validate_latitude(45.0) == 45.0

    def test_validate_latitude_valid_negative(self):
        """Test valid negative latitude."""
        assert validate_latitude(-45.0) == -45.0

    def test_validate_latitude_valid_zero(self):
        """Test valid zero latitude."""
        assert validate_latitude(0.0) == 0.0

    def test_validate_latitude_valid_max(self):
        """Test valid maximum latitude."""
        assert validate_latitude(90.0) == 90.0

    def test_validate_latitude_valid_min(self):
        """Test valid minimum latitude."""
        assert validate_latitude(-90.0) == -90.0

    def test_validate_latitude_invalid_too_high(self):
        """Test latitude above 90."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90, got 91.0"):
            validate_latitude(91.0)

    def test_validate_latitude_invalid_too_low(self):
        """Test latitude below -90."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90, got -91.0"):
            validate_latitude(-91.0)


class TestValidateLongitude:
    """Test longitude validation."""

    def test_validate_longitude_valid_positive(self):
        """Test valid positive longitude."""
        assert validate_longitude(120.0) == 120.0

    def test_validate_longitude_valid_negative(self):
        """Test valid negative longitude."""
        assert validate_longitude(-120.0) == -120.0

    def test_validate_longitude_valid_zero(self):
        """Test valid zero longitude."""
        assert validate_longitude(0.0) == 0.0

    def test_validate_longitude_valid_max(self):
        """Test valid maximum longitude."""
        assert validate_longitude(180.0) == 180.0

    def test_validate_longitude_valid_min(self):
        """Test valid minimum longitude."""
        assert validate_longitude(-180.0) == -180.0

    def test_validate_longitude_invalid_too_high(self):
        """Test longitude above 180."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180, got 181.0"):
            validate_longitude(181.0)

    def test_validate_longitude_invalid_too_low(self):
        """Test longitude below -180."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180, got -181.0"):
            validate_longitude(-181.0)


class TestValidatePositiveInt:
    """Test positive integer validation."""

    def test_validate_positive_int_valid(self):
        """Test valid positive integer."""
        assert validate_positive_int(5) == 5

    def test_validate_positive_int_valid_min(self):
        """Test valid at minimum."""
        assert validate_positive_int(1, min_val=1) == 1

    def test_validate_positive_int_valid_max(self):
        """Test valid at maximum."""
        assert validate_positive_int(100, min_val=1, max_val=100) == 100

    def test_validate_positive_int_custom_min(self):
        """Test custom minimum value."""
        assert validate_positive_int(10, min_val=10) == 10

    def test_validate_positive_int_no_max(self):
        """Test with no maximum limit."""
        assert validate_positive_int(99999, min_val=1, max_val=None) == 99999

    def test_validate_positive_int_invalid_too_low(self):
        """Test value below minimum."""
        with pytest.raises(ValueError, match="Value must be at least 1, got 0"):
            validate_positive_int(0, min_val=1)

    def test_validate_positive_int_invalid_too_high(self):
        """Test value above maximum."""
        with pytest.raises(ValueError, match="Value must be at most 100, got 101"):
            validate_positive_int(101, min_val=1, max_val=100)

    def test_validate_positive_int_negative(self):
        """Test negative value."""
        with pytest.raises(ValueError, match="Value must be at least 1, got -5"):
            validate_positive_int(-5, min_val=1)


class TestValidateLimit:
    """Test limit validation callback."""

    def test_validate_limit_valid(self):
        """Test valid limit."""
        assert validate_limit(10) == 10

    def test_validate_limit_valid_min(self):
        """Test minimum limit."""
        assert validate_limit(1) == 1

    def test_validate_limit_valid_max(self):
        """Test maximum limit."""
        assert validate_limit(1000) == 1000

    def test_validate_limit_invalid_too_low(self):
        """Test limit below minimum."""
        with pytest.raises(typer.BadParameter, match="Value must be at least 1"):
            validate_limit(0)

    def test_validate_limit_invalid_too_high(self):
        """Test limit above maximum."""
        with pytest.raises(typer.BadParameter, match="Value must be at most 1000"):
            validate_limit(1001)


class TestValidateLatitudeCallback:
    """Test latitude validation callback."""

    def test_validate_latitude_callback_valid(self):
        """Test valid latitude callback."""
        assert validate_latitude_callback(45.0) == 45.0

    def test_validate_latitude_callback_invalid(self):
        """Test invalid latitude callback."""
        with pytest.raises(typer.BadParameter, match="Latitude must be between -90 and 90"):
            validate_latitude_callback(100.0)


class TestValidateLongitudeCallback:
    """Test longitude validation callback."""

    def test_validate_longitude_callback_valid(self):
        """Test valid longitude callback."""
        assert validate_longitude_callback(120.0) == 120.0

    def test_validate_longitude_callback_invalid(self):
        """Test invalid longitude callback."""
        with pytest.raises(typer.BadParameter, match="Longitude must be between -180 and 180"):
            validate_longitude_callback(200.0)


class TestRunAsync:
    """Test run_async helper."""

    def test_run_async_simple(self):
        """Test running simple async function."""

        async def simple_coro():
            return "result"

        result = run_async(simple_coro())
        assert result == "result"

    def test_run_async_with_await(self):
        """Test running async function with await."""

        async def async_operation():
            await asyncio.sleep(0.001)
            return 42

        result = run_async(async_operation())
        assert result == 42

    def test_run_async_with_exception(self):
        """Test running async function that raises."""

        async def failing_coro():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            run_async(failing_coro())


class TestGetRelativeTime:
    """Test get_relative_time function."""

    def test_get_relative_time_just_now(self):
        """Test 'just now' for recent times."""
        now = datetime.now(UTC)
        assert get_relative_time(now) == "just now"

    def test_get_relative_time_seconds_ago(self):
        """Test times within last minute."""
        dt = datetime.now(UTC) - timedelta(seconds=30)
        assert get_relative_time(dt) == "just now"

    def test_get_relative_time_one_minute(self):
        """Test exactly one minute ago."""
        dt = datetime.now(UTC) - timedelta(minutes=1)
        assert get_relative_time(dt) == "1 min ago"

    def test_get_relative_time_multiple_minutes(self):
        """Test multiple minutes ago."""
        dt = datetime.now(UTC) - timedelta(minutes=30)
        assert get_relative_time(dt) == "30 mins ago"

    def test_get_relative_time_one_hour(self):
        """Test exactly one hour ago."""
        dt = datetime.now(UTC) - timedelta(hours=1)
        assert get_relative_time(dt) == "1 hour ago"

    def test_get_relative_time_multiple_hours(self):
        """Test multiple hours ago."""
        dt = datetime.now(UTC) - timedelta(hours=12)
        assert get_relative_time(dt) == "12 hours ago"

    def test_get_relative_time_yesterday(self):
        """Test yesterday."""
        dt = datetime.now(UTC) - timedelta(days=1)
        assert get_relative_time(dt) == "yesterday"

    def test_get_relative_time_days_ago(self):
        """Test multiple days ago."""
        dt = datetime.now(UTC) - timedelta(days=3)
        assert get_relative_time(dt) == "3 days ago"

    def test_get_relative_time_week_ago(self):
        """Test week or more ago returns formatted date."""
        dt = datetime.now(UTC) - timedelta(days=8)
        result = get_relative_time(dt)
        assert "-" in result  # Should be formatted as YYYY-MM-DD

    def test_get_relative_time_naive_datetime(self):
        """Test with naive datetime (assumes UTC)."""
        # Use UTC to avoid timezone issues
        dt = datetime.now(UTC) - timedelta(minutes=5)
        # Remove timezone to make it naive, then test
        dt_naive = dt.replace(tzinfo=None)
        result = get_relative_time(dt_naive)
        assert "min" in result

    def test_get_relative_time_future(self):
        """Test with future datetime."""
        dt = datetime.now(UTC) + timedelta(hours=1)
        result = get_relative_time(dt)
        assert "-" in result  # Should return formatted date


class TestImageValidationExceptions:
    """Test image validation exceptions."""

    def test_image_validation_error_base(self):
        """Test base ImageValidationError."""
        error = ImageValidationError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_image_too_large_error(self):
        """Test ImageTooLargeError."""
        error = ImageTooLargeError("File too large")
        assert str(error) == "File too large"
        assert isinstance(error, ImageValidationError)

    def test_invalid_image_error(self):
        """Test InvalidImageError."""
        error = InvalidImageError("Invalid format")
        assert str(error) == "Invalid format"
        assert isinstance(error, ImageValidationError)


class TestValidateImagePath:
    """Test validate_image_path function."""

    def test_validate_image_path_valid_png(self, tmp_path):
        """Test valid PNG image."""
        img_path = tmp_path / "test.png"
        # PNG magic number
        img_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        validate_image_path(str(img_path))  # Should not raise

    def test_validate_image_path_valid_jpeg(self, tmp_path):
        """Test valid JPEG image."""
        img_path = tmp_path / "test.jpg"
        # JPEG magic number
        img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        validate_image_path(str(img_path))  # Should not raise

    def test_validate_image_path_valid_gif87(self, tmp_path):
        """Test valid GIF87a image."""
        img_path = tmp_path / "test.gif"
        img_path.write_bytes(b"GIF87a" + b"\x00" * 100)

        validate_image_path(str(img_path))  # Should not raise

    def test_validate_image_path_valid_gif89(self, tmp_path):
        """Test valid GIF89a image."""
        img_path = tmp_path / "test.gif"
        img_path.write_bytes(b"GIF89a" + b"\x00" * 100)

        validate_image_path(str(img_path))  # Should not raise

    def test_validate_image_path_valid_webp(self, tmp_path):
        """Test valid WEBP image."""
        img_path = tmp_path / "test.webp"
        # WEBP: RIFF[size]WEBP
        img_path.write_bytes(b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100)

        validate_image_path(str(img_path))  # Should not raise

    def test_validate_image_path_not_found(self, tmp_path):
        """Test non-existent file."""
        with pytest.raises(FileNotFoundError, match="Image not found"):
            validate_image_path(str(tmp_path / "nonexistent.png"))

    def test_validate_image_path_directory(self, tmp_path):
        """Test path is a directory."""
        directory = tmp_path / "dir.png"
        directory.mkdir()

        with pytest.raises(InvalidImageError, match="Path is not a regular file"):
            validate_image_path(str(directory))

    def test_validate_image_path_unsupported_extension(self, tmp_path):
        """Test unsupported file extension."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("Not an image")

        with pytest.raises(InvalidImageError, match="Unsupported file extension"):
            validate_image_path(str(txt_path))

    def test_validate_image_path_too_large(self, tmp_path):
        """Test file exceeds size limit."""
        img_path = tmp_path / "large.png"
        # Create file larger than MAX_IMAGE_SIZE_BYTES
        large_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * (MAX_IMAGE_SIZE_BYTES + 1000)
        img_path.write_bytes(large_data)

        with pytest.raises(ImageTooLargeError, match="Image file is too large"):
            validate_image_path(str(img_path))

    def test_validate_image_path_empty_file(self, tmp_path):
        """Test empty file."""
        img_path = tmp_path / "empty.png"
        img_path.write_bytes(b"")

        with pytest.raises(InvalidImageError, match="File is empty"):
            validate_image_path(str(img_path))

    def test_validate_image_path_invalid_magic_number(self, tmp_path):
        """Test file with invalid magic number."""
        img_path = tmp_path / "fake.png"
        img_path.write_bytes(b"NOTANIMAGE" + b"\x00" * 100)

        with pytest.raises(InvalidImageError, match="File content does not match any supported image format"):
            validate_image_path(str(img_path))


class TestReadImageAsBase64:
    """Test read_image_as_base64 function."""

    def test_read_image_as_base64_valid(self, tmp_path):
        """Test reading valid image as base64."""
        img_path = tmp_path / "test.png"
        content = b"\x89PNG\r\n\x1a\n" + b"test_image_data"
        img_path.write_bytes(content)

        result = read_image_as_base64(str(img_path))

        # Should return base64 encoded string
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert decoded == content

    def test_read_image_as_base64_invalid(self, tmp_path):
        """Test reading invalid file raises error."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("Not an image")

        with pytest.raises(InvalidImageError):
            read_image_as_base64(str(txt_path))


class TestParseDateString:
    """Test parse_date_string function."""

    def test_parse_date_string_today(self):
        """Test parsing 'today'."""
        result = parse_date_string("today")
        expected = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == expected.date()
        assert result.hour == 0
        assert result.minute == 0

    def test_parse_date_string_yesterday(self):
        """Test parsing 'yesterday'."""
        result = parse_date_string("yesterday")
        expected = (datetime.now(UTC) - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == expected.date()

    def test_parse_date_string_relative_days(self):
        """Test parsing relative days like '-1', '-2'."""
        result = parse_date_string("-3")
        expected = (datetime.now(UTC) - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == expected.date()

    def test_parse_date_string_iso_format(self):
        """Test parsing ISO format YYYY-MM-DD."""
        result = parse_date_string("2026-01-15")
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15
        assert result.tzinfo == UTC

    def test_parse_date_string_us_format_slash(self):
        """Test parsing US format MM/DD/YYYY."""
        result = parse_date_string("01/15/2026")
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_string_us_format_dash(self):
        """Test parsing US format MM-DD-YYYY."""
        result = parse_date_string("01-15-2026")
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_string_uppercase_today(self):
        """Test case insensitivity."""
        result = parse_date_string("TODAY")
        expected = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result.date() == expected.date()

    def test_parse_date_string_with_whitespace(self):
        """Test parsing with leading/trailing whitespace."""
        result = parse_date_string("  2026-01-15  ")
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_string_invalid(self):
        """Test parsing invalid date string."""
        with pytest.raises(ValueError, match="Cannot parse date"):
            parse_date_string("invalid-date")

    def test_parse_date_string_invalid_format(self):
        """Test parsing unsupported format."""
        with pytest.raises(ValueError, match="Cannot parse date"):
            parse_date_string("15-Jan-2026")


class TestHandleCliError:
    """Test handle_cli_error function."""

    def test_handle_cli_error_basic(self):
        """Test basic error handling."""
        console = Console(file=StringIO())
        error = ValueError("Test error")

        with patch("logging.getLogger") as mock_logger:
            logger_instance = MagicMock()
            mock_logger.return_value = logger_instance

            handle_cli_error(console, error, "Operation failed")

            # Should log the exception
            logger_instance.exception.assert_called_once()

    def test_handle_cli_error_with_hint(self):
        """Test error handling with hint."""
        console = Console(file=StringIO())
        error = ValueError("Test error")

        with patch("logging.getLogger") as mock_logger:
            logger_instance = MagicMock()
            mock_logger.return_value = logger_instance

            handle_cli_error(
                console,
                error,
                "Operation failed",
                hint="Try running with --debug flag",
            )

            logger_instance.exception.assert_called_once()

    def test_handle_cli_error_no_hint(self):
        """Test error handling without hint."""
        console = Console(file=StringIO())
        error = ValueError("Test error")

        with patch("logging.getLogger") as mock_logger:
            logger_instance = MagicMock()
            mock_logger.return_value = logger_instance

            handle_cli_error(console, error, "Operation failed", hint=None)

            logger_instance.exception.assert_called_once()

    def test_handle_cli_error_empty_error_message(self):
        """Test error handling with empty error message."""
        console = Console(file=StringIO())
        error = ValueError("")

        with patch("logging.getLogger") as mock_logger:
            logger_instance = MagicMock()
            mock_logger.return_value = logger_instance

            handle_cli_error(console, error, "Operation failed")

            logger_instance.exception.assert_called_once()

    def test_handle_cli_error_output_format(self):
        """Test error output format to console."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)
        error = ValueError("Connection timeout")

        with patch("logging.getLogger"):
            handle_cli_error(
                console,
                error,
                "Failed to connect",
                hint="Check your network connection",
            )

            result = output.getvalue()
            # Check that error message appears in output
            # Note: Rich formatting adds ANSI codes, so we just check for presence
            assert "Failed to connect" in result or "Error" in result


class TestDemoSafe:
    """Test demo_safe decorator for graceful error handling."""

    def test_demo_safe_successful_execution(self):
        """Test that demo_safe allows successful execution."""

        @demo_safe
        def successful_func(x: int, y: int) -> int:
            return x + y

        result = successful_func(2, 3)
        assert result == 5

    def test_demo_safe_with_exception(self):
        """Test that demo_safe catches exceptions and exits gracefully."""

        @demo_safe
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(typer.Exit) as exc_info:
            failing_func()

        assert exc_info.value.exit_code == 1

    def test_demo_safe_exception_message_displayed(self, capsys):
        """Test that demo_safe displays user-friendly error message."""

        @demo_safe
        def failing_func():
            raise ValueError("Something went wrong")

        with pytest.raises(typer.Exit):
            failing_func()

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Something went wrong" in captured.out

    def test_demo_safe_keyboard_interrupt(self):
        """Test that demo_safe catches KeyboardInterrupt."""

        @demo_safe
        def interrupted_func():
            raise KeyboardInterrupt

        with pytest.raises(typer.Exit) as exc_info:
            interrupted_func()

        # KeyboardInterrupt should exit with code 0 (clean exit)
        assert exc_info.value.exit_code == 0

    def test_demo_safe_keyboard_interrupt_message(self, capsys):
        """Test that demo_safe shows 'Cancelled' message for KeyboardInterrupt."""

        @demo_safe
        def interrupted_func():
            raise KeyboardInterrupt

        with pytest.raises(typer.Exit):
            interrupted_func()

        captured = capsys.readouterr()
        assert "Cancelled" in captured.out

    def test_demo_safe_with_debug_flag(self, monkeypatch):
        """Test that demo_safe re-raises exceptions when --debug flag is present."""
        monkeypatch.setattr("sys.argv", ["fcp", "--debug", "command"])

        @demo_safe
        def failing_func():
            raise ValueError("Debug mode error")

        # With --debug flag, the original exception should be raised
        with pytest.raises(ValueError, match="Debug mode error"):
            failing_func()

    def test_demo_safe_without_debug_flag(self, monkeypatch):
        """Test that demo_safe suppresses exceptions without --debug flag."""
        monkeypatch.setattr("sys.argv", ["fcp", "command"])

        @demo_safe
        def failing_func():
            raise ValueError("Normal mode error")

        # Without --debug flag, should raise typer.Exit instead
        with pytest.raises(typer.Exit) as exc_info:
            failing_func()

        assert exc_info.value.exit_code == 1

    def test_demo_safe_preserves_function_metadata(self):
        """Test that demo_safe preserves function name and docstring."""

        @demo_safe
        def documented_func():
            """This is a documented function."""
            return "result"

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a documented function."

    def test_demo_safe_with_arguments(self):
        """Test that demo_safe works with functions that have arguments."""

        @demo_safe
        def func_with_args(a: str, b: int, c: bool = True):
            return f"{a}-{b}-{c}"

        result = func_with_args("test", 42, c=False)
        assert result == "test-42-False"

    def test_demo_safe_with_kwargs(self):
        """Test that demo_safe works with keyword arguments."""

        @demo_safe
        def func_with_kwargs(**kwargs):
            return kwargs

        result = func_with_kwargs(x=1, y=2, z=3)
        assert result == {"x": 1, "y": 2, "z": 3}

    def test_demo_safe_exception_types(self):
        """Test that demo_safe handles different exception types."""

        @demo_safe
        def runtime_error():
            raise RuntimeError("Runtime issue")

        @demo_safe
        def type_error():
            raise TypeError("Type issue")

        @demo_safe
        def key_error():
            raise KeyError("Key issue")

        # All should exit with code 1
        with pytest.raises(typer.Exit) as exc1:
            runtime_error()
        assert exc1.value.exit_code == 1

        with pytest.raises(typer.Exit) as exc2:
            type_error()
        assert exc2.value.exit_code == 1

        with pytest.raises(typer.Exit) as exc3:
            key_error()
        assert exc3.value.exit_code == 1

    def test_demo_safe_no_exception_message(self, capsys):
        """Test handling of exceptions with empty messages."""

        @demo_safe
        def empty_error():
            raise ValueError()

        with pytest.raises(typer.Exit):
            empty_error()

        captured = capsys.readouterr()
        # Should still show "Error:" prefix
        assert "Error:" in captured.out


class TestResolutionControl:
    """Test image resolution validation and auto-selection."""

    def test_validate_resolution_valid(self):
        """Test that validate_resolution accepts valid resolutions."""
        from fcp_cli.utils import validate_resolution

        assert validate_resolution("low") == "low"
        assert validate_resolution("medium") == "medium"
        assert validate_resolution("high") == "high"

        # Should normalize case
        assert validate_resolution("LOW") == "low"
        assert validate_resolution("Medium") == "medium"
        assert validate_resolution("  HIGH  ") == "high"

    def test_validate_resolution_invalid(self):
        """Test that validate_resolution raises ValueError for invalid resolutions."""
        from fcp_cli.utils import validate_resolution

        with pytest.raises(ValueError, match="Invalid resolution"):
            validate_resolution("ultra")

        with pytest.raises(ValueError, match="Invalid resolution"):
            validate_resolution("very_high")

        with pytest.raises(ValueError, match="Invalid resolution"):
            validate_resolution("")

    def test_auto_select_resolution_low(self, tmp_path):
        """Test auto-selection of low resolution for small images."""
        from fcp_cli.utils import auto_select_resolution

        # Create small file (<100KB)
        small_file = tmp_path / "small.jpg"
        small_file.write_bytes(b"x" * 50_000)  # 50KB

        resolution = auto_select_resolution(str(small_file))
        assert resolution == "low"

    def test_auto_select_resolution_medium(self, tmp_path):
        """Test auto-selection of medium resolution for medium images."""
        from fcp_cli.utils import auto_select_resolution

        # Create medium file (100KB-500KB)
        medium_file = tmp_path / "medium.jpg"
        medium_file.write_bytes(b"x" * 300_000)  # 300KB

        resolution = auto_select_resolution(str(medium_file))
        assert resolution == "medium"

    def test_auto_select_resolution_high(self, tmp_path):
        """Test auto-selection of high resolution for large images."""
        from fcp_cli.utils import auto_select_resolution

        # Create large file (>500KB)
        large_file = tmp_path / "large.jpg"
        large_file.write_bytes(b"x" * 600_000)  # 600KB

        resolution = auto_select_resolution(str(large_file))
        assert resolution == "high"

    def test_auto_select_resolution_edge_cases(self, tmp_path):
        """Test auto-selection at threshold boundaries."""
        from fcp_cli.utils import auto_select_resolution

        # Exactly at 100KB boundary
        boundary_low = tmp_path / "boundary_low.jpg"
        boundary_low.write_bytes(b"x" * 99_999)
        assert auto_select_resolution(str(boundary_low)) == "low"

        boundary_med = tmp_path / "boundary_med.jpg"
        boundary_med.write_bytes(b"x" * 100_000)
        assert auto_select_resolution(str(boundary_med)) == "medium"

        # Exactly at 500KB boundary
        boundary_med2 = tmp_path / "boundary_med2.jpg"
        boundary_med2.write_bytes(b"x" * 499_999)
        assert auto_select_resolution(str(boundary_med2)) == "medium"

        boundary_high = tmp_path / "boundary_high.jpg"
        boundary_high.write_bytes(b"x" * 500_000)
        assert auto_select_resolution(str(boundary_high)) == "high"

    def test_auto_select_resolution_file_not_found(self):
        """Test auto-selection raises FileNotFoundError for missing files."""
        from fcp_cli.utils import auto_select_resolution

        with pytest.raises(FileNotFoundError, match="Image not found"):
            auto_select_resolution("/nonexistent/path.jpg")

    def test_resolution_constants(self):
        """Test that resolution constants are defined correctly."""
        from fcp_cli.utils import DEFAULT_RESOLUTION, VALID_RESOLUTIONS

        assert DEFAULT_RESOLUTION == "medium"
        assert VALID_RESOLUTIONS == {"low", "medium", "high"}

    def test_resolution_thresholds(self):
        """Test that resolution thresholds are defined correctly."""
        from fcp_cli.utils import RESOLUTION_AUTO_THRESHOLDS

        assert RESOLUTION_AUTO_THRESHOLDS["low"] == (0, 100_000)
        assert RESOLUTION_AUTO_THRESHOLDS["medium"] == (100_000, 500_000)
        assert RESOLUTION_AUTO_THRESHOLDS["high"] == (500_000, float("inf"))


class TestAutoSelectResolutionEdgeCases:
    """Test auto_select_resolution edge cases."""

    def test_auto_select_resolution_fallback(self, tmp_path, monkeypatch):
        """Test auto_select_resolution fallback to default."""
        from fcp_cli import utils

        # Temporarily modify thresholds to test fallback
        original_thresholds = utils.RESOLUTION_AUTO_THRESHOLDS.copy()

        # Set thresholds that won't match any file size
        monkeypatch.setattr(utils, "RESOLUTION_AUTO_THRESHOLDS", {})

        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        result = utils.auto_select_resolution(str(test_file))

        # Should return DEFAULT_RESOLUTION when no threshold matches
        assert result == utils.DEFAULT_RESOLUTION

        # Restore original thresholds
        monkeypatch.setattr(utils, "RESOLUTION_AUTO_THRESHOLDS", original_thresholds)
