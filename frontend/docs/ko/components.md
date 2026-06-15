# `src/components`

`src/components`는 WebTiles 스타일 gallery UI를 구성하는 React component 계층입니다.

## 책임

- artifact card, detail panel, filter bar, shell layout을 렌더링합니다.
- `ArtifactCard`의 `token-row`는 Gallery API의 `allAttributes` 전체를 한 줄 압축/ellipsis로 표시합니다.
- `DcssItemDescription`에서 DCSS/WebTiles 아이템 설명창 표현을 유지합니다.
- `DcssItemDescription`은 상세 팝업 하단에 최초 발견 version/datetime을 표시합니다.
- 플레이어 입력 UI는 `player` 필터를 갱신해 Gallery API에서 해당 플레이어의 저장된 랜다트를 불러옵니다.
- `FilterBar`는 type segmented control과 type별 하위 slot/subtype segmented control을 렌더링합니다.
- `FilterBar`는 기본 최근 30일과 전체 기간을 전환하는 `timeRange` control도 렌더링합니다.
- 하위 slot/subtype 옵션은 Gallery API의 `/filters.displayCategories` 메타데이터에서 계산하고,
  실제 표시 목록만 slot으로 필터링합니다. 장신구 하위 필터는 `Ring`과 `Amulet`만 표시합니다.

## UI 기준

아이템 상세 패널과 WebTiles 스타일 수정은 [Style Sources](style-sources.md)와 [UI Reference](ui-reference.md)를 기준으로 확인합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Style Sources](style-sources.md)
- [UI Reference](ui-reference.md)
