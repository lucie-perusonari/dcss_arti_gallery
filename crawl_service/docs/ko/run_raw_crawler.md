# raw crawler 실행 wrapper

`run_raw_crawler_dev.sh`와 `run_raw_crawler_prod.sh`는 `crawl_service.worker` 실행을
개발용과 운영용으로 분리한 shell wrapper입니다. 기존 `run_raw_crawler.sh`는 호환용이며
dev wrapper를 호출합니다.

## 책임

- raw crawler 실행에 필요한 기본 환경을 준비합니다.
- dev wrapper는 명시적인 MongoDB override가 없으면 `mongodb://localhost:27018`과
  `dcss_arti_gallery`를 사용합니다.
- prod wrapper는 `MONGODB_URI`가 없으면 실행하지 않습니다.
- `DETACH=1`일 때 worker를 백그라운드로 실행하고 dev/prod별 log와 PID 파일에 기록합니다.
- `crawl_service.worker --once`는 한 번의 crawl pass만 실행하고 종료합니다.

## 비소유 책임

- 저장된 raw source를 artifact read model로 재생성하지 않습니다. 해당 작업은 `arti_parser/process_raw_morgue_files.sh`가 담당합니다.

## 실행

dev host 실행:

```sh
crawl_service/run_raw_crawler_dev.sh
DETACH=1 crawl_service/run_raw_crawler_dev.sh
```

prod host 실행:

```sh
MONGODB_URI=<prod-uri> crawl_service/run_raw_crawler_prod.sh
DETACH=1 MONGODB_URI=<prod-uri> crawl_service/run_raw_crawler_prod.sh
```

Compose 실행:

```sh
docker compose -f infra/dev/docker-compose.yml run --rm crawl-service
docker compose -f infra/prod/docker-compose.yml run --rm crawl-service
```

## 관련 문서

- [Processing Layers](processing-layers.md)
