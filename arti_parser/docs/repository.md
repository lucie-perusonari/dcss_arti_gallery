# repository.py

`repository.py`는 MongoDB-backed artifact processing repository입니다. raw source 조회,
pending 판정, artifact upsert, stale 삭제, 처리 상태 기록을 담당합니다.

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
- `content_hash`, `parser_version`, `scoring_version` 중 하나가 현재 값과 다릅니다.

## 저장 동작

- 현재 raw file에서 생성된 artifact는 `id` 기준으로 upsert합니다.
- 같은 `source.player`, `source.file`에 속하지만 이번 결과에 없는 artifact는 stale로 삭제합니다.
- 처리 성공/실패 상태는 `artifact_processing_files`에 upsert합니다.
- 저장 문서에는 `source_content_hash`, `parser_version`, `scoring_version` metadata가 추가됩니다.

## 변경 시 주의점

- `_player_key`는 player 값을 trim/lowercase하여 저장 key를 안정화합니다.
- repository는 artifact 파싱 로직을 가져서는 안 됩니다.
- MongoDB collection 이름과 기본값은 서비스 README의 환경 변수 설명과 맞아야 합니다.
