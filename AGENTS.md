# 저장소 Agents 가이드

## 원칙

- 보고서, 분석 노트, 저장소 문서는 기본적으로 한국어로 작성합니다. 코드 식별자, 명령어, API 필드명, 인용 텍스트는 원문을 유지합니다.
- 실행 방법, 테스트 명령, 환경 변수, 의존성 설치, 서비스별 상세 문서 링크는 각 서비스 README를 기준으로 봅니다.
- 테스트 실행은 기본적으로 금지합니다. 사용자가 명시적으로 요청했거나, 작업 지시/이슈/PR 컨텍스트에 검증 실행이 요구된 경우에만 실행합니다.
- 테스트를 실행해야 하는 경우에도 변경 범위에 맞는 최소 검증만 선택합니다. 저장소 전체 테스트, 전체 빌드, 라이브 crawl, 네트워크 의존 테스트는 명시 요청이 없는 한 실행하지 않습니다.
- 테스트 파일 추가/수정은 사용자가 요청했거나, 작업 범위가 테스트 작성 자체인 경우에만 수행합니다.
- 검증이 필요한 경우 우선 정적 확인, 타입/문법 수준 확인, 또는 변경한 서비스 README의 테스트/빌드 섹션에 있는 좁은 검증을 사용합니다.

## Git 작업 규칙

### Git flow

- git flow에서 사용하는 브랜치/분류 표기는 영어로 작성합니다.
- 예: `main`, `feature/<topic>`, `fix/<topic>`, `docs/<topic>`

### 커밋 메시지

- 커밋 메시지는 한글로 작성합니다. 코드 식별자, 파일명, 명령어, API 필드명은 원문을 유지합니다.

## 문서 구조

- 루트 `README.md`는 저장소 전체의 진입점입니다. 프로젝트 개요, 독립 프로젝트 목록, 최상위 데이터 흐름과 책임 경계만 둡니다.
- 루트에는 공통 `docs/`를 만들지 않습니다. 공통 문서로 서비스 책임이 흐려지는 구조를 피합니다.
- 각 서비스의 기본 문서는 `<service>/README.md`입니다. 서비스 README는 서비스를 처음 보는 사람이 역할과 사용법을 빠르게 파악할 수 있는 진입점입니다.
- 서비스 README에는 서비스 목적, 소유 책임과 비소유 책임, 최상위 처리 흐름, 실행 방법, 주요 환경 변수, 의존성 설치, 테스트/빌드 명령, 관련 상세 문서 링크를 둡니다.
- 서비스 README는 제목과 개요 설명 다음에 `## 모듈` 항목을 둡니다. 이 항목은 에이전트가 빠르게 참조할 수 있는 파일/디렉터리 단위 색인이며, 각 항목은 해당 모듈의 개별 상세 문서로 직접 연결합니다.
- 모듈 상세 문서는 모듈별로 분리합니다. 예를 들어 `<service>/docs/ko/<module>.md`처럼 파일/디렉터리 단위 문서를 만들고, 여러 모듈 설명을 `modules.md` 같은 단일 문서에 모으지 않습니다.
- 서비스 README에는 모듈별 구현 세부사항을 길게 두지 않습니다. README의 `## 모듈`에는 한 줄 요약과 개별 상세 문서 링크만 두고, 파일별 책임, 처리 계층, 데이터 타입, API 계약, UI 규칙, 운영 정책처럼 세부 설명이 필요한 내용은 `<service>/docs/` 아래 모듈별 문서 또는 주제별 문서로 분리합니다.
- 각 서비스의 상세 문서는 `<service>/docs/` 아래에 둡니다. 서비스가 소유한 세부 계약과 설계 설명은 해당 서비스 docs가 소유합니다.
- 여러 서비스가 맞닿는 계약은 중앙 문서로 합치지 않습니다. 공개 계약을 소유한 서비스 문서에 기준을 두고, 소비하는 서비스 문서에는 참조와 사용 규칙만 기록합니다.

## 프로젝트 경계

- 이 저장소는 여섯 개의 독립 프로젝트로 구성됩니다: `crawl_service`, `arti_parser`, `api`, `admin_api`, `frontend`, `admin-frontend`.
- `crawl_service`는 원격 morgue 조회, raw morgue 원본 MongoDB 저장, crawl file/user 캐시 기록, 백그라운드 crawl worker만 소유합니다.
- `arti_parser`는 저장된 raw morgue 원본에서 artifact 파싱, 분류, 평가, `ArtifactDocument` 생성, `artifacts` read model 재생성/저장을 소유합니다.
- `api`는 갤러리 읽기 API를 소유합니다. API 전용 repository와 Pydantic response model로 MongoDB artifact를 읽습니다.
- `admin_api`는 crawl 운영 상태 읽기 API를 소유합니다. Admin API 전용 repository와 Pydantic response model로 MongoDB crawl 상태 컬렉션을 읽습니다.
- `frontend`는 갤러리 UI를 소유하고 Gallery API 응답만 사용합니다.
- `admin-frontend`는 crawl 운영 대시보드 UI를 소유하고 Admin API 응답만 사용합니다.
- `infra`는 개발/운영 MongoDB lifecycle script와 index 같은 인프라 작업을 소유합니다.
- 루트 `scripts/`는 새 기능의 소유 위치로 사용하지 않습니다. 장기적으로 제거 대상입니다.

## 금지 사항

- `crawl_service`에 artifact 파싱, 분류, 평가, 문서 생성, `artifacts` 저장 로직을 두지 않습니다.
- `crawl_service`에서 `arti_parser`를 import하지 않습니다. raw source 이후 artifact 처리와 `artifacts` 저장은 `arti_parser`가 소유합니다.
- `api`와 `admin_api`는 `crawl_service`를 import하지 않습니다.
- `frontend`는 persisted artifact data를 Gallery API 외 경로로 읽지 않습니다.
- `admin-frontend`는 crawl 운영 상태를 Admin API 외 경로로 읽지 않습니다.
- 옛 루트 패키지 `morgue`, `application`, `artifacts`, `evaluation`, `documents`, `repositories`, `cli`를 다시 도입하지 않습니다.
- 네트워크 동작 확인이 필요하거나 사용자가 명시적으로 요청하지 않으면 실제 라이브 morgue 크롤은 실행하지 않습니다.
- 중앙 검증 매트릭스를 다시 만들지 않습니다. 검증 책임은 각 서비스 README에 둡니다.
- 실행용 스크립트를 루트 `scripts/`에 새로 추가하지 않습니다. 필요한 run script는 해당 서비스 디렉터리에 둡니다.
- mock 검증 로직을 루트 `scripts/`에 두지 않습니다. mock/fake helper는 해당 테스트 파일 또는 테스트 패키지 안에 둡니다.
- 생성용 스크립트는 강한 재사용 필요성이 있을 때만 유지하고, 가능하면 생성 대상 또는 소유 서비스 아래에 둡니다.

## 공통 스크립트 정책

- `.sh` 실행 스크립트, 테스트 보조 스크립트, fixture/mock 생성 스크립트의 배치와 유지 기준은 모든 서비스에 동일하게 적용합니다.
- 실행용 `.sh`는 가장 직접적인 실행 대상을 소유한 서비스 디렉터리에 둡니다. 여러 서비스를 조합하는 개발용 실행 스크립트는 `infra/dev`처럼 조합을 소유한 인프라 영역에 둡니다.
- mock/fake 서버, smoke test helper, test fixture 생성 로직은 테스트 코드로 취급합니다. 해당 서비스의 `tests/` 또는 테스트 패키지 안에 둡니다.
- 생성용 스크립트는 생성 산출물을 소유한 서비스에 둡니다. 네트워크나 외부 소스에 의존하는 생성기는 자동 검증 경로에 넣지 않고, 명시 요청이 있을 때만 실행합니다.
- 공통 스크립트 정책을 바꿀 때는 각 서비스 README의 명령 예시와 package script 참조도 함께 갱신합니다.

## 작업 라우팅

- 다중 경계 작업은 `.agents/skills/dcss-pipeline-orchestrator/SKILL.md`로 시작합니다.
- 수정/구현 작업은 범위가 맞으면 `.agents/skills/bugfix/SKILL.md`를 사용합니다.
- 리뷰/감사 요청은 `.agents/skills/code-review/SKILL.md`를 사용합니다.
- 테스트 추가/수정/설계가 명시된 작업은 `.agents/skills/test-generation/SKILL.md`를 사용합니다.
- WebTiles UI 표시와 충실도 작업은 `.agents/skills/webtiles-ui/SKILL.md`를 사용합니다.

## 미정

- 현재 저장소 전체 기준 Python 버전, 가상환경 매니저, formatter, linter, 배포 타깃이 아직 정해지지 않았습니다.
