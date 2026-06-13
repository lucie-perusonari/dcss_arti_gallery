# `mongo/`

`infra/mongo`는 기존 명령 호환을 위한 dev wrapper입니다.

## 책임

- 기존에 `infra/mongo/*`를 호출하던 스크립트가 dev 환경으로 이어지도록 호환 경로를 제공합니다.
- 새 문서와 새 스크립트에서는 `infra/dev` 또는 `infra/prod`를 명시하도록 유도합니다.

## 관련 문서

- [Dev](dev.md)
- [Prod](prod.md)
