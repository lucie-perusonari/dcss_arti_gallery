# Ashenzari Morgue Tokens

Use this reference when item parsing, documentation, or display logic touches Ashenzari cursed equipment.

## Actual Morgue Shape

Ashenzari does not add individual skill boost properties like `Fighting+3` or `Long Blades+2` to the item property block in observed current morgues.

Observed item lines use curse group tokens inside the property block:

```text
{^Contam Int+6, Self, Comp}
{repulsion, rC+, Sorc, Dev}
{rF+++ rC+ Int-2 Forge Fire, Bglg, Comp}
{rC+++ Int-3 Dex+6, Cun, Elem}
```

The following item description block explains the group meanings:

```text
It has a curse which improves the following skills:
Introspection: Fighting and Spellcasting.
Companions: Summonings, Necromancy and Forgecraft.
```

Treat the group tokens as parser metadata and the description text as explanatory evidence.

## Token Mapping

| Property token | Curse group | Description skills |
| --- | --- | --- |
| `Self` | `Introspection` | `Fighting`, `Spellcasting` |
| `Melee` | `Melee Combat` | `Short Blades`, `Long Blades`, `Axes`, `Maces & Flails`, `Polearms`, `Staves`, `Unarmed Combat` |
| `Range` | `Ranged Combat` | current: `Ranged Weapons`, `Throwing`; older: `Slings`, `Bows`, `Crossbows`, `Throwing` |
| `Elem` | `Elements` | `Fire Magic`, `Ice Magic`, `Air Magic`, `Earth Magic` |
| `Sorc` | `Sorcery` | current: `Conjurations`, `Alchemy` |
| `Comp` | `Companions` | current: `Summonings`, `Necromancy`, `Forgecraft`; older: no `Forgecraft` |
| `Bglg` | `Beguiling` | current: `Hexes`, `Translocations`; older: may include `Conjurations` |
| `Fort` | `Fortitude` | `Armour`, `Shields` |
| `Cun` | `Cunning` | `Dodging`, `Stealth` |
| `Dev` | `Devices` | current: `Evocations`, `Shapeshifting` |
| `Evo` | `Evocations` | older morgues: `Evocations` |

## Parser Contract

- Add group tokens to internal/ignored token sets, not normal artifact attributes.
- Preserve group tokens in `ignored_attributes` for traceability.
- Exclude group tokens from `all_attributes`, `random_attributes`, scoring, filter chips, and frontend display tokens.
- Do not synthesize skill tokens from the description block.
- Keep old `Evo` compatibility because 2021-era morgues show `{Fort, Evo}` and `Evocations: Evocations.`

## Example Public Morgues

- `archive.nemelex.cards/morgue/sekai/morgue-sekai-20250508-151548.txt`
- `cbro.berotato.org/morgue/particleface/morgue-particleface-20250508-171153.txt`
- `cbro.berotato.org/morgue/mimimomo/morgue-mimimomo-20210806-212554.txt`
- `cbro.berotato.org/morgue/particleface/morgue-particleface-20250504-183752.txt`
