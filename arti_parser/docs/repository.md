# repository.py

`repository.py`는 MongoDB-backed artifact processing repository입니다. raw source 조회,
pending 판정, canonical artifact upsert, stale source evidence 삭제, 처리 상태 기록을
담당합니다.

## 주요 구성

- `RawMorgueSource`: `raw_morgue_files` 입력 record입니다.
- `ArtifactProcessingRecord`: `artifact_processing_files` 처리 상태 record입니다.
- `ArtifactSaveResult`: artifact 저장 결과입니다.
- `ArtifactProcessingRepository`: batch가 의존하는 protocol입니다.
- `MongoArtifactProcessingRepository`: MongoDB 구현체입니다.
- `repository_from_env`: 환경 변수 기반 repository factory입니다.
- `create_mongo_artifact_processing_repository`: 명시 설정 기반 MongoDB repository factory입니다.

## pending 판정

raw file은 다음 경우 처리 대상입니다.

- `fetch_status`가 `fetched`입니다.
- 이전 처리 record가 없습니다.
- 이전 처리 상태가 `completed`가 아닙니다.
- `content_hash`가 현재 raw file 값과 다릅니다.

pending scan은 먼저 raw file metadata만 읽어 처리 필요 여부를 판정하고, 실제 처리할
raw file에 대해서만 `text` 본문을 다시 조회합니다. batch 내부 보조 조회는
`player IN (...) AND name IN (...)` 교차 조합이 아니라 정확한 `(player, name)` 쌍 `$or`
조건을 사용해야 합니다.

## 저장 동작

- 현재 raw file에서 생성된 artifact는 canonical `id` 기준으로 upsert합니다.
- 같은 canonical `id`가 이미 있으면 새 문서를 만들지 않고 `sources` evidence를 병합합니다.
- 같은 raw file에 속하지만 이번 결과에 없는 occurrence evidence는 stale로 삭제합니다.
- source evidence가 더 이상 남지 않은 canonical artifact 문서는 삭제합니다.
- 처리 성공/실패 상태는 `artifact_processing_files`에 upsert합니다.
- 저장 문서와 source evidence에는 `source_content_hash` metadata가 추가됩니다.

stale source 삭제는 현재 raw file의 `sources.player`/`sources.file` 또는 legacy
`source.player`/`source.file`에 매칭되는 artifact 문서만 조회해야 합니다. `artifacts`
전체를 raw file마다 반복 scan하면 재처리 시간이 artifact 문서 수와 raw file 수의 곱으로
증가합니다.

## 변경 시 주의점

- `_player_key`는 player 값을 trim/lowercase하여 저장 key를 안정화합니다.
- repository는 artifact 파싱 로직을 가져서는 안 됩니다.
- MongoDB collection 이름과 기본값은 서비스 README의 환경 변수 설명과 맞아야 합니다.
