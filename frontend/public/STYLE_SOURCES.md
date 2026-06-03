# WebTiles Style Sources

The local UI mirrors the current DCSS WebTiles client structure and values used by:

- <https://crawl.nemelex.cards/>
- `crawl-ref/source/webserver/static/style.css`
- `crawl-ref/source/webserver/game_data/static/style.css`
- `crawl-ref/source/webserver/static/fonts/fonts.css`
- `frontend/reference/dcinside-log-gallery/`

The item description panel intentionally uses the same class vocabulary as WebTiles:

- `#game`
- `#ui-stack`
- `.ui-popup`
- `.ui-popup-outer`
- `.ui-popup-inner`
- `.describe-item`
- `.fg0` through `.fg15`

The item tile in `.describe-item > .header` is drawn into a 32x32 `canvas`, matching the WebTiles describe panel structure. The local mock app does not run the DCSS game client, but the item description window is rendered with the same popup layout, font family, color palette, canvas tile slot, and `pre-wrap` description behavior used by WebTiles.

Use `frontend/reference/dcinside-log-gallery/` as the visual reference for actual DCSS screen density, item grid spacing, dark background, pixel tile treatment, and monospace description text. Use `artifact-gloves-description.png`, `armour-description-large.png`, and `jewellery-description-english.png` first when changing the item description panel.

The screenshots in `frontend/screenshots/current-ui/` are implementation snapshots, not design source material.
