# API Processing Layers

This document defines the layers and project boundary for the Gallery/admin read API.

## Project Boundary

- Module: `api/`
- Role: read MongoDB `artifacts` and expose the HTTP API used by the frontend gallery; read crawl-status collections
  and expose a read-only API for the admin dashboard
- Restriction: `api` does not import `crawl_service`. It owns the API-specific repository and Pydantic response models.

## Internal Layers

- `api.app`: FastAPI app factory, CORS setup, and gallery/admin router wiring
- `api.repository`: MongoDB artifact read repository, search/filter/sort
- `api.admin_repository`: MongoDB crawl-status read repository
- `api.models`: frontend-facing artifact response DTOs
- `api.admin_models`: admin-facing crawl status response DTOs
- `api.routes`: `/artifacts`, `/artifacts/{artifact_id}`, `/artifact-types`, `/filters`
- `api.admin_routes`: `/admin/crawl-status`

## Data Flow

```text
MongoDB artifacts / crawl status collections
  -> api repository
  -> api-owned Pydantic DTO
  -> FastAPI response
  -> frontend / admin-frontend
```

## Related Docs

- [API Data Types](./data-types.md)
- [Frontend Data Types](../../../frontend/docs/en/data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/en/data-types.md)
