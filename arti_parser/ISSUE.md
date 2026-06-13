# arti_parser 이슈

## Canonical artifact 중복 제거

### 배경

현재 `artifacts` read model은 raw source에서 관측된 artifact occurrence를 거의 그대로
저장한다. artifact `id`는 `source file + line + name` 기반이므로, 같은 artifact가 여러
`.lst`/`.txt` snapshot에서 반복 관측되면 서로 다른 문서로 저장된다.

dev DB에서 v4 기준 raw file 12,000개를 처리했을 때 `artifacts`는 11,753개 생성되었다.
이 중 일부 artifact는 같은 player 아래에서 매우 많이 반복된다.

대표 사례:

- `the ring of Xom's Malicious Joy {rF+ rC+ rN+++ Int+3 Dex+3}`
- 총 174개 문서
- 158개는 `.lst`의 같은 상점 위치에서 반복 관측
- 16개는 `.txt` inventory에서 관측
- `.txt` 16개는 모두 `Game seed: 11579032504736784048 (custom seed)` 기반

즉 이 현상은 한 게임에서 같은 옵션의 artifact가 174번 생성된 것이 아니라, 같은 custom
seed 반복 플레이와 `.lst` snapshot 반복 관측이 겹쳐 생긴 read model 중복이다.

확인한 사실:

- `artifact.id` 중복은 없다.
- `raw_morgue_files.name` 중복은 없다.
- `raw_morgue_files.url` 중복은 없다.
- 중복은 source 저장 중복이 아니라 artifact identity 설계 문제다.

### 책임 경계

중복 제거는 Gallery API의 책임이 아니다. API는 `arti_parser`가 생성한 read model을 읽는
계층이므로 dedupe 정책을 직접 계산하지 않는다.

`arti_parser`가 해야 할 일:

- artifact occurrence에서 `canonical_key`를 생성한다.
- canonical 중복 제거용 read index를 생성하거나 갱신한다.
- 원본 source evidence는 보존한다.

API가 해야 할 일:

- 이미 생성된 canonical index 또는 canonical read model을 읽는다.
- API 내부에서 `canonical_key` 기준 dedupe 계산을 수행하지 않는다.

### 1차 설계안

기존 `artifacts` 문서를 바로 canonical 문서로 바꾸는 것은 변경 폭이 크다. 우선 occurrence
문서는 유지하고, 별도 canonical index 컬렉션을 두는 점진적 구조가 적절하다.

```text
artifacts
  - occurrence 문서 유지
  - id = source file + line 기반
  - canonical_key 추가

artifact_canonical_index
  - canonical_key unique
  - artifact_id: 대표 occurrence id
  - source_count
  - updated_at
```

이 구조의 장점:

- 기존 artifact occurrence와 source evidence를 잃지 않는다.
- `canonical_key` unique index와 bulk upsert로 중복 확인 쿼리를 줄일 수 있다.
- 중복 제거 책임은 `arti_parser`에 남는다.
- API/frontend 변경 폭을 줄일 수 있다.

### Canonical key 후보

초기 후보:

```text
player + normalized_name + base_item + sorted_random_attributes + item_location
```

고려 사항:

- `item_location`을 포함하면 같은 이름/옵션이 다른 위치에서 실제로 다시 생성된 경우를
  과도하게 합치지 않는다.
- `.txt` inventory는 `item_location`이 없는 경우가 많아 `.lst` shop occurrence와 바로
  합쳐지지 않을 수 있다.
- seed/run labeling을 도입하면 `.txt`와 `.lst`를 더 정확히 연결할 수 있지만, 1차 구현에는
  과하다.

### 대표 occurrence 선택 기준 후보

`artifact_canonical_index.artifact_id`는 canonical group을 대표하는 occurrence를 가리킨다.
대표 선택 기준은 후속 구현에서 확정한다.

후보:

- `evaluation.total`이 높은 문서
- `.txt` source 우선
- 최신 source 우선
- source evidence가 더 풍부한 문서 우선

### Stale 처리 필요성

같은 raw file을 재처리했을 때 이전 처리 결과에서만 나오던 artifact가 DB에 남으면 안 된다.
기존 occurrence 모델에서는 `source.file == raw_file.name`이면서 이번 artifact id 목록에 없는
문서를 삭제하면 됐다.

canonical index를 추가하면 stale 처리 시 다음도 함께 갱신해야 한다.

- 삭제되거나 변경된 occurrence가 대표 artifact였는지 확인
- 대표 artifact가 사라진 canonical group은 새 대표 occurrence를 선택
- source가 더 이상 없는 canonical group은 `artifact_canonical_index`에서 제거

### 후속 작업

- `ArtifactDocument`에 `canonical_key` 필드 추가
- `extractor.py` 또는 별도 helper에서 canonical key 생성
- `repository.py`에서 `artifact_canonical_index` bulk upsert 추가
- canonical key unique index 생성 스크립트 또는 infra 문서 추가
- stale 처리와 canonical index 재선정 로직 설계
- API repository가 canonical index를 읽는 방식 검토
- seed/run labeling은 2단계 작업으로 분리
