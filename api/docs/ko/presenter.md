# `presenter.py`

`presenter.py`는 persisted artifact document를 Gallery API public response 형태로 변환합니다.

## 책임

- MongoDB document field를 API DTO 입력 형태로 정규화합니다.
- frontend가 사용하는 camelCase field와 score/source 구조를 조립합니다.
- 저장 문서 내부 필드가 API 응답에 직접 새어 나가지 않도록 경계를 둡니다.

## 관련 문서

- [Data Types](data-types.md)
