# DCSS 아티 갤러리

Dungeon Crawl Stone Soup morgue 로그와 `lst` 파일에서 랜덤 아티팩트 정보를 수집하고,
원본 아이템에는 없는 랜덤 속성을 분리해 갤러리로 보여주는 저장소입니다.

이 저장소는 여러 독립 모듈을 한 checkout 안에 둡니다. 루트 README는 프로젝트 개요,
모듈 목록, 최상위 데이터 흐름과 책임 경계만 제공합니다. 서비스별 실행 방법, 테스트,
환경 변수, 의존성 설치, 상세 문서 링크는 각 서비스의 `README.md`를 기준으로 봅니다.

## 문서 구조

- 루트 `README.md`는 저장소 전체의 진입점이며, 프로젝트 개요, 모듈 목록, 최상위 데이터 흐름과 책임 경계만 설명합니다.
- 루트에는 공통 `docs/`를 두지 않습니다. 서비스별 책임과 구현 세부사항이 루트 공통 문서로 섞이지 않게 합니다.
- 각 서비스의 기본 문서는 `<service>/README.md`입니다. 이 문서는 서비스를 처음 보는 사람이 역할과 사용법을 빠르게 파악할 수 있는 진입점이어야 합니다.
- 서비스 README에는 서비스 목적, 소유 책임과 비소유 책임, 최상위 처리 흐름, 실행 방법, 주요 환경 변수, 의존성 설치, 테스트/빌드 명령, 관련 상세 문서 링크를 둡니다.
- 서비스 README는 제목과 개요 설명 다음에 `## 모듈` 항목을 둡니다. 이 항목은 에이전트가 빠르게 참조할 수 있는 파일/디렉터리 단위 색인이며, 각 항목은 해당 모듈의 개별 상세 문서로 직접 연결합니다.
- 모듈 상세 문서는 모듈별로 분리합니다. 예를 들어 `<service>/docs/ko/<module>.md`처럼 파일/디렉터리 단위 문서를 만들고, 여러 모듈 설명을 `modules.md` 같은 단일 문서에 모으지 않습니다.
- 서비스 README는 모듈별 구현 세부사항을 길게 설명하지 않습니다. README의 `## 모듈`에는 한 줄 요약과 개별 상세 문서 링크만 두고, 파일별 책임, 처리 계층, 데이터 타입, API 계약, UI 규칙, 운영 정책처럼 세부 설명이 필요한 내용은 `<service>/docs/` 아래 모듈별 문서 또는 주제별 문서로 분리합니다.
- 서비스별 상세 문서는 `<service>/docs/` 아래에 둡니다. 특정 서비스가 소유한 세부 계약과 설계 설명은 해당 서비스의 docs가 소유합니다.
- 여러 서비스가 맞닿는 계약을 설명해야 할 때도 중앙 공통 문서로 모으지 않고, 공개 계약을 소유한 서비스 문서에 기준을 두고 소비 서비스 문서에는 참조와 사용 규칙만 둡니다.

English version: [README.en.md](README.en.md)

## 모듈

- [crawl_service](crawl_service/README.md): 원격 morgue 탐색/가져오기, raw morgue 원본 저장, crawl 상태 기록, 백그라운드 워커
- [arti_parser](arti_parser/README.md): 저장된 raw morgue 원본에서 랜덤 아티팩트를 파싱하고 `artifacts` read model 재생성
- [api](api/README.md): 갤러리용 artifact 읽기 API, API 소유 DTO, FastAPI 라우트
- [admin_api](admin_api/README.md): crawl 운영 상태 읽기 API, admin API 소유 DTO, FastAPI 라우트
- [frontend](frontend/README.md): React/Vite 기반 WebTiles 스타일 artifact 갤러리
- [admin-frontend](admin-frontend/README.md): React/Vite 기반 crawl 운영 대시보드
- [infra](infra/README.md): 개발/운영 Docker Compose stack과 환경 정책

## 데이터 흐름

```text
remote morgue
  -> crawl_service
  -> raw_morgue_files
  -> arti_parser
  -> artifacts
  -> api
  -> frontend

crawl status collections
  -> admin_api
  -> admin-frontend
```

`crawl_service`는 원격 원본 수집과 raw 저장만 담당하고, artifact 파싱/평가/read model
생성은 `arti_parser`가 담당합니다. 갤러리와 운영 대시보드는 각각 `api`와 `admin_api`를
통해서만 데이터를 읽습니다.

## 검증 기준

여러 서비스 경계를 건드리는 변경은 dev compose stack 기준으로 검증합니다. 자동화할 상세 통과 조건은
[infra dev 문서](infra/docs/ko/dev.md)의 `검증 기준`을 봅니다.

## 책임 경계

- `crawl_service`는 원격 morgue 조회, raw morgue 원본 저장, crawl 상태 기록, 백그라운드 worker만 소유합니다. artifact 파싱, 분류, 평가, `artifacts` 저장은 담당하지 않습니다.
- `arti_parser`는 저장된 `raw_morgue_files`를 입력으로 사용해 랜덤 아티팩트를 파싱하고, 평가한 뒤 `artifacts` read model을 재생성합니다. 원격 morgue 조회나 HTTP API 제공은 담당하지 않습니다.
- `api`는 `artifacts` read model을 읽어 갤러리 API 응답을 제공합니다. API 공개 계약은 `api`의 DTO가 소유하며, `crawl_service` 내부 모델을 import하지 않습니다.
- `admin_api`는 crawl 상태 컬렉션을 읽어 운영 대시보드 API 응답을 제공합니다. crawl worker 내부 구현에 직접 의존하지 않습니다.
- `frontend`는 갤러리 화면을 소유하고, persisted artifact data는 Gallery API를 통해서만 읽습니다.
- `admin-frontend`는 운영 대시보드를 소유하고, crawl 상태 데이터는 Admin API를 통해서만 읽습니다.
- `infra`는 MongoDB lifecycle script와 index 같은 인프라 작업을 소유합니다. application repository가 infra DDL을 대신 수행하지 않습니다.
- 루트 `scripts/`는 장기적으로 제거 대상입니다. 실행용 스크립트는 해당 서비스 아래에 두고, mock 검증 로직과 테스트 fixture 생성기는 테스트 파일 또는 테스트 패키지 안에 둡니다. 운영 로직에 빠지면 안 되는 필수 생성기만 예외적으로 서비스 아래에 유지합니다.
