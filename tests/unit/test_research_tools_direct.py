"""Direct tests for research agent tool implementations."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fcp_cli.agents.research import ResearchDependencies, _create_research_agent

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
class TestResearchToolsDirect:
    """Test research agent tools by calling them directly."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    async def test_deep_research_tool_execution(self):
        """Test deep_research tool makes correct HTTP request."""
        agent = _create_research_agent()

        # Create mock dependencies
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={"summary": "Test result", "findings": ["Finding 1"]})
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        deps = ResearchDependencies(
            fcp_url="https://test.api",
            user_id="test_user",
            http_client=mock_client,
        )

        # Access the tool directly from the agent's tools
        # PydanticAI stores tools in a registry
        tools = agent._function_toolset.tools
        deep_research_tool = None
        for tool in tools.values():
            if tool.name == "deep_research":
                deep_research_tool = tool
                break

        assert deep_research_tool is not None, "deep_research tool not found"

        # Create a mock context
        mock_ctx = MagicMock()
        mock_ctx.deps = deps

        # Call the tool function directly
        result = await deep_research_tool.function(mock_ctx, query="test query")

        # Verify HTTP request was made correctly
        mock_client.post.assert_called_once_with(
            "https://test.api/research",
            json={"query": "test query", "user_id": "test_user"},
            timeout=300.0,
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == {"summary": "Test result", "findings": ["Finding 1"]}

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    async def test_search_food_logs_tool_execution(self):
        """Test search_food_logs tool makes correct HTTP request."""
        agent = _create_research_agent()

        # Create mock dependencies
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json = MagicMock(
            return_value={
                "results": [
                    {"id": "log1", "dish_name": "Pizza"},
                    {"id": "log2", "dish_name": "Salad"},
                ]
            }
        )
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        deps = ResearchDependencies(
            fcp_url="https://test.api",
            user_id="test_user",
            http_client=mock_client,
        )

        # Access the tool directly
        tools = agent._function_toolset.tools
        search_tool = None
        for tool in tools.values():
            if tool.name == "search_food_logs":
                search_tool = tool
                break

        assert search_tool is not None, "search_food_logs tool not found"

        # Create a mock context
        mock_ctx = MagicMock()
        mock_ctx.deps = deps

        # Call the tool function directly
        result = await search_tool.function(mock_ctx, query="pizza", limit=5)

        # Verify HTTP request was made correctly
        mock_client.post.assert_called_once_with(
            "https://test.api/search",
            json={"query": "pizza", "user_id": "test_user", "limit": 5},
            timeout=30.0,
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == [
            {"id": "log1", "dish_name": "Pizza"},
            {"id": "log2", "dish_name": "Salad"},
        ]

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    async def test_search_food_logs_default_limit(self):
        """Test search_food_logs uses default limit when not specified."""
        agent = _create_research_agent()

        # Create mock dependencies
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={"results": []})
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        deps = ResearchDependencies(
            fcp_url="https://test.api",
            user_id="test_user",
            http_client=mock_client,
        )

        # Access the tool directly
        tools = agent._function_toolset.tools
        search_tool = None
        for tool in tools.values():
            if tool.name == "search_food_logs":
                search_tool = tool
                break

        # Create a mock context
        mock_ctx = MagicMock()
        mock_ctx.deps = deps

        # Call without specifying limit (should use default of 10)
        _ = await search_tool.function(mock_ctx, query="test")

        # Verify default limit is used
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["limit"] == 10
