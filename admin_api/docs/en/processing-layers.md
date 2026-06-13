# Admin API Processing Layers

This document defines the layers and project boundary for the admin dashboard read API.

## Project Boundary

- Module: `admin_api/`
- Role: read MongoDB crawl-status/artifact-processing-status collections and Gallery API metrics from Prometheus, then expose the HTTP API used by the admin dashboard.
- Restriction: `admin_api` does not import `crawl_service`. It owns the admin API-specific repository and Pydantic response models.

## Internal Layers

- `admin_api.app`: admin FastAPI app factory, CORS setup, and admin router wiring
- `admin_api.repository`: MongoDB crawl-status and artifact-processing-status read repository
- `admin_api.prometheus`: read-only Prometheus HTTP API client for Gallery API metrics
- `admin_api.models`: admin-facing crawl status and Gallery API metrics response DTOs
- `admin_api.routes`: `/admin/crawl-status`, `/admin/metrics/gallery-api`

## Data Flow

```text
MongoDB artifacts / crawl status / artifact_processing_files collections
  -> admin_api repository
  -> admin_api-owned Pydantic DTO
  -> FastAPI response
  -> admin-frontend

Prometheus Gallery API metrics
  -> admin_api prometheus repository
  -> admin_api-owned Pydantic DTO
  -> FastAPI response
  -> admin-frontend
```

## Related Docs

- [Admin API Data Types](./data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/en/data-types.md)
