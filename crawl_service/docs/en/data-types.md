# Data Types

This document defines the data types that move between layers in the backend pipeline.
Implementation details live in the processing-layer docs or the module code.

## `MorgueFile`

A `txt`/`lst` file discovered in a remote morgue directory fetched over HTTP.

- Defined in: `crawl_service.morgue.types`
- Fields:
  - `name: str`: remote file name
  - `url: str`: remote file URL
  - `extension: str`: file extension; derived from `name`

## `MorgueUser`

A player directory discovered in a remote morgue root directory fetched over HTTP.

- Defined in: `crawl_service.morgue.types`
- Fields:
  - `nickname: str`: player directory name
  - `url: str`: player morgue directory URL
  - `modified_at: str`: raw `Date` column from the root index

## `MorgueRawText`

Raw morgue text fetched over HTTP and ready for the morgue artifact extractor.

- Defined in: `crawl_service.morgue.types`
- Fields:
  - `name: str`
  - `url: str`
  - `extension: str`: raw source type, currently `txt` or `lst`
  - `text: str`

## `RawMorgueFileRecord`

The raw morgue source and processing state stored by the `crawl_service` ingest flow in MongoDB `raw_morgue_files`.
This record is the source of truth for artifact read models; artifact documents are reproducible derived results.
Ingest is responsible only for the fetch state of this record, and processing reads this record to update artifact
documents and process state.

- Defined in: `crawl_service.core.repository`
- Fields:
  - `player: str`
  - `name: str`
  - `url: str`
  - `extension: str`
  - `text: str`
  - `content_hash: str`
  - `fetch_status: str`
  - `process_status: str`
  - `fetched_at: str | None`
  - `processed_at: str | None`
  - `artifact_count: int`
  - `fetch_error: str | None`
  - `process_error: str | None`
  - `parser_version: str | None`
  - `scoring_version: str | None`

## `ArtifactDocument`

The canonical artifact read-model document regenerated from `RawMorgueFileRecord` and stored in MongoDB.
Display tiles, description assembly, attribute kind/scoreImpact, and camelCase response fields are created in the
`api` read model.

- Defined in: `crawl_service.artifacts.models`
- Implementation: Pydantic `BaseModel`
- Key fields:
  - `id: str`
  - `name: str`
  - `base_item: str`
  - `base_subtype: str | None`
  - `item_class: str`
  - `item_subtype: str`
  - `weapon_subtype`, `armour_slot`, `jewellery_slot`
  - `enchantment: int | None`
  - `brand: str | None`
  - `source: ArtifactDocumentSource`
  - `attributes: list[ArtifactDocumentAttribute]`
  - `all_attributes`, `base_attributes`, `random_attributes`
  - `evaluation: ArtifactDocumentEvaluation`
  - `visible_item_description`, `visible_description_labels`
  - `raw_text_block`, `item_location`, `item_source`

## `ArtifactDocumentEvaluation`

The persisted shape of the evaluation result owned by `crawl_service.artifacts`.
`crawl_service.artifacts.evaluator` creates this model directly, and the processor stores it in
`ArtifactDocument.evaluation`.

- Defined in: `crawl_service.artifacts.models`
- Implementation: Pydantic `BaseModel`
- Fields:
  - `total: int`
  - `practical_score: int | None`
  - `rarity_score: int`
  - `offense: int`
  - `defense: int`
  - `utility: int`
  - `penalty: int`
  - `base_fit: int`
  - `grade: str`
  - `luxury_grade: str | None`

## `ArtifactDocumentSource`

The raw morgue source location for a document.

- Defined in: `crawl_service.artifacts.models`
- Implementation: Pydantic `BaseModel`
- Fields:
  - `player: str`
  - `file: str`
  - `url: str | None`
  - `line: int`

## `ArtifactDocumentAttribute`

Parsed attribute token data stored in the document. The API uses this to build display-friendly `kind` and
`scoreImpact` values.

- Defined in: `crawl_service.artifacts.models`
- Implementation: Pydantic `BaseModel`
- Fields:
  - `token: str`
  - `key: str`
  - `value: int | bool | None`
  - `description: str | None`

## `CrawlFileRecord`

The cache record that stores the worker completion state for each remote morgue file.
The source-of-truth state for raw source and reprocessing belongs to `RawMorgueFileRecord`; this record is used
when deciding whether to skip or cache files during archive scans.

- Defined in: `crawl_service.core.repository`
- Fields:
  - `player: str`
  - `name: str`
  - `url: str`
  - `status: str`
  - `artifact_count: int`
  - `processed_at: str | None`
  - `error: str | None`

## `CrawlUserRecord`

The cache record that stores the root-index `Date` and scan result for each user directory.

- Defined in: `crawl_service.core.repository`
- Fields:
  - `player: str`
  - `url: str`
  - `observed_at: str`
  - `status: str`
  - `scanned_at: str | None`
  - `processed_files: int`
  - `artifact_count: int`
  - `error: str | None`
