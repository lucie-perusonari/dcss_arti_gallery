# 데이터 타입

이 문서는 백엔드 파이프라인에서 계층 사이를 이동하는 데이터 타입을 정의합니다.
구현 세부 로직은 처리 계층 문서나 각 모듈의 코드에서 다룹니다.

## `MorgueFile`

HTTP로 조회한 원격 morgue 디렉터리에서 발견한 txt/lst 파일 항목입니다.

- 정의 위치: `crawl_service.morgue.types`
- 필드:
  - `name: str`: 원격 파일명
  - `url: str`: 원격 파일 URL
  - `extension: str`: 파일 확장자. `name`에서 계산되는 property

## `MorgueUser`

HTTP로 조회한 원격 morgue root 디렉터리에서 발견한 player 디렉터리 항목입니다.

- 정의 위치: `crawl_service.morgue.types`
- 필드:
  - `nickname: str`: player directory 이름
  - `url: str`: player morgue 디렉터리 URL
  - `modified_at: str`: root index의 Date 컬럼 원문

## `MorgueRawText`

HTTP로 가져온, artifact parser가 처리할 수 있는 원격 morgue 원문입니다.

- 정의 위치: `crawl_service.morgue.types`
- 필드:
  - `name: str`: 원격 파일명
  - `url: str`: 원격 파일 URL
  - `extension: str`: 원문 종류. 현재 `txt` 또는 `lst`
  - `text: str`: 파일 본문

## `RawMorgueFileRecord`

`crawl_service` ingest flow가 MongoDB `raw_morgue_files` 컬렉션에 저장하는 원본 morgue 파일과 처리 상태입니다.
원본 파일은 artifact read model의 source of truth이며, artifact 문서는 이 레코드에서 재생성 가능한 파생 결과입니다.
ingest는 이 레코드의 fetch 상태까지만 책임지고, processing은 이 레코드를 읽어 artifact 문서와 process 상태를 갱신합니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`: player directory 이름
  - `name: str`: 원격 파일명
  - `url: str`: 원격 파일 URL
  - `extension: str`: 원문 종류. 현재 `txt` 또는 `lst`
  - `text: str`: 파일 본문
  - `content_hash: str`: 원문 본문의 SHA-256 hash
  - `fetch_status: str`: 원본 확보 상태. 현재 `fetched` 또는 `failed`
  - `process_status: str`: 파생 artifact 처리 상태. 현재 `pending`, `processed`, `failed`
  - `fetched_at: str | None`
  - `processed_at: str | None`
  - `artifact_count: int`
  - `fetch_error: str | None`: 네트워크/원본 확보 실패 원인
  - `process_error: str | None`: parser/classifier/evaluator/document 처리 실패 원인
  - `parser_version: str | None`: 처리에 사용한 parser version
  - `scoring_version: str | None`: 처리에 사용한 scoring version

## `ArtifactRawTextInput`

`processor`가 `RawMorgueFileRecord`에서 만든 parser-ready raw text 입력입니다.

- 정의 위치: `crawl_service.domain.artifacts.types`
- 필드:
  - `name: str`
  - `url: str`
  - `extension: str`
  - `text: str`

## `ArtifactRawInfo`

한 개의 randart 원문 블록과 원문에서 바로 얻을 수 있는 색인 정보입니다.

- 정의 위치: `crawl_service.domain.artifacts.types`
- 필드:
  - `source_name: str | None`: 원본 파일명
  - `source_url: str | None`: 원본 파일 URL
  - `line_no: int`: artifact 블록 시작 줄 번호
  - `raw_text_block: str`: artifact 원문 블록
  - `artifact_name: str`: 속성 블록을 포함한 artifact 이름
  - `item_location: str | None`: lst 위치 정보
  - `item_source: str | None`: 획득 또는 상점 출처 정보
  - `visible_item_description: list[str]`: 화면에 표시된 설명 문장
  - `visible_description_labels: list[str]`: 설명 label 목록
  - `bracket_subtype: str | None`: `[ring of ...]` 같은 bracket subtype

## `ArtifactAttribute`

artifact 이름의 `{...}` 안에서 파싱한 단일 속성 토큰입니다.

- 정의 위치: `crawl_service.domain.artifacts.types`
- 필드:
  - `token: str`: 원문 속성 토큰
  - `key: str`: 정규화된 속성 key
  - `value: int | bool | None`: 수치화된 값 또는 boolean 값
  - `description: str | None`: 원문 설명에서 대응되는 설명 문장

## `ArtifactInfo`

`ArtifactRawInfo`에서 파싱한 구조화된 artifact 정보입니다.

- 정의 위치: `crawl_service.domain.artifacts.types`
- 필드:
  - `raw_info: ArtifactRawInfo`: 원본 raw info
  - `display_name: str`: 표시용 artifact 이름
  - `base_item: str`: 기본 아이템명
  - `enchantment: int | None`: 강화 수치
  - `attributes: list[ArtifactAttribute]`: 파싱된 속성 목록
  - `base_subtype: str | None`: 기본 subtype

## `RandomArtifact`

NoSQL 문서로 저장하기 쉬운 최종 randart 객체입니다.

- 정의 위치: `crawl_service.domain.artifacts.types`
- 필드:
  - `artifact_info: ArtifactInfo`: 구조화된 artifact 정보
  - `name: str`: 속성 블록을 포함한 artifact 이름
  - `base_item: str`: 기본 아이템명
  - `enchantment: int | None`: 강화 수치
  - `brand: str | None`: 무기 brand
  - `base_subtype: str | None`: `[ring of ...]`, `[staff of ...]` 같은 기본 subtype
  - `item_class: str`: 아이템 대분류
  - `item_subtype: str`: 아이템 subtype
  - `weapon_subtype: str | None`: 무기 subtype
  - `armour_slot: str | None`: 방어구 slot
  - `jewellery_slot: str | None`: 장신구 slot
  - `all_attributes: list[str]`: 전체 속성 token
  - `base_attributes: list[str]`: 기본 장비/subtype에서 온 속성 token
  - `random_attributes: list[str]`: randart 생성으로 추가된 속성 token
  - `all_attribute_text: str`: 검색/표시용 전체 속성 문자열
  - `base_attribute_text: str`: 검색/표시용 기본 속성 문자열
  - `random_attribute_text: str`: 검색/평가용 랜덤 속성 문자열

## `ArtifactEvaluation`

`RandomArtifact`의 점수 결과입니다.

- 정의 위치: `crawl_service.domain.evaluation.evaluator`
- 필드:
  - `total: int`: 최종 점수
  - `practical_score: int`: 실전성 점수. 현재 `total`과 같은 값
  - `rarity_score: int`: `random_attributes` 기반 희소/압축 신호 점수
  - `offense: int`: 공격 점수
  - `defense: int`: 방어 점수
  - `utility: int`: 유틸리티 점수
  - `penalty: int`: 페널티 점수
  - `base_fit: int`: 기본 아이템 적합도 점수
  - `grade: str`: 실전성 점수 등급
  - `luxury_grade: str`: 실전성 점수와 희소도 점수를 결합한 명품 판정

## `ArtifactDocument`

`crawl_service`가 `RawMorgueFileRecord`에서 재생성해 MongoDB에 저장하는 canonical artifact read model 문서입니다. 표시용 tile, 설명 조립,
attribute kind/scoreImpact, camelCase 응답 필드는 `api` read model에서 생성합니다.

- 정의 위치: `crawl_service.domain.documents.builder`
- 구현 형태: Pydantic `BaseModel`
- 주요 필드:
  - `id: str`: stable artifact identifier
  - `name: str`: artifact 원문 이름
  - `base_item: str`: 기본 아이템명
  - `base_subtype: str | None`: 원문 bracket subtype
  - `item_class: str`: 아이템 대분류
  - `item_subtype: str`: subtype 또는 slot
  - `weapon_subtype`, `armour_slot`, `jewellery_slot`: 분류 보조 필드
  - `enchantment: int | None`: enchantment 숫자
  - `brand: str | None`: 무기 brand
  - `source: ArtifactDocumentSource`: 원본 파일, URL, 줄 번호 정보
  - `attributes: list[ArtifactDocumentAttribute]`: 파싱된 속성 token data
  - `all_attributes`, `base_attributes`, `random_attributes`: 검색과 평가에 쓰는 token 목록
  - `evaluation: ArtifactDocumentEvaluation`: 문서/API용 평가 결과
  - `visible_item_description`, `visible_description_labels`: 원문에서 파싱한 설명 근거
  - `raw_text_block`, `item_location`, `item_source`: 원문 보존/출처 근거

## `ArtifactDocumentEvaluation`

`crawl_service.domain.documents` 도메인이 소유하는 평가 결과의 저장 모양입니다. 값은 `crawl_service.domain.evaluation.evaluator`가
생성한 결과에서 `crawl_service.processor`의 document 생성 흐름을 거쳐 복사되지만, document 모델은 evaluation 도메인 타입에
직접 의존하지 않습니다.

- 정의 위치: `crawl_service.domain.documents.builder`
- 구현 형태: Pydantic `BaseModel`
- 필드:
  - `total: int`
  - `practical_score: int | None`
  - `rarity_score: int`
  - `offense: int`
  - `defense: int`
  - `utility: int`
  - `penalty: int`
  - `base_fit: int`
  - `grade: str`
  - `luxury_grade: str | None`

## `ArtifactDocumentSource`

문서의 원본 morgue 위치 정보입니다.

- 정의 위치: `crawl_service.domain.documents.builder`
- 구현 형태: Pydantic `BaseModel`
- 필드:
  - `player: str`
  - `file: str`
  - `url: str | None`
  - `line: int`

## `ArtifactDocumentAttribute`

문서에 저장하는 파싱된 속성 token data입니다. API는 이 값을 바탕으로 표시용 `kind`와 `scoreImpact`를 만듭니다.

- 정의 위치: `crawl_service.domain.documents.builder`
- 구현 형태: Pydantic `BaseModel`
- 필드:
  - `token: str`
  - `key: str`
  - `value: int | bool | None`
  - `description: str | None`

## `CrawlFileRecord`

`crawl_service`가 remote morgue 파일별 worker 완료 상태를 저장하는 cache record입니다.
원본과 재처리의 기준 상태는 `RawMorgueFileRecord`가 소유하고, 이 record는 archive scan 중 파일 skip/cache 판단에 사용됩니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`
  - `name: str`
  - `url: str`
  - `status: str`
  - `artifact_count: int`
  - `processed_at: str | None`
  - `error: str | None`

## `CrawlUserRecord`

`crawl_service` worker가 user directory별 root index Date와 scan 결과를 저장하는 cache record입니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`
  - `url: str`
  - `observed_at: str`: root morgue index의 user directory Date
  - `status: str`
  - `scanned_at: str | None`
  - `processed_files: int`
  - `artifact_count: int`
  - `error: str | None`
