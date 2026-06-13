# Frontend Processing Layers

This document defines the API boundary and UI layers for the gallery frontend.

## Project Boundary

- Module: `frontend/`
- Role: bring Gallery API responses into React UI state and present a WebTiles-style gallery and detail view
- Input: Gallery API artifact response
- Output: browser UI state

## Internal Layers

- `src/api`: Gallery API client backed by `VITE_ARTIFACT_API_URL`
- `src/types`: TypeScript artifact types used for API responses and gallery rendering
- `src/components`: WebTiles-style panels, filters, cards, item details, and nickname crawl UI
- `public/tiles`: local DCSS tile PNG assets
- `docs/en/style-sources.md`: WebTiles CSS/font source notes
- `reference`: DCInside roguelike gallery reference material for the DCSS item UI

## Related Docs

- [Frontend Data Types](./data-types.md)
- [API Data Types](../../../api/docs/en/data-types.md)
