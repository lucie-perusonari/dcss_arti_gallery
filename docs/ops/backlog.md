# 후속 작업

# 데이터 품질/운영 후속 항목

이 문서는 즉시 차단되지 않는 데이터 품질 및 운영 후속 작업을 정리합니다.
현재는 운영 메모이며 계약 문서가 아닙니다.

## 데이터 커버리지

- 버전별/레거시 아이템은 `crawl_service.domain.documents.builder::ITEM_FLAVOUR_TEXT`에 flavor text가 빠져 있을 수 있습니다.
- 장기적으로는 DCSS 정식 버전별 설명 데이터를 동기화하거나 morgue 파일 버전을 파싱해 일치하는 설명을 선택해야 합니다.

## 기존 Mongo 데이터

- `raw_morgue_files`가 없던 시점에 생성된 Mongo `artifacts`는 원본 추적 정보가 없을 수 있습니다. source-of-truth 재생성용으로는 기존 소스 재수집이 필요합니다.
- 필터링 이전에 저장된 고정/unrand 아티팩트는 DB 마이그레이션 또는 재임포트로 정리해야 합니다.

## 캐시 및 스키마 버전 관리

- `raw_morgue_files`는 `parser_version`/`scoring_version`을 저장합니다. artifact 문서 스키마가 바뀌어 자동 재생성이 필요하면 문서 스키마 버전을 추가하세요.
- `crawl_files`는 워커의 skip/cache 기록에 불과합니다. 재처리 판단의 근거 데이터로 쓰면 안 됩니다.

## 확장성

- `api.repository.MongoArtifactReadRepository.list_artifacts`는 검색 필터링을 현재 Python 메모리에서 처리합니다.
- 문서 수가 커지면 Mongo 쿼리 기반 검색, 텍스트 인덱스, 정렬, 페이지네이션을 추가해야 합니다.

## 워커 상태

- `crawl_service.worker`는 user 단위 스캔 상태를 `crawl_users`, 파일 단위 skip/cache 상태를 `crawl_files`, 원본/처리 상태를 `raw_morgue_files`에 저장합니다.
- 워커 루프 위치는 메모리에만 있어 재시작 시 다음 패스로 가면서 저장된 user/file 상태에서 이어집니다.

## 중복 제거 정책

- 동일한 artifact가 `.txt`/`.lst` 또는 여러 morgue 파일에서 중복 저장될 수 있습니다.
- 소스 추적은 유지하면서 갤러리 노출 시 중복 제거할지 여부를 결정해야 합니다.

## 프론트엔드 계약 정리

- `frontend/src/components/DcssItemDescription.tsx`에는 기존 fallback 설명 로직이 남아 있습니다.
- 백엔드 데이터 계약이 안정되면 fallback을 줄이고 계약 기반 테스트로 고정하세요.
