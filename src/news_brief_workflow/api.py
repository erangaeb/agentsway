"""FastAPI application that exposes the Agentsway news-brief workflow."""

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.news_brief_workflow.workflow import generate_news_brief

app = FastAPI(
    title="Agentsway News Brief API",
    description="Research, edit, fact-check, and write a short news brief with agents.",
    version="1.0.0",
)


class NewsBriefRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)
    provider: Literal["openai", "gemini"] = "gemini"


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/news-briefs")
async def create_news_brief(request: NewsBriefRequest) -> dict:
    try:
        return await generate_news_brief(request.topic, request.provider)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
