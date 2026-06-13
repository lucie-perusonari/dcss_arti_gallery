# API 처리 계층

이 문서는 Gallery read API의 계층과 프로젝트 경계를 정의합니다.

## 프로젝트 경계

- 모듈: `api/`
- 역할: MongoDB `artifacts` 컬렉션을 읽어 frontend gallery가 사용할 HTTP API를 제공한다.
- 제한: `api`는 `crawl_service`를 import하지 않는다. API 전용 repository와 Pydantic response model을 소유한다.
- 제한: collection index 생성 같은 DDL은 `api` 런타임에서 수행하지 않고 `infra/`에서 수행한다.

## 내부 계층

- `api.app`: 갤러리 FastAPI app factory, CORS 설정, 갤러리 라우터 연결
- `api.repository`: MongoDB artifact read repository, 검색/filter/sort
- `api.models`: frontend-facing artifact response DTO
- `api.routes`: `/artifacts`, `/artifacts/{artifact_id}`, `/artifact-types`, `/filters`

## 데이터 흐름

```text
MongoDB artifacts collection
  -> api repository
  -> api-owned Pydantic DTO
  -> FastAPI response
  -> frontend
```

## 연계 문서

- [API Data Types](./data-types.md)
- [Frontend Data Types](../../../frontend/docs/ko/data-types.md)
