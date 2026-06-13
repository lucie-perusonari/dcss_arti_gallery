# API Processing Layers

This document defines the layers and project boundary for the Gallery read API.

## Project Boundary

- Module: `api/`
- Role: read MongoDB `artifacts` and expose the HTTP API used by the frontend gallery.
- Restriction: `api` does not import `crawl_service`. It owns the API-specific repository and Pydantic response models.
- Restriction: DDL such as collection index creation is not performed by the `api` runtime; it belongs in `infra/`.

## Internal Layers

- `api.app`: gallery FastAPI app factory, CORS setup, and gallery router wiring
- `api.repository`: MongoDB artifact read repository, search/filter/sort
- `api.models`: frontend-facing artifact response DTOs
- `api.routes`: `/artifacts`, `/artifacts/{artifact_id}`, `/artifact-types`, `/filters`

## Data Flow

```text
MongoDB artifacts collection
  -> api repository
  -> api-owned Pydantic DTO
  -> FastAPI response
  -> frontend
```

## Related Docs

- [API Data Types](./data-types.md)
- [Frontend Data Types](../../../frontend/docs/en/data-types.md)
