# DCSS Randart Luxury Scoring Formula Draft

This document defines a scoring formula for evaluating DCSS random artifacts (randarts) from a "luxury item"
perspective.

## Judgment Culture Referenced

DCInside roguelike gallery posts tagged around `돌품명품` usually show an item screenshot and let recommendations or
comments judge whether the item qualifies as a luxury randart. A 2019 `돌품명품대회` notice-style post used separate
scoring categories and bonus conditions for weapons, armour, and jewellery.

Observed examples include:

- `돌품명품) 체이신도 돌품명품 출품합니다.`: a submission-style post with views, recommendations, and comments
- `ㄷㅈ) 돌품명품`: a high-recommendation single item screenshot post
- `돌품명품 가능?`: a title that asks whether an item can qualify
- `돌품명품 심플이즈베스트`: a title emphasizing clean strengths over complex option piles

Therefore, luxury scoring should not measure raw combat power alone. It should also consider whether the item is
actually usable, whether it fits a build, whether penalties are tolerable, and whether the item is impressive enough
to show off.

The useful lessons from contest-style scoring are:

- Weapons and armour judge enchantment, base type, and brand/ego on separate axes.
- Auxiliary armour and jewellery receive extra value because their slots are highly valuable.
- Recommendation and comment counts can be scored, so "performance + community reaction" both matter.
- Unusual combinations, cursed options, identification context, and screenshot quality can matter as bonus signals.

Similar English-language expressions and good randart examples from Reddit `r/dcss` are summarized separately in
[`reddit_randart_language.md`](../ko/research/randart-corpus/reddit_randart_language.md).

## Total Score

```text
luxury_score = round(
    base_fit
  + power
  + synergy
  + purity
  + flex
  + timing
)
```

Clamp the total score to `0..100`.

| Component | Points | Meaning |
| --- | ---: | --- |
| `base_fit` | 20 | Is the base item or slot good by itself? |
| `power` | 30 | Raw performance of the options |
| `synergy` | 20 | How well build and properties reinforce each other |
| `purity` | 15 | Few penalties and little junk |
| `flex` | 10 | Rare high roll, brag value, or meme value |
| `timing` | 5 | Whether the item changes the game when found |

## Grades

| Score | Grade | Judgment |
| ---: | --- | --- |
| `90..100` | `돌품명품` | A luxury item likely to get a reaction if posted |
| `80..89` | `명품` | A premium item that is strong in most situations |
| `65..79` | `실전템` | Good in practice, but not very showy |
| `45..64` | `애매템` | Depends heavily on build or context |
| `0..44` | `돌품` | Penalties, anti-synergy, or weak base are significant |

`grade` is the practical-use grade. Community-style luxury judgment separately uses `luxury_grade`, which combines
the practical score with `rarity_score`, a rarity signal based on `random_attributes`. Base item intrinsics, ring
subtype effects, staff/talisman base effects, and armour base properties are excluded from rarity scoring. High weapon
or armour enchantment is still included in `rarity_score`, because it is a core luxury signal.

## Rarity Score

`rarity_score` measures how unusual the compression of randart-added options is. The current baseline follows the
simulation in `crawl_service/docs/ko/research/randart-corpus/rarity_report.md`.

| Signal | Score |
| --- | ---: |
| `Slay+6` or higher | 45 |
| `Slay+4` or higher | 25 |
| `Slay+3` or higher on jewellery/auxiliary armour | 15 |
| Four or more resistance/Will families | 30 |
| Three or more resistance/Will families | 20 |
| `Slay + stat + resistance/Will` compression on jewellery | 15 |
| Weapon `+9` or higher | 30 |
| Weapon `+7..+8` | 20 |
| Weapon `+5..+6` | 10 |
| Auxiliary armour `+4` or higher | 25 |
| Auxiliary armour `+2..+3` | 10 |
| Body armour/shield `+15` or higher | 45 |
| Body armour/shield `+10..+14` | 35 |
| Body armour/shield `+7..+9` | 25 |
| Body armour/shield `+5..+6` | 10 |
| Rare signal above with no penalty | 5 |
| Has penalty | `-10..-25` |

`luxury_grade` uses:

| Condition | Grade |
| --- | --- |
| `practical_score >= 80` and `rarity_score >= 60` | `전설급` |
| `rarity_score >= 45` and `practical_score >= 55` | `돌품명품 후보` |
| `practical_score >= 65` and `rarity_score >= 30` | `명품` |
| `practical_score >= 65` | `실전템` |
| `rarity_score >= 30` | `희귀 잡템` |
| `practical_score >= 45` | `애매템` |
| otherwise | `돌품` |

## 1. Base Fit: 0..20

This measures whether the base item itself is good. With identical options, naturally strong bases such as `broad
axe`, `eveningstar`, `gold dragon scales`, `cloak`, `boots`, `ring`, or `amulet` score higher.

```text
base_fit = slot_value + base_item_value + enchant_value + ego_or_brand_value
```

### Common Slot Value

| Slot | Score |
| --- | ---: |
| amulet | 7 |
| ring | 6 |
| cloak/boots/gloves/helmet | 6 |
| body armour/shield | 5 |
| weapon | 5 |
| staff/talisman | 4 |

### Base Item Value

| Category | Score |
| --- | ---: |
| top-tier base | 6 |
| good base | 4 |
| ordinary base | 2 |
| bad base | 0 |

Examples:

- Top-tier weapons: `broad axe`, `eveningstar`, `demon whip`, `triple sword`, `hand cannon`
- Good armour: `cloak`, `boots`, `gloves`, `helmet`, `kite shield`, high-end dragon armour
- Good jewellery: ring/amulet base intrinsics that are already useful

### Enchantment, Brand, Ego

| Condition | Score |
| --- | ---: |
| Weapon/armour enchantment near cap | `0..5` |
| Good weapon brand: speed, heavy, electrocution, freezing, flaming, holy, etc. | `0..4` |
| Good armour ego: resistance, willpower, stealth, flying, archmagi, etc. | `0..4` |

Clamp `base_fit` to `20`.

## 2. Power: 0..30

Raw performance of the options. Prefer evaluating `random_attributes` after excluding base intrinsics.

```text
power = min(30, offense + defense + utility)
```

### Offense Score

| Property | Score |
| --- | ---: |
| `Slay+n` | `4 * n`, max 16 |
| `Str+n` on melee/ranged build | `1.5 * n`, max 9 |
| `Dex+n` on short blade/ranged/EV build | `1.5 * n`, max 9 |
| `Int+n` on caster build | `1.5 * n`, max 9 |
| Good weapon brand | `4..10` |
| Spell school bonus matching main spells | `3..8` |

### Defense Score

| Property | Score |
| --- | ---: |
| `AC+n` | `2 * n`, max 12 |
| `EV+n` | `2 * n`, max 12 |
| `SH+n` | `1.5 * n`, max 9 |
| `Will+` | 5 |
| `Will++` or higher | 9 |
| `rF+`, `rC+` | 4 each |
| `rF++`, `rC++` | 7 each |
| `rElec` | 6 |
| `rPois` | 4 |
| `rCorr` | 3 |
| `rN+` | 2 |
| `rN++` | 4 |
| `rN+++` | 6 |

### Utility Score

| Property | Score |
| --- | ---: |
| `SInv` | 3 |
| `Fly` | 2 |
| `Regen+` | 5 |
| `RegenMP+` | 5 |
| `Rampage` | 5 |
| `Reflect` | 6 |
| `Wiz` | 5 |
| `MP+n` | `n`, max 8 |
| `Stlth+` | 2 |
| `Stlth++` or higher | 4 |

## 3. Synergy: 0..20

This is the core of luxury value. What matters more than "strong options" is "options the current character wants."

```text
synergy = archetype_match + hole_cover + stack_quality + anti_synergy_guard
```

| Item | Score |
| --- | ---: |
| Core options match the main build | `0..8` |
| Exactly covers missing resistances/Will/defense | `0..6` |
| Options stack cleanly in the same direction | `0..4` |
| No anti-synergy | `0..2` |

Examples:

- For heavy melee, `Slay`, `rF`, `rC`, `Will`, `AC`, and `Reflect` have high synergy.
- For a Deep Elf caster, `Int`, `Wiz`, `RegenMP`, and spell schools have high synergy.
- For a stealth stabber, `Dex`, `Stlth`, `SInv`, and `Will` have high synergy.
- `Int+8` plate armour has high power, but without build context its synergy is low.

When build information is unavailable, default `synergy` to `8`. Standalone item evaluation should avoid giving
excessive build-specific points.

## 4. Purity: 0..15

This captures the "simple is best" side of luxury evaluation. Even an item with many good options loses luxury value
if it has severe penalties.

```text
purity = clamp(15 - penalty_points - junk_points, 0, 15)
```

### Penalties

| Property | Penalty |
| --- | ---: |
| `*Slow` | 8 |
| `^Drain` | 7 |
| `Fragile` | 10 |
| `-Tele` | 6 |
| `-Cast` | 8 |
| `Will-` | 6 |
| `rF-`, `rC-` | 6 each |
| `rPois-`, `rElec-` | 5 each |
| `Str-n`, `Dex-n`, `Int-n` | `n`, max 8 |
| `Stlth-` | 2 |

### Junk Options

Unrelated spell schools, excessive resistance stacking that is already covered, or meaningless stats subtract
`1..3` points each. Extreme values with meme value can recover some points through `flex`.

## 5. Flex: 0..10

This is the brag-value score closest to the DCInside `돌품명품` feel.

| Condition | Score |
| --- | ---: |
| Extreme high roll: `Slay+6` or higher, `Int+9`, `Dex+9`, `AC+8`-class | `3..5` |
| Rare combination that is also practical | `2..4` |
| Story value including penalties | `1..3` |
| Funny name, screenshot, or situation | `1..2` |

`flex` does not replace performance score. If practical value is low, cap it at 4 points.

## 6. Timing: 0..5

Timing measures how the item feels when found.

| Condition | Score |
| --- | ---: |
| Solves a core weakness from D:1 to before Lair | 5 |
| Major power jump before Lair/Orc/S-branch | 4 |
| Immediately wearable around Vaults/Depths | 3 |
| Only matters in Zot/extended | `1..2` |
| A similar better item is already available | 0 |

When acquisition timing is unknown, use default `2`.

## Type Multipliers

The same property has different value by item type.

```text
typed_score = luxury_score * type_multiplier
```

| Type | Multiplier |
| --- | ---: |
| jewellery | `1.05` |
| cloak/boots/gloves/helmet | `1.05` |
| weapon | `1.00` |
| shield/body armour | `0.98` |
| staff/talisman | `0.95` |

Jewellery and auxiliary armour are slightly boosted because their opportunity cost is low and they tend to stay useful
longer. Staff/talisman items are slightly reduced in standalone evaluation because they are highly build-dependent.

## Final Formula

```text
raw_score =
    base_fit
  + min(30, offense + defense + utility)
  + synergy
  + purity
  + flex
  + timing

luxury_score = clamp(round(raw_score * type_multiplier), 0, 100)
```

## Evaluation Examples

### Ring: `rF++ rCorr Slay+3 Stlth-`

```text
base_fit = 12    # ring + useful subtype
power    = 22    # rF++ 7, rCorr 3, Slay+3 12
synergy  = 12    # good for most combat builds
purity   = 13    # only Stlth- is a small flaw
flex     = 4     # rF++ + Slay combination
timing   = 2     # unknown timing
type     = 1.05

score = round(65 * 1.05) = 68
grade = 실전템
```

This ring is strong, but to call it `돌품명품` it would need more context such as `Will+`, `AC/EV`, another resistance,
or an early find.

### Weapon: `+9 broad axe of holy wrath {SInv Str+5 *Slow}`

```text
base_fit = 19    # good base, high enchantment, good brand
power    = 25    # weapon high roll + Str+5 + SInv
synergy  = 14    # strong for melee/extended
purity   = 7     # *Slow is a major flaw
flex     = 5     # +9 holy broad axe brag value
timing   = 2
type     = 1.00

score = 72
grade = 실전템
```

Without `*Slow`, or with defensive properties such as `rN`, `Will`, or `rF`, this would move into `명품` range.

## Implementation Notes

1. Separate original item intrinsics from randart-added properties first.
2. Without build information, use standalone evaluation mode and score `synergy` conservatively.
3. Apply diminishing returns to excessive stacking of the same property.
4. Penalties are not just flat deductions; for specific builds, they may become severe penalties.
5. Storing `practical_score`, `meme_score`, and `risk_score` separately from `luxury_score` makes it easier for the UI
   to explain why an item is `명품` or `돌품`.

## Reference Links

- DCInside roguelike gallery, `돌품명품대회를 개최합니다.`:
  <https://gall.dcinside.com/mgallery/board/view/?id=rlike&no=236434>
- DCInside roguelike gallery, `돌품명품) 체이신도 돌품명품 출품합니다.`:
  <https://gall.dcinside.com/board/view/?id=rlike&no=517964>
- DCInside roguelike gallery, `돌품명품 가능?`:
  <https://gall.dcinside.com/mgallery/board/view/?id=rlike&no=478064>
- DCInside roguelike gallery, `돌품명품 심플이즈베스트`:
  <https://gall.dcinside.com/mgallery/board/view/?id=rlike&no=395290>
