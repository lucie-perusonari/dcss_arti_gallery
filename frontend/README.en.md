# DCSS Artifact Gallery Frontend

`frontend` is a React + TypeScript + Vite WebTiles-style artifact gallery.
It reads persisted artifact data from the Gallery API.

## Modules

- [`src/api`](docs/ko/api.md): frontend API boundary. Calls the artifact repository read path through `VITE_ARTIFACT_API_URL`
- [`src/types`](docs/ko/types.md): TypeScript artifact types used for the API response and gallery rendering
- [`src/components`](docs/ko/components.md): WebTiles-style panels, filters, cards, item details, and player filter UI
- [`public/tiles`](docs/ko/public-tiles.md): local DCSS tile PNG assets
- [`reference/`](docs/ko/reference.md): DCSS/WebTiles UI references and regression comparison screenshots
- [docs/en/style-sources.md](docs/en/style-sources.md): source notes for the WebTiles CSS/font recreation
- [UI Reference](docs/en/ui-reference.md): DCSS item UI reference material based on the DCInside roguelike gallery
- [Current UI Screenshots](docs/en/current-ui-screenshots.md): current UI screenshots for regression comparison

## Runtime

Dependencies:

```sh
npm install
```

Connect to the Gallery API:

```sh
VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

In the full development stack, compose manages the frontend and Gallery API URL together:

```sh
docker compose -f infra/dev/docker-compose.yml up frontend
```

## Build

```sh
npm run build
```

When the API/frontend contract changes, check [Frontend Data Types](docs/en/data-types.md) and
[API Data Types](../api/docs/en/data-types.md), then run the API tests together with the frontend build.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
