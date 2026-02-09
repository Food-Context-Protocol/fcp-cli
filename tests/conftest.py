"""Pytest configuration and shared fixtures for fcp-cli tests."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_server_url():
    """Provide mock server URL for testing."""
    return "http://localhost:8080"


@pytest.fixture
def mock_user_id():
    """Provide mock user ID for testing."""
    return "test_user_123"


@pytest.fixture(autouse=True)
def mock_env(monkeypatch, mock_server_url, mock_user_id):
    """Set up mock environment variables for all tests."""
    monkeypatch.setenv("FCP_SERVER_URL", mock_server_url)
    monkeypatch.setenv("FCP_USER_ID", mock_user_id)
