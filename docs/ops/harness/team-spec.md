# Codex Harness 팀 규칙

## 도메인 요약

이 저장소는 네 개의 독립 프로젝트를 가집니다.

```text
remote morgue
  -> crawl_service/ writer project
  -> MongoDB raw_morgue_files 원본 저장소
  -> MongoDB artifacts read model
  -> api/ read project
  -> frontend/ gallery project
  -> admin-frontend/ operations dashboard
```

`crawl_service`는 아카이브 전체 morgue 탐색, 요청 간격 제어, raw source 영속화, 파싱, 분류, 점수 계산, 문서 생성, Mongo 저장, crawl file/user 캐시 기록을 담당합니다.
source-of-truth 흐름은 `raw file` 우선, `process` 나중 순서로,
`raw_morgue_files`가 artifact 재생성을 구동하고 `artifacts`는 API 대상 read model로 사용됩니다.

`api`는 Mongo 읽기, API 전용 Pydantic response DTO, 갤러리 HTTP 엔드포인트를 소유합니다. `crawl_service`를 import하면 안 됩니다.

`frontend`는 React + Vite 갤러리 UI를 소유하며 Gallery API 응답만 사용합니다.

`admin-frontend`는 React + Vite로 운영 상태를 표시하는 독립 crawl operations dashboard 프로젝트이며 API admin status endpoint를 사용합니다.

계약의 기준 문서는 아래를 참고합니다.

- `docs/README.md`
- `crawl_service/docs/ko/data-types.md`
- `crawl_service/docs/ko/processing-layers.md`
- `crawl_service/docs/ko/artifact_scoring_formula.md`
- `crawl_service/docs/ko/randart_properties.md`
- `api/docs/ko/data-types.md`
- `api/docs/ko/processing-layers.md`
- `frontend/docs/ko/data-types.md`
- `frontend/docs/ko/processing-layers.md`
- `admin-frontend/docs/ko/data-types.md`
- `admin-frontend/docs/ko/processing-layers.md`
- `README.md`
- `crawl_service/README.md`
- `api/README.md`
- `frontend/README.md`
- `admin-frontend/README.md`
- `docs/ops/harness/scenarios.md`

## 라우팅

- 리포트, 분석 노트, 저장소 문서는 기본적으로 한국어로 작성합니다. 코드 식별자, 명령어, API 필드명, 외부 제목, 인용문은 원어 유지.
- 다중 프로젝트 요청은 먼저 `dcss-pipeline-orchestrator`를 사용합니다.
- crawl ingest, processor, parser, scorer, document-build 변경은 `crawl_service` 소유권으로 `bugfix`로 라우팅합니다.
- 갤러리 읽기 API 변경은 `api` 소유권으로 `bugfix`를 사용하고, 프런트엔드 응답 호환성을 유지해야 합니다.
- API 응답 형태 작업은 `api.models`, `api.routes`, `frontend/src/types/artifact.ts`, `frontend/src/api/artifacts.ts`를 함께 비교합니다.
- 프런트엔드 표시/ WebTiles 충실도 작업은 `webtiles-ui`로 라우팅합니다.
- 테스트 전용 작업은 `test-generation`으로 라우팅합니다.
- 리뷰/감사 요청은 `code-review`로 라우팅합니다.

## 실패 정책

- `api`를 `crawl_service`로, 또는 `crawl_service`를 `api`로 import하지 않습니다.
- 옛 루트 패키지 `morgue`, `application`, `artifacts`, `evaluation`, `documents`, `repositories`, `cli`를 다시 도입하지 않습니다.
- 네트워크 동작 확인이 필요하거나 사용자가 명시적으로 요청하지 않으면 라이브 morgue 크롤은 실행하지 않습니다.
- parser/importer/repository/API 동작은 우선 fixture 기반 또는 mock 테스트로 검증합니다.
- 점수 변경이 있을 경우 `crawl_service/docs/ko/artifact_scoring_formula.md`와 비교 검증합니다.
- TODO: formatter, linter, 커버리지 임계값, CI 구성, 배포 게이트, 릴리스 타깃은 아직 정의되지 않았습니다.
