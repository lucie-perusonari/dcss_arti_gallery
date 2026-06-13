# Admin API Processing Layers

This document defines the layers and project boundary for the admin dashboard read API.

## Project Boundary

- Module: `admin_api/`
- Role: read MongoDB crawl-status collections and expose the HTTP API used by the admin dashboard.
- Restriction: `admin_api` does not import `crawl_service`. It owns the admin API-specific repository and Pydantic response models.

## Internal Layers

- `admin_api.app`: admin FastAPI app factory, CORS setup, and admin router wiring
- `admin_api.repository`: MongoDB crawl-status read repository
- `admin_api.models`: admin-facing crawl status response DTOs
- `admin_api.routes`: `/admin/crawl-status`

## Data Flow

```text
MongoDB artifacts / crawl status collections
  -> admin_api repository
  -> admin_api-owned Pydantic DTO
  -> FastAPI response
  -> admin-frontend
```

## Related Docs

- [Admin API Data Types](./data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/en/data-types.md)
