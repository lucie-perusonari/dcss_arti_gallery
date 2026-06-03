# 문서 인덱스

이 디렉터리는 모듈 문서로 가는 인덱스와 루트 수준 운영/harness 문서를 둡니다.
모듈별 실행 방법, 내부 구조, 타입, 처리 계층 문서는 각 모듈의 `README.md`와 `docs/`를 기준으로 봅니다.

## 모듈 문서

- [crawl_service README](../crawl_service/README.md)
- [crawl_service Reference](../crawl_service/docs/reference/processing-layers.md)
- [crawl_service Research](../crawl_service/docs/research/randart-corpus/README.md)
- [api README](../api/README.md)
- [api Reference](../api/docs/reference/processing-layers.md)
- [frontend README](../frontend/README.md)
- [frontend Reference](../frontend/docs/reference/processing-layers.md)
- [admin-frontend README](../admin-frontend/README.md)
- [admin-frontend Reference](../admin-frontend/docs/reference/processing-layers.md)

## 모듈 간 참고

- [Reference Index](./reference/README.md): 모듈별 reference 문서 링크

## 운영

운영 기준, 검증, 후속 작업처럼 수시로 바뀔 수 있는 root-level 문서입니다.

- [Harness Team Spec](./ops/harness/team-spec.md)
- [Harness Workflow](./ops/harness/workflow.md)
- [Harness Validation](./ops/harness/validation.md)
- [Harness Scenarios](./ops/harness/scenarios.md)
- [Backlog](./ops/backlog.md)
- [Memo](./ops/memo.md)

## 기준

- 특정 모듈만 설명하는 문서는 해당 모듈의 `docs/`에 둡니다.
- 두 개 이상의 모듈 계약은 [Reference Index](./reference/README.md)에서 관련 모듈 문서를 함께 링크합니다.
- 작업 방식, validation, agent routing 문서는 `docs/ops`에 둡니다.
- 실험과 재생성 가능한 분석 산출물은 해당 소유 모듈의 `docs/research`에 둡니다.
