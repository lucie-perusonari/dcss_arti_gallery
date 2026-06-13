# `dev/`

`infra/dev`는 개발 Docker Compose stack과 개발 기본 환경값을 소유합니다.

## 책임

- 개발 MongoDB, API, admin API, frontend, admin frontend, Prometheus, Grafana 컨테이너를
  compose stack으로 생성, 시작, 중지합니다.
- 개발 기본 포트 `27018`과 database `dcss_arti_gallery`를 제공합니다.
- `mongo-indexes` service가 필요한 index DDL을 적용합니다.
- `docker-compose.yml`로 MongoDB, API, admin API, frontend, admin frontend, Prometheus, Grafana를
  한 번에 실행합니다.

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

## MongoDB만 실행

host에서 개별 서비스를 직접 실행해야 할 때는 compose stack 중 MongoDB와 index service만 올립니다.

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

이 경로에서 host 실행 프로세스는 기본적으로 `mongodb://localhost:27018`을 사용합니다.
MongoDB lifecycle은 compose가 소유하며 별도 lifecycle script는 두지 않습니다.

## 관련 문서

- [Index DDL](ensure_mongo_indexes.md)
