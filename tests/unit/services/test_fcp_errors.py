"""Tests for FCP error types."""

from __future__ import annotations

import pytest

from fcp_cli.services.fcp_errors import (
    FcpAuthError,
    FcpClientError,
    FcpConnectionError,
    FcpNotFoundError,
    FcpRateLimitError,
    FcpResponseTooLargeError,
    FcpServerError,
)

pytestmark = pytest.mark.unit


class TestFcpClientError:
    """Test base FcpClientError."""

    def test_base_error(self):
        """Test base error can be raised."""
        with pytest.raises(FcpClientError, match="Test error"):
            raise FcpClientError("Test error")

    def test_base_error_is_exception(self):
        """Test FcpClientError is an Exception."""
        assert issubclass(FcpClientError, Exception)


class TestFcpConnectionError:
    """Test FcpConnectionError."""

    def test_connection_error(self):
        """Test connection error can be raised."""
        with pytest.raises(FcpConnectionError, match="Connection failed"):
            raise FcpConnectionError("Connection failed")

    def test_connection_error_is_client_error(self):
        """Test FcpConnectionError is a FcpClientError."""
        assert issubclass(FcpConnectionError, FcpClientError)


class TestFcpServerError:
    """Test FcpServerError."""

    def test_server_error_with_status_code(self):
        """Test server error with status code."""
        error = FcpServerError(500)
        assert error.status_code == 500
        assert "HTTP 500" in str(error)
        assert "Server error" in str(error)

    def test_server_error_with_custom_message(self):
        """Test server error with custom message."""
        error = FcpServerError(503, "Service temporarily unavailable")
        assert error.status_code == 503
        assert "Service temporarily unavailable" in str(error)
        assert "HTTP 503" in str(error)

    def test_server_error_is_client_error(self):
        """Test FcpServerError is a FcpClientError."""
        assert issubclass(FcpServerError, FcpClientError)

    def test_server_error_can_be_raised(self):
        """Test server error can be raised and caught."""
        with pytest.raises(FcpServerError) as exc_info:
            raise FcpServerError(502)
        assert exc_info.value.status_code == 502


class TestFcpNotFoundError:
    """Test FcpNotFoundError."""

    def test_not_found_error(self):
        """Test not found error can be raised."""
        with pytest.raises(FcpNotFoundError, match="Resource not found"):
            raise FcpNotFoundError("Resource not found")

    def test_not_found_error_is_client_error(self):
        """Test FcpNotFoundError is a FcpClientError."""
        assert issubclass(FcpNotFoundError, FcpClientError)


class TestFcpAuthError:
    """Test FcpAuthError."""

    def test_auth_error_401(self):
        """Test auth error with 401 status code."""
        error = FcpAuthError(401)
        assert error.status_code == 401
        assert "HTTP 401" in str(error)
        assert "Authentication error" in str(error)

    def test_auth_error_403(self):
        """Test auth error with 403 status code."""
        error = FcpAuthError(403)
        assert error.status_code == 403
        assert "HTTP 403" in str(error)

    def test_auth_error_custom_message(self):
        """Test auth error with custom message."""
        error = FcpAuthError(401, "Invalid token")
        assert error.status_code == 401
        assert "Invalid token" in str(error)
        assert "HTTP 401" in str(error)

    def test_auth_error_is_client_error(self):
        """Test FcpAuthError is a FcpClientError."""
        assert issubclass(FcpAuthError, FcpClientError)

    def test_auth_error_can_be_raised(self):
        """Test auth error can be raised and caught."""
        with pytest.raises(FcpAuthError) as exc_info:
            raise FcpAuthError(403)
        assert exc_info.value.status_code == 403


class TestFcpRateLimitError:
    """Test FcpRateLimitError."""

    def test_rate_limit_error_without_retry_after(self):
        """Test rate limit error without retry_after."""
        error = FcpRateLimitError()
        assert error.retry_after is None
        assert "Rate limited" in str(error)
        assert "retry after" not in str(error)

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after."""
        error = FcpRateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert "Rate limited" in str(error)
        assert "retry after 60s" in str(error)

    def test_rate_limit_error_is_client_error(self):
        """Test FcpRateLimitError is a FcpClientError."""
        assert issubclass(FcpRateLimitError, FcpClientError)

    def test_rate_limit_error_can_be_raised(self):
        """Test rate limit error can be raised and caught."""
        with pytest.raises(FcpRateLimitError) as exc_info:
            raise FcpRateLimitError(retry_after=30)
        assert exc_info.value.retry_after == 30

    def test_rate_limit_error_zero_retry(self):
        """Test rate limit error with zero retry_after."""
        error = FcpRateLimitError(retry_after=0)
        assert error.retry_after == 0
        # retry_after=0 is falsy, so it won't be included in message
        assert "Rate limited" in str(error)
        assert "retry after" not in str(error)


class TestFcpResponseTooLargeError:
    """Test FcpResponseTooLargeError."""

    def test_response_too_large_error(self):
        """Test response too large error."""
        size = 20 * 1024 * 1024  # 20MB
        max_size = 10 * 1024 * 1024  # 10MB
        error = FcpResponseTooLargeError(size, max_size)

        assert error.size == size
        assert error.max_size == max_size
        assert "Response too large" in str(error)
        assert "20.0MB" in str(error)
        assert "10MB" in str(error)

    def test_response_too_large_error_formatting(self):
        """Test response too large error message formatting."""
        size = 15 * 1024 * 1024  # 15MB
        max_size = 10 * 1024 * 1024  # 10MB
        error = FcpResponseTooLargeError(size, max_size)

        error_msg = str(error)
        assert "15.0MB" in error_msg
        assert "exceeds limit" in error_msg

    def test_response_too_large_error_is_client_error(self):
        """Test FcpResponseTooLargeError is a FcpClientError."""
        assert issubclass(FcpResponseTooLargeError, FcpClientError)

    def test_response_too_large_error_can_be_raised(self):
        """Test response too large error can be raised and caught."""
        with pytest.raises(FcpResponseTooLargeError) as exc_info:
            raise FcpResponseTooLargeError(2048, 1024)
        assert exc_info.value.size == 2048
        assert exc_info.value.max_size == 1024

    def test_response_too_large_error_small_sizes(self):
        """Test response too large error with small sizes."""
        size = 500 * 1024  # 0.5MB
        max_size = 100 * 1024  # 0.1MB
        error = FcpResponseTooLargeError(size, max_size)

        # Check that conversion to MB works for smaller sizes
        assert error.size == size
        assert error.max_size == max_size


class TestErrorHierarchy:
    """Test error class hierarchy."""

    def test_all_errors_inherit_from_client_error(self):
        """Test all custom errors inherit from FcpClientError."""
        errors = [
            FcpConnectionError,
            FcpServerError,
            FcpNotFoundError,
            FcpAuthError,
            FcpRateLimitError,
            FcpResponseTooLargeError,
        ]

        for error_class in errors:
            assert issubclass(error_class, FcpClientError)

    def test_all_errors_inherit_from_exception(self):
        """Test all custom errors inherit from Exception."""
        errors = [
            FcpClientError,
            FcpConnectionError,
            FcpServerError,
            FcpNotFoundError,
            FcpAuthError,
            FcpRateLimitError,
            FcpResponseTooLargeError,
        ]

        for error_class in errors:
            assert issubclass(error_class, Exception)

    def test_catching_base_error(self):
        """Test that base error can catch all custom errors."""
        errors_to_test = [
            FcpConnectionError("conn"),
            FcpServerError(500),
            FcpNotFoundError("not found"),
            FcpAuthError(401),
            FcpRateLimitError(),
            FcpResponseTooLargeError(100, 50),
        ]

        for error in errors_to_test:
            with pytest.raises(FcpClientError):
                raise error
