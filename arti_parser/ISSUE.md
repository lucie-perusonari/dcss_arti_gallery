# arti_parser 이슈

## Canonical artifact 중복 제거

상태: 해결됨.

`arti_parser`가 source 위치 기반 occurrence identity와 artifact signature 기반 canonical
identity를 분리해 `artifacts` read model을 생성하도록 변경했다. API와 frontend는 별도
dedupe 계산 없이 canonical read model을 그대로 읽는다.

추가로, 통합 확인 중 `the +0 pair of fencer's gloves {Riposte Dex+3}`가 랜다트로 저장되는
문제를 발견해 unrandart 이름 데이터를 CrawlWiki 상세 페이지의 실제 게임 표기 기준으로
정정했다. 이 변경은 canonical dedupe와 별개의 parser 입력 데이터 보정이지만, 같은 read model
재생성 시 반영되어야 하므로 parser version을 올려 재처리 대상이 되게 했다.

### 배경

현재 `artifacts` read model은 raw source에서 관측된 artifact occurrence를 거의 그대로
저장한다. artifact `id`는 `source file + line + name` 기반이므로, 같은 artifact가 여러
`.lst`/`.txt` snapshot에서 반복 관측되면 서로 다른 문서로 저장된다.

dev DB에서 v4 기준 raw file 12,000개를 처리했을 때 `artifacts`는 11,753개 생성되었다.
이 중 일부 artifact는 여러 raw snapshot에서 매우 많이 반복된다.

대표 사례:

- `the ring of Xom's Malicious Joy {rF+ rC+ rN+++ Int+3 Dex+3}`
- 총 174개 문서
- 158개는 `.lst`의 같은 상점 위치에서 반복 관측
- 16개는 `.txt` inventory에서 관측
- `.txt` 16개는 모두 `Game seed: 11579032504736784048 (custom seed)` 기반

즉 이 현상은 같은 옵션의 artifact가 174번 별개로 수집할 가치가 있다는 뜻이 아니라,
동일한 artifact signature가 `.lst` snapshot과 `.txt` inventory에서 반복 관측되어 gallery
read model에 중복 노출된 것이다.

확인한 사실:

- `artifact.id` 중복은 없다.
- `raw_morgue_files.name` 중복은 없다.
- `raw_morgue_files.url` 중복은 없다.
- 중복은 source 저장 중복이 아니라 artifact identity 설계 문제다.
- raw source는 관측 evidence이므로 중복처럼 보여도 보존한다.

### 책임 경계

중복 제거는 Gallery API의 책임이 아니다. API는 `arti_parser`가 생성한 read model을 읽는
계층이므로 dedupe 정책을 직접 계산하지 않는다.

`arti_parser`가 해야 할 일:

- artifact occurrence에서 `canonical_key`를 생성한다.
- canonical 중복 제거용 read model을 생성하거나 갱신한다.
- 원본 source evidence는 보존한다.

API가 해야 할 일:

- 이미 생성된 canonical read model을 읽는다.
- API 내부에서 `canonical_key` 기준 dedupe 계산을 수행하지 않는다.

### Identity 정책

현재 occurrence id와 이후 canonical id의 의미를 분리한다.

```text
현재 occurrence id
  - source file + line + name 기반
  - raw source의 특정 위치에서 관측된 한 번의 등장
  - source evidence와 stale 처리에 사용

이후 canonical artifact id
  - normalized artifact signature 기반
  - 유저가 실제로 발견할 수 있었던 동일 랜다트 자체
  - Gallery/API가 중복 없이 노출할 public id
```

`player`, `seed`, `source.file`, `source.url`, `line`, `item_location`, `item_source`는
canonical identity에 넣지 않는다. 이 값들은 artifact 자체의 정체성이 아니라 발견자, 출처,
위치, seed 보강 정보 같은 source evidence metadata로 누적한다.

이 정책은 같은 artifact signature가 다른 seed/run에서 우연히 다시 관측되더라도 하나의
canonical artifact로 합친다. 이 프로젝트의 목적은 개별 run 재현이 아니라 실제로 발견
가능했던 랜다트 catalog를 만드는 것이므로, seed는 필수 identity가 아니라 나중에 보강 가능한
metadata로 취급한다.

### 구현 기준

`artifacts` 컬렉션은 Gallery/API가 읽는 canonical read model로 사용한다. raw source의
occurrence identity는 `occurrence_id`와 `sources` evidence로 보존한다.

```text
artifacts
  - id: canonical_key hash
  - canonical_key unique
  - occurrence_id: 대표 occurrence id
  - source: 대표 occurrence metadata
  - occurrence_ids
  - sources
  - source_count
  - first_discovered_by
  - first_source
  - known_seeds
  - updated_at
```

이 구조의 장점:

- 기존 artifact occurrence와 source evidence를 잃지 않는다.
- `id`/`canonical_key` unique index와 upsert로 canonical 중복 저장을 막을 수 있다.
- 중복 제거 책임은 `arti_parser`에 남는다.
- API/frontend는 dedupe를 계산하지 않고 canonical read model을 읽는다.
- 대표 occurrence가 바뀌어도 API public id는 stable하게 유지된다.

### Canonical key

canonical key는 source metadata를 제외한 artifact signature만 사용한다.

```text
normalized_name
+ base_item
+ enchantment
+ brand
+ item_class
+ item_subtype
+ sorted_random_attributes
```

고려 사항:

- `random_attributes`는 base intrinsic 속성을 제외한 실제 randart property만 사용한다.
- `sorted_random_attributes`는 파싱 순서 차이가 key를 흔들지 않도록 정렬한다.
- `base_attributes`는 base item의 intrinsic 성질이므로 canonical identity에 넣지 않는다.
- `item_location`을 넣으면 `.txt` inventory와 `.lst` shop occurrence가 같은 artifact라도
  갈라질 수 있으므로 제외한다.
- `player`와 `seed`는 발견 evidence로 보존하되 canonical identity에는 넣지 않는다.

### 대표 occurrence 선택 기준 후보

canonical artifact의 `occurrence_id`와 `source`는 대표 occurrence를 가리킨다.

현재 기준:

- `.txt` source 우선
- source evidence가 더 풍부한 문서 우선
- `evaluation.total`이 높은 문서 우선

대표 occurrence가 바뀌어도 canonical id는 바뀌지 않아야 한다. API/frontend에 노출하는 public
id는 occurrence id가 아니라 canonical key hash를 사용한다.

### Stale 처리 필요성

같은 raw file을 재처리했을 때 이전 처리 결과에서만 나오던 artifact가 DB에 남으면 안 된다.
기존 occurrence 모델에서는 `source.file == raw_file.name`이면서 이번 artifact id 목록에 없는
문서를 삭제하면 됐다.

canonical artifact를 저장하면 stale 처리 시 다음도 함께 갱신해야 한다.

- 삭제되거나 변경된 occurrence가 대표 artifact였는지 확인
- 대표 artifact가 사라진 canonical group은 새 대표 occurrence를 선택
- source가 더 이상 없는 canonical artifact는 `artifacts`에서 제거
- source evidence 목록이나 count가 재처리 시 중복 누적되지 않도록 occurrence id 기준으로
  idempotent하게 갱신한다.

### 적용 작업

- 완료: `ArtifactDocument`에 `canonical_key` 필드 추가
- 완료: `ArtifactDocument`에 source 위치 기반 `occurrence_id` 필드 추가
- 완료: `extractor.py`에서 source metadata를 제외한 canonical key 생성
- 완료: `repository.py`에서 canonical `artifacts` upsert와 `sources` evidence 병합 추가
- 완료: canonical key unique index를 `infra/ensure_mongo_indexes.py`와 infra 문서에 추가
- 완료: source evidence shape 설계 및 저장: `first_discovered_by`, `first_source`, `source_count`, `occurrence_ids`, `sources`, `known_seeds`
- 완료: stale source evidence 삭제, source count 갱신, source가 없는 canonical artifact 삭제
- 완료: 대표 occurrence가 stale 처리로 사라지면 남은 source evidence에서 대표 source 재선정
- 완료: API repository가 canonical `artifacts`를 읽고 `sources.player`까지 player filter 대상으로 사용
- 분리: seed/run labeling은 필수 identity가 아니라 source evidence 보강 작업이므로 이번 해결 범위에서 제외

### 검증 기록

- 실제 dev MongoDB의 raw `.lst` 두 개에서 같은 `the +0 pair of fencer's gloves {Riposte Dex+3}`
  occurrence가 canonical id 하나로 합쳐지는 것을 확인했다.
- 이후 해당 아이템이 fixed artefact임을 확인하고 unrandart 이름 데이터를 실제 표기
  `pair of fencer's gloves`로 보정했다.
- 같은 raw 두 개를 재처리했을 때 `fencer` artifact가 저장되지 않고, 임의 랜다트 후보
  `the +0 pair of gloves {Str+3}`는 계속 randart로 판정되는 것을 확인했다.
