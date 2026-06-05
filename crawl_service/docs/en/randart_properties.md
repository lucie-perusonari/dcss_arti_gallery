# DCSS Randart Properties

This document classifies properties that may appear on DCSS random artifacts (randarts) for development use. It is
based on the official Crawl source's `artefact_prop_type` and `artp_data`, and focuses on properties that can be
randomly selected as additional properties from the general randart generation pool.

## Scope

Included:

- Properties whose `artp_data` generation weight is greater than zero during randart generation
- Weapon brands automatically assigned to randart weapons
- Armour egos that can probabilistically appear on randart armour

Excluded:

- Enum values whose general randart random generation weight is zero
- Properties that come only from jewellery base type, armour/staff/talisman intrinsic effects, or base-item effects
- Fixed artifacts, vault fixed props, and legacy compatibility properties
- Spell lists on randart spellbooks

Notes:

- Not every property can appear on every item.
- Morgues and item descriptions may display base item, ego, and intrinsic properties together with randart
  properties. To isolate only randart-added properties, remove base subtype and intrinsic properties first.
- `AC`, `EV`, and `SH` can appear in randart descriptions. They are usually from jewellery base subtype or intrinsic
  properties rather than general randart random-property selection.

## Positive Or Mixed Property Groups

### Weapon Brand

Randart weapons always have a brand.

Examples:

- `flaming`
- `freezing`
- `venom`
- `draining`
- `heavy`
- `speed`
- `antimagic`
- `holy wrath`
- `electrocution`
- `pain`
- `vampirism`
- `protection`
- `spectral`
- `reaping`
- `distortion`
- `chaos`
- `penetration` - crossbow only

Suggested classification:

- `kind`: `brand`
- `polarity`: `positive` or `mixed`

### Armour Ego

Randart armour can probabilistically have an ego. Some equipment, such as scarves or orbs, may always require an ego.

When an ego has the same functional meaning as an artefact property, normalize it to the property below:

- fire resistance -> `rF`
- cold resistance -> `rC`
- poison resistance -> `rPois`
- corrosion resistance -> `rCorr`
- see invisible -> `SInv`
- invisibility -> `+Inv`
- strength -> `Str`
- dexterity -> `Dex`
- intelligence -> `Int`
- flying -> `Fly`
- willpower -> `Will`
- stealth -> `Stlth`
- positive energy -> `rN`
- archmagi -> `Archmagi`
- harm -> `Harm`
- rampaging -> `Rampage`
- ice/fire/air/earth enhancer -> `Ice`, `Fire`, `Air`, `Earth`

Suggested classification:

- `kind`: `ego`
- `normalized_property`: matching artefact property notation, when one exists

### Stat Properties

| Property | Meaning | Value |
| --- | --- | --- |
| `Str` | strength modifier | signed integer |
| `Int` | intelligence modifier | signed integer |
| `Dex` | dexterity modifier | signed integer |

Notes:

- Positive and negative values are both possible.
- Randart generation can stack and strengthen the same stat.

Suggested classification:

- `kind`: `stat`
- `polarity`: `positive` when value is positive, `negative` when value is negative

### Combat And Resource Modifiers

| Property | Meaning | Value | Notes |
| --- | --- | --- | --- |
| `Slay` | slaying modifier | signed integer | not randomly added to weapons or staves |
| `MP` | max MP modifier | signed integer | not randomly added to weapons or staves |

Suggested classification:

- `kind`: `combat` for `Slay`
- `kind`: `resource` for `MP`
- `polarity`: `positive` when value is positive, `negative` when value is negative

## Resistance Properties

| Property | Meaning | Value | Negative Value |
| --- | --- | --- | --- |
| `rF` | fire resistance | signed integer | fire vulnerability |
| `rC` | cold resistance | signed integer | cold vulnerability |
| `rElec` | electricity resistance | boolean | none |
| `rPois` | poison resistance | boolean | none |
| `rN` | negative energy resistance | positive integer | none |
| `Will` | willpower | signed integer | willpower penalty |
| `rCorr` | corrosion resistance | boolean | none |

Notes:

- `rF`, `rC`, and `Will` can be negative.
- In general randart generation, `rN` only has a positive side.
- `rElec`, `rPois`, and `rCorr` are boolean positive properties.
- `rCorr` conflicts with `*Corrode`, so they cannot appear together.

Suggested classification:

- `kind`: `resistance`
- `polarity`: `positive` for positive/boolean true, `negative` for negative values

## Utility Properties

| Property | Meaning | Value | Notes |
| --- | --- | --- | --- |
| `SInv` | see invisible | boolean | positive |
| `+Inv` | evoke invisibility | boolean | mostly non-swappable items |
| `Fly` | flight | boolean | positive |
| `+Blink` | evoke blink | boolean | conflicts with `-Tele` |
| `Regen` | HP regeneration | boolean | restricted on talismans |
| `Harm` | harm | boolean | mostly non-swappable items |
| `Rampage` | rampaging | boolean | mostly non-swappable items |
| `Archmagi` | archmagi spell power bonus | boolean | robe only |

Suggested classification:

- `kind`: `utility`
- `polarity`: mostly `positive`; `Harm` can be treated as `mixed` depending on build

## Spell School Enhancer Properties

| Property | Spell School |
| --- | --- |
| `Conj` | Conjurations |
| `Hexes` | Hexes |
| `Summ` | Summonings |
| `Necro` | Necromancy |
| `Tloc` | Translocations |
| `Fire` | Fire Magic |
| `Ice` | Ice Magic |
| `Air` | Air Magic |
| `Earth` | Earth Magic |
| `Alch` | Alchemy |
| `Forge` | Forgecraft |

Item restrictions:

- staves
- orbs
- some armour slots
  - `Earth`: boots, barding
  - `Fire`: gloves
  - `Air`: cloak
  - `Ice`: helmet, hat

Conflicts:

- Enhancers cannot be added to items with `-Cast`.
- `*Silence` conflicts with enhancer properties.

Suggested classification:

- `kind`: `spell_school`
- `polarity`: `positive`

## Penalty Properties

| Property | Meaning | Value | Notes |
| --- | --- | --- | --- |
| `*Noise` | melee attack noise | positive integer | melee weapon only |
| `-Tele` | prevents teleportation | boolean | conflicts with `+Blink` |
| `*Rage` | chance to berserk on melee attack | positive integer | melee weapon only |
| `^Contam` | magical contamination risk | boolean-like positive | restricted on talismans |
| `*Corrode` | corrosion risk | boolean | conflicts with `rCorr` |
| `^Drain` | drain risk | boolean | restricted on talismans |
| `*Slow` | slow risk | boolean | negative |
| `^Fragile` | destroyed when unequipped | boolean | random generation restricted on armour/talisman/ring |
| `*Silence` | silence risk | boolean | conflicts with enhancer properties |
| `Bane` | harmful bane property | boolean | weapon/armour only |

Suggested classification:

- `kind`: `penalty`
- `polarity`: `negative`

## Intrinsic Properties Displayed Directly In Descriptions

The following properties can appear inside randart description braces, so the parser should recognize them. However,
they should not be classified as general randart-added properties.

| Display Property | Typical Origin | Example Base Subtype | Suggested Origin |
| --- | --- | --- | --- |
| `AC` | ring intrinsic | `ring of protection` | `intrinsic` |
| `EV` | ring intrinsic | `ring of evasion` | `intrinsic` |
| `SH` | amulet intrinsic | `amulet of reflection` | `intrinsic` |

Example:

```text
the ring of Gairch {rPois AC+4}
[ring of protection]
```

Here `AC+4` is not a new randart-added property. It comes from the `ring of protection` base type. The remaining
randart-added property is `rPois`.

```text
the amulet "Buosiylo" {Reflect Rampage rC++ Regen+ SH+5}
[amulet of reflection]
```

Here `SH+5` and `Reflect` come from `amulet of reflection` as intrinsic/base properties. The remaining randart-added
property candidates are `Rampage`, `rC++`, and `Regen+`.

Recommended parser handling:

- The property tokenizer recognizes `AC`, `EV`, `SH`, and `Reflect`.
- Read the bracket subtype shown in artifact info first.
- If subtype is `ring of protection`, classify `AC` as `origin: intrinsic`.
- If subtype is `ring of evasion`, classify `EV` as `origin: intrinsic`.
- If subtype is `amulet of reflection`, classify `SH` and `Reflect` as `origin: intrinsic` or
  `origin: base_subtype`.
- Randart analysis keeps only properties whose origin is `randart_property`.

## Random-Generation Candidate Property Set

The minimum set usable by parser/schema code as "randart-added property candidates" is:

```text
Str
Int
Dex
rF
rC
rElec
rPois
rN
Will
SInv
+Inv
Fly
+Blink
*Noise
-Tele
*Rage
^Contam
Slay
Stlth
MP
Regen
rCorr
*Corrode
^Drain
*Slow
^Fragile
Harm
Rampage
Archmagi
Conj
Hexes
Summ
Necro
Tloc
Fire
Ice
Air
Earth
Alch
Forge
*Silence
Bane
```

Handle these separately:

```text
weapon brand
armour ego
```

## Property Groups Outside The General Random Pool

The following properties may exist in enums or description output, but should not be treated as general randart-added
property candidates. If a property can visibly appear in item descriptions, such as `AC`, `EV`, or `SH`, the parser
should keep it and record a separate `origin`.

```text
AC
EV
HP
SH
Clar
BAcc
BDam
Delay
RMsl
nupgr
rMut
Acrobat
RegenMP
Wiz
```

Legacy or current zero-weight properties:

```text
+Rage
-Cast
*Tele
Hungry
Acc
*Curse
+Fog
SustAt
+Twstr
Tmut
```

Notes:

- `AC`, `EV`, `SH`, `Wiz`, `Acrobat`, `RegenMP`, and similar properties may appear through jewellery base type,
  armour ego, amulet/ring intrinsic effects, fixed artifacts, and similar origins.
- `-Cast` has negative-property generation code, but its general random selection weight is zero.

## Suggested Parser Classification

| Category | Properties |
| --- | --- |
| `brand` | weapon brand |
| `ego` | armour ego |
| `stat` | `Str`, `Int`, `Dex` |
| `resistance` | `rF`, `rC`, `rElec`, `rPois`, `rN`, `Will`, `rCorr` |
| `combat` | `Slay` |
| `resource` | `MP` |
| `utility` | `SInv`, `+Inv`, `Fly`, `+Blink`, `Regen`, `Harm`, `Rampage`, `Archmagi` |
| `spell_school` | `Conj`, `Hexes`, `Summ`, `Necro`, `Tloc`, `Fire`, `Ice`, `Air`, `Earth`, `Alch`, `Forge` |
| `penalty` | `*Noise`, `-Tele`, `*Rage`, `^Contam`, `*Corrode`, `^Drain`, `*Slow`, `^Fragile`, `*Silence`, `Bane` |

## Source Notes

- `crawl-ref/source/artefact-prop-type.h`: artefact property enum
- `crawl-ref/source/artefact.cc`: `artp_data`, randart property generation, item compatibility restrictions
- `crawl-ref/source/describe.cc`: property display formatting
