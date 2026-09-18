"""Authenticated Streamable HTTP MCP server for the Agentsway news-brief API."""

import os
import secrets
import logging
from contextvars import ContextVar

import httpx

from mcp.server.mcpserver import MCPServer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import uvicorn

from src.news_brief_workflow.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

NEWS_BRIEF_API_URL = os.getenv("NEWS_BRIEF_API_URL", "http://127.0.0.1:8000/news-briefs")
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8001"))

mcp = MCPServer("Agentsway News Brief")
incoming_bearer_token: ContextVar[str | None] = ContextVar("incoming_bearer_token", default=None)


class AuthMiddleware(BaseHTTPMiddleware):
    """Require an exact bearer token for the MCP endpoint."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == "/healthz":
            return await call_next(request)
        if not MCP_AUTH_TOKEN:
            logger.error("news_brief.mcp.auth.token_not_configured")
            return JSONResponse({"error": "MCP_AUTH_TOKEN is not configured."}, status_code=503)

        authorization = request.headers.get("authorization", "")
        bearer_prefix = "Bearer "
        supplied_token = authorization[len(bearer_prefix) :].strip() if authorization.startswith(bearer_prefix) else ""
        if not secrets.compare_digest(supplied_token, MCP_AUTH_TOKEN):
            logger.warning("news_brief.mcp.auth.invalid_bearer_token path=%s", request.url.path)
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        token_context = incoming_bearer_token.set(supplied_token)
        try:
            return await call_next(request)
        finally:
            incoming_bearer_token.reset(token_context)


@mcp.custom_route("/healthz", methods=["GET"])
async def health_check(_: Request) -> Response:
    logger.debug("news_brief.mcp.health_check")
    return JSONResponse({"status": "ok"})


@mcp.tool()
async def create_news_brief(topic: str) -> dict:
    """Research recent news, filter it, fact-check it, and write a short spoken news script."""
    if not topic.strip():
        logger.warning("news_brief.mcp.invalid_topic")
        raise ValueError("topic cannot be empty.")
    bearer_token = incoming_bearer_token.get()
    if not bearer_token:
        logger.error("news_brief.mcp.missing_request_token")
        raise RuntimeError("A bearer token is required to call the News Brief API.")

    logger.info("news_brief.mcp.request.start topic_length=%d", len(topic.strip()))
    headers = {"Authorization": f"Bearer {bearer_token}"}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                NEWS_BRIEF_API_URL,
                headers=headers,
                json={"topic": topic.strip()},
            )
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError):
        logger.exception("news_brief.mcp.api_request_failed")
        raise RuntimeError("The News Brief API request failed.") from None

    logger.info("news_brief.mcp.request.complete source_count=%d", len(result.get("sources", [])))
    return result


if __name__ == "__main__":
    logger.info("news_brief.mcp.start host=%s port=%d", HOST, PORT)
    app = mcp.streamable_http_app(streamable_http_path="/mcp", host=HOST)
    app.add_middleware(AuthMiddleware)
    uvicorn.run(app, host=HOST, port=PORT)
