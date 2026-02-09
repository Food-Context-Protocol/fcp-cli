"""Tests for logfire_service."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fcp_cli.services import logfire_service

pytestmark = pytest.mark.unit


class TestLogfireConfiguration:
    """Test logfire configuration."""

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service._initialized", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_configure_logfire_with_token(self, mock_logfire):
        """Test configure_logfire when token is available."""
        # Reset initialization state
        logfire_service._initialized = False

        result = logfire_service.configure_logfire()

        assert result is True
        mock_logfire.configure.assert_called_once_with(
            service_name="fcp-cli",
            send_to_logfire=True,
        )
        mock_logfire.instrument_httpx.assert_called_once()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    @patch("fcp_cli.services.logfire_service._initialized", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_configure_logfire_without_token(self, mock_logfire):
        """Test configure_logfire when token is not available."""
        # Reset initialization state
        logfire_service._initialized = False

        result = logfire_service.configure_logfire()

        assert result is False
        mock_logfire.configure.assert_not_called()
        mock_logfire.instrument_httpx.assert_not_called()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service._initialized", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_configure_logfire_already_initialized(self, mock_logfire):
        """Test configure_logfire when already initialized."""
        result = logfire_service.configure_logfire()

        # Should return True since it's enabled
        assert result is True
        # Should not configure again
        mock_logfire.configure.assert_not_called()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    def test_is_enabled_true(self):
        """Test is_enabled returns True when enabled."""
        assert logfire_service.is_enabled() is True

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    def test_is_enabled_false(self):
        """Test is_enabled returns False when not enabled."""
        assert logfire_service.is_enabled() is False


class TestLogfireSpan:
    """Test logfire span context manager."""

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_span_when_enabled(self, mock_logfire):
        """Test span creates logfire span when enabled."""
        mock_logfire.span.return_value.__enter__ = MagicMock()
        mock_logfire.span.return_value.__exit__ = MagicMock()

        with logfire_service.span("test_span", key="value"):
            pass

        mock_logfire.span.assert_called_once_with("test_span", key="value")

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_span_when_disabled(self, mock_logfire):
        """Test span does nothing when disabled."""
        with logfire_service.span("test_span", key="value"):
            pass

        mock_logfire.span.assert_not_called()


class TestLogfireLogging:
    """Test logfire logging functions."""

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_info_when_enabled(self, mock_logfire):
        """Test info logs when enabled."""
        logfire_service.info("Test message", key="value")
        mock_logfire.info.assert_called_once_with("Test message", key="value")

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_info_when_disabled(self, mock_logfire):
        """Test info does nothing when disabled."""
        logfire_service.info("Test message", key="value")
        mock_logfire.info.assert_not_called()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_warn_when_enabled(self, mock_logfire):
        """Test warn logs when enabled."""
        logfire_service.warn("Warning message", key="value")
        mock_logfire.warn.assert_called_once_with("Warning message", key="value")

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_warn_when_disabled(self, mock_logfire):
        """Test warn does nothing when disabled."""
        logfire_service.warn("Warning message", key="value")
        mock_logfire.warn.assert_not_called()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_error_when_enabled(self, mock_logfire):
        """Test error logs when enabled."""
        logfire_service.error("Error message", key="value")
        mock_logfire.error.assert_called_once_with("Error message", key="value")

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_error_when_disabled(self, mock_logfire):
        """Test error does nothing when disabled."""
        logfire_service.error("Error message", key="value")
        mock_logfire.error.assert_not_called()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_debug_when_enabled(self, mock_logfire):
        """Test debug logs when enabled."""
        logfire_service.debug("Debug message", key="value")
        mock_logfire.debug.assert_called_once_with("Debug message", key="value")

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", False)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_debug_when_disabled(self, mock_logfire):
        """Test debug does nothing when disabled."""
        logfire_service.debug("Debug message", key="value")
        mock_logfire.debug.assert_not_called()

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_logging_with_multiple_attributes(self, mock_logfire):
        """Test logging with multiple attributes."""
        logfire_service.info("Message", key1="value1", key2="value2", count=42)
        mock_logfire.info.assert_called_once_with("Message", key1="value1", key2="value2", count=42)

    @patch("fcp_cli.services.logfire_service._LOGFIRE_ENABLED", True)
    @patch("fcp_cli.services.logfire_service.logfire")
    def test_logging_without_attributes(self, mock_logfire):
        """Test logging without attributes."""
        logfire_service.info("Message")
        mock_logfire.info.assert_called_once_with("Message")
