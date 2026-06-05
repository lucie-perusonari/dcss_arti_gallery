# Harness 검증 가이드

## 검증 명령

이 문서는 이 저장소의 표준 게이트입니다.

| 구분 | 명령 |
| --- | --- |
| API 테스트 | `python3 -m unittest discover -s api/tests -t .` |
| Crawl service 테스트 | `python3 -m unittest discover -s crawl_service/tests -t .` |
| 프런트엔드 빌드 | `cd frontend && npm run build` |

주의:

- Python 테스트는 FastAPI/Starlette의 `TestClient` deprecation 경고(예: `httpx`)가 나올 수 있습니다.
- Mongo 기반 테스트는 `MongoClient.close()`의 `ResourceWarning`이 보일 수 있습니다.

## 표준 검증 매트릭스

| 변경 영역 | 최소 검증 |
| --- | --- |
| Crawl service 원격 fetch | `python3 -m unittest discover -s crawl_service/tests/morgue -t .` |
| Crawl service artifact domain | `python3 -m unittest discover -s crawl_service/tests/domain/artifacts -t .` |
| Crawl service scoring | `python3 -m unittest discover -s crawl_service/tests/domain/evaluation -t .` 및 `crawl_service/docs/ko/artifact_scoring_formula.md` 대조 |
| Crawl service 문서/쓰기 흐름 | `python3 -m unittest discover -s crawl_service/tests/domain/documents -t .` 및 `python3 -m unittest discover -s crawl_service/tests -t .` |
| Gallery API read 계약 | `python3 -m unittest discover -s api/tests -t .` |
| Frontend UI/API client | `cd frontend && npm run build` |
| 크로스 프로젝트 변경 | `python3 -m unittest discover -s api/tests -t .`, `python3 -m unittest discover -s crawl_service/tests -t .`, `cd frontend && npm run build` |

## 선택적 통합 확인

네트워크 또는 end-to-end 동작이 필요한 경우에만 아래를 사용합니다.

```sh
eval "$(infra/mongo/mongo_up.sh)"
python3 -m crawl_service.worker
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
cd frontend
VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

프런트엔드만 mock으로 볼 때는:

```sh
./scripts/run_frontend.sh
```

## 품질 게이트

- `api`는 `crawl_service`를 import할 수 없습니다.
- API 필드 변경은 `api.models`, FastAPI 응답, 프런트의 TypeScript 타입, UI 사용 지점을 함께 확인합니다.
- Crawl worker/document 변경은 `crawl_service.worker`, `crawl_service.domain.documents`, `crawl_service.repository`, API DTO 호환성까지 교차 확인합니다.
- 점수 변경은 random 속성만 반영되는지, base 아이템 처리까지 포함되는지 반드시 문서화합니다.
- 네트워크 노출 변경은 사용자 요청이 있거나 mock으로 대체할 수 없을 때만 실제 네트워크 동작으로 검증합니다.
- TODO: 저장소에는 아직 formatter, linter, 커버리지 임계값, CI 구성, 배포 게이트가 없습니다.
