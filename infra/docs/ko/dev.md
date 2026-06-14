# `dev/`

`infra/dev`는 개발 Docker Compose stack과 개발 기본 환경값을 소유합니다.

## 책임

- 개발 MongoDB, API, admin API, frontend, admin frontend, Prometheus, Grafana 컨테이너를
  compose stack으로 생성, 시작, 중지합니다.
- 개발 기본 포트 `27018`과 database `dcss_arti_gallery`를 제공합니다.
- `mongo-indexes` service가 필요한 index DDL을 적용합니다.
- `docker-compose.yml`로 MongoDB, API, admin API, frontend, admin frontend, Prometheus, Grafana를
  한 번에 실행합니다.
- raw crawler와 artifact parser는 기본 stack과 분리된 `jobs` profile의 one-shot service로만 실행합니다.

## 전체 스택 실행

```sh
docker compose -f infra/dev/docker-compose.yml up
```

기본 포트:

- Gallery frontend: `http://127.0.0.1:15173`
- Admin frontend: `http://127.0.0.1:15174`
- Gallery API: `http://127.0.0.1:18000`
- Admin API: `http://127.0.0.1:18001`
- Prometheus: `http://127.0.0.1:19090`
- Grafana dashboard: `http://127.0.0.1:13000/d/dcss-gallery-api/dcss-gallery-api`

Grafana는 개발용 compose에서 anonymous Viewer를 활성화하므로 로그인 없이 dashboard를 볼 수 있습니다.

## Job 실행

raw crawler와 artifact parser는 기본 stack에 포함되지 않습니다. 개발 MongoDB에 raw morgue 원본을 수집하고
artifact read model을 갱신해야 할 때만 one-shot job으로 실행합니다.

```sh
docker compose -f infra/dev/docker-compose.yml run --rm crawl-service
docker compose -f infra/dev/docker-compose.yml run --rm arti-parser
```

## MongoDB만 실행

host에서 개별 서비스를 직접 실행해야 할 때는 compose stack 중 MongoDB와 index service만 올립니다.

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

이 경로에서 host 실행 프로세스는 기본적으로 `mongodb://localhost:27018`을 사용합니다.
MongoDB lifecycle은 compose가 소유하며 별도 lifecycle script는 두지 않습니다.

## 검증 기준

변경이 여러 서비스 경계를 건드릴 때는 dev compose stack을 기준으로 검증합니다. GitHub Actions 등으로
자동화할 때도 아래 조건을 통과 기준으로 삼습니다.

1. dev compose 전체 stack이 기동되어야 합니다.

```sh
docker compose -f infra/dev/docker-compose.yml up -d --force-recreate
docker compose -f infra/dev/docker-compose.yml ps
```

통과 조건:

- `mongo`, `api`, `admin-api`, `frontend`, `admin-frontend`, `prometheus`, `grafana`가 `Up` 상태입니다.
- `mongo`는 `healthy` 상태입니다.
- `mongo-indexes`는 성공적으로 종료되어 MongoDB index DDL을 적용합니다.

2. 20,000개 raw file batch 처리가 성공해야 합니다.

```sh
docker compose -f infra/dev/docker-compose.yml exec -T api \
  sh -c 'MONGODB_URI=mongodb://mongo:27017 MONGODB_DATABASE=dcss_arti_gallery python -m arti_parser.batch --once --limit 20000 --scan-batch-size 2000'
```

통과 조건:

- batch summary에 `20000 raw files seen`, `20000 processed`, `0 failed`가 표시됩니다.
- MongoDB `artifact_processing_files`에 `status: "failed"` record가 없어야 합니다.

3. dev compose service endpoint가 응답해야 합니다.

```sh
python3 - <<'PY'
from urllib.request import urlopen
import json

checks = [
    ("api_filters", "http://127.0.0.1:18000/filters"),
    ("api_artifacts", "http://127.0.0.1:18000/artifacts?limit=5&offset=0"),
    ("api_recent_artifacts", "http://127.0.0.1:18000/artifacts?since=30d&limit=5"),
    ("api_metrics", "http://127.0.0.1:18000/metrics"),
    ("admin_status", "http://127.0.0.1:18001/admin/crawl-status"),
    ("admin_gallery_metrics", "http://127.0.0.1:18001/admin/metrics/gallery-api"),
    ("frontend", "http://127.0.0.1:15173/"),
    ("admin_frontend", "http://127.0.0.1:15174/"),
    ("prometheus_targets", "http://127.0.0.1:19090/api/v1/targets"),
    ("grafana_health", "http://127.0.0.1:13000/api/health"),
]

for name, url in checks:
    with urlopen(url, timeout=10) as response:
        body = response.read()
        if response.status != 200:
            raise SystemExit(f"{name} returned {response.status}")
        if name == "prometheus_targets":
            data = json.loads(body.decode())
            targets = data.get("data", {}).get("activeTargets", [])
            if not targets or any(target.get("health") != "up" for target in targets):
                raise SystemExit(f"Prometheus target unhealthy: {targets}")
        if name.startswith("api_") and name.endswith("artifacts"):
            data = json.loads(body.decode())
            if not data.get("artifacts"):
                raise SystemExit(f"{name} returned no artifacts")
PY
```

통과 조건:

- 모든 endpoint가 HTTP `200`을 반환합니다.
- `/artifacts`와 최근 artifact 조회가 비어 있지 않습니다.
- Prometheus의 `gallery-api` target이 `up`입니다.
- Grafana `/api/health`가 정상 응답을 반환합니다.

4. 서비스별 계약 테스트와 frontend build가 통과해야 합니다.

```sh
docker compose -f infra/dev/docker-compose.yml exec -T api python -m unittest discover -s api/tests -t .
docker compose -f infra/dev/docker-compose.yml exec -T admin-api python -m unittest discover -s admin_api/tests -t .
docker compose -f infra/dev/docker-compose.yml exec -T api python -m unittest discover -s arti_parser/tests -t .
docker compose -f infra/dev/docker-compose.yml exec -T api python -m unittest discover -s crawl_service/tests -t .
cd frontend && npm run build
cd ../admin-frontend && npm run build
```

통과 조건:

- Python test는 compose 컨테이너 안에서 통과해야 합니다. host Python 환경의 누락 dependency 상태는
  dev compose 검증의 통과/실패 기준으로 삼지 않습니다.
- `frontend`와 `admin-frontend` build가 성공해야 합니다.

## 관련 문서

- [Index DDL](ensure_mongo_indexes.md)
