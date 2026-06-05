# WebTiles 스타일 출처

로컬 UI는 현재 DCSS WebTiles 클라이언트 구조와 값 조합을 그대로 따라갑니다.

- <https://crawl.nemelex.cards/>
- `crawl-ref/source/webserver/static/style.css`
- `crawl-ref/source/webserver/game_data/static/style.css`
- `crawl-ref/source/webserver/static/fonts/fonts.css`
- `frontend/reference/dcinside-log-gallery/`

아이템 상세 패널은 WebTiles와 동일한 클래스 네이밍을 사용합니다.

- `#game`
- `#ui-stack`
- `.ui-popup`
- `.ui-popup-outer`
- `.ui-popup-inner`
- `.describe-item`
- `.fg0` through `.fg15`

- `.describe-item > .header` 내 아이템 타일은 32x32 `canvas`로 렌더링되며, WebTiles의 describe 패널 구조를 따릅니다.
- 로컬 mock 앱은 DCSS 게임 클라이언트를 실행하지 않지만, 아이템 설명 창은 WebTiles와 동일한 팝업 레이아웃, 폰트, 색상 팔레트, 캔버스 타일 슬롯, `pre-wrap` 동작으로 렌더링합니다.

실제 DCSS 화면 밀도, 아이템 그리드 간격, 짙은 배경, 픽셀 타일 처리, monospace 설명 텍스트의 시각 기준은
`frontend/reference/dcinside-log-gallery/`를 사용합니다. 아이템 상세 패널 수정 시에는 `artifact-gloves-description.png`, `armour-description-large.png`, `jewellery-description-english.png`를 우선 확인하세요.

`frontend/reference/screenshots/current-ui/`의 스크린샷은 구현 상태 점검용 스냅샷이지 디자인 원본은 아닙니다.
