---
name: dcss-item-audit
description: Audit DCSS item, artefact, property-token, equipment-stat, and morgue parsing behavior against real Crawl morgue output and DCSS source conventions. Use when reviewing or changing EQUIPS.md, arti_parser item parsing/classification/scoring, artifact attributes, Ashenzari cursed equipment handling, base item inference, unrandart exclusion, weapon/armour/jewellery/staff/talisman rules, or API/frontend item display contracts.
---

# DCSS Item Audit

## Core Workflow

1. Start from real evidence. Prefer local raw morgue records, checked-in fixtures, or publicly archived morgues before relying on source-code inference.
2. Compare three surfaces:
   - raw morgue item line and following description block
   - parser/model output (`all_attributes`, `random_attributes`, `ignored_attributes`, base item, category, subtype)
   - user-facing API/frontend display contract
3. Keep service boundaries intact:
   - parsing/classification/evaluation belongs in `arti_parser`
   - gallery response shaping belongs in `api`
   - display only belongs in `frontend`
   - crawl/raw storage belongs in `crawl_service`
4. Treat item property block tokens as the primary parser input. Use following description lines only to attach descriptions or validate meaning, unless the existing parser explicitly consumes them.
5. Do not run tests unless the user explicitly asks. Use static review, targeted source reads, and narrow diffs by default.

## Evidence Gathering

Use `rg` first:

```bash
rg -n "Ashenzari|cursed .*\\{|It has a curse which improves|Inventory:|Jewellery|Armour|Magical Staves" .
rg -n "INTERNAL_PROPERTY_TOKENS|ARTIFACT_PROPERTY_BLOCK_RE|artifact_ignored_attributes|parse_property_token" arti_parser
```

If local real morgue records are not present, use a few public archived morgues and quote only short excerpts:

```bash
curl -fsSL "<morgue-url>" -o /tmp/morgue.txt
rg -n "\\{[^}]+\\}|It has a curse which improves|^[[:space:]]+[A-Za-z ]+: " /tmp/morgue.txt -C 2
```

When source behavior is needed, inspect upstream DCSS source after checking real morgues. Relevant source names include `artefact.cc`, `god-abil.cc`, `describe.cc`, `skills.cc`, `item-name.cc`, and item property tables.

## Ashenzari Cursed Equipment

For Ashenzari-specific audits, read `references/ashenzari-morgue-tokens.md`.

Default rule:
- Property block tokens such as `Self`, `Melee`, `Range`, `Elem`, `Sorc`, `Comp`, `Bglg`, `Fort`, `Cun`, `Dev`, and old `Evo` are Ashenzari curse group metadata.
- Preserve those tokens in `ignored_attributes`.
- Exclude them from `all_attributes`, `random_attributes`, scoring, filters, and item token display.
- Do not treat explanation text skills such as `Fighting`, `Spellcasting`, `Maces & Flails`, or `Shapeshifting` as artifact properties unless they appear as actual property block tokens in the raw item line.

## Review Checks

When auditing an item change, verify:

- `cursed`/`chaotic` prefixes are status text, not part of the normalized artifact identity.
- fixed artefacts remain excluded even when cursed or renamed by Ashenzari.
- base intrinsic attributes do not leak into `random_attributes`.
- ignored/internal tokens do not appear in Gallery API `allAttributes` or frontend token rows.
- multi-word properties remain a single token when the morgue property block uses spaces or `&`.
- source examples in docs match observed morgue strings, not imagined normalized forms.

## Reporting

Report in Korean for this repository. Lead with concrete findings and file references. Include the raw morgue excerpt shape that proves the behavior, but keep quotes short. If you changed docs or code, state exactly which token rules changed and whether tests were intentionally not run.
