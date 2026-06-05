# DCSS Frontend References

This directory contains real DCSS screen captures used when implementing the frontend design.
The source is limited to the DCInside roguelike gallery.

The image assets live outside the docs tree in `frontend/reference/dcinside-log-gallery/`.
The current React implementation screenshots live separately in `frontend/reference/screenshots/current-ui/`.

## Primary Item Descriptions

Use the following images as the primary reference for the item detail panel.

1. Artifact gloves description

   Key reference with the left tile, title row, description body, property explanation table, equipment stat
   changes, acquisition location, and stash/search prefix.

2. Large armour description

   Covers the wide description window, long title, bottom action keys, and unique flavour text.

3. Equipped armour description

   Use this to check equipped state, the `take off` action, the thin border, and panel width.

4. Long description with scrollbar

   An item description window with long flavour text and a scrollbar on the right.

5. Short gloves description

   Use this to check how the tile, title, body text, and property table are compressed in a short window.

6. Short equipped gloves description

   Use this to check the equipped state and title line composition in the short window.

7. English jewellery description

   The closest ring reference for comparing the current frontend's English artifact descriptions.

8. Korean jewellery description

   Use this to inspect how the jewellery tile, title, property explanation, and equipment changes look in a larger
   font environment.

## Lists, Menus, And Rows

Use these when adjusting gallery lists, cards, filter results, or mobile row density.

1. Mobile / expanded item row

   Shows how a long randart name and attribute list fit on one row.

2. Equipment list

   Use this to check category labels, equipped state, tiles, hotkeys, item names, and spacing in the property list.

3. Shop item list

   Use this to check the density of price, hotkey, icon, item name, property list, and selected-row highlight.

4. Acquirement item menu

   Use this to check the popup border, selected-row highlight, and bottom command line.

5. Artifact link in the message log

   Use this to check how artifact names appear as colored links in the bottom log.

## WebTiles Shell

Use these when adjusting the full-screen layout, right-side status panel, popup overlay, black margins, or map/message density.

1. Current WebTiles play screen

   The current WebTiles screen running in the browser.

2. WebTiles popup overlay

   A screen with the centered popup, dimmed background, right-side status panel, and chat box.

3. WebTiles map/status crop

   A crop that shows the map, minimap, and right-side status text.

4. Legacy Korean tiles inventory

   Although this is an older Korean client, it is still useful for tile-based equipment, inventory, and status-panel
   density reference.

## Source Notes

- `artifact-gloves-description.png`: DCInside roguelike gallery `ㄷㅈ)상급장갑`, <https://gall.dcinside.com/board/view/?id=rlike&no=511423&page=1>.
- `mobile-artifact-row.jpg`: DCInside roguelike gallery `ㄷㅈ) 그래서 이거 들고 승천하면 되죠?`, <https://gall.dcinside.com/board/view/?id=rlike&no=518762&page=1>.
- `webtiles-current-play-screen.png`: DCInside roguelike gallery `ㄷㅈ)검정드라코 쉐슆 올룬클`, <https://gall.dcinside.com/board/view/?id=rlike&no=493572>.
- `armour-description-large.png`: DCInside roguelike gallery `ㄷㅈ) 신이름 아티`, <https://gall.dcinside.com/board/view/?id=rlike&no=510916&page=1>.
- `armour-description-equipped.png`: DCInside roguelike gallery `ㄷㅈ) 1층 황금용갑옷`, <https://gall.dcinside.com/board/view/?id=rlike&no=515834&page=1>.
- `armour-description-scrollbar.png`: DCInside roguelike gallery `ㄷㅈ) 이거 뭔데`, <https://gall.dcinside.com/board/view/?id=rlike&no=508025&page=1>.
- `message-log-artifact-link.png`: DCInside roguelike gallery `ㄷㅈ) 변이 선물`, <https://gall.dcinside.com/board/view/?id=rlike&no=507529&page=1>.
- `webtiles-popup-overlay.png` and `webtiles-map-status-crop.png`: DCInside roguelike gallery `ㄷㅈ) '시시하군'`, <https://gall.dcinside.com/board/view/?id=rlike&no=518532&page=1>.
- `jewellery-description-korean.png`: DCInside roguelike gallery `ㄷㅈ) 장검전사 부문 돌품명품 출품`, <https://gall.dcinside.com/board/view/?id=rlike&no=516900&page=1>.
- `shop-item-list.png`: DCInside roguelike gallery `ㄷㅈ)고자그 치곤 좋은거 나온`, <https://gall.dcinside.com/board/view/?id=rlike&no=518324&page=1>.
- `acquirement-item-menu.png`: DCInside roguelike gallery `ㄷㅈ) 오카왈도 니뮤ㅠㅠ`, <https://gall.dcinside.com/board/view/?id=rlike&no=518030&page=1>.
- `gloves-description-equipped-short.png` and `gloves-description-short.png`: DCInside roguelike gallery `ㄷㅈ) 이끼 미노타 장갑 추천해주세요`, <https://gall.dcinside.com/board/view/?id=rlike&no=517805&page=1>.
- `jewellery-description-english.png`: DCInside roguelike gallery `돌죽 아주 조금 안 좋은 불저 냉저 반지`, <https://gall.dcinside.com/board/view/?id=rlike&no=518662&page=1>.
- `equipment-list-mobile.png`: DCInside roguelike gallery `ㄷㅈ) 문어 탈리스만 선택존`, <https://gall.dcinside.com/board/view/?id=rlike&no=518522&page=1>.
- `legacy-korean-tiles-inventory.png`: DCInside roguelike gallery `ㄷㅈ) 0.13 버전 오랫만에 클리어 해본 후기`, <https://gall.dcinside.com/board/view/?id=rlike&no=389186&page=1>.

## Design Use

- Use `artifact-gloves-description.png`, `armour-description-large.png`, and `jewellery-description-english.png` before changing `DcssItemDescription`.
- Preserve the real DCSS structure: item tile plus title row, black background, monospace body, property explanation rows, acquisition/source lines, search prefix lines, and bottom action row.
- Use the list/menu references before changing gallery card density, selected states, or mobile rows.
- Do not use non-DCInside images as frontend design reference material in this directory.
