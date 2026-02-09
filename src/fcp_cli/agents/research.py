"""Research agent for deep food research using Pydantic AI."""

from dataclasses import dataclass
from typing import Any, cast

import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from fcp_cli.config import settings

# Type alias for the research agent
ResearchAgentType = Agent[Any, Any]


class ResearchResult(BaseModel):
    """Structured research result."""

    summary: str = Field(description="Brief summary of findings")
    key_points: list[str] = Field(description="Key takeaways from the research")
    sources_consulted: int = Field(description="Number of sources analyzed", ge=0)
    confidence: str = Field(description="Confidence level: high, medium, or low")


@dataclass
class ResearchDependencies:
    """Dependencies for the research agent."""

    fcp_url: str
    user_id: str
    http_client: httpx.AsyncClient


def _create_research_agent() -> ResearchAgentType:
    """Create a new research agent instance with tools."""
    agent: ResearchAgentType = Agent(
        "google-gla:gemini-2.0-flash",
        deps_type=ResearchDependencies,
        output_type=ResearchResult,
        instructions="""You are a food research specialist. Your role is to:
1. Analyze food-related questions thoroughly
2. Use the deep_research tool to gather comprehensive information
3. Synthesize findings into clear, actionable insights
4. Focus on nutrition, health effects, and culinary applications

Always provide evidence-based responses with appropriate confidence levels.""",
    )

    @agent.tool
    async def deep_research(
        ctx: RunContext[ResearchDependencies],
        query: str,
    ) -> dict[str, Any]:
        """
        Conduct deep research on a food-related topic using the FCP server.

        Args:
            query: The research question or topic to investigate

        Returns:
            Research report with findings
        """
        response = await ctx.deps.http_client.post(
            f"{ctx.deps.fcp_url}/research",
            json={"query": query, "user_id": ctx.deps.user_id},
            timeout=300.0,  # Research can take several minutes
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    @agent.tool
    async def search_food_logs(
        ctx: RunContext[ResearchDependencies],
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search the user's food logs for relevant entries.

        Args:
            query: Natural language search query
            limit: Maximum number of results to return

        Returns:
            List of matching food log entries
        """
        response = await ctx.deps.http_client.post(
            f"{ctx.deps.fcp_url}/search",
            json={"query": query, "user_id": ctx.deps.user_id, "limit": limit},
            timeout=30.0,
        )
        response.raise_for_status()
        return cast(list[dict[str, Any]], response.json().get("results", []))

    return agent


class ResearchAgent:
    """High-level interface for the research agent."""

    def __init__(
        self,
        fcp_url: str | None = None,
        user_id: str | None = None,
        agent: ResearchAgentType | None = None,
    ):
        self.fcp_url = fcp_url or settings.fcp_server_url
        self.user_id = user_id or settings.fcp_user_id
        self._agent = agent or _create_research_agent()

    async def research(self, question: str) -> ResearchResult:
        """
        Conduct research on a food-related question.

        Args:
            question: The research question

        Returns:
            Structured research result
        """
        async with httpx.AsyncClient() as client:
            deps = ResearchDependencies(
                fcp_url=self.fcp_url,
                user_id=self.user_id,
                http_client=client,
            )
            result = await self._agent.run(question, deps=deps)
            return cast(ResearchResult, result.output)
