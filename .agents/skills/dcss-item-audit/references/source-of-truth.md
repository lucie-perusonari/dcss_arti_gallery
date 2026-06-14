# Source of Truth

Use these references when auditing DCSS item, artefact, property-token, equipment-stat, or morgue parsing behavior.

## Priority

1. DCSS official repository: final authority for current mechanics, item property generation, naming, descriptions, and source-level contracts.
2. Local checked-in fixtures or narrowly selected public morgue excerpts: evidence for the exact text shape the parser consumes. Do not attempt exhaustive morgue-output review.
3. ChaosForge CrawlWiki: useful for player-facing terminology and cross-checking broad mechanics, but not authoritative over source code.
4. Namu Wiki: supplemental Korean-language context only. Use it to understand local terminology, not to override official source behavior.

If references conflict, follow the official repository first. Use wiki pages to explain terminology or discover likely source files, then verify implementation in source.

## Reference URLs

- DCSS official repository: https://github.com/crawl/crawl
- Official source tree: https://github.com/crawl/crawl/tree/master/crawl-ref/source
- `artefact.cc`: https://github.com/crawl/crawl/blob/master/crawl-ref/source/artefact.cc
- `item-name.cc`: https://github.com/crawl/crawl/blob/master/crawl-ref/source/item-name.cc
- ChaosForge CrawlWiki artefact page: https://crawl.chaosforge.org/Artefact
- ChaosForge CrawlWiki randart page: https://crawl.chaosforge.org/Randart
- Namu Wiki search: https://namu.moe/Search?q=Dungeon%20Crawl%20Stone%20Soup%20%EC%95%84%ED%8B%B0%ED%8C%A9%ED%8A%B8
