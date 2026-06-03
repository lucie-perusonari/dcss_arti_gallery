# API Processing Layers

이 문서는 Gallery/admin read API의 계층과 프로젝트 경계를 정의합니다.

## Project Boundary

- 모듈: `api/`
- 역할: MongoDB `artifacts` 컬렉션을 읽어 frontend gallery가 사용할 HTTP API를 제공하고, crawl 상태 컬렉션을 읽어 admin dashboard용 read-only API를 제공한다.
- 제한: `api`는 `crawl_service`를 import하지 않는다. API 전용 repository와 Pydantic response model을 소유한다.

## Internal Layers

- `api.app`: FastAPI app factory, CORS 설정, gallery/admin router wiring
- `api.repository`: MongoDB artifact read repository, 검색/filter/sort
- `api.admin_repository`: MongoDB crawl 상태 read repository
- `api.models`: frontend-facing artifact response DTO
- `api.admin_models`: admin-facing crawl status response DTO
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
- [Frontend Data Types](../../../frontend/docs/reference/data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/reference/data-types.md)
