"""FastAPI gallery API server."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.admin_repository import repository_from_env as admin_repository_from_env
from api.admin_routes import create_admin_router
from api.repository import repository_from_env
from api.routes import create_router


def create_app(
    repository=None,
    admin_repository=None,
) -> FastAPI:
    """Create the gallery API app with an injectable repository."""

    artifact_repository = repository or repository_from_env()
    crawl_status_repository = admin_repository or admin_repository_from_env()

    app = FastAPI(title="DCSS Best Artifact Gallery API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_origin_regex=_allowed_origin_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_router(artifact_repository))
    app.include_router(create_admin_router(crawl_status_repository))
    return app


def _allowed_origins() -> list[str]:
    configured = os.environ.get("ARTIFACT_API_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def _allowed_origin_regex() -> str | None:
    configured = os.environ.get("ARTIFACT_API_CORS_ORIGIN_REGEX")
    if configured:
        return configured
    return (
        r"^http://("
        r"localhost|127\.0\.0\.1|"
        r"10(?:\.\d{1,3}){3}|"
        r"192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2}"
        r"):5173$"
    )


app = create_app()
