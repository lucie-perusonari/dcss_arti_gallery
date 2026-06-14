# Changelog

## beta - 2026-06-15

### 요약

- 갤러리 프론트엔드를 mock 데이터 중심 구조에서 Gallery API 기반 표시 흐름으로 전환했습니다.
- artifact 분류와 표시 계약을 보강해 무기, unrand, 하위 장비 분류, 발견 정보 표시의 누락 가능성을 줄였습니다.
- Admin API와 운영 문서를 정리해 crawl 처리 상태와 compose 기반 실행 경로를 더 일관되게 확인할 수 있게 했습니다.

### 해결된 이슈

- 악세서리 artifact에서 원본 아이템 속성이 UI 표시 데이터에서 생략되던 문제를 해결했습니다.
  - jewellery base item의 intrinsic 속성은 `baseAttributes`로 유지합니다.
  - 상세 설명에는 `[ring of protection from fire]`처럼 bracket subtype을 표시합니다.
  - 속성 요약에는 원본 속성과 랜덤 속성을 포함한 표시 대상 속성을 출력합니다.

- 카드 `token-row`에 일부 속성명만 출력되던 문제를 해결했습니다.
  - API 응답에 `allAttributes`를 추가했습니다.
  - `frontend`는 `randomAttributes.slice(0, 4)` 대신 `allAttributes` 전체를 렌더링합니다.
  - Ashenzari skill boost처럼 artifact 고유 속성이 아닌 값은 표시 대상에서 제외합니다.

- 상세 팝업 하단에 발견 version과 datetime이 표시되지 않던 문제를 해결했습니다.
  - `arti_parser`가 morgue source evidence에 version metadata를 저장합니다.
  - API 응답에 최초 발견 source 기준 `discovery.version`, `discovery.datetime`을 추가했습니다.
  - `frontend` 상세 팝업 하단에 발견 정보를 표시합니다.

- 갤러리 UI가 mock artifact 데이터에 의존해 실제 API 응답과 표시 계약이 어긋날 수 있던 문제를 해결했습니다.
  - `frontend`가 Gallery API 응답을 직접 사용하도록 정리했습니다.
  - 프론트엔드 데이터 타입과 API 문서를 실제 응답 구조에 맞게 갱신했습니다.

- 갤러리 필터에서 일부 하위 장비 분류와 발견 정보가 충분히 드러나지 않던 문제를 해결했습니다.
  - 하위 필터 처리와 발견 정보 표시를 보강했습니다.
  - 관련 프론트엔드 타입과 컴포넌트 문서를 갱신했습니다.

- randart와 unrand 아이템의 tile 경로가 단순 파일명 또는 임시 randart 경로에 의존하던 문제를 해결했습니다.
  - 장비 tile 자산을 `frontend/public/tiles/equipment/` 아래로 정리했습니다.
  - API 응답의 tile 경로와 프론트엔드 tile 매핑을 equipment 자산 구조에 맞췄습니다.
  - 무기 tile 매핑을 보강해 더 많은 무기 base item이 실제 tile로 표시되도록 했습니다.

- 일부 unrand 이름이 parser alias에 걸리지 않아 분류나 표시가 흔들릴 수 있던 문제를 해결했습니다.
  - unrand 이름 alias를 보강했습니다.

- 고정 아티팩트, `cursed`/`chaotic` prefix, 구버전 또는 변종 버전 데이터가 정상 randart와 같은 경로로 처리될 수 있던 문제를 해결했습니다.
  - 고정 아티팩트는 저장 대상에서 제외합니다.
  - `cursed` randart는 저장하되 표시 이름에서 prefix를 제거합니다.
  - randart가 아닌 `cursed`/`chaotic` 아이템은 저장하지 않습니다.
  - DCSS `0.29` 이상 정식 release와 trunk만 처리하고, 변종 suffix가 있는 morgue는 artifact 0개 처리 완료로 기록합니다.

- `cursed` 아이템에서 Ashenzari skill boost가 artifact 속성처럼 노출되던 문제를 해결했습니다.
  - Ashenzari skill boost는 `ignored_attributes` metadata로만 보존합니다.
  - `allAttributes`, `baseAttributes`, `randomAttributes`, evaluation 입력, UI `token-row`에는 포함하지 않습니다.

- artifact 문서에서 분류 계약이 충분히 명확하지 않아 API와 프론트엔드가 item type을 안정적으로 소비하기 어려운 문제를 해결했습니다.
  - `arti_parser`의 classifier, extractor, parser, model 흐름을 보강했습니다.
  - API 데이터 타입 문서에 artifact 분류 계약을 반영했습니다.

- Admin frontend가 API fallback 값을 사용할 수 있어 실제 운영 상태와 다른 값을 보여줄 수 있던 문제를 해결했습니다.
  - Admin frontend의 상태 API fallback을 제거했습니다.

- 개발 환경 MongoDB 기본값이 서비스별로 어긋날 수 있던 문제를 해결했습니다.
  - `crawl_service`, `arti_parser`, `infra`의 개발 MongoDB 기본값을 정리했습니다.

- production frontend Docker build에서 install 명령이 workspace lockfile 흐름과 맞지 않을 수 있던 문제를 해결했습니다.
  - `infra/prod`의 frontend, admin frontend Dockerfile install 명령을 조정했습니다.

- 서비스별 실행 스크립트와 문서가 compose 기반 실행 경로와 중복되던 문제를 해결했습니다.
  - 서비스 루트의 개별 실행 `.sh`와 관련 상세 문서를 제거하고, 실행 기준을 compose 문서로 통일했습니다.

### 추가된 기능

- Admin API에서 crawl 처리 상태를 조회할 수 있는 repository 흐름을 추가했습니다.
- DCSS item 검수용 에이전트 스킬과 Ashenzari morgue token 참고 자료를 추가했습니다.
- `EQUIPS.md`를 추가해 장비 속성과 artifact token 검수 기준을 문서화했습니다.
- Gallery API 응답에 `allAttributes`, `baseAttributes`, `discovery`를 추가했습니다.

### 운영 영향

- MongoDB schema migration은 포함하지 않습니다.
- live morgue crawl 재실행은 포함하지 않습니다.
- 기존 raw morgue 원본은 그대로 사용할 수 있습니다.
- 변경된 parsing/classification 결과를 `artifacts` read model에 반영하려면 `arti_parser` 재처리가 필요합니다.
- 저장 metadata가 바뀌어 `artifact_processing_files.metadata_version` 기준 재처리 대상이 늘어날 수 있습니다.
- 프론트엔드 배포 시 새 equipment tile 자산 경로가 함께 배포되어야 합니다.
- 서비스 실행은 개별 서비스 `.sh`가 아니라 `infra/dev` 또는 `infra/prod`의 compose 경로를 기준으로 합니다.

### 알려진 이슈

- beta 단계이므로 DCSS 버전별 오래된 morgue 표현과 일부 edge case artifact token은 추가 검수가 필요할 수 있습니다.
- parser/scoring 결과는 원본 raw morgue 재처리 여부에 따라 기존 read model과 일시적으로 다를 수 있습니다.

### 검증

- 2026-06-15 dev compose 통합 검증을 통과했습니다.
  - `docker compose -f infra/dev/docker-compose.yml up -d --force-recreate`
  - `docker compose -f infra/dev/docker-compose.yml ps`
  - `python -m arti_parser.batch --once --limit 20000 --scan-batch-size 2000`: `20000 raw files seen`, `20000 processed`, `0 failed`
  - `artifact_processing_files` failed record 확인: `0`
  - Gallery API, Admin API, frontend, admin frontend, Prometheus, Grafana endpoint smoke 확인
  - `docker compose -f infra/dev/docker-compose.yml exec -T api python -m unittest discover -s api/tests -t .`
  - `docker compose -f infra/dev/docker-compose.yml exec -T admin-api python -m unittest discover -s admin_api/tests -t .`
  - `docker compose -f infra/dev/docker-compose.yml exec -T api python -m unittest discover -s arti_parser/tests -t .`
  - `docker compose -f infra/dev/docker-compose.yml exec -T api python -m unittest discover -s crawl_service/tests -t .`
  - `npm run build` in `frontend/`
  - `npm run build` in `admin-frontend/`
- `admin-frontend` build 전 로컬 `node_modules`가 비어 있어 `npm install`로 의존성을 복원했습니다. lockfile 변경은 없습니다.
- API 테스트에서 기존 `MongoClient` ResourceWarning이 출력됐지만 테스트는 `OK`로 종료됐습니다.
- 커밋 범위: `origin/feature/frontend-gallery-api..feature/frontend-gallery-api`
