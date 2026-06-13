# WebTiles Style Sources

The local UI currently follows the structure and visual combinations used by the current DCSS WebTiles client.

- <https://crawl.nemelex.cards/>
- `crawl-ref/source/webserver/static/style.css`
- `crawl-ref/source/webserver/game_data/static/style.css`
- `crawl-ref/source/webserver/static/fonts/fonts.css`
- `frontend/reference/dcinside-log-gallery/`

The item detail panel uses the same class naming as WebTiles.

- `#game`
- `#ui-stack`
- `.ui-popup`
- `.ui-popup-outer`
- `.ui-popup-inner`
- `.describe-item`
- `.fg0` through `.fg15`

- The item tile in `.describe-item > .header` is rendered as a 32x32 `canvas`, following the WebTiles describe panel structure.
- The gallery frontend does not run the DCSS game client, but the item description window is rendered with the same popup layout, font, color palette, canvas tile slot, and `pre-wrap` behavior used by WebTiles.

For the actual DCSS item description panel density, dark background, pixel tile treatment, and monospace description text, use `frontend/reference/dcinside-log-gallery/`.
When changing the item detail panel, start by checking `artifact-gloves-description.png`, `armour-description-large.png`, and `jewellery-description-english.png`.

The screenshots in `frontend/reference/screenshots/current-ui/` are implementation checkpoints, not the design source of truth.
