# `routes.py`

`routes.py`는 Gallery API HTTP endpoint를 소유합니다.

## 책임

- `GET /artifacts` 목록 조회를 제공합니다.
- `GET /artifacts/{artifact_id}` 단건 조회를 제공합니다.
- `GET /artifact-types`와 `GET /filters` 필터 메타데이터를 제공합니다.
- repository 결과를 API response model로 반환합니다.

## 비소유 책임

- MongoDB index DDL은 `infra/`가 소유합니다.
- frontend state와 렌더링은 `frontend`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Data Types](data-types.md)
