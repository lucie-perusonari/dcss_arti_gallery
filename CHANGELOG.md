# Changelog

## beta-v3-hotfix4 - 2026-06-18

### 요약

- player 식별자를 morgue 원문 파일명 기준 대소문자로 보존하도록 저장/조회 경로를 정리했습니다.
- 운영 MongoDB의 기존 player casing 데이터를 복구하는 마이그레이션 도구를 추가했습니다.
- crawl worker를 one-shot raw ingest job으로 단순화하고, crawl 실패 관측을 `crawl_errors` 이벤트 로그로 통합했습니다.

### 해결된 이슈

- Gallery API player 필터와 `arti_parser` read model 저장 경로가 player 값을 lowercase로 정규화해 원문 nickname 대소문자를 잃던 문제를 정리했습니다.
  - `raw_morgue_files`, `artifact_processing_files`, `artifacts.source`, `artifacts.sources`, `first_source`, `first_discovered_by`가 morgue 파일명에서 복원한 player casing을 사용할 수 있습니다.
  - 운영 적용 전 기존 문서를 감사하고, blocking risk가 없을 때만 적용하는 `infra/prod/migrate_player_casing.py`를 추가했습니다.
- crawl worker의 장기 loop, user/file cache 상태, failed raw placeholder 저장을 제거하고, one-shot job이 새 raw file과 실패 이벤트만 기록하도록 단순화했습니다.
- Admin API와 admin frontend의 crawl 상태 계약에서 제거된 `crawl_files`/`crawl_users` 집계와 `scannedAt` 표시를 정리했습니다.

### 운영 영향

- 운영 MongoDB에 player casing 마이그레이션이 필요합니다.
  - 적용 전 `raw_morgue_files`, `artifact_processing_files`, `artifacts` 백업을 생성해야 합니다.
  - dry-run audit에서 collision/blocking risk가 없어야 `--apply`를 실행합니다.
- 운영 compose pull 후 `mongo-indexes`, `api`, `admin-api`, `crawl-service` 관련 이미지는 새 코드 기준으로 갱신해야 합니다.
- crawler는 더 이상 `--once` 옵션을 받지 않고 기본 실행이 one-shot입니다.

### 검증

- 로컬 dev MongoDB에서 기존 player casing 백업을 별도 테스트 DB로 복사한 뒤 dry-run, apply, 재 dry-run을 수행했습니다.
  - dry-run 수정 대상: `raw_morgue_files` 91,110건, `artifact_processing_files` 1,468건, `artifacts` 47,690문서.
  - apply 후 수정 대상 0건과 collision/blocking risk 없음으로 수렴했습니다.
- Gallery API 테스트와 Admin API 테스트를 실행했습니다.
  - `python3 -m unittest discover -s api/tests -t .`
  - `python3 -m unittest discover -s admin_api/tests -t .`

## beta-v3-hotfix3 - 2026-06-17

### 요약

- 구버전 morgue에서 남는 무기 이름의 Gallery API/frontend 표시 fallback을 보강했습니다.
- Gallery frontend의 `명품` 필터를 제거했습니다.
- 구버전 무기 감사 기준과 릴리즈 기록 작성 기준을 문서화했습니다.

### 해결된 이슈

- `scythe`가 무기 하위 카테고리와 tile fallback에서 일반 fallback으로 떨어질 수 있던 문제를 정리했습니다.
  - API와 frontend 모두 `scythe`를 `polearms`로 분류합니다.
  - API와 frontend tile fallback은 알려지지 않은 `* sword` 계열 이름을 `long sword` tile/category 기준으로 표시합니다.
- `명품` 필터가 임시 기준과 타입별 예외를 유지해야 하던 부담을 제거했습니다.
  - frontend filter state, query 초기화, 버튼 UI, 타입 문서에서 `luxuryOnly`를 제거했습니다.

### 구현 메모

- parser read model schema 변경은 없습니다.
- `hammer`와 `scythe`는 구버전/특수 base item으로 보존해야 한다는 감사 기준을
  `.agents/skills/dcss-item-audit/references/equipment-reference.md`에 기록했습니다.
- `CHANGELOG.md`는 날짜별 릴리즈 섹션을 분리해 작성하도록 `AGENTS.md` 작업 규칙을 보강했습니다.

### 운영 영향

- MongoDB schema migration과 read model 재처리는 필요하지 않습니다.
- Gallery API와 Gallery frontend 정적 파일이 바뀌므로 운영 `api`와 `reverse-proxy` 이미지를 재빌드해 반영합니다.

### 알려진 이슈

- `barding` 계열 armour가 frontend/API fallback category에서 `boots`처럼 취급될 수 있습니다.
  - armour slot/category 계산에서 `barding`을 별도 하위 카테고리로 다룰지, boots 계열로 통합할지 후속 정리가 필요합니다.

### 검증

- 저장소 정책에 따라 로컬 테스트는 실행하지 않았습니다.
- 운영 배포 후 `https://perusonari.ddns.net/` HTTP 응답으로 smoke 확인합니다.

## beta-v3 - 2026-06-16

### 요약

- Gallery API와 frontend의 하위 카테고리 로딩 계약을 확장했습니다.
- Admin API가 최근 raw morgue 증가 여부로 crawl 진행 상태를 표시하도록 했습니다.
- artifact detail의 source/discovery 표시와 최상위 타입 필터 표시 순서를 정리했습니다.

### 해결된 이슈

- 전체 기간 또는 최근 30일 조회에서 특정 하위 카테고리의 artifact가 충분히 로드되지 않을 수 있던 문제를 해결했습니다.
  - Gallery API가 `displayCategory` query parameter와 `/filters.displayCategories`를 제공합니다.
  - frontend는 30일/전체 기간 모두 타입별 하위 카테고리마다 70개씩 artifact를 로드합니다.
  - 하위 필터 버튼은 `/filters.displayCategories`를 기준으로 만들기 때문에 DB에 존재하는 카테고리는 현재 로드된 목록 구성과 무관하게 표시됩니다.
- artifact detail의 발견 정보가 source 링크와 분리되어 읽기 어려웠던 문제를 정리했습니다.
  - `Found By @player datetime`과 `View original morgue.`를 하나의 source 묶음으로 표시합니다.
  - `@player`를 강조 표시하고, `Version`은 source 묶음 아래에 공백을 두고 별도 표시합니다.
- 최상위 타입 필터에서 `All`을 제거하고, 표시 순서를 `Weapon`, `Armour`, `Jewellery`, `Staff`, `Talisman`으로 고정했습니다.
- 명품 필터가 `weapon`, `armour` 외 타입을 모두 숨기던 문제를 완화했습니다.
  - `jewellery`, `staff`, `talisman`은 임시로 `score.total >= 45` 기준을 사용합니다.
  - 추후 타입별 명품 기준을 별도로 고도화해야 합니다.
- Gallery frontend의 talisman 하위 필터가 개별 talisman subtype을 길게 나열하던 문제를 정리했습니다.
  - Talisman 하위 필터는 form tier 단위로 표시합니다.
  - `spore talisman`은 Tier 2, `eel talisman`은 Tier 3, `talisman of death`는 Tier 5로 분류합니다.
  - `Recent 30d`와 `All time` 기간 필터를 하위 필터 아래 별도 구분선 섹션으로 이동했습니다.
- Admin API가 `crawlActive`를 제공해 crawl 진행 여부를 dashboard에서 확인할 수 있게 했습니다.

### 구현 메모

- 현재 `display_category` 저장 필드는 없습니다. API가 기존 `item_class`, `item_subtype`,
  `armour_slot`, `jewellery_slot`, `weapon_subtype`, `base_item`에서 fallback 계산합니다.
- 향후 read model에 `display_category`를 도입하면 API는 저장 필드를 우선 사용할 수 있습니다.
- `crawlActive`는 Admin API 프로세스가 관측한 `raw_morgue_files` 총 개수를 3분 이상 지난 샘플과 비교해 증가 여부로 계산합니다.

### 운영 영향

- MongoDB schema migration은 포함하지 않습니다.
- 기존 `artifacts` read model 재처리는 필요하지 않습니다.
- 운영 배포는 `beta-v3` tag 기준으로 prod compose stack을 재빌드해 반영합니다.
- Talisman 필터 hotfix는 frontend 정적 파일만 바뀌므로 운영 `reverse-proxy` 재빌드로 반영할 수 있습니다.

### 알려진 이슈

- `barding` 계열 armour가 frontend/API fallback category에서 `boots`처럼 취급될 수 있습니다.
  - armour slot/category 계산에서 `barding`을 별도 하위 카테고리로 다룰지, boots 계열로 통합할지 후속 정리가 필요합니다.

### 검증

- 로컬 dev compose stack에서 Gallery API `/filters`, `displayCategory` 조회, Admin API `/admin/crawl-status` smoke 확인을 수행했습니다.
- 프론트엔드 dev server HMR로 detail/source 표시와 타입 필터 변경을 확인했습니다.
- 2026-06-16 운영 서버에서 `reverse-proxy` production build와 컨테이너 재생성을 수행했고,
  `https://perusonari.ddns.net/` HTTP 200 응답을 확인했습니다.

## beta-v2 - 2026-06-16

### 요약

- 운영 서버에 `beta-v2`를 배포하고, 갤러리에 표시되면 안 되는 운영 read model 문서를 정리했습니다.
- `hammer`와 `scythe` 삭제 기준을 정정하고, 관련 raw file 재처리로 잘못 삭제된 문서를 복구했습니다.

### 해결된 이슈

- beta-v2 운영 데이터에서 갤러리에 표시되면 안 되는 read model 문서를 정리했습니다.
  - `item_class: "unknown"`으로 분류된 문서 13개를 삭제했습니다.
  - parser의 `UNRANDART_NAME_KEYS`와 같은 normalized name key 기준으로 고정 아티팩트 159개를 삭제했습니다.
  - `hand crossbow`, `hunting sling`, `large shield`, `blowgun`, `fustibalus`, `sabre`, `cutlass`,
    `bow`, `crossbow`, 구버전 `dragon armour` 표기처럼 현행 장비 기준에서 제외할 구버전 base item 문서를 삭제했습니다.
  - `hammer`와 `scythe`는 각각 `mace`, `halberd` 계열로 취급해야 하므로 구버전 삭제 대상에서 제외하도록 정정했습니다.
  - 잘못 삭제된 `hammer`/`scythe` 문서를 복구하기 위해 관련 raw file 4,004개를 `arti-parser`로 재처리했고,
    재처리 후 되살아난 실제 구버전 제외 대상 19개를 다시 삭제했습니다.

### 운영 영향

- 운영 `artifacts` read model을 수동 정리한 경우, raw file을 강제 재처리하면 삭제한 문서가 다시 생성될 수 있습니다.
  parser 제외 규칙이 반영되기 전에는 재처리 후 운영 데이터 정리 쿼리를 다시 적용해야 합니다.

### 검증

- 2026-06-16 운영 서버 beta-v2 배포 후 데이터 정리를 수행했습니다.
  - `beta-v2` tag 기준 서버 repository 갱신과 `infra/prod/docker-compose.yml` 재빌드를 완료했습니다.
  - `item_class: "unknown"` 문서 13개, 고정 아티팩트 159개, 구버전 base item 문서 1,601개를 삭제했습니다.
  - 이후 `hammer`/`scythe` 삭제 기준을 정정하고 관련 raw file 4,004개를 재처리했습니다.
  - 재처리 후 `hammer` 1,388개와 `scythe` 20개가 read model에 남아 있음을 확인했습니다.
  - 재처리로 되살아난 실제 구버전 제외 대상 19개를 다시 삭제했고, `hand crossbow`/`hunting sling` 잔여 0개를 확인했습니다.

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

- 장비 기준 문서에 게임 참고 정보와 `arti_parser` 정책이 섞여 있던 문제를 정리했습니다.
  - DCSS 장비, morgue brand alias, Ashenzari curse group 같은 게임 정보는 equipment reference에 남겼습니다.
  - parser 소유 분류, 후보 제외, brand alias 처리 정책은 `arti_parser/docs/classifier.md`에 반영했습니다.
  - attribute 필드 계약과 Ashenzari `ignored_attributes` 보존 규칙은 `arti_parser/docs/models.md`에 반영했습니다.
  - weapon stat과 최저 공격 delay 기준은 `arti_parser/docs/evaluator.md`에 반영했습니다.

### 추가된 기능

- Admin API에서 crawl 처리 상태를 조회할 수 있는 repository 흐름을 추가했습니다.
- DCSS item 검수용 에이전트 스킬과 Ashenzari morgue token 참고 자료를 추가했습니다.
- DCSS 장비와 morgue 표기 참고 정보는 `.agents/skills/dcss-item-audit/references/equipment-reference.md`에 남기고,
  parser 소유 분류/속성/평가 정책은 `arti_parser/docs/`의 모듈 문서에 반영했습니다.
- Gallery API 응답에 `allAttributes`, `baseAttributes`, `discovery`를 추가했습니다.

### 운영 영향

- MongoDB schema migration은 포함하지 않습니다.
- live morgue crawl 재실행은 포함하지 않습니다.
- 기존 raw morgue 원본은 그대로 사용할 수 있습니다.
- 변경된 parsing/classification 결과를 `artifacts` read model에 반영하려면 `arti_parser` 재처리가 필요합니다.
- 저장 metadata가 바뀌어 `artifact_processing_files.metadata_version` 기준 재처리 대상이 늘어날 수 있습니다.
- 프론트엔드 배포 시 새 equipment tile 자산 경로가 함께 배포되어야 합니다.
- 서비스 실행은 개별 서비스 `.sh`가 아니라 `infra/dev` 또는 `infra/prod`의 compose 경로를 기준으로 합니다.
- 서비스 검증도 `infra/dev` 또는 `infra/prod` compose 경로를 기준으로 합니다.
- reverse proxy에서는 Gallery API의 `/api/metrics`, `/api/docs`, `/api/redoc`, `/api/openapi.json` 외부 노출
  차단 정책을 확인해야 합니다.
- Admin API 배포 환경에서는 `PROMETHEUS_URL`, `PROMETHEUS_TIMEOUT_SECONDS`,
  `PROMETHEUS_METRICS_WINDOW_SECONDS` 값을 확인해야 합니다.

### 알려진 이슈

- beta 단계이므로 DCSS 버전별 오래된 morgue 표현과 일부 edge case artifact token은 추가 검수가 필요할 수 있습니다.
- parser/scoring 결과는 원본 raw morgue 재처리 여부에 따라 기존 read model과 일시적으로 다를 수 있습니다.
- API 테스트에서 기존 `MongoClient` ResourceWarning이 출력될 수 있지만 테스트는 정상 종료됩니다.

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
