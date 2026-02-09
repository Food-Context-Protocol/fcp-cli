"""FCP client error types."""


class FcpClientError(Exception):
    """Base exception for FCP client errors."""


class FcpConnectionError(FcpClientError):
    """Raised when unable to connect to FCP server."""


class FcpServerError(FcpClientError):
    """Raised when FCP server returns a 5xx error."""

    def __init__(self, status_code: int, message: str = "Server error"):
        self.status_code = status_code
        super().__init__(f"{message} (HTTP {status_code})")


class FcpNotFoundError(FcpClientError):
    """Raised when resource is not found (404)."""


class FcpAuthError(FcpClientError):
    """Raised when authentication fails (401/403)."""

    def __init__(self, status_code: int, message: str = "Authentication error"):
        self.status_code = status_code
        super().__init__(f"{message} (HTTP {status_code})")


class FcpRateLimitError(FcpClientError):
    """Raised when rate limited (429)."""

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        msg = "Rate limited"
        if retry_after:
            msg += f" (retry after {retry_after}s)"
        super().__init__(msg)


class FcpResponseTooLargeError(FcpClientError):
    """Raised when response exceeds maximum allowed size."""

    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(
            f"Response too large: {size / 1024 / 1024:.1f}MB exceeds limit of {max_size / 1024 / 1024:.0f}MB"
        )
