# `prometheus.py`

`prometheus.py`는 Admin API가 내부 Prometheus HTTP API를 읽는 read-only 경계입니다.

## 책임

- `PROMETHEUS_URL`을 기준으로 Prometheus `/api/v1/query`를 호출합니다.
- Gallery API의 request rate, 5xx rate, p95 latency, in-flight 요청 수를 `GalleryApiMetrics` DTO로 변환합니다.
- Prometheus 연결이나 query 실패 시 HTTP 예외를 전파하지 않고 `status="unavailable"` 응답으로 변환합니다.

## 비소유 책임

- Prometheus scrape와 time series 저장은 `prometheus` 서비스가 소유합니다.
- Gallery API의 `/metrics` endpoint와 metric 이름은 `api.metrics`가 소유합니다.
- admin 화면 렌더링은 `admin-frontend`가 소유합니다.
