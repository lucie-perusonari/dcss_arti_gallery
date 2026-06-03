# Harness 워크플로우

## 기본 흐름

1. 대상 프로젝트를 먼저 정합니다: `crawl_service`, `api`, `frontend`.
2. 해당 프로젝트의 최소 범위 코드와 테스트를 먼저 확인합니다.
3. 리포트/분석 노트/저장소 문서는 기본적으로 한국어로 작성하고, 코드 식별자·명령·API 필드·외부 제목·직접 인용문은 원문 유지.
4. 프로젝트 독립성을 지킵니다.
   - `crawl_service`: 원격 morgue source 저장, artifact read model 재생성, crawl 캐시 상태 소유
   - `api`: API 소유 DTO와 repository로 artifact를 읽음
   - `frontend`: Gallery API 응답만 사용
5. 프로젝트별 검증을 실행합니다. 계약 변경은 영향 받은 모든 프로젝트 게이트를 수행.

## 공통 작업면

- 크롤 원격 fetch: `crawl_service/morgue/`
- raw source 영속화 및 처리 상태: `crawl_service/repository.py`
- raw source에서 artifact read model 생성: `crawl_service/processor.py`
- 아티팩트 파싱/분류: `crawl_service/domain/artifacts/`
- 점수 계산: `crawl_service/domain/evaluation/`
- 문서 생성: `crawl_service/domain/documents/`
- 크롤 오케스트레이션: `crawl_service/worker.py`
- 갤러리 API: `api/`
- Mongo 생명주기 스크립트: `infra/mongo/`
- 프런트 갤러리: `frontend/`

## 검증

- 크로스 프로젝트 변경: `python3 -m unittest discover -s api/tests -t .`, `python3 -m unittest discover -s crawl_service/tests -t .`, `cd frontend && npm run build`
- API 전용 변경: `python3 -m unittest discover -s api/tests -t .`
- Crawl 전용 변경: `crawl_service/tests` 범위를 먼저 확인하고, 변경 범위가 넓으면 `python3 -m unittest discover -s crawl_service/tests -t .`
- 프런트 전용 변경: `cd frontend && npm run build`
