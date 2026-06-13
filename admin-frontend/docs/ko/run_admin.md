# `run_admin.sh`

`run_admin.sh`는 repository root에서 admin frontend dev server를 실행하는 shell wrapper입니다.

## 책임

- `npm` 사용 가능 여부를 확인합니다.
- `admin-frontend/node_modules`가 없으면 `npm install`을 실행합니다.
- `ADMIN_HOST`, `ADMIN_PORT`, `VITE_ADMIN_API_URL` 환경 변수를 읽어 dev server와 Admin API URL을 정합니다.
- `VITE_ADMIN_API_URL`이 없으면 `http://127.0.0.1:8001`을 기본 Admin API URL로 사용합니다.
- `admin-frontend` 디렉터리에서 `npm run dev`를 실행합니다.

## 비소유 책임

- Admin API 실행은 `admin_api`가 소유합니다.
- crawl 상태 쓰기는 `crawl_service`가 소유합니다.
- MongoDB lifecycle은 `infra`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
