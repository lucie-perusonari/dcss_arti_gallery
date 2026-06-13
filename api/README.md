# 갤러리 API

`api`는 MongoDB에 저장된 artifact read model을 읽어 갤러리용 FastAPI endpoint로 제공합니다.
API response model은 `api`가 소유하며, `crawl_service` document model과 중복될 수 있습니다.

`api`는 `crawl_service`를 import하지 않습니다. 두 프로젝트의 경계는 MongoDB에 저장된 문서와
API-owned Pydantic DTO입니다.

## 모듈

- [`app.py`](docs/ko/app.md): 갤러리 FastAPI app factory, CORS 설정, 갤러리 라우터 연결
- [`metrics.py`](docs/ko/metrics.md): Gallery API Prometheus 메트릭 registry, HTTP middleware, `/metrics` endpoint
- [`routes.py`](docs/ko/routes.md): 갤러리 조회 엔드포인트
- [`models.py`](docs/ko/models.md): artifact API 응답 DTO
- [`presenter.py`](docs/ko/presenter.md): 영속 artifact 문서를 public 응답 형태로 변환
- [`repository.py`](docs/ko/repository.md): MongoDB artifact 읽기 repository
- [`tests/`](docs/ko/tests.md): Gallery API 응답 계약과 read-only repository 검증

English version: [README.en.md](README.en.md)

## 책임

- `artifacts` read model을 읽어 갤러리 API 응답을 제공합니다.
- API 공개 계약을 API-owned Pydantic DTO로 소유합니다.
- 영속 MongoDB 문서를 frontend가 사용할 public 응답 형태로 변환합니다.
- `crawl_service` 내부 모델을 import하지 않습니다.

## 엔드포인트

- `GET /artifacts`: 아티팩트 목록 조회 (`q`, `type`, `player` 필터 지원)
- `GET /artifacts/{artifact_id}`: 단일 아티팩트 조회
- `GET /artifact-types`: 사용 가능한 아티팩트 타입 목록
- `GET /filters`: 갤러리 필터 메타데이터
- `GET /metrics`: Prometheus scrape용 메트릭 endpoint (`ARTIFACT_API_METRICS_ENABLED=0`이면 비활성화)

## 실행 방법

의존성:

```sh
python3 -m pip install -r requirements.txt
```

로컬 MongoDB:

```sh
eval "$(infra/dev/mongo_up.sh)"
```

갤러리 API 서버:

```sh
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

갤러리 API 기본 CORS origin은 `http://localhost:5173`과 `http://127.0.0.1:5173`입니다.
필요하면 `ARTIFACT_API_CORS_ORIGINS` 또는 `ARTIFACT_API_CORS_ORIGIN_REGEX`로 조정합니다.
Prometheus 메트릭은 기본 활성화되어 있으며, 운영 reverse proxy에서는 `/metrics`를 외부에 공개하지 않는 구성을 사용합니다.
필요하면 `ARTIFACT_API_METRICS_ENABLED=0`으로 endpoint와 middleware를 끌 수 있습니다.

## 테스트

```sh
python3 -m unittest discover -s api/tests -t .
```

API 테스트는 Gallery API 응답이 frontend `Artifact` 계약에 필요한 필드만 노출하는지 검증합니다.

## 관련 상세 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
