"""FastAPI routes for crawl operations dashboard status."""

from __future__ import annotations

from fastapi import APIRouter

from admin_api.repository import CrawlStatusRepository


def create_router(status_repository: CrawlStatusRepository) -> APIRouter:
    router = APIRouter(prefix="/admin")

    @router.get("/crawl-status")
    def get_crawl_status() -> dict:
        return status_repository.get_crawl_status().model_dump()

    return router
