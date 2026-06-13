# arti_parser

`arti_parser`는 `crawl_service`가 MongoDB에 저장한 raw morgue 원본을 읽어 갤러리용
artifact read model을 재생성하는 배치 처리 모듈입니다.

이 모듈은 원격 morgue를 조회하지 않습니다. 입력은 이미 수집된 `raw_morgue_files`
문서이고, 출력은 `artifacts` read model 및 `artifact_processing_files` 처리 상태
문서입니다.

## 모듈

- [`batch.py`](docs/batch.md): MongoDB pending raw file을 순회하고 처리 결과를 저장하는 batch entrypoint입니다.
- [`processor.py`](docs/processor.md): raw text 하나를 `ArtifactDocument` 목록으로 변환하는 상위 processor입니다.
- [`extractor.py`](docs/extractor.md): `.txt`/`.lst` raw text에서 artifact block을 추출하고 저장 문서를 조립합니다.
- [`parser.py`](docs/parser.md): artifact 이름, enchantment, base item, property token, randart 여부를 파싱합니다.
- [`classifier.py`](docs/classifier.md): item class/subtype, armour/jewellery slot, brand, base/random attributes를 분류합니다.
- [`evaluator.py`](docs/evaluator.md): random attributes와 item metadata를 점수/등급으로 평가합니다.
- [`models.py`](docs/models.md): MongoDB에 저장되는 canonical `ArtifactDocument` Pydantic 모델입니다.
- [`repository.py`](docs/repository.md): `raw_morgue_files`, `artifacts`, `artifact_processing_files` 접근 계층입니다.
- [`constants.py`](docs/constants.md): 파싱/분류 정규식, lookup table, 공식 DCSS item/unrandart 정적 상수입니다.
- [`worker.py`](docs/worker.md): 기존 호출 호환을 위한 batch entrypoint alias입니다.
- [`process_raw_morgue_files.sh`](docs/process_raw_morgue_files.md): batch 실행 shell wrapper입니다.

## 책임 범위

- `raw_morgue_files`에서 `fetch_status: "fetched"`인 `.txt`, `.lst` 원본을 읽습니다.
- morgue/lst 텍스트에서 랜덤 아티팩트 블록을 추출합니다.
- 아이템 이름, enchantment, base item, property token, visible description을 파싱합니다.
- unrandart와 일반 magic item을 제외하고 랜덤 아티팩트만 문서화합니다.
- base item intrinsic 속성과 랜덤 속성을 분리합니다.
- 랜덤 속성 기준으로 artifact 평가 점수와 등급을 계산합니다.
- `artifacts` 컬렉션에 갤러리/API가 읽는 canonical artifact document를 upsert합니다.
- 같은 raw file에서 더 이상 나오지 않는 이전 artifact source evidence는 삭제합니다.
- `artifact_processing_files`에 처리 성공/실패와 content hash를 기록합니다.

`crawl_service`, `api`, `admin_api`의 책임을 대신하지 않습니다. 특히 remote crawl,
gallery HTTP API, admin HTTP API 로직은 이 모듈에 두지 않습니다.

## 데이터 흐름

```text
raw_morgue_files
  -> arti_parser.batch
  -> arti_parser.processor.ArtifactProcessor
  -> arti_parser.extractor
  -> arti_parser.parser
  -> arti_parser.classifier
  -> arti_parser.evaluator
  -> ArtifactDocument
  -> arti_parser.repository
  -> artifacts
  -> artifact_processing_files
```

전체 흐름은 다음 순서로 진행됩니다.

1. `batch.py`가 `repository.py`를 통해 `fetch_status: "fetched"`이고 재처리가 필요한 raw
   file을 조회합니다.
2. `processor.py`가 raw text 하나를 처리하는 상위 진입점 역할을 합니다.
3. `extractor.py`가 `.txt`의 `Inventory:` 섹션 또는 `.lst`의 level/shop/location 문맥에서
   artifact 후보 block을 추출합니다.
4. `parser.py`가 이름, 강화 수치, base item, property token을 파싱하고 unrandart/plain magic
   item을 제외할 근거를 제공합니다.
5. `classifier.py`가 item class, subtype, slot, brand를 결정하고 base intrinsic 속성과 실제
   random 속성을 분리합니다.
6. `evaluator.py`가 `random_attributes` 기준으로 점수와 등급을 계산합니다.
7. `models.py`의 `ArtifactDocument` shape로 저장 문서를 조립합니다.
8. `repository.py`가 canonical artifact를 upsert하고, 같은 raw file에서 사라진 stale source evidence를 삭제하며,
   `artifact_processing_files`에 성공/실패 상태를 기록합니다.

주요 컬렉션:

- `raw_morgue_files`: `crawl_service`가 저장한 raw morgue 원본입니다.
- `artifacts`: `api`와 `frontend`가 사용하는 artifact read model입니다.
- `artifact_processing_files`: raw file별 artifact 재생성 상태입니다.

재처리 여부는 raw file의 `content_hash`와 이전 처리 상태가 `completed`인지로 결정합니다.
파서나 평가 로직 변경 뒤 기존 raw 원본까지 다시 처리해야 한다면
`artifact_processing_files`의 대상 처리 record를 제거하거나 상태를 미완료로 되돌려 재처리
대상에 포함시킵니다.

### Stale source 삭제 주의

`repository.py`는 raw file 하나를 다시 처리할 때 같은 raw file에서 사라진 stale source evidence만
삭제해야 합니다. 이 로직에서 `artifacts` 전체를 full scan하면 batch가 raw file 수만큼 전체 컬렉션을
반복 스캔하게 되어 재처리가 심각하게 느려집니다.

Stale 후보는 반드시 현재 raw file의 source metadata로 제한합니다. 기존 문서 호환을 위해
`sources.player`/`sources.file`과 legacy `source.player`/`source.file` 조건을 모두 사용하되, 두 조건은
각각 MongoDB index를 타야 합니다.

## 실행

개발 MongoDB 환경에서는 루트에서 다음 스크립트를 사용합니다.

```sh
arti_parser/process_raw_morgue_files.sh --once
```

이 스크립트는 `infra/dev/mongo_env.sh`가 있으면 읽고, 기본값으로 다음 연결 정보를
사용합니다.

```text
MONGODB_URI=mongodb://localhost:27018
MONGODB_DATABASE=dcss_arti_gallery
MONGODB_RAW_FILES_COLLECTION=raw_morgue_files
MONGODB_COLLECTION=artifacts
MONGODB_ARTIFACT_PROCESSING_COLLECTION=artifact_processing_files
```

직접 모듈을 실행할 수도 있습니다.

```sh
python3 -m arti_parser.batch --once
```

반복 처리 모드에서는 처리할 raw file이 남아 있는 동안 batch를 반복하고, 남은 항목이
없으면 종료합니다.

```sh
python3 -m arti_parser.batch
```

## 옵션과 환경 변수

`arti_parser.batch`는 CLI 옵션과 환경 변수를 모두 지원합니다. CLI 옵션이 명시되면
해당 실행의 값을 직접 지정합니다.

| CLI 옵션 | 환경 변수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `--once` | `ONCE` | `false` | batch를 한 번만 실행합니다. |
| `--limit` | `PROCESS_LIMIT` | 없음 | 이번 실행에서 처리할 raw file 최대 개수입니다. |
| `--batch-size` | `BATCH_SIZE` | `100` | 한 batch에서 처리할 pending raw file 개수입니다. |
| `--scan-batch-size` | `SCAN_BATCH_SIZE` | `500` | pending 여부를 판정할 때 Mongo cursor에서 묶어 확인할 raw file 개수입니다. |
| `--loop-interval-seconds` | `PROCESS_LOOP_INTERVAL_SECONDS` | `60.0` | 반복 처리 사이 대기 시간입니다. |
| 없음 | `ARTIFACT_PROCESS_LOG_LEVEL` | `INFO` | batch processor 로그 레벨입니다. |

MongoDB 연결 환경 변수:

| 환경 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB 연결 문자열입니다. |
| `MONGODB_DATABASE` | `dcss_arti_gallery` | 사용할 database 이름입니다. |
| `MONGODB_RAW_FILES_COLLECTION` | `raw_morgue_files` | raw source 입력 컬렉션입니다. |
| `MONGODB_COLLECTION` | `artifacts` | artifact read model 출력 컬렉션입니다. |
| `MONGODB_ARTIFACT_PROCESSING_COLLECTION` | `artifact_processing_files` | 처리 상태 컬렉션입니다. |

## 출력 문서

`artifacts` 문서는 canonical `ArtifactDocument` 형태로 저장됩니다. 같은 artifact signature가
여러 `.lst`/`.txt` snapshot에서 반복 관측되어도 `id`가 같으면 하나의 문서로 병합하고,
관측 source evidence는 `sources`에 누적합니다. 주요 필드는 다음과 같습니다.

- `id`: source metadata를 제외한 normalized artifact signature 기반 canonical 식별자입니다.
- `occurrence_id`: raw source, line, display name 기반 occurrence 식별자입니다.
- `canonical_key`: `id` 계산에 쓰는 normalized artifact signature입니다.
- `name`, `base_item`, `base_subtype`: 표시 이름과 base item 정보입니다.
- `item_class`, `item_subtype`, `weapon_subtype`, `armour_slot`, `jewellery_slot`: 갤러리 필터와 렌더링에 쓰는 분류 필드입니다.
- `attributes`: 파싱된 property token, normalized key/value, visible description입니다.
- `all_attributes`, `base_attributes`, `random_attributes`: 전체 속성, base intrinsic 속성, 실제 랜덤 속성입니다.
- `evaluation`: 총점, practical score, rarity score, grade, 세부 점수입니다.
- `visible_item_description`, `visible_description_labels`, `raw_text_block`: UI 표시와 디버깅용 원문 근거입니다.
- `item_location`, `item_source`: 대표 occurrence에서 확인한 위치/상점 정보입니다.
- `source`: 대표 occurrence의 player, file, URL, line metadata입니다.
- `sources`, `occurrence_ids`, `source_count`, `first_source`, `first_discovered_by`, `known_seeds`, `updated_at`: canonical artifact에 누적된 source evidence metadata입니다.

저장 시 repository가 `source_content_hash`도 함께 추가합니다.

## 개발 규칙

- artifact 파싱, 분류, 평가, `ArtifactDocument` 생성, `artifacts` 저장 로직은
  `arti_parser`에 둡니다.
- `crawl_service`에는 raw morgue 수집과 crawl 상태 기록만 둡니다.
- `api`는 `arti_parser`나 `crawl_service` 모델을 import하지 않고, API 전용 DTO로
  MongoDB artifact 문서를 읽습니다.
- 평가는 `random_attributes`를 기준으로 해야 합니다. base item intrinsic 속성을
  평가에 섞으면 특정 base item이 과점수될 수 있습니다.
- `ArtifactDocument` 필드를 바꾸면 `api` response model과 `frontend` TypeScript 타입도
  함께 정렬해야 합니다.

## 검증

저장소 정책상 테스트는 사용자가 명시적으로 요청한 경우에만 실행합니다. `arti_parser`
범위를 검증해야 할 때는 변경 범위에 맞춰 최소 테스트를 선택합니다.

```sh
python3 -m unittest discover -s arti_parser/tests -t .
```

문서만 변경한 경우에는 링크와 명령 예시를 diff로 확인하는 것으로 충분합니다.
