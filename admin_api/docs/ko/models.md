# `models.py`

`models.py`는 Admin API가 외부로 반환하는 Pydantic response DTO를 소유합니다.

## 책임

- crawl operations dashboard 응답 shape를 정의합니다.
- crawl worker 내부 record와 분리된 admin-facing 공개 계약을 유지합니다.
- raw file, crawl file/user, latest activity, recent error 요약 타입을 관리합니다.

## 변경 규칙

DTO 필드를 변경하면 `admin-frontend/src/types`와 [Admin Frontend Data Types](../../../admin-frontend/docs/ko/data-types.md)를 함께 확인합니다.

## 관련 문서

- [Data Types](data-types.md)
