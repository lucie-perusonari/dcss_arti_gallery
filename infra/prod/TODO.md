# Prod TODO

- [x] `crawl_service`와 `arti_parser` job이 실행 중이 아닌 시간을 골라 player casing 마이그레이션을 실행한다.
  - 먼저 감사만 실행: `infra/prod/run_player_casing_migration.sh`
  - 감사 결과에 blocking risk가 없으면 백업 포함 적용: `infra/prod/run_player_casing_migration.sh --apply`
  - 별도 `mongodump`를 이미 확보한 경우에만: `infra/prod/run_player_casing_migration.sh --apply --backup-confirmed`
  - 적용 후 Gallery API를 재시작하고 `player` 필터가 exact-case로 동작하는지 확인한다.
  - 완료: 2026-06-18 운영 서버에서 백업 생성 후 적용했다.
  - 백업: `_workspace/backups/prod-player-casing-20260617-172503`
  - 적용 결과: `raw_morgue_files` 95,428건, `artifact_processing_files` 95,428건, `artifacts` 177,867문서 업데이트.
  - 검증: 적용 후 dry-run 수정 대상 0건, `player=13Xi`는 결과를 반환하고 `player=13xi`는 0건을 반환한다.
