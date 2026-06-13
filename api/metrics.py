"""Prometheus metrics for the gallery API."""

from __future__ import annotations

import os
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client import generate_latest
from starlette.responses import Response


METRICS_PATH = "/metrics"


class GalleryApiMetrics:
    """Owns the per-app Prometheus registry and HTTP instrumentation."""

    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.requests_total = Counter(
            "dcss_gallery_api_http_requests_total",
            "Total Gallery API HTTP requests.",
            ("method", "route", "status"),
            registry=self.registry,
        )
        self.request_duration_seconds = Histogram(
            "dcss_gallery_api_http_request_duration_seconds",
            "Gallery API HTTP request duration in seconds.",
            ("method", "route"),
            registry=self.registry,
        )
        self.requests_in_progress = Gauge(
            "dcss_gallery_api_http_requests_in_progress",
            "Gallery API HTTP requests currently in progress.",
            ("method",),
            registry=self.registry,
        )
        self.service_info = Gauge(
            "dcss_gallery_api_service_info",
            "Gallery API service metadata.",
            ("service",),
            registry=self.registry,
        )
        self.service_info.labels(service="api").set(1)

    async def instrument_request(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path == METRICS_PATH:
            return await call_next(request)

        method = request.method
        status = "500"
        route = "unmatched"
        started_at = time.perf_counter()
        self.requests_in_progress.labels(method=method).inc()
        try:
            response = await call_next(request)
            status = str(response.status_code)
            route = self._route_label(request)
            return response
        finally:
            duration = time.perf_counter() - started_at
            self.requests_in_progress.labels(method=method).dec()
            self.requests_total.labels(method=method, route=route, status=status).inc()
            self.request_duration_seconds.labels(method=method, route=route).observe(duration)

    def render(self) -> Response:
        return Response(generate_latest(self.registry), media_type=CONTENT_TYPE_LATEST)

    def _route_label(self, request: Request) -> str:
        route = request.scope.get("route")
        path = getattr(route, "path", None)
        if isinstance(path, str) and path:
            return path
        return "unmatched"


def install_api_metrics(app: FastAPI) -> GalleryApiMetrics | None:
    """Install Prometheus instrumentation when enabled by environment."""

    if not _env_bool("ARTIFACT_API_METRICS_ENABLED", default=True):
        return None

    metrics = GalleryApiMetrics()
    app.state.metrics = metrics

    @app.middleware("http")
    async def _metrics_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        return await metrics.instrument_request(request, call_next)

    @app.get(METRICS_PATH, include_in_schema=False)
    def _metrics() -> Response:
        return metrics.render()

    return metrics


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}
