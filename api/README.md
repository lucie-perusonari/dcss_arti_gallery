# 갤러리 API

`api`는 MongoDB에 저장된 artifact read model과 crawl status 데이터를 읽어 FastAPI로 제공합니다.
API response model은 `api`가 소유하며, `crawl_service` document model과 중복될 수 있습니다.

`api`는 `crawl_service`를 import하지 않습니다. 두 프로젝트의 경계는 MongoDB에 저장된 문서와
API-owned Pydantic DTO입니다.

English version: [README.en.md](README.en.md)

## 책임

- `app.py`: FastAPI app factory, CORS 설정, 갤러리/admin 라우터 연결
- `routes.py`: 갤러리 조회 엔드포인트
- `models.py`: artifact API 응답 DTO
- `presenter.py`: 영속 artifact 문서를 public 응답 형태로 변환
- `repository.py`: MongoDB artifact 읽기 repository
- `admin_routes.py`: crawl operations 대시보드 상태 엔드포인트
- `admin_models.py`: admin 상태 응답 DTO
- `admin_repository.py`: crawl 파일/user/raw 파일 상태 read repository

## 엔드포인트

- `GET /artifacts`: 아티팩트 목록 조회 (`q`, `type`, `player` 필터 지원)
- `GET /artifacts/{artifact_id}`: 단일 아티팩트 조회
- `GET /artifact-types`: 사용 가능한 아티팩트 타입 목록
- `GET /filters`: 갤러리 필터 메타데이터
- `GET /admin/crawl-status`: crawl operations 대시보드 상태

## 실행 방법

의존성:

```sh
python3 -m pip install -r requirements.txt
```

로컬 MongoDB:

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

API 서버:

```sh
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

기본 CORS origin은 `http://localhost:5173`과 `http://127.0.0.1:5173`입니다.
필요하면 `ARTIFACT_API_CORS_ORIGINS` 또는 `ARTIFACT_API_CORS_ORIGIN_REGEX`로 조정합니다.
admin dev server 기본 port는 `5174`이므로 admin 대시보드에서 직접 호출할 때는 예를 들어 다음처럼 실행합니다.

```sh
ARTIFACT_API_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:5174 \
  python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

## 테스트

```sh
python3 -m unittest discover -s api/tests -t .
```

API/frontend contract 변경은 API 테스트와 `cd frontend && npm run build`를 함께 확인합니다.
admin status contract 변경은 API 테스트와 `cd admin-frontend && npm run build`를 함께 확인합니다.

## 연계 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
- [Harness Validation](../docs/ops/harness/validation.md)
