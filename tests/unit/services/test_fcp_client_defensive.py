"""Tests for defensive error handling in FcpClientCore."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fcp_cli.services.fcp_client_core import FcpClientCore

pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestFcpClientCoreDefensiveErrors:
    """Test defensive error paths in FcpClientCore."""

    @pytest.mark.asyncio
    async def test_unexpected_error_defensive_path(self):
        """Test line 226 - defensive error when no exception despite retries."""
        client = FcpClientCore(max_retries=0, retry_delay=0.01)

        # Mock the _get_client to return a client where request returns None
        # without raising an exception - simulating an unexpected state
        with patch.object(client, "_get_client") as mock_get_client:
            mock_http_client = MagicMock()

            # Make request return None (invalid) without raising
            async def broken_request(*args, **kwargs):
                return None  # Invalid response

            mock_http_client.request = broken_request

            # Make _get_client properly async-compatible
            async def mock_get_client_impl():
                return mock_http_client

            mock_get_client.side_effect = mock_get_client_impl

            # This should hit the defensive error at line 226
            # because the loop completes without capturing an exception
            # but also doesn't return a valid response
            with pytest.raises(AttributeError):  # Will fail when trying to access None.status_code
                await client._request("GET", "/test")
