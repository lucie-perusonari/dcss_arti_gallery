# `prod/`

`infra/prod`는 운영 MongoDB lifecycle script와 운영 보호 정책을 소유합니다.

## 책임

- 운영 MongoDB 컨테이너 생성, 시작, 중지, 상태 확인 script를 제공합니다.
- Gallery API, Admin API, MongoDB, Prometheus, Grafana, reverse proxy를 묶는 Docker Compose 배포 예시를 제공합니다.
- destructive 또는 운영 영향 명령에 `CONFIRM_PROD=1` 확인을 요구합니다.
- 운영 기본 포트 `27017`과 database `dcss_arti_gallery`를 기준으로 합니다.
- Prometheus는 host loopback에만 bind하고, `/metrics`는 reverse proxy에서 외부 접근을 차단합니다.

## Gallery API 메트릭 배포

`docker-compose.yml`은 다음 서비스를 실행합니다.

- `mongo`: 운영 MongoDB 컨테이너
- `api`: `api.app:app`을 실행하는 Gallery API
- `prometheus`: `api:8000/metrics`를 Docker network 내부에서 scrape
- `grafana`: Prometheus datasource와 Gallery API dashboard를 provisioning
- `admin-api`: MongoDB와 `prometheus:9090`을 read-only로 조회해 admin frontend용 API 제공
- `reverse-proxy`: public API port를 열고 `/metrics`, `/docs`, `/redoc`, `/openapi.json`을 차단

예시:

```sh
ARTIFACT_API_CORS_ORIGINS=https://<frontend-host> PUBLIC_API_PORT=8000 docker compose -f infra/prod/docker-compose.yml up -d --build
```

Prometheus UI는 서버 내부 `127.0.0.1:9090`에만 노출합니다.
Grafana UI는 서버 내부 `127.0.0.1:3000`에만 노출합니다. 기본 계정은 compose 환경 변수
`GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`로 바꾸고, 지정하지 않으면 `admin`/`admin`입니다.

```sh
ssh -L 9090:127.0.0.1:9090 <server>
ssh -L 3000:127.0.0.1:3000 <server>
```

admin frontend에 Grafana 링크를 표시하려면 build 환경에 `VITE_GRAFANA_URL`을 지정합니다.

```sh
VITE_GRAFANA_URL=http://127.0.0.1:3000/d/dcss-gallery-api/dcss-gallery-api npm run build
```

정적 호스팅된 frontend에서 `http://<server-ip>:8000` API를 호출하면, frontend가 HTTPS로 제공되는 경우 브라우저의
mixed content 정책에 막힐 수 있습니다. 이 경우 frontend도 같은 reverse proxy에서 제공하거나 frontend 도메인 아래
`/api` reverse proxy를 두는 방식으로 바꿔야 합니다.

## 관련 문서

- [Index DDL](ensure_mongo_indexes.md)
