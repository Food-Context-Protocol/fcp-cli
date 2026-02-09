"""Core HTTP client for FCP CLI service."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import httpx

from fcp_cli.config import settings
from fcp_cli.services.fcp_errors import (
    FcpAuthError,
    FcpClientError,
    FcpConnectionError,
    FcpNotFoundError,
    FcpRateLimitError,
    FcpResponseTooLargeError,
    FcpServerError,
)

logger = logging.getLogger(__name__)


class FcpClientCore:
    """HTTP client for the FCP server with retry logic and connection pooling."""

    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_RETRY_BACKOFF = 2.0

    RETRYABLE_STATUS_CODES = {502, 503, 504}

    DEFAULT_MAX_RESPONSE_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        base_url: str | None = None,
        user_id: str | None = None,
        timeout: float = 30.0,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        auth_token: str | None = None,
        max_response_size: int | None = None,
        auto_close: bool = True,
    ):
        self.base_url = (base_url or settings.fcp_server_url).rstrip("/")
        self.user_id = user_id or settings.fcp_user_id
        self.timeout = timeout
        self.max_retries = max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES
        self.retry_delay = retry_delay if retry_delay is not None else self.DEFAULT_RETRY_DELAY
        self.auth_token = auth_token if auth_token is not None else settings.fcp_auth_token
        self.max_response_size = max_response_size if max_response_size is not None else self.DEFAULT_MAX_RESPONSE_SIZE
        self._client: httpx.AsyncClient | None = None
        self._auto_close = auto_close
        self._auto_close_default = auto_close

    @property
    def is_authenticated(self) -> bool:
        return self.auth_token is not None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {
                "User-Agent": "FCP-CLI/1.0",
                "X-Client-Type": "cli",
            }
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"

            # Optimized HTTP client with connection pooling and HTTP/2
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers,
                limits=httpx.Limits(
                    max_connections=20,  # Total connection pool
                    max_keepalive_connections=10,  # Keep connections alive
                    keepalive_expiry=30.0,  # Keep alive for 30s
                ),
                http2=True,  # Enable HTTP/2 for multiplexing
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> FcpClientCore:
        self._auto_close = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        await self.close()
        self._auto_close = self._auto_close_default

    def _handle_http_error(self, response: httpx.Response) -> None:
        status_code = response.status_code

        if status_code == 404:
            raise FcpNotFoundError(f"Resource not found: {response.url}")
        if status_code in (401, 403):
            raise FcpAuthError(status_code)
        if status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise FcpRateLimitError(retry_seconds)
        if status_code >= 500:
            raise FcpServerError(status_code)
        response.raise_for_status()

    def _retry_wait(self, delay: float) -> float:
        jitter = random.uniform(0, 0.1) * delay
        return delay + jitter

    def _parse_retry_after(self, response: httpx.Response, fallback: float) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            return float(int(retry_after))
        return fallback

    def _should_retry_response(self, response: httpx.Response, attempt: int) -> bool:
        if attempt >= self.max_retries:
            return False
        if response.status_code == 429:
            return True
        return response.status_code in self.RETRYABLE_STATUS_CODES

    async def _cleanup_if_needed(self) -> None:
        """Close client if auto_close is enabled."""
        if self._auto_close:
            await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        client = await self._get_client()
        last_exception: Exception | None = None
        delay = self.retry_delay

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.request(
                        method=method,
                        url=f"{self.base_url}{path}",
                        json=json,
                        params=params,
                    )

                    if response.status_code >= 400:
                        if self._should_retry_response(response, attempt):
                            if response.status_code == 429:
                                wait_time = self._parse_retry_after(response, delay)
                                logger.warning(
                                    "Rate limited on %s, waiting %ss (attempt %s/%s)",
                                    path,
                                    int(wait_time),
                                    attempt + 1,
                                    self.max_retries,
                                )
                            else:
                                wait_time = self._retry_wait(delay)
                                logger.warning(
                                    "Retrying request to %s after %s (attempt %s/%s)",
                                    path,
                                    response.status_code,
                                    attempt + 1,
                                    self.max_retries,
                                )
                            await asyncio.sleep(wait_time)
                            delay *= self.DEFAULT_RETRY_BACKOFF
                            continue
                        self._handle_http_error(response)

                    if self.max_response_size > 0:
                        content_length = len(response.content)
                        if content_length > self.max_response_size:
                            raise FcpResponseTooLargeError(content_length, self.max_response_size)

                    return response.json()

                except httpx.ConnectError as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        logger.warning(
                            "Connection error to %s, retrying (attempt %s/%s): %s",
                            path,
                            attempt + 1,
                            self.max_retries,
                            e,
                        )
                        await asyncio.sleep(self._retry_wait(delay))
                        delay *= self.DEFAULT_RETRY_BACKOFF
                        continue
                    break

                except httpx.TimeoutException as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        logger.warning(
                            "Timeout on %s, retrying (attempt %s/%s): %s",
                            path,
                            attempt + 1,
                            self.max_retries,
                            e,
                        )
                        await asyncio.sleep(self._retry_wait(delay))
                        delay *= self.DEFAULT_RETRY_BACKOFF
                        continue
                    break
        finally:
            await self._cleanup_if_needed()

        if last_exception:
            message = f"Connection error: request failed after {self.max_retries} retries: {last_exception}"
            if isinstance(last_exception, httpx.TimeoutException) and "timed out" not in message.lower():
                message = f"{message} (timed out)"
            raise FcpConnectionError(message) from last_exception
        raise FcpClientError("Unexpected error in request handling")

    async def health_check(self) -> dict[str, Any]:
        return await self._request("GET", "/health/")
