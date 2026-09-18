"""MCP server that exposes the Agentsway news-brief workflow as one tool."""

from typing import Literal

from mcp.server.mcpserver import MCPServer

from src.news_brief_workflow import generate_news_brief

mcp = MCPServer("Agentsway News Brief")


@mcp.tool()
async def create_news_brief(
    topic: str,
    provider: Literal["openai", "gemini"] = "gemini",
) -> dict:
    """Research recent news, filter it, fact-check it, and write a short spoken news script."""
    return await generate_news_brief(topic, provider)


if __name__ == "__main__":
    mcp.run(transport="stdio")
