# `tests/`

`tests/`는 Gallery API 응답 계약과 read-only repository 동작을 검증합니다.

## 책임

- API 응답이 frontend `Artifact` 계약에 필요한 필드를 노출하는지 확인합니다.
- repository가 `artifacts` read model을 읽기 전용으로 사용하는지 확인합니다.

## 실행 정책

저장소 정책상 테스트는 사용자가 명시적으로 요청한 경우에만 실행합니다.

```sh
python3 -m unittest discover -s api/tests -t .
```
