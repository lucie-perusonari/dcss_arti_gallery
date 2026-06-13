# `routes.py`

`routes.py`는 crawl operations dashboard용 HTTP endpoint를 소유합니다.

## 책임

- `GET /admin/crawl-status` endpoint를 제공합니다.
- repository에서 읽은 crawl 운영 상태를 Admin API response DTO로 반환합니다.

## 비소유 책임

- crawl worker 실행과 상태 쓰기는 `crawl_service`가 소유합니다.
- dashboard 렌더링은 `admin-frontend`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Data Types](data-types.md)
