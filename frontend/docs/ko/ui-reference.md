# DCSS 아이템 설명창 참고 자료

이 디렉터리는 프론트엔드 아이템 설명창 디자인 구현 때 참고할 실제 DCSS 화면 자료입니다.
자료 출처는 DCInside 로그라이크 갤러리로 제한합니다.

이미지 자산은 문서 디렉터리가 아니라 `frontend/reference/dcinside-log-gallery/`에 둡니다.
현재 React 구현 결과 스크린샷은 `frontend/reference/screenshots/current-ui/`에 따로 둡니다.

## 아이템 설명창

아이템 상세 패널 구현은 아래 이미지를 우선 기준으로 삼습니다.

1. 아티팩트 장갑 설명창

   왼쪽 타일, 제목 한 줄, 설명 본문, 속성 설명 표, 장착 수치 변화, 획득 위치, stash/search prefix까지 포함한 핵심 reference입니다.

   ![Artifact gloves description](../../reference/dcinside-log-gallery/artifact-gloves-description.png)

2. 대형 방어구 설명창

   넓은 설명창, 긴 제목, 하단 액션 키, 고유 flavour text까지 포함합니다.

   ![Large armour description](../../reference/dcinside-log-gallery/armour-description-large.png)

3. 착용 중 방어구 설명창

   착용 중 상태, `take off` 액션, 얇은 테두리와 패널 폭을 확인합니다.

   ![Equipped armour description](../../reference/dcinside-log-gallery/armour-description-equipped.png)

4. 긴 설명과 스크롤바

   긴 flavour text와 오른쪽 스크롤바가 있는 아이템 설명창입니다.

   ![Scrollable armour description](../../reference/dcinside-log-gallery/armour-description-scrollbar.png)

5. 짧은 장갑 설명창

   짧은 설명창에서 타일, 제목, 본문, 속성 표가 얼마나 압축되는지 확인합니다.

   ![Short gloves description](../../reference/dcinside-log-gallery/gloves-description-short.png)

6. 착용 중 짧은 장갑 설명창

   짧은 설명창의 착용 상태와 제목 줄 구성을 확인합니다.

   ![Short equipped gloves description](../../reference/dcinside-log-gallery/gloves-description-equipped-short.png)

7. 영어 장신구 설명창

   현재 프론트엔드의 영어 artifact 설명과 가장 직접적으로 비교할 ring reference입니다.

   ![English jewellery description](../../reference/dcinside-log-gallery/jewellery-description-english.png)

8. 한글 장신구 설명창

   장신구의 타일, 제목, 속성 설명, 착용 시 변화가 큰 글자 환경에서 어떻게 보이는지 확인합니다.

   ![Korean jewellery description](../../reference/dcinside-log-gallery/jewellery-description-korean.png)

## 출처 메모

- `artifact-gloves-description.png`: DCInside 로그라이크 갤러리 `ㄷㅈ)상급장갑`, <https://gall.dcinside.com/board/view/?id=rlike&no=511423&page=1>.
- `armour-description-large.png`: DCInside 로그라이크 갤러리 `ㄷㅈ) 신이름 아티`, <https://gall.dcinside.com/board/view/?id=rlike&no=510916&page=1>.
- `armour-description-equipped.png`: DCInside 로그라이크 갤러리 `ㄷㅈ) 1층 황금용갑옷`, <https://gall.dcinside.com/board/view/?id=rlike&no=515834&page=1>.
- `armour-description-scrollbar.png`: DCInside 로그라이크 갤러리 `ㄷㅈ) 이거 뭔데`, <https://gall.dcinside.com/board/view/?id=rlike&no=508025&page=1>.
- `jewellery-description-korean.png`: DCInside 로그라이크 갤러리 `ㄷㅈ) 장검전사 부문 돌품명품 출품`, <https://gall.dcinside.com/board/view/?id=rlike&no=516900&page=1>.
- `gloves-description-equipped-short.png` and `gloves-description-short.png`: DCInside 로그라이크 갤러리 `ㄷㅈ) 이끼 미노타 장갑 추천해주세요`, <https://gall.dcinside.com/board/view/?id=rlike&no=517805&page=1>.
- `jewellery-description-english.png`: DCInside 로그라이크 갤러리 `돌죽 아주 조금 안 좋은 불저 냉저 반지`, <https://gall.dcinside.com/board/view/?id=rlike&no=518662&page=1>.

## 디자인 사용

- Use `artifact-gloves-description.png`, `armour-description-large.png`, and `jewellery-description-english.png` before changing `DcssItemDescription`.
- Preserve the real DCSS structure: item tile plus title row, black background, monospace body, property explanation rows, acquisition/source lines, search prefix lines, and bottom action row.
- Do not use list, menu, full WebTiles shell, map, status, inventory, or message-log captures as design reference in this directory.
- Do not use non-DCInside images as frontend design reference in this directory.
