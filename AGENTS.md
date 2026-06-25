# 저장소 Agents 가이드

## 원칙

- 보고서, 분석 노트, 저장소 문서는 기본적으로 한국어로 작성합니다. 코드 식별자, 명령어, API 필드명, 인용 텍스트는 원문을 유지합니다.
- 작업을 시작하기 전에 루트 `README.md`를 먼저 확인해 저장소의 현재 모듈 목록, 데이터 흐름, 책임 경계를 기준으로 삼습니다. 서비스별 실행 방법, 테스트 명령, 환경 변수, 의존성 설치, 상세 문서 링크는 각 서비스 README를 기준으로 봅니다.
- 테스트 실행은 기본적으로 금지합니다. 사용자가 명시적으로 요청했거나, 작업 지시/이슈/PR 컨텍스트에 검증 실행이 요구된 경우에만 실행합니다.
- 테스트를 실행해야 하는 경우에도 변경 범위에 맞는 최소 검증만 선택합니다. 저장소 전체 테스트, 전체 빌드, 라이브 crawl, 네트워크 의존 테스트는 명시 요청이 없는 한 실행하지 않습니다.
- 테스트 파일 추가/수정은 사용자가 요청했거나, 작업 범위가 테스트 작성 자체인 경우에만 수행합니다.
- 검증이 필요한 경우 우선 정적 확인, 타입/문법 수준 확인, 또는 변경한 서비스 README의 테스트/빌드 섹션에 있는 좁은 검증을 사용합니다.
- 운영 배포나 릴리즈 작업이 아닌 일반 변경은 `develop`에서 수행합니다. `main`에서는 작업트리 변경을 만들지 않고,
  운영 배포는 태그가 붙은 깨끗한 `main` commit에서만 실행합니다.
- 릴리즈는 반드시 모든 변경을 커밋하고 `git status --short`가 비어 있는 것을 확인한 뒤 진행합니다.
  커밋되지 않은 작업트리 상태에서 태그, GitHub Release, 운영 compose build를 만들지 않습니다.

## 기준 문서

- 저장소 구조, 문서 구조, 데이터 흐름, 서비스별 책임 경계는 루트 `README.md`를 기준으로 합니다. `AGENTS.md`에는 에이전트 작업 규칙만 둡니다.
- 모듈별 구현 세부사항, API 계약, UI 규칙, 운영 정책은 해당 서비스 README와 서비스별 `docs/` 아래 문서를 기준으로 확인합니다.
- 새 문서나 상세 설명을 추가할 때는 루트 `README.md`의 문서 구조 원칙을 따르고, 공통 문서로 서비스 책임을 섞지 않습니다.
- `CHANGELOG.md`는 릴리즈 날짜별 섹션을 기준으로 작성하고, 최신 릴리즈 날짜가 위에 오도록 내림차순으로 유지합니다. 새 날짜의 운영 배포, 데이터 정리, 검증 기록은 이전 날짜 릴리즈 섹션에 섞지 않고 별도 릴리즈 섹션으로 분리합니다.
- 운영 반영이 있었다면 같은 변경을 커밋하고 릴리즈 노트를 갱신한 뒤 태그와 GitHub Release를 만들어야 합니다. 이미 공유된 태그는 옮기지 않고 새 릴리즈 태그를 만듭니다.

## 도메인 로직 배치

- 새 도메인 로직은 루트 `README.md`의 책임 경계를 기준으로 가장 직접적으로 소유하는 서비스에 배치합니다. 기존 코드 위치가 책임 경계와 맞지 않으면 기능을 확장하기 전에 적합한 서비스로 이동하는 방향을 우선 검토합니다.
- morgue 원본 수집과 raw 저장은 `crawl_service`, artifact 파싱/분류/평가/read model 생성은 `arti_parser`, 갤러리 읽기 계약은 `api`, 운영 상태 읽기 계약은 `admin_api`, 화면 로직은 각각 `frontend`와 `admin-frontend`, 인프라 lifecycle은 `infra`에 둡니다.
- 서비스 경계를 넘는 계약 변경은 공개 계약을 소유한 서비스 문서에 먼저 기준을 두고, 소비하는 서비스에는 참조와 사용 규칙만 둡니다.

## 도메인별 제한 참조

- 작업 중 금지/비소유 책임을 판단할 때는 루트 `README.md`의 `책임 경계`를 먼저 보고, 실제 변경 대상 서비스의 README와 상세 docs를 함께 확인합니다.
- crawl 수집, raw 저장, worker, live crawl 실행 제한은 `crawl_service/README.md`와 관련 docs를 기준으로 확인합니다.
- artifact 파싱, 분류, 평가, `ArtifactDocument`, `artifacts` read model 생성/저장 제한은 `arti_parser/README.md`와 관련 docs를 기준으로 확인합니다.
- Gallery API 계약, DTO, repository, cross-service import 제한은 `api/README.md`를 기준으로 확인합니다.
- Admin API 계약, crawl 운영 상태 조회, Gallery API 지표 조회, cross-service import 제한은 `admin_api/README.md`를 기준으로 확인합니다.
- 갤러리 화면, persisted artifact data 접근 경계, WebTiles 스타일 규칙은 `frontend/README.md`와 관련 docs를 기준으로 확인합니다.
- 운영 대시보드 화면과 crawl 상태 데이터 접근 경계는 `admin-frontend/README.md`를 기준으로 확인합니다.
- 실행 스크립트, fixture/mock helper, 생성용 스크립트, MongoDB lifecycle/index, dev/prod compose 경계는 `infra/README.md`와 관련 docs를 기준으로 확인합니다.
- 옛 루트 패키지나 루트 `scripts/`처럼 현재 모듈 구조 밖에 새 소유 위치를 만들려는 변경은 먼저 루트 `README.md`의 모듈 목록과 책임 경계에 맞는 서비스 위치로 재배치합니다.

## 스크립트 작업 참조

- `.sh` 실행 스크립트, fixture/mock helper, 생성용 스크립트, compose, MongoDB lifecycle/index 작업은 먼저 `infra/README.md`와 관련 docs를 확인합니다.
- 특정 서비스만 직접 실행하는 wrapper나 테스트 helper가 필요한 경우에는 해당 서비스 README의 명령/검증 기준을 함께 확인하고, 가장 직접적인 소유 서비스 아래에 둡니다.
- 스크립트 정책을 바꾸는 작업은 `infra/README.md`를 기준으로 갱신하고, 영향받는 서비스 README의 명령 예시와 package script 참조도 함께 맞춥니다.

## 작업 라우팅

- 다중 경계 작업은 `.agents/skills/dcss-pipeline-orchestrator/SKILL.md`로 시작합니다.
- 수정/구현 작업은 범위가 맞으면 `.agents/skills/bugfix/SKILL.md`를 사용합니다.
- 리뷰/감사 요청은 `.agents/skills/code-review/SKILL.md`를 사용합니다.
- DCSS 아이템, 장비 속성, artifact token, morgue 원문 대조 검수는 `.agents/skills/dcss-item-audit/SKILL.md`를 사용합니다.
- 테스트 추가/수정/설계가 명시된 작업은 `.agents/skills/test-generation/SKILL.md`를 사용합니다.
- WebTiles UI 표시와 충실도 작업은 `.agents/skills/webtiles-ui/SKILL.md`를 사용합니다.
- git 이력/브랜치/커밋/PR 작업은 `.agents/skills/git-workflow/SKILL.md`를 사용합니다.

## 미정

- 현재 저장소 전체 기준 Python 버전, 가상환경 매니저, formatter, linter, 배포 타깃이 아직 정해지지 않았습니다.
