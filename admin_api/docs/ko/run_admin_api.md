# `run_admin_api.sh`

`run_admin_api.sh`는 repository root에서 Admin API dev server를 실행하는 shell wrapper입니다.

## 책임

- 명시적인 `MONGODB_URI`, `MONGODB_DATABASE`, `MONGODB_ARTIFACT_PROCESSING_COLLECTION`이 없으면 compose dev MongoDB host bind와 기본 처리 상태 컬렉션 값을 사용합니다.
- `ADMIN_API_HOST`, `ADMIN_API_PORT` 환경 변수를 읽어 uvicorn host/port를 정합니다.
- `admin_api.app:app`을 Admin API entrypoint로 실행합니다.

## 비소유 책임

- MongoDB lifecycle 생성/시작은 `infra/dev`가 소유합니다.
- crawl 상태 쓰기와 raw ingest는 `crawl_service`가 소유합니다.
- dashboard UI 렌더링은 `admin-frontend`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
