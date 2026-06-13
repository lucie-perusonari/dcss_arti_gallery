# `tests/`

`tests/`는 `crawl_service`의 fetch, repository, worker 동작을 검증하는 테스트 모듈입니다.

## 책임

- remote morgue HTML parsing과 fetcher 동작을 검증합니다.
- repository의 raw/cache record 저장과 조회 동작을 검증합니다.
- worker orchestration, skip, failure 기록 동작을 검증합니다.

## 실행 정책

저장소 정책상 테스트는 사용자가 명시적으로 요청한 경우에만 실행합니다. 실행이 필요한 경우 README의 좁은 명령을 기준으로 합니다.

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```
