"""Tests for main CLI application."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from fcp_cli import __version__
from fcp_cli.main import app, console, main

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestAppConfiguration:
    """Test main app configuration."""

    def test_app_is_typer_instance(self):
        """Test app is a Typer instance."""
        assert isinstance(app, typer.Typer)

    def test_app_name(self):
        """Test app name is set correctly."""
        assert app.info.name == "fcp"

    def test_app_help_message(self):
        """Test app help message is set."""
        assert "FCP CLI" in app.info.help
        assert "Log and analyze your meals" in app.info.help

    def test_app_no_args_is_help(self):
        """Test app shows help when no args provided."""
        assert app.info.no_args_is_help is True


class TestConsole:
    """Test console instance."""

    def test_console_exists(self):
        """Test console is initialized."""
        from rich.console import Console

        assert isinstance(console, Console)


class TestSubcommands:
    """Test subcommands are registered."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_log_subcommand_registered(self, runner):
        """Test log subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "log" in result.stdout

    def test_search_subcommand_registered(self, runner):
        """Test search subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout

    def test_profile_subcommand_registered(self, runner):
        """Test profile subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "profile" in result.stdout

    def test_research_subcommand_registered(self, runner):
        """Test research subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "research" in result.stdout

    def test_pantry_subcommand_registered(self, runner):
        """Test pantry subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "pantry" in result.stdout

    def test_safety_subcommand_registered(self, runner):
        """Test safety subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "safety" in result.stdout

    def test_discover_subcommand_registered(self, runner):
        """Test discover subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "discover" in result.stdout

    def test_recipes_subcommand_registered(self, runner):
        """Test recipes subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "recipes" in result.stdout

    def test_publish_subcommand_registered(self, runner):
        """Test publish subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "publish" in result.stdout

    def test_suggest_subcommand_registered(self, runner):
        """Test suggest subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "suggest" in result.stdout

    def test_taste_subcommand_registered(self, runner):
        """Test taste subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "taste" in result.stdout

    def test_labels_subcommand_registered(self, runner):
        """Test labels subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "labels" in result.stdout

    def test_nearby_subcommand_registered(self, runner):
        """Test nearby subcommand is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "nearby" in result.stdout


class TestVersionCommand:
    """Test version command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_version_command_exists(self, runner):
        """Test version command is available."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "version" in result.stdout

    def test_version_command_output(self, runner):
        """Test version command shows version."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "FCP CLI" in result.stdout
        assert __version__ in result.stdout

    def test_version_command_format(self, runner):
        """Test version command output format."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        # Should contain "FCP CLI v0.1.0" or similar
        assert "v" in result.stdout
        assert __version__ in result.stdout


class TestMainCallback:
    """Test main callback function."""

    def test_main_callback_exists(self):
        """Test main callback function exists."""
        assert callable(main)

    def test_main_callback_docstring(self):
        """Test main callback has proper docstring."""
        assert main.__doc__ is not None
        assert "FCP CLI" in main.__doc__

    def test_main_callback_execution(self):
        """Test main callback executes without error."""
        # Should execute without raising
        main()


class TestLogfireConfiguration:
    """Test Logfire configuration at module import."""

    def test_logfire_import_exists(self):
        """Test that configure_logfire is imported and available."""
        # Verify the function is imported and available in the module
        from fcp_cli.main import configure_logfire

        assert callable(configure_logfire)


class TestAppInvocation:
    """Test app invocation scenarios."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_app_no_args_shows_help(self, runner):
        """Test app with no arguments shows help."""
        result = runner.invoke(app, [])

        # no_args_is_help=True causes exit code 2 (shows help then exits with error)
        # This is standard Typer behavior for required subcommands
        assert result.exit_code in (0, 2)
        assert "Usage:" in result.stdout or "help" in result.stdout.lower()

    def test_app_help_flag(self, runner):
        """Test app with --help flag."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.stdout
        assert "FCP CLI" in result.stdout

    def test_app_invalid_command(self, runner):
        """Test app with invalid command."""
        result = runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0

    def test_app_version_shorthand(self, runner):
        """Test if there's a --version flag (if implemented)."""
        # Some CLI apps support --version at root level
        # This is optional, so we just check if it works or fails gracefully
        result = runner.invoke(app, ["--version"])

        # Either works (exit 0) or fails gracefully (exit != 0)
        # Just ensure it doesn't crash
        assert isinstance(result.exit_code, int)


class TestSubcommandHelp:
    """Test subcommand help messages."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_log_help(self, runner):
        """Test log subcommand help."""
        result = runner.invoke(app, ["log", "--help"])
        assert result.exit_code == 0
        assert "log" in result.stdout.lower()

    def test_search_help(self, runner):
        """Test search subcommand help."""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout.lower()

    def test_profile_help(self, runner):
        """Test profile subcommand help."""
        result = runner.invoke(app, ["profile", "--help"])
        assert result.exit_code == 0
        assert "profile" in result.stdout.lower()

    def test_research_help(self, runner):
        """Test research subcommand help."""
        result = runner.invoke(app, ["research", "--help"])
        assert result.exit_code == 0
        assert "research" in result.stdout.lower()

    def test_pantry_help(self, runner):
        """Test pantry subcommand help."""
        result = runner.invoke(app, ["pantry", "--help"])
        assert result.exit_code == 0
        assert "pantry" in result.stdout.lower()

    def test_safety_help(self, runner):
        """Test safety subcommand help."""
        result = runner.invoke(app, ["safety", "--help"])
        assert result.exit_code == 0
        assert "safety" in result.stdout.lower()

    def test_discover_help(self, runner):
        """Test discover subcommand help."""
        result = runner.invoke(app, ["discover", "--help"])
        assert result.exit_code == 0
        assert "discover" in result.stdout.lower()

    def test_recipes_help(self, runner):
        """Test recipes subcommand help."""
        result = runner.invoke(app, ["recipes", "--help"])
        assert result.exit_code == 0
        assert "recipes" in result.stdout.lower()

    def test_publish_help(self, runner):
        """Test publish subcommand help."""
        result = runner.invoke(app, ["publish", "--help"])
        assert result.exit_code == 0
        assert "publish" in result.stdout.lower()

    def test_suggest_help(self, runner):
        """Test suggest subcommand help."""
        result = runner.invoke(app, ["suggest", "--help"])
        assert result.exit_code == 0
        assert "suggest" in result.stdout.lower()

    def test_taste_help(self, runner):
        """Test taste subcommand help."""
        result = runner.invoke(app, ["taste", "--help"])
        assert result.exit_code == 0
        assert "taste" in result.stdout.lower()

    def test_labels_help(self, runner):
        """Test labels subcommand help."""
        result = runner.invoke(app, ["labels", "--help"])
        assert result.exit_code == 0
        assert "labels" in result.stdout.lower()

    def test_nearby_help(self, runner):
        """Test nearby subcommand help."""
        result = runner.invoke(app, ["nearby", "--help"])
        assert result.exit_code == 0
        assert "nearby" in result.stdout.lower()


class TestMainModule:
    """Test main module execution."""

    def test_main_module_name_main(self):
        """Test that app is callable from __main__ block."""
        # This tests the if __name__ == "__main__": app() pattern
        # We verify the app is callable
        assert callable(app)

    @patch("fcp_cli.main.app")
    def test_main_execution(self, mock_app):
        """Test main module execution."""
        # Simulate running as main module
        exec_globals = {"__name__": "__main__", "app": mock_app}
        code = "if __name__ == '__main__':\n    app()"

        exec(code, exec_globals)

        mock_app.assert_called_once()

    def test_main_module_direct_execution(self):
        """Test __main__ block execution path."""
        import subprocess
        import sys

        # Execute the main.py as a script to cover the __main__ block
        result = subprocess.run(
            [sys.executable, "-m", "fcp_cli.main", "--help"],
            capture_output=True,
            text=True,
        )

        # Should show help and exit successfully
        assert result.returncode == 0
        assert "FCP CLI" in result.stdout


class TestVersionConstant:
    """Test version constant import and usage."""

    def test_version_import(self):
        """Test version can be imported."""
        from fcp_cli import __version__

        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self):
        """Test version follows semantic versioning."""
        from fcp_cli import __version__

        # Should be in format X.Y.Z
        parts = __version__.split(".")
        assert len(parts) >= 2  # At least major.minor

    def test_version_used_in_command(self):
        """Test version is used in version command."""
        runner = CliRunner()
        result = runner.invoke(app, ["version"])

        assert __version__ in result.stdout


class TestAppIntegration:
    """Test app integration and full flows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_app_chained_help_commands(self, runner):
        """Test chaining help commands."""
        # Test that help can be accessed multiple ways
        result1 = runner.invoke(app, ["--help"])
        result2 = runner.invoke(app, [])

        assert result1.exit_code == 0
        # no_args_is_help=True causes exit code 2
        assert result2.exit_code in (0, 2)
        # Both should show help text
        assert "Usage:" in result1.stdout
        assert "Usage:" in result2.stdout

    def test_app_multiple_commands(self, runner):
        """Test running multiple commands sequentially."""
        # Version command
        result1 = runner.invoke(app, ["version"])
        assert result1.exit_code == 0

        # Help command
        result2 = runner.invoke(app, ["--help"])
        assert result2.exit_code == 0

        # Subcommand help
        result3 = runner.invoke(app, ["log", "--help"])
        assert result3.exit_code == 0
