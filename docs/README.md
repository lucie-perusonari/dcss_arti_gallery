# 문서 인덱스

이 디렉터리는 모듈 문서로 가는 인덱스와 루트 수준 운영/harness 문서를 둡니다.
모듈별 실행 방법, 내부 구조, 타입, 처리 계층 문서는 각 모듈의 `README.md`와 `docs/`를 기준으로 봅니다.
`docs/ops`는 작업용 문서이므로 영어 대응 문서를 따로 두지 않습니다.

English version: [README.en.md](README.en.md)

## 모듈 문서

- [crawl_service README](../crawl_service/README.md)
- [crawl_service Docs](../crawl_service/docs/ko/processing-layers.md)
- [crawl_service Research](../crawl_service/docs/ko/research/randart-corpus/README.md)
- [api README](../api/README.md)
- [api Docs](../api/docs/ko/processing-layers.md)
- [frontend README](../frontend/README.md)
- [frontend Docs](../frontend/docs/ko/processing-layers.md)
- [admin-frontend README](../admin-frontend/README.md)
- [admin-frontend Docs](../admin-frontend/docs/ko/processing-layers.md)

## 모듈 간 참고

상세 문서는 각 모듈 `docs/ko`에 둡니다.
두 개 이상의 모듈을 함께 바꾸는 작업에서는 관련 모듈 문서를 모두 확인합니다.

### Crawl Service

- [Processing Layers](../crawl_service/docs/ko/processing-layers.md)
- [Data Types](../crawl_service/docs/ko/data-types.md)
- [Artifact Scoring Formula](../crawl_service/docs/ko/artifact_scoring_formula.md)
- [Randart Properties](../crawl_service/docs/ko/randart_properties.md)
- [DCSS Item Data](../crawl_service/docs/ko/dcss_item_data.md)

### API

- [Processing Layers](../api/docs/ko/processing-layers.md)
- [Data Types](../api/docs/ko/data-types.md)

### Frontend

- [Processing Layers](../frontend/docs/ko/processing-layers.md)
- [Data Types](../frontend/docs/ko/data-types.md)

### Admin Frontend

- [Processing Layers](../admin-frontend/docs/ko/processing-layers.md)
- [Data Types](../admin-frontend/docs/ko/data-types.md)

## 운영

운영 기준, 검증, 후속 작업처럼 수시로 바뀔 수 있는 root-level 문서입니다.

- [Harness Team Spec](ops/harness/team-spec.md)
- [Harness Workflow](ops/harness/workflow.md)
- [Harness Validation](ops/harness/validation.md)
- [Harness Scenarios](ops/harness/scenarios.md)
- [Backlog](ops/backlog.md)
- [Memo](ops/memo.md)

## 빠른 검증 명령

```sh
python3 -m unittest discover -s api/tests -t .
python3 -m unittest discover -s crawl_service/tests -t .
cd frontend && npm run build
cd admin-frontend && npm run build
```

범위별 검증 조합은 [Harness Validation](ops/harness/validation.md)을 기준으로 합니다.

## 기준

- 특정 모듈만 설명하는 문서는 해당 모듈의 `docs/`에 둡니다.
- 두 개 이상의 모듈 계약은 위의 모듈 간 참고 목록에서 관련 모듈 문서를 함께 링크합니다.
- 작업 방식, validation, agent routing 문서는 `docs/ops`에 두고 한국어로만 관리합니다.
- 실험과 재생성 가능한 분석 산출물은 해당 소유 모듈의 언어별 `docs/{ko,en}/research`에 둡니다.
