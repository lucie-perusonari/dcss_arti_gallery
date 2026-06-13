# `repository.py`

`repository.py`는 MongoDB `artifacts` read model을 읽는 Gallery API persistence 계층입니다.

## 책임

- artifact 목록과 단건 조회를 수행합니다.
- 검색어, type, player 필터를 MongoDB query로 변환합니다.
- player 필터는 canonical artifact의 대표 `source.player`와 누적 evidence인 `sources.player`를
  함께 조회합니다.
- 필터 메타데이터 조회에 필요한 distinct/count 성격의 read를 제공합니다.

## 비소유 책임

- index 생성 같은 DDL은 `infra/`가 소유합니다.
- artifact document 생성과 저장은 `arti_parser`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
