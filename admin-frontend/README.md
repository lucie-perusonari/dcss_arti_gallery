# 크롤 Admin Frontend

`admin-frontend`는 React + TypeScript + Vite 기반 crawl 운영 대시보드입니다.
Admin API endpoint에서 crawl file/user/raw file 상태를 읽어 운영 상태를 보여줍니다.

## 모듈

- [`src/App.tsx`](docs/ko/app.md): crawl status dashboard 화면
- [`src/api/status.ts`](docs/ko/api-status.md): `VITE_ADMIN_API_URL` 기반 admin API client
- [`src/types/status.ts`](docs/ko/types-status.md): Admin API 응답 TypeScript 타입
- [`src/styles.css`](docs/ko/styles.md): dashboard layout과 상태 표시 스타일
- [`vite.config.ts`](docs/ko/vite-config.md): Vite build/dev 설정
- [`tests/test_mock_smoke.py`](docs/ko/mock-smoke-test.md): 목업 admin API smoke test

English version: [README.en.md](README.en.md)

## 책임

- Admin API endpoint에서 crawl file/user/raw file 상태를 읽습니다.
- crawl 운영 대시보드 화면과 상태 표시 스타일을 소유합니다.
- Admin API 응답 타입과 frontend 사용 경계를 소유합니다.

## 실행 방법

dependencies:

```sh
npm install
```

API URL을 지정해 dev server를 실행합니다.

```sh
VITE_ADMIN_API_URL=http://127.0.0.1:8001 npm run dev -- --host 127.0.0.1 --port 5174
```

서비스 스크립트로 실행:

```sh
./admin_api/run_admin_api.sh
./admin-frontend/run_admin.sh
```

기본 Admin URL은 `http://127.0.0.1:5174`입니다.
Admin API 기본 URL은 `http://127.0.0.1:8001`이고, 기본 CORS 설정은 admin dev port `5174`를 허용합니다.
다른 origin에서 호출해야 하면 API 실행 환경에 `ADMIN_API_CORS_ORIGINS` 또는 `ADMIN_API_CORS_ORIGIN_REGEX`를 지정합니다.

## 빌드

```sh
npm run build
```

목업 admin API를 이용한 smoke test:

```sh
npm run test:mock
```

admin API contract 변경은 `python3 -m unittest discover -s admin_api/tests -t .`와 admin frontend build를 함께 확인합니다.

## 관련 상세 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
