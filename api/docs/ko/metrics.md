# `metrics.py`

`metrics.py`는 Gallery API의 Prometheus 메트릭을 소유합니다.

## 책임

- 앱 instance별 `CollectorRegistry`를 생성해 테스트와 app factory 재호출 시 metric 중복 등록을 피합니다.
- HTTP 요청 수, 처리 시간, in-flight 요청 수를 middleware에서 기록합니다.
- `/metrics` endpoint를 `prometheus_client` text format으로 제공합니다.
- `ARTIFACT_API_METRICS_ENABLED=0`이면 메트릭 middleware와 endpoint를 등록하지 않습니다.

## 지표

- `dcss_gallery_api_http_requests_total`: `method`, `route`, `status`별 요청 수
- `dcss_gallery_api_http_request_duration_seconds`: `method`, `route`별 요청 처리 시간 histogram
- `dcss_gallery_api_http_requests_in_progress`: `method`별 진행 중 요청 수
- `dcss_gallery_api_service_info`: 서비스 식별용 static gauge

`/metrics` 요청 자체는 HTTP 요청 지표에서 제외합니다. 매칭되지 않는 경로는 높은 cardinality를 피하기 위해
`route="unmatched"`로 기록합니다.

## 운영 정책

운영 reverse proxy는 `/metrics`를 외부에 공개하지 않습니다. Prometheus는 같은 Docker network 안에서
`api:8000/metrics`를 scrape하고, Prometheus UI는 `127.0.0.1:9090` 또는 SSH tunnel로만 접근합니다.
