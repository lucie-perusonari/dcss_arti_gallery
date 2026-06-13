# Infra 환경 정책

이 저장소의 Docker 기반 MongoDB infra는 `dev`와 `prod`를 물리적으로 분리합니다.
개발 단계의 모든 프로젝트와 스크립트는 기본적으로 `infra/dev`만 참조합니다.

## 모듈

- [`dev/`](docs/ko/dev.md): 개발 MongoDB lifecycle script와 dev 기본 환경값
- [`prod/`](docs/ko/prod.md): 운영 MongoDB lifecycle script와 prod 보호 정책
- [`mongo/`](docs/ko/mongo.md): 기존 명령 호환을 위한 dev wrapper
- [`ensure_mongo_indexes.py`](docs/ko/ensure_mongo_indexes.md): MongoDB collection index DDL 적용 스크립트

## 환경 구분

| 환경 | 경로 | 기본 컨테이너 | 기본 포트 | 기본 DB |
| --- | --- | --- | --- | --- |
| dev | `infra/dev` | `dcss-arti-gallery-mongo-dev` | `27018` | `dcss_arti_gallery_dev` |
| prod | `infra/prod` | `dcss-arti-gallery-mongo-prod` | `27017` | `dcss_arti_gallery` |

`infra/mongo`는 기존 명령 호환을 위한 dev wrapper입니다. 새 문서와 스크립트에서는 `infra/dev` 또는
`infra/prod`를 명시합니다.

## 개발 정책

- 개발 실행, 로컬 테스트, mock이 아닌 로컬 API 확인은 `infra/dev`를 사용합니다.
- `api`, `admin_api`, `crawl_service`의 코드 기본 MongoDB 값은 dev 환경을 가리킵니다.
- `infra/dev/mongo_env.sh`는 기본적으로 기존 shell의 `MONGODB_*` 값을 무시하고 dev 값을 강제합니다.
  의도적으로 dev 값을 바꿔야 할 때만 `ALLOW_DEV_MONGO_ENV_OVERRIDE=1`을 사용합니다.
- `infra/dev/run_dev.sh`는 `infra/dev/mongo_up.sh`를 사용합니다.
- MongoDB collection index 같은 DDL 작업은 application repository가 아니라 `infra/ensure_mongo_indexes.py`가
  수행하며, `infra/dev/mongo_up.sh`에서 자동 실행됩니다.
- `infra/dev/run_dev.sh`는 기본적으로 live morgue crawl worker를 실행하지 않습니다. 필요할 때만
  `RUN_CRAWL_WORKER=1 ./infra/dev/run_dev.sh`를 사용합니다.
- `crawl_service/run_raw_crawler.sh`와 `arti_parser/process_raw_morgue_files.sh`는 명시적인
  `MONGODB_*` override가 없으면 dev 환경값을 사용합니다.
- Admin API 테스트 유틸은 자동 MongoDB가 필요할 때 `infra/dev/mongo_up.sh`를 호출합니다.
  테스트에서 외부 MongoDB를 명시적으로 쓰려면 `ALLOW_TEST_MONGO_ENV_OVERRIDE=1`을 함께 지정합니다.

## Prod 정책

- prod lifecycle script는 명시적으로 `infra/prod` 경로를 사용해야 합니다.
- prod 컨테이너 생성, 시작, 중지는 `CONFIRM_PROD=1`이 있어야 실행됩니다.
- prod MongoDB index DDL은 `infra/prod/mongo_up.sh`가 `infra/ensure_mongo_indexes.py`를 통해 수행합니다.
- 개발 스크립트와 테스트 유틸에서 `infra/prod`를 호출하면 안 됩니다.
- prod에 연결해야 하는 배포/운영 프로세스는 `MONGODB_URI`, `MONGODB_DATABASE`, collection 환경변수를
  명시적으로 주입해야 합니다.

## 명령

개발 MongoDB:

```sh
eval "$(infra/dev/mongo_up.sh)"
infra/dev/mongo_status.sh
infra/dev/mongo_down.sh
```

운영 MongoDB:

```sh
eval "$(CONFIRM_PROD=1 infra/prod/mongo_up.sh)"
infra/prod/mongo_status.sh
CONFIRM_PROD=1 infra/prod/mongo_down.sh
```
