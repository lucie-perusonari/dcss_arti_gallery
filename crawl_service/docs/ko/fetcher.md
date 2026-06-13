# `fetcher.py`

`fetcher.py`는 remote morgue HTML index와 원문 파일을 HTTP로 읽는 입력 계층입니다.

## 책임

- remote morgue root index에서 user directory 목록을 읽어 `MorgueUser`로 반환합니다.
- user directory index에서 `.txt`, `.lst` 파일 목록을 읽어 `MorgueFile`로 반환합니다.
- 개별 morgue 파일 본문을 가져옵니다.
- 원격 HTML 구조와 HTTP timeout/user agent 같은 fetch 세부사항을 캡슐화합니다.

## 비소유 책임

- 중복 저장 여부 판단과 MongoDB 쓰기는 `repository.py`와 `worker.py`가 담당합니다.
- artifact parsing, scoring, document 생성은 `arti_parser`가 담당합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Data Types](data-types.md)
