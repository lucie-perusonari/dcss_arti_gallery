# Prod TODO

- [ ] `crawl_service`와 `arti_parser` job이 실행 중이 아닌 시간을 골라 player casing 마이그레이션을 실행한다.
  - 먼저 감사만 실행: `infra/prod/run_player_casing_migration.sh`
  - 감사 결과에 blocking risk가 없으면 백업 포함 적용: `infra/prod/run_player_casing_migration.sh --apply`
  - 별도 `mongodump`를 이미 확보한 경우에만: `infra/prod/run_player_casing_migration.sh --apply --backup-confirmed`
  - 적용 후 Gallery API를 재시작하고 `player` 필터가 exact-case로 동작하는지 확인한다.
