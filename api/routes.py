"""FastAPI routes for the gallery API server."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.repository import (
    DEFAULT_ARTIFACT_LIMIT,
    DEFAULT_RECENT_DAYS,
    MAX_ARTIFACT_LIMIT,
    ArtifactReadRepository,
)


def create_router(artifact_repository: ArtifactReadRepository) -> APIRouter:
    router = APIRouter()

    @router.get("/artifacts")
    def list_artifacts(
        q: str | None = Query(default=None),
        type: str = Query(default="all"),
        displayCategory: str | None = Query(default=None),
        player: str | None = Query(default=None),
        since: str = Query(default=f"{DEFAULT_RECENT_DAYS}d"),
        limit: int = Query(default=DEFAULT_ARTIFACT_LIMIT, ge=1, le=MAX_ARTIFACT_LIMIT),
        offset: int = Query(default=0, ge=0),
    ) -> dict:
        list_kwargs = {
            "query": q,
            "item_type": type,
            "player": player,
            "since_days": _since_days(since),
            "limit": limit,
            "offset": offset,
        }
        if displayCategory is not None:
            list_kwargs["display_category"] = displayCategory
        artifacts = artifact_repository.list_artifacts(**list_kwargs)
        return {"artifacts": [artifact.model_dump() for artifact in artifacts]}

    @router.get("/artifacts/{artifact_id}")
    def get_artifact(artifact_id: str) -> dict:
        artifact = artifact_repository.get_artifact(artifact_id)
        if artifact is None:
            raise HTTPException(status_code=404, detail="artifact not found")
        return artifact.model_dump()

    @router.get("/artifact-types")
    def list_artifact_types() -> list[str]:
        return artifact_repository.list_artifact_types()

    @router.get("/filters")
    def get_filters() -> dict:
        list_categories = getattr(artifact_repository, "list_display_categories", None)
        return {
            "types": artifact_repository.list_artifact_types(),
            "displayCategories": list_categories() if list_categories else {},
        }

    return router


def _since_days(value: str) -> int | None:
    normalized = value.strip().lower()
    if normalized in {"all", "none", "0"}:
        return None
    if normalized.endswith("d"):
        normalized = normalized[:-1]
    try:
        days = int(normalized)
    except ValueError:
        return DEFAULT_RECENT_DAYS
    return max(days, 0)
