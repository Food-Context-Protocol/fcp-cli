"""Tests for research commands."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.research import app

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestResearchAskCommand:
    """Test research ask command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def full_research_result(self):
        """Full research result with all fields."""
        # Create a mock object with the expected attributes
        result = MagicMock()
        result.summary = "Fermented foods contain beneficial probiotics that support gut health and immune function."
        result.key_points = [
            "Probiotics in fermented foods improve digestive health",
            "May enhance immune system function",
            "Can help with nutrient absorption",
            "Some studies show benefits for mental health",
        ]
        result.sources_consulted = 12
        result.confidence = "high"
        return result

    @pytest.fixture
    def minimal_research_result(self):
        """Minimal research result."""
        result = MagicMock()
        result.summary = "Limited information available on this topic."
        result.key_points = ["Further research needed"]
        result.sources_consulted = 2
        result.confidence = "low"
        return result

    @pytest.fixture
    def medium_confidence_result(self):
        """Research result with medium confidence."""
        result = MagicMock()
        result.summary = "Cooking methods affect nutrient retention to varying degrees."
        result.key_points = [
            "Steaming preserves more nutrients than boiling",
            "High heat can degrade some vitamins",
            "Fat-soluble vitamins may increase with cooking",
        ]
        result.sources_consulted = 7
        result.confidence = "medium"
        return result

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_basic_question(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test asking a basic research question."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        result = runner.invoke(
            app,
            ["What are the health benefits of fermented foods?"],
        )

        assert result.exit_code == 0
        assert "fermented foods" in result.stdout.lower()
        assert "probiotics" in result.stdout.lower()

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_displays_summary(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test that summary is displayed."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        result = runner.invoke(app, ["Test question?"])

        assert result.exit_code == 0
        assert "Summary" in result.stdout
        # Check for key words from summary (Rich may wrap the text)
        assert "beneficial probiotics" in result.stdout or "Fermented foods" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_displays_key_points(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test that key points are displayed."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        result = runner.invoke(app, ["Test question?"])

        assert result.exit_code == 0
        assert "Key Points" in result.stdout
        for point in full_research_result.key_points:
            assert point in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_displays_metadata(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test that metadata (sources, confidence) is displayed."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        result = runner.invoke(app, ["Test question?"])

        assert result.exit_code == 0
        assert "Metadata" in result.stdout
        assert "Sources: 12" in result.stdout
        assert "Confidence: high" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_minimal_result(self, mock_run_async, mock_agent_class, runner, minimal_research_result):
        """Test with minimal research result."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=minimal_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = minimal_research_result

        result = runner.invoke(app, ["Obscure food topic?"])

        assert result.exit_code == 0
        assert "Limited information" in result.stdout
        assert "Sources: 2" in result.stdout
        assert "Confidence: low" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_medium_confidence(self, mock_run_async, mock_agent_class, runner, medium_confidence_result):
        """Test result with medium confidence level."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=medium_confidence_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = medium_confidence_result

        result = runner.invoke(app, ["How does cooking affect nutrients?"])

        assert result.exit_code == 0
        assert "Confidence: medium" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_long_question(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test with a long, detailed question."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        long_question = (
            "What are the comprehensive health benefits and potential risks "
            "of consuming fermented foods like kimchi, sauerkraut, and kombucha "
            "on a daily basis for digestive health?"
        )

        result = runner.invoke(app, [long_question])

        assert result.exit_code == 0
        assert "Summary" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_question_with_quotes(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test question containing quotes."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        result = runner.invoke(
            app,
            ['What is the "superfood" status of blueberries?'],
        )

        assert result.exit_code == 0

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_single_key_point(self, mock_run_async, mock_agent_class, runner):
        """Test result with single key point."""
        result = MagicMock()
        result.summary = "Brief summary"
        result.key_points = ["Single important point"]
        result.sources_consulted = 3
        result.confidence = "medium"

        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = result

        cli_result = runner.invoke(app, ["Simple question?"])

        assert cli_result.exit_code == 0
        assert "Single important point" in cli_result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_many_key_points(self, mock_run_async, mock_agent_class, runner):
        """Test result with many key points."""
        result = MagicMock()
        result.summary = "Detailed summary"
        result.key_points = [f"Key point {i}" for i in range(1, 11)]
        result.sources_consulted = 20
        result.confidence = "high"

        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = result

        cli_result = runner.invoke(app, ["Complex question?"])

        assert cli_result.exit_code == 0
        for i in range(1, 11):
            assert f"Key point {i}" in cli_result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_zero_sources(self, mock_run_async, mock_agent_class, runner):
        """Test result with zero sources consulted."""
        result = MagicMock()
        result.summary = "No sources found"
        result.key_points = ["Unable to find reliable information"]
        result.sources_consulted = 0
        result.confidence = "low"

        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = result

        cli_result = runner.invoke(app, ["Unknown topic?"])

        assert cli_result.exit_code == 0
        assert "Sources: 0" in cli_result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_shows_progress_spinner(self, mock_run_async, mock_agent_class, runner, full_research_result):
        """Test that progress spinner is shown during research."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(return_value=full_research_result)
        mock_agent_class.return_value = mock_agent
        mock_run_async.return_value = full_research_result

        result = runner.invoke(app, ["Test question?"])

        assert result.exit_code == 0
        # Progress spinner is transient, so we just check command succeeded

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_generic_error(self, mock_run_async, mock_agent_class, runner):
        """Test handling of generic exceptions."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(side_effect=Exception("Research failed"))
        mock_agent_class.return_value = mock_agent
        mock_run_async.side_effect = Exception("Research failed")

        result = runner.invoke(app, ["Test question?"])

        assert result.exit_code == 1
        assert "Research failed" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_network_error(self, mock_run_async, mock_agent_class, runner):
        """Test handling of network errors."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(side_effect=Exception("Network error"))
        mock_agent_class.return_value = mock_agent
        mock_run_async.side_effect = Exception("Network error")

        result = runner.invoke(app, ["Test question?"])

        assert result.exit_code == 1
        assert "Research failed" in result.stdout

    @patch("fcp_cli.agents.ResearchAgent")
    @patch("fcp_cli.commands.research.run_async")
    def test_ask_timeout_error(self, mock_run_async, mock_agent_class, runner):
        """Test handling of timeout errors."""
        mock_agent = MagicMock()
        mock_agent.research = AsyncMock(side_effect=Exception("Timeout"))
        mock_agent_class.return_value = mock_agent
        mock_run_async.side_effect = Exception("Timeout")

        result = runner.invoke(app, ["Complex question requiring lots of research?"])

        assert result.exit_code == 1
        assert "Research failed" in result.stdout


@pytest.mark.parametrize(
    "question,expected_in_output",
    [
        ("What are the benefits of omega-3?", "omega-3"),
        ("How does fiber affect digestion?", "fiber"),
        ("What is the glycemic index?", "glycemic"),
        ("Are artificial sweeteners safe?", "sweeteners"),
    ],
)
@patch("fcp_cli.agents.ResearchAgent")
@patch("fcp_cli.commands.research.run_async")
def test_ask_various_questions(mock_run_async, mock_agent_class, question, expected_in_output):
    """Test asking various research questions."""
    result = MagicMock()
    result.summary = f"Information about {expected_in_output}"
    result.key_points = [f"Key point about {expected_in_output}"]
    result.sources_consulted = 5
    result.confidence = "medium"

    mock_agent = MagicMock()
    mock_agent.research = AsyncMock(return_value=result)
    mock_agent_class.return_value = mock_agent
    mock_run_async.return_value = result

    runner = CliRunner()
    cli_result = runner.invoke(app, [question])

    assert cli_result.exit_code == 0
    assert expected_in_output in cli_result.stdout


@pytest.mark.parametrize(
    "confidence_level",
    ["high", "medium", "low"],
)
@patch("fcp_cli.agents.ResearchAgent")
@patch("fcp_cli.commands.research.run_async")
def test_ask_confidence_levels(mock_run_async, mock_agent_class, confidence_level):
    """Test all confidence levels are displayed correctly."""
    result = MagicMock()
    result.summary = "Test summary"
    result.key_points = ["Point 1", "Point 2"]
    result.sources_consulted = 5
    result.confidence = confidence_level

    mock_agent = MagicMock()
    mock_agent.research = AsyncMock(return_value=result)
    mock_agent_class.return_value = mock_agent
    mock_run_async.return_value = result

    runner = CliRunner()
    cli_result = runner.invoke(app, ["Test question?"])

    assert cli_result.exit_code == 0
    assert f"Confidence: {confidence_level}" in cli_result.stdout


@pytest.mark.parametrize(
    "sources_count",
    [0, 1, 5, 10, 25, 100],
)
@patch("fcp_cli.agents.ResearchAgent")
@patch("fcp_cli.commands.research.run_async")
def test_ask_sources_count_display(mock_run_async, mock_agent_class, sources_count):
    """Test various source counts are displayed correctly."""
    result = MagicMock()
    result.summary = "Test summary"
    result.key_points = ["Point 1"]
    result.sources_consulted = sources_count
    result.confidence = "medium"

    mock_agent = MagicMock()
    mock_agent.research = AsyncMock(return_value=result)
    mock_agent_class.return_value = mock_agent
    mock_run_async.return_value = result

    runner = CliRunner()
    cli_result = runner.invoke(app, ["Test question?"])

    assert cli_result.exit_code == 0
    assert f"Sources: {sources_count}" in cli_result.stdout
