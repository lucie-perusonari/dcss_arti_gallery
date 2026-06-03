from __future__ import annotations


def artifact_document(
    name: str = 'the +1 cloak "Rain" {rPois}',
    source_name: str = "morgue-wiiwiwi-20260516-185425.txt",
    source_url: str = "https://example.test/morgue.txt",
    line_no: int = 2,
    attributes: list[str] | None = None,
    base_item: str = "cloak",
    item_class: str = "armour",
    item_subtype: str = "cloak",
    enchantment: int | None = 1,
    brand: str | None = None,
    base_subtype: str | None = None,
    armour_slot: str | None = "cloak",
    jewellery_slot: str | None = None,
    **ignored,
) -> dict:
    tokens = attributes or ["rPois"]
    player = _player_from_source(source_name)
    artifact_id = _artifact_id(name, source_name, line_no)
    evaluation = {
        "total": 42,
        "offense": 0,
        "defense": 8,
        "utility": 3,
        "penalty": 0,
        "base_fit": 12,
        "grade": "좋음",
    }
    return {
        "id": artifact_id,
        "name": name,
        "base_item": base_item,
        "base_subtype": base_subtype,
        "item_class": item_class,
        "item_subtype": item_subtype,
        "weapon_subtype": "ranged" if item_class == "weapon" and base_item in {"shortbow", "longbow"} else None,
        "armour_slot": armour_slot,
        "jewellery_slot": jewellery_slot,
        "enchantment": enchantment,
        "brand": brand,
        "source": {
            "player": player,
            "file": source_name,
            "url": source_url,
            "line": line_no,
        },
        "attributes": [
            {
                "token": token,
                "key": token.rstrip("+-0123456789") or token,
                "value": True,
                "description": "",
            }
            for token in tokens
        ],
        "all_attributes": tokens,
        "base_attributes": [],
        "random_attributes": tokens,
        "all_attribute_text": " ".join(tokens),
        "base_attribute_text": "",
        "random_attribute_text": " ".join(tokens),
        "evaluation": evaluation,
        "visible_item_description": tokens,
        "visible_description_labels": [],
        "raw_text_block": name,
        "item_location": None,
        "item_source": None,
    }


def _artifact_id(name: str, source_name: str, line_no: int) -> str:
    return f"{name.lower().replace(' ', '-')[:32]}-{source_name}-{line_no}"


def _player_from_source(source_name: str) -> str:
    parts = source_name.split("-")
    return parts[1] if len(parts) > 2 and source_name.startswith("morgue-") else ""
