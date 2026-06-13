# `tests/test_mock_smoke.py`

`tests/test_mock_smoke.py`는 mock Admin API를 이용해 admin frontend를 확인하는 smoke test입니다.

## 책임

- Admin API 없이 dashboard가 status response를 소비할 수 있는지 확인하는 보조 흐름을 제공합니다.
- frontend dev/build 검증과 Admin API contract 확인 사이의 좁은 수동 점검 지점을 제공합니다.

## 실행 정책

저장소 정책상 테스트와 smoke test는 사용자가 명시적으로 요청한 경우에만 실행합니다.
