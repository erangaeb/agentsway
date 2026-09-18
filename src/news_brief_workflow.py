"""Reusable multi-agent news-brief workflow for the API and MCP server."""

import asyncio
import os
from typing import Any

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from ddgs import DDGS
from openai import AsyncOpenAI

OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-5-mini")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def _create_model(provider: str) -> str | OpenAIChatCompletionsModel:
    """Create the selected model without exposing API keys in workflow output."""
    provider = provider.lower()

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Set OPENAI_API_KEY before using the OpenAI provider.")
        return OPENAI_MODEL_NAME

    if provider == "gemini":
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Set GEMINI_API_KEY before using the Gemini provider.")
        set_tracing_disabled(disabled=True)
        return OpenAIChatCompletionsModel(
            model=GEMINI_MODEL_NAME,
            openai_client=AsyncOpenAI(
                base_url=GEMINI_BASE_URL,
                api_key=gemini_api_key,
            ),
        )

    raise ValueError("provider must be 'openai' or 'gemini'.")


def _search_recent_news(topic: str) -> list[dict[str, str]]:
    """Find recent public news and retain the fields used by the agents."""
    results = DDGS(timeout=15).news(topic, timelimit="d", max_results=10)
    if not results:
        raise RuntimeError("No recent news results were found. Try a different topic.")

    return [
        {
            "title": item.get("title", "Untitled"),
            "date": item.get("date", "Unknown"),
            "summary": item.get("body", "No summary available."),
            "url": item.get("url", ""),
            "source": item.get("source", "Unknown source"),
        }
        for item in results
    ]


def _format_news_items(news_items: list[dict[str, str]]) -> str:
    return "\n\n".join(
        f"Title: {item['title']}\nDate: {item['date']}\nSource: {item['source']}\n"
        f"Summary: {item['summary']}\nURL: {item['url']}"
        for item in news_items
    )


async def generate_news_brief(topic: str, provider: str = "gemini") -> dict[str, Any]:
    """Research, edit, fact-check, and write a source-grounded news brief."""
    clean_topic = topic.strip()
    if not clean_topic:
        raise ValueError("topic cannot be empty.")

    model = _create_model(provider)
    sources = await asyncio.to_thread(_search_recent_news, clean_topic)
    source_text = _format_news_items(sources)

    editor_agent = Agent(
        name="News Editor",
        instructions=(
            "Select up to three relevant, credible, non-duplicative items. Exclude ads, clickbait, "
            "speculation, and weak evidence. Preserve each selected item's key facts, date, source, and URL."
        ),
        model=model,
    )
    fact_checker_agent = Agent(
        name="Fact Consistency Checker",
        instructions=(
            "Compare the edited news with the supplied source items. Remove or correct unsupported claims. "
            "Do not add facts. Return a concise, source-grounded brief for the script writer."
        ),
        model=model,
    )
    writer_agent = Agent(
        name="News Script Writer",
        instructions=(
            "Write a neutral 45- to 60-second spoken news script using only the supplied brief. "
            "Do not add unsupported facts. End by naming the source publications without reading URLs aloud."
        ),
        model=model,
    )

    editor_result = await Runner.run(
        editor_agent,
        f"Topic: {clean_topic}\n\nNews items:\n{source_text}",
    )
    edited_brief = editor_result.final_output
    fact_check_result = await Runner.run(
        fact_checker_agent,
        f"Source items:\n{source_text}\n\nEdited news:\n{edited_brief}",
    )
    fact_checked_brief = fact_check_result.final_output
    writer_result = await Runner.run(writer_agent, fact_checked_brief)

    return {
        "topic": clean_topic,
        "provider": provider.lower(),
        "sources": sources,
        "edited_brief": edited_brief,
        "fact_checked_brief": fact_checked_brief,
        "news_script": writer_result.final_output,
    }
