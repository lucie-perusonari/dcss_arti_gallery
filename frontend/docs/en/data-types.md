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

## `Artifact`

- Defined in: `frontend/src/types/artifact.ts`
- Purpose: gallery list/detail rendering state
- Key fields:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype?: string | null`
  - `armourSlot?: string | null`
  - `jewellerySlot?: string | null`
  - `source`
  - `randomAttributes`
  - `score`
  - `dcssDescription`

The subtype/slot fields support type-specific secondary filters. When they are missing,
the UI falls back to `subtype`.

## `ArtifactFilters`

- Defined in: `frontend/src/types/artifact.ts`
- Fields:
  - `search: string`
  - `type: ArtifactType | 'all'`
  - `slot: string`

`slot` is a frontend display filter, not a Gallery API query parameter.

## Related Docs

- [Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/en/data-types.md)
