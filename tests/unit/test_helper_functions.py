"""Tests for extracted helper functions to achieve 100% branch coverage."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


class TestProfileHelpers:
    """Test profile.py extracted helpers."""

    @patch("fcp_cli.commands.profile.console")
    def test_print_streak_encouragement_3_to_6_days(self, mock_console):
        """Test streak encouragement for 3-6 days."""
        from fcp_cli.commands.profile import _print_streak_encouragement

        # Call with streak between 3-6
        _print_streak_encouragement(5)

        # Should print "Great job!" message
        mock_console.print.assert_called_once()
        assert "Great job" in str(mock_console.print.call_args)

    @patch("fcp_cli.commands.profile.console")
    def test_print_streak_encouragement_1_to_2_days(self, mock_console):
        """Test streak encouragement for 1-2 days - covers line 185->exit."""
        from fcp_cli.commands.profile import _print_streak_encouragement

        # Call with streak of 1 or 2 - no encouragement message
        # This hits the implicit exit when all conditions are false
        _print_streak_encouragement(2)

        # Should NOT print anything (no conditions match)
        mock_console.print.assert_not_called()


class TestSearchHelpers:
    """Test search.py extracted helpers."""

    def test_format_log_timestamp_none(self):
        """Test formatting timestamp when None - covers line 146->149."""
        from fcp_cli.commands.search import _format_log_timestamp

        # Pass None timestamp to hit else branch at 146->149
        result = _format_log_timestamp(None)

        # Should return empty string
        assert result == ""


class TestFcpClientCoreHelpers:
    """Test fcp_client_core.py extracted helpers."""

    @pytest.mark.asyncio
    async def test_cleanup_if_needed_false(self):
        """Test cleanup when auto_close is False - covers line 218->221."""
        from fcp_cli.services.fcp_client_core import FcpClientCore

        # Create client with auto_close=False
        client = FcpClientCore(auto_close=False)

        # Spy on close method
        close_called = False
        original_close = client.close

        async def spy_close():
            nonlocal close_called
            close_called = True
            await original_close()

        client.close = spy_close

        # Call cleanup - should NOT close when auto_close is False
        await client._cleanup_if_needed()

        # Verify close was NOT called (branch 218->221)
        assert not close_called
