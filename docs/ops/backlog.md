# Backlog

This document tracks non-blocking data quality and operational follow-up work.
It is an operational note, not a contract.

## Data Coverage

- Some DCSS version-specific or legacy items may be missing flavour text in `crawl_service.domain.documents.builder::ITEM_FLAVOUR_TEXT`.
- Long term, synchronize official DCSS description data by version or parse the morgue file version and select matching text.

## Existing Mongo Data

- Mongo `artifacts` documents created before `raw_morgue_files` existed may not have a persisted raw source record. Re-ingest old sources before relying on source-of-truth replay.
- Legacy fixed/unrand artifacts saved before filtering should be cleaned up with a DB migration or refresh import.

## Cache And Schema Versioning

- `raw_morgue_files` stores `parser_version` and `scoring_version`; add a document schema version if stored artifact document shape changes should trigger automatic regeneration.
- `crawl_files` remains a worker skip/cache record. Do not use it as the source of truth for reprocessing decisions.

## Scale

- `api.repository.MongoArtifactReadRepository.list_artifacts` still applies search text filtering in Python memory.
- Add Mongo query support, text indexes, sorting, and pagination when artifact volume grows.

## Worker State

- `crawl_service.worker` persists user-level scan state in `crawl_users`, file-level skip/cache state in `crawl_files`, and raw source/process state in `raw_morgue_files`.
- The worker process loop position is still in memory only; after restart, it resumes from the saved user/file state on the next pass.

## Deduplication Policy

- The same artifact may be saved repeatedly from `.txt`/`.lst` files or multiple morgue files.
- Decide whether gallery display should deduplicate artifacts while preserving source provenance.

## Frontend Contract Cleanup

- `frontend/src/components/DcssItemDescription.tsx` still has legacy description fallback logic.
- Once the backend data contract is stable, reduce fallback behavior and lock the contract with tests.
