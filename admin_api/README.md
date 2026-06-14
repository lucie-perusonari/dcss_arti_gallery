# Admin API

`admin_api`는 MongoDB crawl 운영 상태 컬렉션과 내부 Prometheus API를 읽어 admin dashboard용 read-only FastAPI endpoint를 제공합니다.
응답 DTO와 repository는 `admin_api`가 소유하며, `crawl_service`를 import하지 않습니다.

## 모듈

- [`app.py`](docs/ko/app.md): admin FastAPI app factory, CORS 설정, admin 라우터 연결
- [`routes.py`](docs/ko/routes.md): crawl operations 대시보드 상태 엔드포인트
- [`models.py`](docs/ko/models.md): admin 상태 응답 DTO
- [`repository.py`](docs/ko/repository.md): crawl 파일/user/raw file 상태 read repository
- [`prometheus.py`](docs/ko/prometheus.md): Prometheus HTTP API를 읽는 Gallery API metrics read repository
- [`tests/`](docs/ko/tests.md): Admin API 응답 계약과 MongoDB 읽기 검증

English version: [README.en.md](README.en.md)

## 책임

- crawl 상태 컬렉션을 읽어 운영 대시보드 API 응답을 제공합니다.
- 내부 Prometheus HTTP API를 읽어 Gallery API request/latency 지표를 admin 응답으로 변환합니다.
- Admin API 공개 계약을 admin API-owned Pydantic DTO로 소유합니다.
- crawl worker 내부 구현에 직접 의존하지 않습니다.
- `crawl_service`를 import하지 않습니다.

## 엔드포인트

- `GET /admin/crawl-status`: crawl operations 대시보드 상태
- `GET /admin/metrics/gallery-api`: Prometheus에서 읽은 Gallery API request/latency 지표

## 실행 방법

의존성:

```sh
python3 -m pip install -r requirements.txt
```

로컬 MongoDB:

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

Admin API 서버:

```sh
python3 -m uvicorn admin_api.app:app --host 0.0.0.0 --port 8001
```

전체 개발 스택에서는 compose가 Admin API 실행과 MongoDB 연결 환경을 함께 관리합니다.

```sh
docker compose -f infra/dev/docker-compose.yml up admin-api
```

Admin API 기본 CORS origin은 `http://localhost:5174`와 `http://127.0.0.1:5174`입니다.
필요하면 `ADMIN_API_CORS_ORIGINS` 또는 `ADMIN_API_CORS_ORIGIN_REGEX`로 조정합니다.
Gallery API 메트릭 조회는 `PROMETHEUS_URL`을 사용하며 기본값은 `http://localhost:9090`입니다.
Artifact 처리 상태는 `MONGODB_ARTIFACT_PROCESSING_COLLECTION`에서 읽고, 기본값은 `artifact_processing_files`입니다.
`ADMIN_CRAWL_STATUS_CACHE_SECONDS`는 `/admin/crawl-status`의 in-process cache TTL이며 기본값은 `5`초입니다.

## 테스트

```sh
python3 -m unittest discover -s admin_api/tests -t .
```

admin status contract 변경은 admin API 테스트와 `cd admin-frontend && npm run build`를 함께 확인합니다.

## 관련 상세 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
