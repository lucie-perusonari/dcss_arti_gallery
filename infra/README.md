# Infra 환경 정책

이 저장소의 Docker 기반 MongoDB infra는 `dev`와 `prod`를 물리적으로 분리합니다.
개발 단계의 모든 프로젝트와 스크립트는 기본적으로 `infra/dev`만 참조합니다.

## 모듈

- [`dev/`](docs/ko/dev.md): 개발 전체 Docker Compose stack과 dev 기본 환경값
- [`prod/`](docs/ko/prod.md): 운영 Docker Compose stack과 prod 보호 정책
- [`ensure_mongo_indexes.py`](docs/ko/ensure_mongo_indexes.md): MongoDB collection index DDL 적용 스크립트

## 환경 구분

| 환경 | 경로 | 기본 컨테이너 | 기본 포트 | 기본 DB |
| --- | --- | --- | --- | --- |
| dev | `infra/dev` | `dcss-arti-gallery-mongo-dev` | `27018` | `dcss_arti_gallery` |
| prod | `infra/prod` | `dcss-arti-gallery-mongo-prod` | `27017` | `dcss_arti_gallery` |

개발과 운영 실행은 Docker Compose 경로인 `infra/dev/docker-compose.yml` 또는
`infra/prod/docker-compose.yml`만 기준으로 합니다.

## 개발 정책

- 개발 실행, 로컬 테스트, mock이 아닌 로컬 API 확인은 `infra/dev/docker-compose.yml`을 사용합니다.
- `api`, `admin_api`, `crawl_service`의 코드 기본 MongoDB 값은 dev 환경을 가리킵니다.
- `infra/dev/docker-compose.yml`은 MongoDB, Gallery API, Admin API, gallery frontend,
  admin frontend, Prometheus, 익명 Viewer Grafana를 한 번에 실행하는 로컬 전체 스택입니다.
- dev raw crawler와 artifact parser는 `jobs` profile의 one-shot service로 분리되어 명시적으로 실행할 때만 동작합니다.
- MongoDB collection index 같은 DDL 작업은 application repository가 아니라 `infra/ensure_mongo_indexes.py`가
  수행하며, compose의 `mongo-indexes` service에서 자동 실행됩니다.
- `crawl_service/run_raw_crawler.sh`, `crawl_service/run_raw_crawler_dev.sh`,
  `arti_parser/process_raw_morgue_files.sh`는 명시적인
  `MONGODB_*` override가 없으면 compose dev MongoDB host bind 값을 사용합니다.
- Admin API 테스트 유틸은 MongoDB lifecycle을 직접 관리하지 않습니다. 테스트 전에 compose dev MongoDB를
  올리거나 `MONGODB_URI`, `MONGODB_DATABASE`를 명시합니다.

## Prod 정책

- `infra/prod/docker-compose.yml`은 Gallery frontend, Gallery API, Admin API, Admin frontend, MongoDB, Prometheus, Grafana, reverse proxy를 묶는 운영 배포 예시입니다.
- 운영 Gallery frontend 정적 파일은 prod compose의 `reverse-proxy` 이미지가 빌드해 Caddy에서 제공합니다.
- 운영 Admin frontend 정적 파일은 prod compose의 `admin-frontend` 이미지가 빌드해 host loopback에만 제공합니다.
- prod MongoDB index DDL은 compose의 `mongo-indexes` service가 `infra/ensure_mongo_indexes.py`를 통해 수행합니다.
- prod raw crawler와 artifact parser는 `jobs` profile의 one-shot service로 분리되어 cron 같은 외부 scheduler가 실행합니다.
- Prometheus는 host `127.0.0.1:9090`에만 bind하고, reverse proxy는 `/metrics`, `/docs`, `/redoc`, `/openapi.json`을 외부에 노출하지 않습니다.
- Admin API는 Prometheus HTTP API를 내부 network에서 read-only로 query하며, 기본 host bind는 `127.0.0.1:8001`입니다.
- Grafana는 host `127.0.0.1:3000`에만 bind하고, Prometheus datasource와 Gallery API dashboard를 provisioning합니다.
- 개발 스크립트와 테스트 유틸에서 `infra/prod`를 호출하면 안 됩니다.
- prod에 연결해야 하는 배포/운영 프로세스는 `MONGODB_URI`, `MONGODB_DATABASE`, collection 환경변수를
  명시적으로 주입해야 합니다.

## 명령

개발 전체 스택:

```sh
docker compose -f infra/dev/docker-compose.yml up
```

개발 MongoDB만 실행해야 하는 host 직접 실행 경로:

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

운영 compose:

```sh
docker compose -f infra/prod/docker-compose.yml up -d --build
ssh -L 9090:127.0.0.1:9090 <server>
ssh -L 3000:127.0.0.1:3000 <server>
ssh -L 5174:127.0.0.1:5174 <server>
```

job compose:

```sh
docker compose -f infra/dev/docker-compose.yml run --rm crawl-service
docker compose -f infra/dev/docker-compose.yml run --rm arti-parser
infra/prod/run_pipeline_once.sh
```

기본 URL:

- Gallery frontend: `http://127.0.0.1:15173`
- Admin frontend: `http://127.0.0.1:15174`
- Gallery API: `http://127.0.0.1:18000`
- Admin API: `http://127.0.0.1:18001`
- Prometheus: `http://127.0.0.1:19090`
- Grafana: `http://127.0.0.1:13000/d/dcss-gallery-api/dcss-gallery-api`
