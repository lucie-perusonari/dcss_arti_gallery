# Admin API 처리 계층

이 문서는 admin dashboard read API의 계층과 프로젝트 경계를 정의합니다.

## 프로젝트 경계

- 모듈: `admin_api/`
- 역할: MongoDB crawl 상태 컬렉션과 내부 Prometheus API를 읽어 admin dashboard가 사용할 HTTP API를 제공한다.
- 제한: `admin_api`는 `crawl_service`를 import하지 않는다. Admin API 전용 repository와 Pydantic response model을 소유한다.
- 제한: `admin_api`는 Prometheus scrape/storage를 수행하지 않고 Prometheus HTTP API를 read-only로 query한다.

## 내부 계층

- `admin_api.app`: admin FastAPI app factory, CORS 설정, admin 라우터 연결
- `admin_api.repository`: MongoDB crawl 상태 read repository
- `admin_api.prometheus`: Prometheus HTTP API read repository
- `admin_api.models`: admin-facing crawl status와 Gallery API metrics response DTO
- `admin_api.routes`: `/admin/crawl-status`, `/admin/metrics/gallery-api`

## 데이터 흐름

```text
MongoDB artifacts / crawl status collections
  -> admin_api repository
  -> admin_api-owned Pydantic DTO
  -> FastAPI response
  -> admin-frontend
```

```text
Prometheus HTTP API
  -> admin_api prometheus repository
  -> admin_api-owned Pydantic DTO
  -> FastAPI response
  -> admin-frontend
```

## 연계 문서

- [Admin API Data Types](./data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/ko/data-types.md)
