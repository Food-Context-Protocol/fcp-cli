"""Unit tests for research agent with dependency injection."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from fcp_cli.agents.research import ResearchAgent, ResearchResult
from fcp_cli.config import settings

pytestmark = pytest.mark.integration


class TestResearchAgentInit:
    """Test research agent initialization."""

    def test_init_with_defaults(self):
        """Test agent initialization with default values."""
        mock_agent = MagicMock()
        agent = ResearchAgent(agent=mock_agent)

        assert agent.fcp_url == settings.fcp_server_url
        assert agent.user_id == settings.fcp_user_id
        assert agent._agent == mock_agent

    def test_init_with_custom_values(self):
        """Test agent initialization with custom values."""
        mock_agent = MagicMock()
        agent = ResearchAgent(
            fcp_url="https://custom.url",
            user_id="custom_user",
            agent=mock_agent,
        )

        assert agent.fcp_url == "https://custom.url"
        assert agent.user_id == "custom_user"
        assert agent._agent == mock_agent

    def test_init_fcp_url_default_fallback(self):
        """Test that None fcp_url falls back to settings."""
        mock_agent = MagicMock()
        agent = ResearchAgent(fcp_url=None, agent=mock_agent)

        assert agent.fcp_url == settings.fcp_server_url

    def test_init_user_id_default_fallback(self):
        """Test that None user_id falls back to settings."""
        mock_agent = MagicMock()
        agent = ResearchAgent(user_id=None, agent=mock_agent)

        assert agent.user_id == settings.fcp_user_id


@pytest.mark.asyncio
class TestResearchAgentResearch:
    """Test research agent research method."""

    async def test_research_calls_agent_run(self):
        """Test that research calls agent.run with correct parameters."""
        mock_agent = MagicMock()
        mock_result = MagicMock()
        mock_result.output = ResearchResult(
            summary="Test summary",
            key_points=["Point 1", "Point 2"],
            sources_consulted=3,
            confidence="high",
        )
        mock_agent.run = AsyncMock(return_value=mock_result)

        agent = ResearchAgent(
            fcp_url="https://test.url",
            user_id="test_user",
            agent=mock_agent,
        )

        result = await agent.research("What is umami?")

        assert result.summary == "Test summary"
        assert result.key_points == ["Point 1", "Point 2"]
        assert result.sources_consulted == 3
        assert result.confidence == "high"

        # Verify agent.run was called
        mock_agent.run.assert_called_once()
        call_args = mock_agent.run.call_args
        assert call_args[0][0] == "What is umami?"
        assert "deps" in call_args[1]

    async def test_research_passes_dependencies(self):
        """Test that research passes correct dependencies to agent."""
        mock_agent = MagicMock()
        mock_result = MagicMock()
        mock_result.output = ResearchResult(
            summary="Test",
            key_points=[],
            sources_consulted=0,
            confidence="low",
        )
        mock_agent.run = AsyncMock(return_value=mock_result)

        agent = ResearchAgent(
            fcp_url="https://api.example.com",
            user_id="user123",
            agent=mock_agent,
        )

        await agent.research("Test question")

        # Check that deps were passed
        call_args = mock_agent.run.call_args
        deps = call_args[1]["deps"]
        assert deps.fcp_url == "https://api.example.com"
        assert deps.user_id == "user123"
        assert deps.http_client is not None

    async def test_research_returns_typed_result(self):
        """Test that research returns correctly typed ResearchResult."""
        mock_agent = MagicMock()
        expected_result = ResearchResult(
            summary="Detailed analysis",
            key_points=["Key finding 1", "Key finding 2", "Key finding 3"],
            sources_consulted=5,
            confidence="medium",
        )
        mock_result = MagicMock()
        mock_result.output = expected_result
        mock_agent.run = AsyncMock(return_value=mock_result)

        agent = ResearchAgent(agent=mock_agent)
        result = await agent.research("Complex query")

        assert isinstance(result, ResearchResult)
        assert result == expected_result
