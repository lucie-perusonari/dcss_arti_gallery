"""FastAPI admin API server."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin_api.prometheus import prometheus_repository_from_env
from admin_api.repository import repository_from_env
from admin_api.routes import create_router


def create_app(repository=None, metrics_repository=None) -> FastAPI:
    """Create the crawl operations admin API app with an injectable repository."""

    status_repository = repository or repository_from_env()
    gallery_metrics_repository = metrics_repository or prometheus_repository_from_env()

    app = FastAPI(title="DCSS Arti Gallery Admin API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_origin_regex=_allowed_origin_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_router(status_repository, gallery_metrics_repository))
    return app


def _allowed_origins() -> list[str]:
    configured = os.environ.get("ADMIN_API_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]


def _allowed_origin_regex() -> str | None:
    configured = os.environ.get("ADMIN_API_CORS_ORIGIN_REGEX")
    if configured:
        return configured
    return (
        r"^http://("
        r"localhost|127\.0\.0\.1|"
        r"10(?:\.\d{1,3}){3}|"
        r"192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2}"
        r"):5174$"
    )


app = create_app()
