# Harness 시나리오

이 문서는 요청별로 적절한 하위 작업 라우팅이 되는지 점검하는 시나리오입니다.

## 정상 흐름: 크로스 레이어 크롤 지속성 변경

프롬프트 예시:

```text
원격 morgue 파일은 먼저 raw_morgue_files에 저장하고, artifact는 저장된 raw에서 재생성한 뒤 갤러리는 API 서버를 통해 read model을 읽도록 바꿔달라.
```

기대 라우팅:

- `dcss-pipeline-orchestrator`부터 시작
- `bugfix`로 repository/API/crawl/frontend 변경 처리
- 테스트 보강이 필요하면 `test-generation`
- 계약 위험이 남으면 `code-review`

예상 산출물:

- `_workspace/handoffs/YYYYMMDD-HHMM-crawl-persistence-analysis.md`가 필요 시 추가
- `raw_morgue_files` 기반 재생성 원칙 유지한 코드 변경
- 변경된 `crawl_service`, `api`, `frontend` 테스트/빌드 결과

합격 조건:

- frontend는 crawl_service를 직접 호출하지 않는다.
- API가 persisted artifact를 repository에서 읽어 반환한다.
- raw source는 `raw_morgue_files`에 저장되고, artifact는 처리 단계에서 생성된다.
- fetch 실패와 processing 실패 상태가 분리된다.
- 점수/회귀 테스트가 새 경로를 덮는다.

## 정상 흐름: WebTiles 상세 UI 변경

프롬프트 예시:

```text
아이템 상세 패널에서 랜덤 속성이 모바일에서 줄임없이 모두 보이되 WebTiles 룩은 유지되도록 바꿔달라.
```

기대 라우팅:

- `webtiles-ui` 우선 사용
- API 계약/타입 변경이 필요할 때만 `bugfix` 추가

예상 산출물:

- 프런트엔드 코드/CSS 변경
- `cd frontend && npm run build`
- 레이아웃 충실도 위험이 크면 스크린샷 또는 수기 점검 노트 추가

합격 조건:

- 첫 화면은 바로 갤러리 사용 가능 상태여야 한다.
- 상세 문구는 `dcssDescription` 또는 `rawDescription`에서 온다.
- DCSS WebTiles 밀도와 타일 사용을 깨는 장식적 대체가 없어야 한다.

## 예외 흐름: 라이브 크롤 접근 불가

프롬프트 예시:

```text
공개 morgue archive에 대한 실제 라이브 크롤 동작을 검증해달라.
```

기대 라우팅:

- `dcss-pipeline-orchestrator` 후 `bugfix` 또는 직접 검증 분기
- 라이브 네트워크 접근이 안 되거나 필수가 아니면 mock/fixture로 대체하고 생략 사유를 명시

예상 산출물:

- Mock 기반 검증과 live 검증 분리를 명확히 기술한 노트
- 점수/코드 변경은 실제 재현된 실패가 있을 때만 수행

합격 조건:

- 크롤 결과를 임의로 만들지 않는다.
- live 수행 여부를 명시하고, 실행 불가 시 필요한 실행 명령을 함께 기재한다.

## 근접 실패: 리뷰만 요청

프롬프트 예시:

```text
릴리즈 전에 이 diff를 리뷰해줄래?
```

기대 라우팅:

- `code-review`만 수행
- 리뷰 후 수정 요청만 제시하고 코드 수정은 즉시 하지 않음

합격 조건:

- 결과는 발견사항(이슈) 중심으로 제시
- 파일/라인 근거를 포함
- 리뷰 중 코드 변경 없음
