# `tests/`

`tests/`는 Admin API 응답 계약과 MongoDB 읽기 동작을 검증합니다.

## 책임

- `/admin/crawl-status` 응답 shape를 검증합니다.
- repository가 crawl 상태 컬렉션을 읽어 dashboard 요약을 만드는지 확인합니다.
- 테스트용 MongoDB 준비 helper를 제공합니다.

## 실행 정책

저장소 정책상 테스트는 사용자가 명시적으로 요청한 경우에만 실행합니다.

```sh
python3 -m unittest discover -s admin_api/tests -t .
```
