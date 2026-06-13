# `dev/`

`infra/dev`는 개발 MongoDB lifecycle script와 개발 기본 환경값을 소유합니다.

## 책임

- 개발 MongoDB 컨테이너를 생성, 시작, 중지, 상태 확인합니다.
- 개발 기본 포트 `27018`과 database `dcss_arti_gallery_dev`를 제공합니다.
- `mongo_up.sh` 실행 시 필요한 index DDL을 적용합니다.

## 관련 문서

- [Index DDL](ensure_mongo_indexes.md)
