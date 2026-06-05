# Documentation Index

This directory contains the English index for module docs.
Use each module's `README.md` and `docs/` directory for execution details, internal structure, types, and processing layers.

## Module Docs

- [crawl_service README](../crawl_service/README.en.md)
- [crawl_service Docs](../crawl_service/docs/en/processing-layers.md)
- [api README](../api/README.en.md)
- [api Docs](../api/docs/en/processing-layers.md)
- [frontend README](../frontend/README.en.md)
- [frontend Docs](../frontend/docs/en/processing-layers.md)
- [admin-frontend README](../admin-frontend/README.en.md)
- [admin-frontend Docs](../admin-frontend/docs/en/processing-layers.md)

## Cross-Module Docs

Detailed documents live under each module's `docs/en` directory.
When changing more than one module, check all related module docs together.

### Crawl Service

- [Processing Layers](../crawl_service/docs/en/processing-layers.md)
- [Data Types](../crawl_service/docs/en/data-types.md)
- [Artifact Scoring Formula](../crawl_service/docs/en/artifact_scoring_formula.md)
- [Randart Properties](../crawl_service/docs/en/randart_properties.md)
- [DCSS Item Data](../crawl_service/docs/en/dcss_item_data.md)

### API

- [Processing Layers](../api/docs/en/processing-layers.md)
- [Data Types](../api/docs/en/data-types.md)

### Frontend

- [Processing Layers](../frontend/docs/en/processing-layers.md)
- [Data Types](../frontend/docs/en/data-types.md)

### Admin Frontend

- [Processing Layers](../admin-frontend/docs/en/processing-layers.md)
- [Data Types](../admin-frontend/docs/en/data-types.md)

## Guidelines

- Documents that explain only one module belong under that module's `docs/` directory.
- Cross-module contracts should link the relevant module docs together from the Cross-Module Docs section above.
- Experimental and reproducible analysis outputs belong under the owning module's language-specific `docs/{ko,en}/research`.
