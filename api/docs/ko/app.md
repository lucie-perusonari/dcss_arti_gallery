# `app.py`

`app.py`는 Gallery API FastAPI application을 구성하는 진입점입니다.

## 책임

- FastAPI app instance를 생성합니다.
- Gallery router를 연결합니다.
- frontend 개발 서버가 접근할 수 있도록 CORS 설정을 적용합니다.
- 활성화된 경우 Prometheus HTTP 메트릭 middleware와 `/metrics` endpoint를 연결합니다.

## 비소유 책임

- endpoint별 조회 로직은 `routes.py`가 담당합니다.
- MongoDB read query는 `repository.py`가 담당합니다.
- 메트릭 registry와 middleware 세부 구현은 `metrics.py`가 담당합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
