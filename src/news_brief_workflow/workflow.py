"""Reusable multi-agent news-brief workflow for the API and MCP server."""

import asyncio
import base64
import logging
import os
import wave
from pathlib import Path
from typing import Any
from uuid import uuid4

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from ddgs import DDGS
from google import genai
from openai import AsyncOpenAI

from src.news_brief_workflow.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-5-mini")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OPENAI_TTS_MODEL_NAME = os.getenv("OPENAI_TTS_MODEL_NAME", "gpt-4o-mini-tts")
GEMINI_TTS_MODEL_NAME = os.getenv("GEMINI_TTS_MODEL_NAME", "gemini-3.1-flash-tts-preview")
NEWS_BRIEF_OUTPUT_DIR = Path(os.getenv("NEWS_BRIEF_OUTPUT_DIR", "generated/news_briefs"))


def _create_model(provider: str) -> str | OpenAIChatCompletionsModel:
    """Create the selected model without exposing API keys in workflow output."""
    provider = provider.lower()
    logger.info("news_brief.model.create provider=%s", provider)

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("news_brief.model.missing_api_key provider=openai")
            raise ValueError("Set OPENAI_API_KEY before using the OpenAI provider.")
        return OPENAI_MODEL_NAME

    if provider == "gemini":
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("news_brief.model.missing_api_key provider=gemini")
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
    logger.info("news_brief.search.start topic_length=%d", len(topic))
    results = DDGS(timeout=15).news(topic, timelimit="d", max_results=10)
    if not results:
        logger.warning("news_brief.search.empty_results topic_length=%d", len(topic))
        raise RuntimeError("No recent news results were found. Try a different topic.")

    logger.info("news_brief.search.complete result_count=%d", len(results))

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


def _save_wav(filename: Path, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> None:
    with wave.open(str(filename), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(rate)
        wav_file.writeframes(pcm)


async def _generate_openai_audio(news_script: str, output_path: Path) -> None:
    logger.info("news_brief.tts.start provider=openai")
    tts_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    speech = await tts_client.audio.speech.create(
        model=OPENAI_TTS_MODEL_NAME,
        voice="coral",
        input=news_script,
        instructions="Speak clearly in a calm, neutral broadcast-news style.",
    )
    speech.write_to_file(output_path)
    logger.info("news_brief.tts.complete provider=openai format=mp3")


def _generate_gemini_audio(news_script: str, output_path: Path) -> None:
    logger.info("news_brief.tts.start provider=gemini")
    gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = gemini_client.interactions.create(
        model=GEMINI_TTS_MODEL_NAME,
        input="Read this in a calm, neutral broadcast-news style:\n\n" + news_script,
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": "Kore"}]},
    )
    _save_wav(output_path, base64.b64decode(response.output_audio.data))
    logger.info("news_brief.tts.complete provider=gemini format=wav")


async def _generate_audio_brief(news_script: str, provider: str, job_id: str) -> tuple[Path, str]:
    NEWS_BRIEF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_job_id = Path(job_id).name
    if provider == "openai":
        output_path = NEWS_BRIEF_OUTPUT_DIR / f"news_brief_{safe_job_id}.mp3"
        await _generate_openai_audio(news_script, output_path)
        return output_path, "audio/mpeg"

    output_path = NEWS_BRIEF_OUTPUT_DIR / f"news_brief_{safe_job_id}.wav"
    await asyncio.to_thread(_generate_gemini_audio, news_script, output_path)
    return output_path, "audio/wav"


async def generate_news_brief(
    topic: str,
    provider: str = "gemini",
    job_id: str | None = None,
) -> dict[str, Any]:
    """Research, edit, fact-check, write, and voice a source-grounded news brief."""
    clean_topic = topic.strip()
    if not clean_topic:
        logger.warning("news_brief.workflow.invalid_topic")
        raise ValueError("topic cannot be empty.")

    logger.info(
        "news_brief.workflow.start provider=%s topic_length=%d",
        provider.lower(),
        len(clean_topic),
    )
    try:
        model = _create_model(provider)
        sources = await asyncio.to_thread(_search_recent_news, clean_topic)
    except Exception:
        logger.exception("news_brief.workflow.setup_failed provider=%s", provider.lower())
        raise
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

    try:
        logger.info("news_brief.editor.start source_count=%d", len(sources))
        editor_result = await Runner.run(
            editor_agent,
            f"Topic: {clean_topic}\n\nNews items:\n{source_text}",
        )
        edited_brief = editor_result.final_output
        logger.info("news_brief.editor.complete output_length=%d", len(edited_brief))

        logger.info("news_brief.fact_check.start")
        fact_check_result = await Runner.run(
            fact_checker_agent,
            f"Source items:\n{source_text}\n\nEdited news:\n{edited_brief}",
        )
        fact_checked_brief = fact_check_result.final_output
        logger.info("news_brief.fact_check.complete output_length=%d", len(fact_checked_brief))

        logger.info("news_brief.writer.start")
        writer_result = await Runner.run(writer_agent, fact_checked_brief)
        news_script = writer_result.final_output
        audio_path, audio_media_type = await _generate_audio_brief(
            news_script,
            provider.lower(),
            job_id or uuid4().hex,
        )
    except Exception:
        logger.exception("news_brief.workflow.failed provider=%s", provider.lower())
        raise

    logger.info("news_brief.workflow.complete source_count=%d", len(sources))

    return {
        "topic": clean_topic,
        "provider": provider.lower(),
        "sources": sources,
        "edited_brief": edited_brief,
        "fact_checked_brief": fact_checked_brief,
        "news_script": news_script,
        "audio_path": str(audio_path),
        "audio_media_type": audio_media_type,
    }
