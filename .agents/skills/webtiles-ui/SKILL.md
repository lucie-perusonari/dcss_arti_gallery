---
name: webtiles-ui
description: Preserve and improve the React gallery's DCSS WebTiles-style layout, item description panel, tile usage, fonts, and interaction fidelity.
---

# WebTiles UI

## When to Use

Use this skill for frontend work where the important outcome is that users see random artifacts through a DCSS-like layout and interface.

Route here for:

- `frontend/src/components/ArtifactDetail.tsx`
- `frontend/src/components/DcssItemDescription.tsx`
- `frontend/src/components/WebtilesShell.tsx`
- `frontend/src/components/ArtifactCard.tsx`
- `frontend/src/styles/app.css`
- `frontend/public/tiles/*`
- `frontend/docs/ko/style-sources.md`
- `frontend/docs/ko/ui-reference.md`
- `frontend/docs/ko/current-ui-screenshots.md`
- `frontend/reference/dcinside-log-gallery/*`
- `frontend/reference/screenshots/current-ui/*`

Use `bugfix` as well when the UI issue depends on backend API shape or data generation.

## Required Inputs

- User-facing screen or component to change
- Current `ArtifactDocument` fields from `frontend/src/types/artifact.ts`
- Existing WebTiles style references:
  - `frontend/docs/ko/style-sources.md`
  - `frontend/docs/ko/ui-reference.md`
  - `frontend/docs/ko/current-ui-screenshots.md`
  - `frontend/reference/dcinside-log-gallery/`
  - `frontend/reference/screenshots/current-ui/`
- Mock state or API data that exercises the target view

## Workflow

1. Inspect the rendered data path: API client, frontend type, selected component, and CSS.
2. Keep the item description panel aligned with the documented WebTiles structure: popup shell, monospace item text, 32x32 canvas tile slot, DCSS color classes, and pre-wrapped description text.
3. Prefer existing tiles and WebTiles class vocabulary over decorative replacements.
4. Preserve dense, game-client-like information layout. Avoid marketing-page patterns, decorative cards inside cards, and purely atmospheric visuals.
5. Check mobile and desktop constraints for text overflow, panel overlap, and selectable artifact state.
6. Use `frontend/README.md` for frontend build validation only when validation is explicitly requested or required by task context.
7. When API data shape changes, use the affected API/frontend README validation commands only when that validation is explicitly requested or required by context.

## Quality Bar

- The first screen should be the usable gallery, not a landing page.
- Artifact tiles should reveal the item class or subtype whenever available.
- Detail text should come from `dcssDescription` or `rawDescription`, not from a separate frontend-only rewrite of artifact properties.
- API fallback to mock data should remain explicit and predictable.
- Mock validation helpers and mock data generation logic should live in the relevant test file or test package, not in root `scripts/`.
- The UI should match DCSS/WebTiles interaction density and typography without hiding backend data.

## Expected Output

- Frontend code or asset mapping changes
- Build result when validation was explicitly requested, or a note that build validation was not run
- Screenshot or manual state checked when layout fidelity was the main risk
- Any known mismatch with upstream WebTiles sources
