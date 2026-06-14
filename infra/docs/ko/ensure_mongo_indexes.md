# `ensure_mongo_indexes.py`

`ensure_mongo_indexes.py`는 MongoDB collection index DDL을 적용하는 infra 스크립트입니다.

## 책임

- application repository가 런타임에서 index를 생성하지 않도록 DDL 책임을 `infra`에 둡니다.
- dev/prod compose의 `mongo-indexes` service에서 호출되어 필요한 index를 보장합니다.
- crawl, processing, gallery read 경로에서 사용하는 collection index를 한곳에서 관리합니다.
- `artifacts`에는 canonical `id`, `canonical_key`, 대표 `source`, 누적 `sources` evidence 조회에
  필요한 index를 둡니다.
- `artifacts`에는 Gallery API 목록 정렬/최근 게임 필터용 `evaluation.total`, `latest_game_ended_at`,
  `item_class` 조합 index도 둡니다.
- `raw_morgue_files`, `crawl_files`, `crawl_users`, `artifact_processing_files`에는 ingest 중복 방지,
  처리 pending 판정, admin 상태/오류 조회에 필요한 index를 둡니다.

## 비소유 책임

- application data read/write 로직은 각 서비스 repository가 소유합니다.
