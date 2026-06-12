# 저장소 Agents 가이드

## 구성

- 이 저장소는 네 개의 독립 프로젝트로 구성됩니다: `crawl_service`, `api`, `frontend`, `admin-frontend`.
- `crawl_service`는 원격 morgue 조회, 파싱, 분류, 평가, artifact 문서 생성, MongoDB 저장, crawl file/user 캐시 기록, 백그라운드 crawl 워커를 담당합니다.
- `api`는 갤러리 읽기 API를 소유합니다. API 전용 repository와 Pydantic response model로 MongoDB artifact을 읽으며 `crawl_service`를 import하면 안 됩니다.
- `frontend`는 `frontend/` 하위의 React + TypeScript + Vite 앱으로, 갤러리 API와 통신합니다.
- `admin-frontend`는 `admin-frontend/` 하위의 React + TypeScript + Vite 앱으로, API admin endpoint에서 crawl 운영 상태를 읽습니다.
- 로컬 MongoDB 라이프사이클 스크립트는 `infra/mongo/`에 있습니다.

## 이유

- `crawl_service`와 `api`는 하나의 저장소를 공유해도 별도 프로젝트로 취급합니다.
- API response 모델은 crawl 문서 모델과 일부 중복될 수 있습니다. 이는 API가 공개 계약을 소유한다는 점에서 의도된 구조입니다.
- 아티팩트 평가는 `RandomArtifact.random_attributes`를 기반으로 해야 합니다. 기본 아이템 속성은 분리해 intrinsic 속성의 과점수를 피합니다.
- 갤러리가 artifact 필드를 그대로 렌더링하므로 `api`와 `frontend` 타입은 항상 정렬되어야 합니다.

## 실행 방식

- 보고서, 분석 노트, 저장소 문서는 기본적으로 한국어로 작성합니다. 코드 식별자, 명령어, API 필드명, 인용 텍스트는 원문을 유지합니다.
- Install Python dependencies with `python3 -m pip install -r requirements.txt`.
- Python 종속성은 `python3 -m pip install -r requirements.txt`로 설치합니다.
- API 테스트는 `python3 -m unittest discover -s api/tests -t .`로 실행합니다.
- crawl service 테스트는 `python3 -m unittest discover -s crawl_service/tests -t .`로 실행합니다.
- 프런트엔드 의존성 설치는 `cd frontend && npm install`입니다.
- 프런트엔드 프로덕션 빌드는 `cd frontend && npm run build`입니다.
- Admin 프런트엔드 의존성 설치는 `cd admin-frontend && npm install`입니다.
- Admin 프런트엔드 프로덕션 빌드는 `cd admin-frontend && npm run build`입니다.
- 로컬 MongoDB는 `eval "$(infra/mongo/mongo_up.sh)"`로 시작합니다.
- 크롤 워커는 `python3 -m crawl_service.worker`로 시작합니다.
- raw morgue 원본만 수집하려면 `crawl_service/run_raw_crawler.sh`를 사용하고, 저장된 원본을 별도로 처리하려면 `crawl_service/process_raw_morgue_files.sh`를 사용합니다.
- API는 `python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000`로 시작합니다.
- 프런트엔드 dev 서버는 `./scripts/run_frontend.sh` 또는 `cd frontend && VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173`로 시작합니다.
- Admin 프런트엔드 dev 서버는 `./scripts/run_admin.sh` 또는 `cd admin-frontend && VITE_ADMIN_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5174`로 시작합니다.
- 경로/소유권/실패 정책은 `docs/ops/harness/team-spec.md`를 참고합니다.
- 기본 작업 흐름은 `docs/ops/harness/workflow.md`를 참고합니다.
- 범위별 및 프로젝트 간 검증 게이트는 `docs/ops/harness/validation.md`를 참고합니다.
- 다중 경계 작업은 `.agents/skills/dcss-pipeline-orchestrator/SKILL.md`로 시작하고, 수정/리뷰/테스트/WebTiles UI 작업은 매칭되는 repo 로컬 skill로 분기합니다.
- 네트워크 동작 확인이 필요하거나 명시적으로 요청되지 않는 한, 실제 라이브 morgue 크롤은 실행하지 않습니다.

## TODO

- 현재 저장소 전체 기준 Python 버전, 가상환경 매니저, formatter, linter, 배포 타깃이 아직 정해지지 않았습니다.
