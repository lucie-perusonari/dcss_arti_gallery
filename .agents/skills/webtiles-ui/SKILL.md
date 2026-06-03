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
- `frontend/public/STYLE_SOURCES.md`
- `frontend/reference/*`

Use `bugfix` as well when the UI issue depends on backend API shape or data generation.

## Required Inputs

- User-facing screen or component to change
- Current `ArtifactDocument` fields from `frontend/src/types/artifact.ts`
- Existing WebTiles style references:
  - `frontend/public/STYLE_SOURCES.md`
  - `frontend/reference/`
- Mock state or API data that exercises the target view

## Workflow

1. Inspect the rendered data path: API client, frontend type, selected component, and CSS.
2. Keep the item description panel aligned with the documented WebTiles structure: popup shell, monospace item text, 32x32 canvas tile slot, DCSS color classes, and pre-wrapped description text.
3. Prefer existing tiles and WebTiles class vocabulary over decorative replacements.
4. Preserve dense, game-client-like information layout. Avoid marketing-page patterns, decorative cards inside cards, and purely atmospheric visuals.
5. Check mobile and desktop constraints for text overflow, panel overlap, and selectable artifact state.
6. Run `cd frontend && npm run build` after TypeScript or CSS changes.
7. When API data shape changes, run API contract tests and `cd frontend && npm run build` to confirm artifact tokens remain visible in detail output.

## Quality Bar

- The first screen should be the usable gallery, not a landing page.
- Artifact tiles should reveal the item class or subtype whenever available.
- Detail text should come from `dcssDescription` or `rawDescription`, not from a separate frontend-only rewrite of artifact properties.
- API fallback to mock data should remain explicit and predictable.
- The UI should match DCSS/WebTiles interaction density and typography without hiding backend data.

## Expected Output

- Frontend code or asset mapping changes
- Build result
- Screenshot or manual state checked when layout fidelity was the main risk
- Any known mismatch with upstream WebTiles sources
