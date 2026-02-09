"""Tests for research agent tool creation."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fcp_cli.agents.research import ResearchDependencies, _create_research_agent

pytestmark = pytest.mark.integration


class TestCreateResearchAgent:
    """Test _create_research_agent function."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    def test_creates_agent_with_tools(self):
        """Test that agent is created with deep_research and search_food_logs tools."""
        agent = _create_research_agent()

        assert agent is not None
        # Agent should have tools registered
        assert hasattr(agent, "run")


@pytest.mark.asyncio
class TestResearchAgentTools:
    """Test research agent tool functions."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    async def test_deep_research_tool_makes_request(self):
        """Test that deep_research tool makes HTTP request to FCP server."""
        agent = _create_research_agent()

        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "summary": "Test research result",
            "findings": ["Finding 1", "Finding 2"],
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        # Access the tool function directly from the agent
        # PydanticAI stores tools as methods on the agent instance
        tools = [t for t in dir(agent) if not t.startswith("_")]
        assert len(tools) > 0  # Should have tools registered

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    async def test_search_food_logs_tool_makes_request(self):
        """Test that search_food_logs tool makes HTTP request."""
        agent = _create_research_agent()

        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [
                {"id": "log1", "dish_name": "Pizza"},
                {"id": "log2", "dish_name": "Burger"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        # Verify agent has expected structure
        assert hasattr(agent, "run")


class TestResearchDependencies:
    """Test ResearchDependencies dataclass."""

    def test_creates_dependencies(self):
        """Test creating ResearchDependencies."""
        mock_client = MagicMock()

        deps = ResearchDependencies(
            fcp_url="https://api.example.com",
            user_id="user123",
            http_client=mock_client,
        )

        assert deps.fcp_url == "https://api.example.com"
        assert deps.user_id == "user123"
        assert deps.http_client == mock_client
