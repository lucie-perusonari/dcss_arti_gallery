# DCSS 아티 갤러리

Dungeon Crawl Stone Soup morgue 로그와 lst 파일에서 랜덤 아티팩트 정보를 수집하고,
원본 아이템에는 없는 랜덤 속성을 분리해 갤러리로 보여주는 저장소입니다.

이 저장소는 여러 독립 모듈을 한 checkout 안에 둡니다. 모듈별 실행 방법과 세부 구조는
각 모듈의 `README.md`를 기준으로 봅니다.

English version: [README.en.md](README.en.md)

## 모듈

- [crawl_service](crawl_service/README.md): 원격 morgue 탐색/가져오기, raw file 저장, 저장된 원본 처리, artifact 문서 생성, MongoDB 기록, 백그라운드 워커
- [api](api/README.md): MongoDB artifact/admin 읽기 API, API 소유 Pydantic response DTO, FastAPI 라우트
- [frontend](frontend/README.md): React/Vite 기반 WebTiles 스타일 artifact 갤러리
- [admin-frontend](admin-frontend/README.md): React/Vite 기반 crawl 운영 대시보드
- `infra/mongo`: Docker 기반 local MongoDB lifecycle scripts
- `scripts`: local development, corpus/report generation, DCSS item data refresh scripts

`crawl_service`와 `api`는 독립 프로젝트로 취급합니다. `api`는 `crawl_service`를 import하지 않고,
MongoDB에 저장된 artifact 문서를 API 전용 DTO로 검증한 뒤 frontend에 반환합니다.

핵심 데이터 흐름은 **원본을 먼저 저장하고, 저장된 원본을 나중에 처리한다**는 것입니다.
`raw_morgue_files` 컬렉션이 재처리 가능한 원본이며, `artifacts` 컬렉션은 API와 frontend가 읽는
재생성 가능한 read model입니다.

## 공유 문서

모듈별 세부 문서는 각 모듈의 `docs/`에 둡니다. 루트 [docs](docs/README.md)는 모듈 문서와
운영/harness 문서로 가는 인덱스 역할을 합니다.

주요 공유 문서:

- [문서 인덱스](docs/README.md): 모듈별 참고 문서 인덱스
- [Crawl Service Data Types](crawl_service/docs/ko/data-types.md): crawl/parser/scoring/storage 타입
- [API Data Types](api/docs/ko/data-types.md): Gallery/admin API response DTO
- [Frontend Data Types](frontend/docs/ko/data-types.md): gallery TypeScript artifact 타입
- [Artifact Scoring Formula](crawl_service/docs/ko/artifact_scoring_formula.md): artifact 점수 산정 기준
- [DCSS Item Data](crawl_service/docs/ko/dcss_item_data.md): 공식 DCSS item data refresh 기준
- [Harness Validation](docs/ops/harness/validation.md): 범위별/프로젝트 간 검증 매트릭스
- [Backlog](docs/ops/backlog.md): 데이터 품질과 운영 확장 후속 작업

## 로컬 MongoDB

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

이 스크립트는 Docker로 `mongo:7.0` 컨테이너를 띄우고 기본 연결 값을 출력합니다.

상태 확인과 중지는 다음 스크립트를 사용합니다.

```sh
infra/mongo/mongo_status.sh
infra/mongo/mongo_down.sh
```

## 로컬 개발

전체 개발 서버를 한 번에 실행하려면 루트에서 다음 스크립트를 사용합니다.

```sh
./scripts/run_dev.sh
```

수동 실행:

```sh
eval "$(infra/mongo/mongo_up.sh)"
python3 -m crawl_service.worker
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
cd frontend && VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

Admin 대시보드:

```sh
./scripts/run_admin.sh
```

기본 Admin URL은 `http://127.0.0.1:5174`이고, API URL은 `VITE_ADMIN_API_URL`로 지정합니다.

## 검증

```sh
python3 -m unittest discover -s api/tests -t .
python3 -m unittest discover -s crawl_service/tests -t .
cd frontend && npm run build
cd admin-frontend && npm run build
```

문서만 변경한 경우에는 링크 점검과 diff 검토를 우선합니다.
