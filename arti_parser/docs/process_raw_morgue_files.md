# process_raw_morgue_files.sh

`process_raw_morgue_files.sh`는 개발/운영에서 raw morgue file 처리 batch를 실행하는 shell
wrapper입니다.

## 동작

1. 저장소 루트로 이동합니다.
2. 명시적인 `MONGODB_*` override가 없으면 compose dev MongoDB host bind 기본값을 사용합니다.
3. 개발 기본 MongoDB 환경 변수를 채웁니다.
4. `python3 -m arti_parser.batch "$@"`를 실행합니다.

## 기본 환경 변수

- `MONGODB_URI`
- `MONGODB_DATABASE`
- `MONGODB_RAW_FILES_COLLECTION`
- `MONGODB_COLLECTION`
- `MONGODB_ARTIFACT_PROCESSING_COLLECTION`

## 변경 시 주의점

- 이 스크립트는 live morgue crawl을 실행하지 않습니다.
- MongoDB 기본값은 서비스 README와 일치해야 합니다.
- batch CLI 옵션은 그대로 `arti_parser.batch`에 전달됩니다.
