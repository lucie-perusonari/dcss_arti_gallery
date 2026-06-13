"""Read-only Prometheus client for admin dashboard metrics."""

from __future__ import annotations

import os
from typing import Any, Protocol

import httpx

from admin_api.models import GalleryApiMetrics


DEFAULT_PROMETHEUS_URL = "http://localhost:9090"
DEFAULT_PROMETHEUS_TIMEOUT_SECONDS = 3.0
DEFAULT_METRICS_WINDOW_SECONDS = 300


class GalleryApiMetricsRepository(Protocol):
    def get_gallery_api_metrics(self) -> GalleryApiMetrics:
        ...


class PrometheusGalleryApiMetricsRepository:
    """Queries Prometheus for Gallery API metrics used by admin frontend."""

    def __init__(
        self,
        prometheus_url: str = DEFAULT_PROMETHEUS_URL,
        timeout_seconds: float = DEFAULT_PROMETHEUS_TIMEOUT_SECONDS,
        window_seconds: int = DEFAULT_METRICS_WINDOW_SECONDS,
    ) -> None:
        self.prometheus_url = prometheus_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.window_seconds = window_seconds

    def get_gallery_api_metrics(self) -> GalleryApiMetrics:
        try:
            request_rate = self._query_number(
                f"sum(rate(dcss_gallery_api_http_requests_total[{self.window_seconds}s]))"
            )
            error_rate = self._query_number(
                f'sum(rate(dcss_gallery_api_http_requests_total{{status=~"5.."}}[{self.window_seconds}s]))'
            )
            p95_latency = self._query_number(
                "histogram_quantile(0.95, "
                f"sum(rate(dcss_gallery_api_http_request_duration_seconds_bucket[{self.window_seconds}s])) "
                "by (le))"
            )
            in_flight = self._query_number("sum(dcss_gallery_api_http_requests_in_progress)")
        except Exception as exc:
            return GalleryApiMetrics(
                status="unavailable",
                windowSeconds=self.window_seconds,
                error=str(exc),
            )

        return GalleryApiMetrics(
            status="ok",
            windowSeconds=self.window_seconds,
            requestRatePerSecond=request_rate,
            errorRatePerSecond=error_rate,
            p95LatencySeconds=p95_latency,
            inFlightRequests=in_flight,
        )

    def _query_number(self, query: str) -> float | None:
        response = httpx.get(
            f"{self.prometheus_url}/api/v1/query",
            params={"query": query},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "success":
            raise RuntimeError(f"Prometheus query failed: {payload!r}")
        return _prometheus_number(payload.get("data", {}))


def prometheus_repository_from_env() -> PrometheusGalleryApiMetricsRepository:
    return PrometheusGalleryApiMetricsRepository(
        prometheus_url=os.environ.get("PROMETHEUS_URL", DEFAULT_PROMETHEUS_URL),
        timeout_seconds=_env_float("PROMETHEUS_TIMEOUT_SECONDS", DEFAULT_PROMETHEUS_TIMEOUT_SECONDS),
        window_seconds=_env_int("PROMETHEUS_METRICS_WINDOW_SECONDS", DEFAULT_METRICS_WINDOW_SECONDS),
    )


def _prometheus_number(data: dict[str, Any]) -> float | None:
    result = data.get("result")
    if not isinstance(result, list) or not result:
        return None
    value = result[0].get("value")
    if not isinstance(value, list) or len(value) < 2:
        return None
    try:
        return float(value[1])
    except (TypeError, ValueError):
        return None


def _env_float(name: str, default: float) -> float:
    configured = os.environ.get(name)
    return default if configured is None else float(configured)


def _env_int(name: str, default: int) -> int:
    configured = os.environ.get(name)
    return default if configured is None else int(configured)
