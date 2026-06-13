# `models.py`

`models.py`는 Gallery API가 외부로 반환하는 Pydantic response DTO를 소유합니다.

## 책임

- frontend-facing artifact response shape를 정의합니다.
- MongoDB 저장 문서와 분리된 API 공개 계약을 유지합니다.
- response field alias와 optional field 기본값을 관리합니다.

## 변경 규칙

DTO 필드를 변경하면 `frontend/src/types`와 [Frontend Data Types](../../../frontend/docs/ko/data-types.md)를 함께 확인합니다.

## 관련 문서

- [Data Types](data-types.md)
