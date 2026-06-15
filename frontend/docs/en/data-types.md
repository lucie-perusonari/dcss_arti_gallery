# Frontend Data Types

This document defines the artifact types consumed by the gallery frontend.
The TypeScript types must stay aligned with the Gallery API response shape.

## `ArtifactType`

- Defined in: `frontend/src/types/artifact.ts`
- Values: `weapon`, `armour`, `jewellery`, `talisman`, `staff`, `misc`

## `ArtifactEvaluation`

- Defined in: `frontend/src/types/artifact.ts`
- Fields:
  - `total: number`
  - `practical_score?: number | null`
  - `rarity_score?: number`
  - `offense`, `defense`, `utility`, `penalty`
  - `base_fit?: number`
  - `grade?: string`
  - `luxury_grade?: string | null`

## `ArtifactDiscovery`

- Defined in: `frontend/src/types/artifact.ts`
- Fields:
  - `version?: string | null`: DCSS version from the first discovered source.
  - `datetime?: string | null`: discovery datetime from the first discovered source.

## `Artifact`

- Defined in: `frontend/src/types/artifact.ts`
- Purpose: gallery list/detail rendering state
- Key fields:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype?: string | null`
  - `armourSubtype?: string | null`
  - `armourSlot?: string | null`
  - `jewellerySlot?: string | null`
  - `source`
  - `allAttributes`
  - `baseAttributes`
  - `randomAttributes`
  - `discovery`
  - `score`
  - `dcssDescription`

The subtype/slot fields support type-specific secondary filters and rendering details. When they are missing,
the UI falls back to `subtype`.
`armourSubtype` preserves the original armour base type within a slot, such as `hat`, `helmet`, or `pair of gloves`,
and is used for armour card labels and tile selection.
When `source.url` is present, the detail panel uses it as the original morgue link.
`allAttributes` is the source for the card `token-row`; it includes base intrinsic attributes and excludes ignored
attributes. `discovery` is rendered at the bottom of the item description popup.

## `ArtifactFilters`

- Defined in: `frontend/src/types/artifact.ts`
- Fields:
  - `search: string`
  - `type: ArtifactType | 'all'`
  - `slot: string`
  - `luxuryOnly: boolean`
  - `player: string`
  - `timeRange: '30d' | 'all'`

`player` is sent as the Gallery API `player` query parameter.

`timeRange` is sent as the Gallery API `since` query parameter. The default `30d` limits the view to recent games,
while `all` removes the date range.

`slot` is a frontend display filter computed with the same fallback category rules as the Gallery API. The frontend
keeps the API result list for the current type/search/player filters and derives the displayed list with `slot`, so
selecting one secondary filter does not remove the other secondary filter buttons for the same type.

Weapon `slot` values follow DCSS weapon skill categories: `short blades`, `long blades`, `axes`,
`maces & flails`, `polearms`, `staves`, and `ranged`. For example, `giant club` and `giant spiked club`
belong to `maces & flails`, while `quick blade` belongs to `short blades`.

Jewellery `slot` values are normalized to `ring` or `amulet`.

Talisman `slot` values group individual subtypes by form tier. The UI uses `tier 1 talismans`
through `tier 5 talismans`, plus `other talismans`.

## Related Docs

- [Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/en/data-types.md)
