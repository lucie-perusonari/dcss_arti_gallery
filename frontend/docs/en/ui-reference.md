# DCSS Item Description References

This directory contains real DCSS screen captures used when implementing the frontend item description window.
The source is limited to the DCInside roguelike gallery.

The image assets live outside the docs tree in `frontend/reference/dcinside-log-gallery/`.
The current React implementation screenshots live separately in `frontend/reference/screenshots/current-ui/`.

## Item Description Windows

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

## Source Notes

- `artifact-gloves-description.png`: DCInside roguelike gallery `ㄷㅈ)상급장갑`, <https://gall.dcinside.com/board/view/?id=rlike&no=511423&page=1>.
- `armour-description-large.png`: DCInside roguelike gallery `ㄷㅈ) 신이름 아티`, <https://gall.dcinside.com/board/view/?id=rlike&no=510916&page=1>.
- `armour-description-equipped.png`: DCInside roguelike gallery `ㄷㅈ) 1층 황금용갑옷`, <https://gall.dcinside.com/board/view/?id=rlike&no=515834&page=1>.
- `armour-description-scrollbar.png`: DCInside roguelike gallery `ㄷㅈ) 이거 뭔데`, <https://gall.dcinside.com/board/view/?id=rlike&no=508025&page=1>.
- `jewellery-description-korean.png`: DCInside roguelike gallery `ㄷㅈ) 장검전사 부문 돌품명품 출품`, <https://gall.dcinside.com/board/view/?id=rlike&no=516900&page=1>.
- `gloves-description-equipped-short.png` and `gloves-description-short.png`: DCInside roguelike gallery `ㄷㅈ) 이끼 미노타 장갑 추천해주세요`, <https://gall.dcinside.com/board/view/?id=rlike&no=517805&page=1>.
- `jewellery-description-english.png`: DCInside roguelike gallery `돌죽 아주 조금 안 좋은 불저 냉저 반지`, <https://gall.dcinside.com/board/view/?id=rlike&no=518662&page=1>.

## Design Use

- Use `artifact-gloves-description.png`, `armour-description-large.png`, and `jewellery-description-english.png` before changing `DcssItemDescription`.
- Preserve the real DCSS structure: item tile plus title row, black background, monospace body, property explanation rows, acquisition/source lines, search prefix lines, and bottom action row.
- Do not use list, menu, full WebTiles shell, map, status, inventory, or message-log captures as design reference material in this directory.
- Do not use non-DCInside images as frontend design reference material in this directory.
