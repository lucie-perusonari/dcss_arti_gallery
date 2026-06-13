# `prod/`

`infra/prod`는 운영 MongoDB lifecycle script와 운영 보호 정책을 소유합니다.

## 책임

- 운영 MongoDB 컨테이너 생성, 시작, 중지, 상태 확인 script를 제공합니다.
- destructive 또는 운영 영향 명령에 `CONFIRM_PROD=1` 확인을 요구합니다.
- 운영 기본 포트 `27017`과 database `dcss_arti_gallery`를 기준으로 합니다.

## 관련 문서

- [Index DDL](ensure_mongo_indexes.md)
