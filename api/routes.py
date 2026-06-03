"""FastAPI routes for the gallery API server."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.repository import ArtifactReadRepository


def create_router(artifact_repository: ArtifactReadRepository) -> APIRouter:
    router = APIRouter()

    @router.get("/artifacts")
    def list_artifacts(
        q: str | None = Query(default=None),
        type: str = Query(default="all"),
        player: str | None = Query(default=None),
    ) -> dict:
        artifacts = artifact_repository.list_artifacts(query=q, item_type=type, player=player)
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
        return {"types": artifact_repository.list_artifact_types()}

    return router
