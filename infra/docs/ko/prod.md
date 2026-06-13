# `prod/`

`infra/prod`는 DDNS hostname으로 공개하는 운영 Docker Compose stack과 운영 보호 정책을 소유합니다.

## 책임

- Gallery frontend, Gallery API, Admin API, MongoDB, Prometheus, Grafana, reverse proxy를 묶는 Docker Compose 배포 예시를 제공합니다.
- 운영 Gallery frontend 정적 파일은 prod compose의 `reverse-proxy` 이미지가 빌드해 Caddy에서 제공합니다.
- Admin frontend 정적 배포는 아직 prod compose에 포함하지 않습니다.
- 운영 기본 포트 `27017`과 database `dcss_arti_gallery`를 기준으로 합니다.
- Prometheus는 host loopback에만 bind하고, `/metrics`는 reverse proxy에서 외부 접근을 차단합니다.

## Gallery API 메트릭 배포

`docker-compose.yml`은 다음 서비스를 실행합니다.

- `mongo`: 운영 MongoDB 컨테이너
- `api`: `api.app:app`을 실행하는 Gallery API
- `prometheus`: `api:8000/metrics`를 Docker network 내부에서 scrape
- `grafana`: Prometheus datasource와 Gallery API dashboard를 provisioning
- `admin-api`: MongoDB와 `prometheus:9090`을 read-only로 조회해 admin frontend용 API 제공
- `reverse-proxy`: Caddy로 HTTPS를 종료하고 frontend 정적 파일과 `/api/*` Gallery API proxy를 제공합니다.

외부에는 공유기 port forwarding으로 `80`과 `443`만 엽니다. Gallery API의 `8000`, MongoDB, Prometheus,
Grafana, Admin API port는 공유기에서 직접 열지 않습니다.

예시:

```sh
docker compose -f infra/prod/docker-compose.yml up -d --build
```

`reverse-proxy`는 frontend를 `VITE_ARTIFACT_API_URL=/api`로 빌드합니다. 브라우저는
`https://perusonari.ddns.net/api/artifacts`처럼 같은 origin의 `/api` 경로를 호출하고, Caddy가 내부
`api:8000`으로 전달합니다. Caddy가 Let's Encrypt 인증서를 발급하려면 DDNS hostname이 집 공인 IP를
가리키고, 공유기에서 외부 `80`/`443`이 compose host로 forwarding되어 있어야 합니다.

Prometheus UI는 서버 내부 `127.0.0.1:9090`에만 노출합니다.
Grafana UI는 서버 내부 `127.0.0.1:3000`에만 노출합니다. 기본 계정은 compose 환경 변수
`GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`로 바꾸고, 지정하지 않으면 `admin`/`admin`입니다.

```sh
ssh -L 9090:127.0.0.1:9090 <server>
ssh -L 3000:127.0.0.1:3000 <server>
```

admin frontend에 Grafana 링크를 표시하려면 별도 정적 배포 build 환경에 `VITE_GRAFANA_URL`을 지정합니다.

```sh
VITE_GRAFANA_URL=http://127.0.0.1:3000/d/dcss-gallery-api/dcss-gallery-api npm run build
```

운영 frontend와 API는 같은 DDNS origin에서 제공되므로 별도 CORS 설정이 필요하지 않습니다. 외부 정적
호스팅을 다시 쓰는 경우에만 `ARTIFACT_API_CORS_ORIGINS` 또는 `ARTIFACT_API_CORS_ORIGIN_REGEX`를 지정합니다.

## 관련 문서

- [Index DDL](ensure_mongo_indexes.md)
