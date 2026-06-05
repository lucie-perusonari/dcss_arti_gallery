# Frontend Data Types

This document defines the artifact types consumed by the gallery frontend.
The TypeScript types must stay aligned with the Gallery API response shape.

## `ArtifactType`

- Defined in: `frontend/src/types/artifact.ts`
- Values: `weapon`, `armour`, `jewellery`, `talisman`, `staff`, `misc`

## `ArtifactAttribute`

- Defined in: `frontend/src/types/artifact.ts`
- Fields:
  - `token: string`
  - `kind: 'resistance' | 'stat' | 'property' | 'penalty' | 'brand' | 'spell_school'`
  - `description: string`
  - `scoreImpact: 'positive' | 'negative' | 'neutral'`

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
  - `enchantment`, `brand`, `origin`
  - `source`
  - `attributes`, `randomAttributes`
  - `allAttributes`, `baseAttributes`
  - `allAttributeText`, `baseAttributeText`, `randomAttributeText`
  - `evaluation`, `score`
  - `rawDescription`, `dcssDescription`

## Related Docs

- [Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/en/data-types.md)
