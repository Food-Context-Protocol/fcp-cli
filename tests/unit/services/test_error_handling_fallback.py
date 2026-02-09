"""Final test for line 226 - exhaust retries via continue without exception."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fcp_cli.services.fcp_client_core import FcpClientCore
from fcp_cli.services.fcp_errors import FcpClientError

pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestLine226Final:
    """Test the real path to reach line 226."""

    @pytest.mark.asyncio
    async def test_exhaust_retries_via_continue_without_exception(self):
        """Test line 226 when retries are exhausted via continue without capturing exception."""
        client = FcpClientCore(max_retries=2, retry_delay=0.001)

        with patch.object(client, "_get_client") as mock_get_client:
            mock_http_client = AsyncMock()

            # Return a 500 error response every time
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.content = b""

            async def mock_request(*args, **kwargs):
                return mock_response

            mock_http_client.request = mock_request

            # Make _get_client properly async-compatible
            async def mock_get_client_impl():
                return mock_http_client

            mock_get_client.side_effect = mock_get_client_impl

            # Mock _should_retry_response to ALWAYS return True
            # This causes the code to hit 'continue' at line 178 every iteration
            with patch.object(client, "_should_retry_response", return_value=True):
                # Mock asyncio.sleep to make test fast
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    # This should exhaust all retries via 'continue' statements
                    # without ever setting last_exception (no except block entered)
                    # Then it reaches line 226!
                    with pytest.raises(FcpClientError, match="Unexpected error in request handling"):
                        await client._request("GET", "/test")
