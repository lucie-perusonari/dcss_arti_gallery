# DCSS Artifact Gallery Frontend

`frontend` is a React + TypeScript + Vite WebTiles-style artifact gallery.
It reads persisted artifact data from the Gallery API and falls back to local mock data when `VITE_ARTIFACT_API_URL`
is not set.

## Responsibilities

- `src/api`: frontend API boundary. Calls the artifact repository read path through `VITE_ARTIFACT_API_URL`
- `src/types`: TypeScript artifact types used for the API response and gallery rendering
- `src/data`: local mock artifact data and DCSS tile mappings
- `src/components`: WebTiles-style panels, filters, cards, item details, and nickname crawl UI
- `public/tiles`: local DCSS tile PNG assets
- [docs/en/style-sources.md](docs/en/style-sources.md): source notes for the WebTiles CSS/font recreation
- [UI Reference](docs/en/ui-reference.md): DCSS item UI reference material based on the DCInside roguelike gallery
- [Current UI Screenshots](docs/en/current-ui-screenshots.md): current UI screenshots for regression comparison

## Runtime

Dependencies:

```sh
npm install
```

Run the mock gallery without connecting to the API:

```sh
npm run dev
```

Connect to the Gallery API:

```sh
VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

From the repository root, you can use:

```sh
./scripts/run_frontend.sh
```

## Build

```sh
npm run build
```

When the API/frontend contract changes, check [Frontend Data Types](docs/en/data-types.md) and
[API Data Types](../api/docs/en/data-types.md), then run the API tests together with the frontend build.

## Mock Screens

- `/`: full gallery
- `/?type=jewellery&selected=keod`: jewellery detail filtered by type
- `/?type=weapon&selected=ashenzari-axe`: weapon detail
- `/?search=regen&selected=ceguteof`: search flow

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
