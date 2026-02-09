"""Tests for CLI configuration with pydantic-settings."""

from __future__ import annotations

import pytest

from fcp_cli.config import CliSettings, settings

pytestmark = pytest.mark.unit


@pytest.fixture
def clean_env(monkeypatch):
    """Provide a clean environment without FCP env vars."""
    # Remove FCP env vars to test true defaults
    monkeypatch.delenv("FCP_SERVER_URL", raising=False)
    monkeypatch.delenv("FCP_USER_ID", raising=False)
    monkeypatch.delenv("FCP_AUTH_TOKEN", raising=False)


class TestCliSettings:
    """Test CliSettings pydantic model."""

    def test_default_values(self, clean_env):
        """Test default configuration values."""
        config = CliSettings()
        assert config.fcp_server_url == "http://localhost:8080"
        assert config.fcp_user_id == "demo"
        assert config.fcp_auth_token is None

    def test_custom_values_via_init(self):
        """Test setting custom values via constructor."""
        config = CliSettings(
            fcp_server_url="https://api.fcp.dev",
            fcp_user_id="test_user",
            fcp_auth_token="test_token",
        )
        assert config.fcp_server_url == "https://api.fcp.dev"
        assert config.fcp_user_id == "test_user"
        assert config.fcp_auth_token == "test_token"

    def test_env_var_loading(self, monkeypatch):
        """Test loading from environment variables."""
        monkeypatch.setenv("FCP_SERVER_URL", "https://prod.fcp.dev")
        monkeypatch.setenv("FCP_USER_ID", "prod_user")
        monkeypatch.setenv("FCP_AUTH_TOKEN", "prod_token")

        config = CliSettings()
        assert config.fcp_server_url == "https://prod.fcp.dev"
        assert config.fcp_user_id == "prod_user"
        assert config.fcp_auth_token == "prod_token"

    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test that env vars are case-insensitive."""
        monkeypatch.setenv("fcp_server_url", "https://test.fcp.dev")
        monkeypatch.setenv("FCP_USER_ID", "test_user")

        config = CliSettings()
        assert config.fcp_server_url == "https://test.fcp.dev"
        assert config.fcp_user_id == "test_user"

    def test_extra_env_vars_ignored(self, monkeypatch):
        """Test that unknown env vars don't cause errors."""
        monkeypatch.setenv("UNKNOWN_VAR", "should_be_ignored")
        monkeypatch.setenv("FCP_UNKNOWN", "also_ignored")

        # Should not raise an error
        config = CliSettings()
        assert not hasattr(config, "unknown_var")
        assert not hasattr(config, "fcp_unknown")


class TestUrlValidation:
    """Test URL validation and security warnings."""

    def test_localhost_http_allowed(self):
        """Test that HTTP is allowed for localhost."""
        config = CliSettings(fcp_server_url="http://localhost:8080")
        assert config.fcp_server_url == "http://localhost:8080"

    def test_127_0_0_1_http_allowed(self):
        """Test that HTTP is allowed for 127.0.0.1."""
        config = CliSettings(fcp_server_url="http://127.0.0.1:8080")
        assert config.fcp_server_url == "http://127.0.0.1:8080"

    def test_https_always_allowed(self):
        """Test that HTTPS is allowed for any host."""
        config = CliSettings(fcp_server_url="https://api.fcp.dev")
        assert config.fcp_server_url == "https://api.fcp.dev"

    def test_http_non_localhost_warns(self, caplog):
        """Test that HTTP to non-localhost produces warning."""
        import logging

        caplog.set_level(logging.WARNING)
        config = CliSettings(fcp_server_url="http://api.fcp.dev")

        # URL should still be accepted
        assert config.fcp_server_url == "http://api.fcp.dev"

        # But should have logged a warning
        assert any("insecure HTTP" in record.message for record in caplog.records)


class TestUserIdValidation:
    """Test user ID validation."""

    def test_demo_user_warns(self, caplog):
        """Test that demo user produces warning."""
        import logging

        caplog.set_level(logging.WARNING)
        config = CliSettings(fcp_user_id="demo")

        assert config.fcp_user_id == "demo"
        assert any("demo" in record.message.lower() for record in caplog.records)

    def test_custom_user_no_warning(self, caplog):
        """Test that custom user doesn't produce warning."""
        import logging

        caplog.set_level(logging.WARNING)
        config = CliSettings(fcp_user_id="real_user")

        assert config.fcp_user_id == "real_user"
        # Should not have demo warning
        assert not any("demo" in record.message.lower() for record in caplog.records)


class TestGlobalSettings:
    """Test the global settings instance."""

    def test_settings_instance_exists(self):
        """Test that global settings instance exists."""
        assert settings is not None
        assert isinstance(settings, CliSettings)

    def test_settings_has_defaults(self):
        """Test that global settings has default values."""
        # Note: This might show demo warning if FCP_USER_ID not set
        assert settings.fcp_server_url
        assert settings.fcp_user_id
        # auth_token can be None


class TestDotEnvLoading:
    """Test .env file loading."""

    def test_dotenv_support(self, tmp_path, monkeypatch, clean_env):
        """Test that .env file is loaded."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            """FCP_SERVER_URL=https://from-dotenv.fcp.dev
FCP_USER_ID=dotenv_user
FCP_AUTH_TOKEN=dotenv_token
"""
        )

        # Change to the directory with .env
        monkeypatch.chdir(tmp_path)

        # Create settings (should load from .env)
        config = CliSettings()

        # Verify values loaded from .env
        assert config.fcp_server_url == "https://from-dotenv.fcp.dev"
        assert config.fcp_user_id == "dotenv_user"
        assert config.fcp_auth_token == "dotenv_token"

    def test_env_vars_override_dotenv(self, tmp_path, monkeypatch, clean_env):
        """Test that environment variables override .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("FCP_SERVER_URL=https://from-dotenv.fcp.dev\n")

        monkeypatch.chdir(tmp_path)

        # Set env var (should override .env)
        monkeypatch.setenv("FCP_SERVER_URL", "https://from-env.fcp.dev")

        config = CliSettings()

        # Env var should win over .env file
        assert config.fcp_server_url == "https://from-env.fcp.dev"
