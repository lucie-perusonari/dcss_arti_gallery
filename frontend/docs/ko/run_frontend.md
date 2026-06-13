# `run_frontend.sh`

`run_frontend.sh`는 repository root에서 gallery frontend dev server를 실행하는 shell wrapper입니다.

## 책임

- `npm` 사용 가능 여부를 확인합니다.
- `frontend/node_modules`가 없으면 `npm install`을 실행합니다.
- `HOST`, `PORT` 환경 변수를 읽어 Vite dev server host/port를 정합니다.
- `frontend` 디렉터리에서 `npm run dev`를 실행합니다.

## 비소유 책임

- Gallery API 실행은 `api`가 소유합니다.
- MongoDB와 index lifecycle은 `infra`가 소유합니다.
- persisted artifact data 생성은 `arti_parser`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
