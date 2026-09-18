"""Authenticated FastAPI application that runs the Agentsway news-brief workflow."""

import os
import secrets
import logging
from typing import Any
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from src.news_brief_workflow.workflow import generate_news_brief
from src.news_brief_workflow.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentsway News Brief API",
    description="Research, edit, fact-check, and write a short news brief with agents.",
    version="1.0.0",
)
jobs: dict[str, dict[str, Any]] = {}


class NewsBriefRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)


def _require_api_token(authorization: str | None = Header(default=None)) -> None:
    expected_token = os.getenv("NEWS_BRIEF_API_TOKEN")
    if not expected_token:
        logger.error("news_brief.api.auth.token_not_configured")
        raise HTTPException(status_code=503, detail="NEWS_BRIEF_API_TOKEN is not configured.")

    bearer_prefix = "Bearer "
    if not authorization or not authorization.startswith(bearer_prefix):
        logger.warning("news_brief.api.auth.missing_bearer_token")
        raise HTTPException(status_code=401, detail="Bearer token required.")

    supplied_token = authorization[len(bearer_prefix) :].strip()
    if not secrets.compare_digest(supplied_token, expected_token):
        logger.warning("news_brief.api.auth.invalid_bearer_token")
        raise HTTPException(status_code=401, detail="Invalid bearer token.")


def _configured_provider() -> str:
    provider = os.getenv("NEWS_BRIEF_PROVIDER", "gemini").lower()
    if provider not in {"openai", "gemini"}:
        logger.error("news_brief.api.invalid_provider_configuration provider=%s", provider)
        raise HTTPException(
            status_code=503,
            detail="NEWS_BRIEF_PROVIDER must be 'openai' or 'gemini'.",
        )
    return provider


@app.get("/health")
async def health_check() -> dict[str, str]:
    logger.debug("news_brief.api.health_check")
    return {"status": "ok"}


async def _run_news_brief_job(job_id: str, topic: str, provider: str) -> None:
    jobs[job_id]["status"] = "running"
    logger.info("news_brief.api.job.start job_id=%s provider=%s", job_id, provider)
    try:
        result = await generate_news_brief(topic, provider, job_id)
    except Exception:
        jobs[job_id].update(
            status="failed",
            error="News Brief workflow failed. Check the API logs for details.",
        )
        logger.exception("news_brief.api.job.failed job_id=%s", job_id)
        return

    audio_path = result.pop("audio_path")
    audio_media_type = result.pop("audio_media_type")
    jobs[job_id].update(
        status="completed",
        result=result,
        audio_path=audio_path,
        audio_media_type=audio_media_type,
    )
    logger.info(
        "news_brief.api.job.complete job_id=%s source_count=%d",
        job_id,
        len(result["sources"]),
    )


@app.post("/news-briefs")
async def create_news_brief(
    request: NewsBriefRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(_require_api_token),
) -> JSONResponse:
    job_id = uuid4().hex
    logger.info(
        "news_brief.api.job.queued job_id=%s provider=%s topic_length=%d",
        job_id,
        _configured_provider(),
        len(request.topic.strip()),
    )
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "topic": request.topic.strip(),
    }
    background_tasks.add_task(
        _run_news_brief_job,
        job_id,
        request.topic.strip(),
        _configured_provider(),
    )
    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "queued",
            "status_url": f"/news-briefs/{job_id}",
        },
    )


@app.get("/news-briefs/{job_id}")
async def get_news_brief_status(
    job_id: str,
    _: None = Depends(_require_api_token),
) -> dict[str, Any]:
    job = jobs.get(job_id)
    if not job:
        logger.warning("news_brief.api.job.not_found job_id=%s", job_id)
        raise HTTPException(status_code=404, detail="News Brief job not found.")
    response = {key: value for key, value in job.items() if key not in {"audio_path", "audio_media_type"}}
    if job["status"] == "completed":
        response["audio_url"] = f"/news-briefs/{job_id}/audio"
    logger.info("news_brief.api.job.status job_id=%s status=%s", job_id, job["status"])
    return response


@app.get("/news-briefs/{job_id}/audio")
async def download_news_brief_audio(
    job_id: str,
    _: None = Depends(_require_api_token),
) -> FileResponse:
    job = jobs.get(job_id)
    if not job:
        logger.warning("news_brief.api.audio.job_not_found job_id=%s", job_id)
        raise HTTPException(status_code=404, detail="News Brief job not found.")
    if job["status"] != "completed" or "audio_path" not in job:
        raise HTTPException(status_code=409, detail="News Brief audio is not ready.")

    audio_path = job["audio_path"]
    if not os.path.exists(audio_path):
        logger.error("news_brief.api.audio.file_missing job_id=%s", job_id)
        raise HTTPException(status_code=404, detail="News Brief audio file is unavailable.")

    logger.info("news_brief.api.audio.download job_id=%s", job_id)
    return FileResponse(
        audio_path,
        media_type=job["audio_media_type"],
        filename=os.path.basename(audio_path),
    )
