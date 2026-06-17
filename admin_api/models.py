"""API-owned models for crawl operations dashboard status."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RawFileStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int
    fetched: int
    fetchFailed: int
    processPending: int
    processProcessed: int
    processFailed: int


class LatestActivity(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fetchedAt: str | None = None
    processedAt: str | None = None


class CrawlError(BaseModel):
    model_config = ConfigDict(extra="ignore")

    kind: str
    player: str
    name: str | None = None
    message: str
    at: str | None = None


class CrawlStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    artifactCount: int
    crawlActive: bool = False
    rawFiles: RawFileStatus
    latest: LatestActivity
    recentErrors: list[CrawlError]


class GalleryApiMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
    windowSeconds: int
    requestRatePerSecond: float | None = None
    errorRatePerSecond: float | None = None
    p95LatencySeconds: float | None = None
    inFlightRequests: float | None = None
    error: str | None = None
