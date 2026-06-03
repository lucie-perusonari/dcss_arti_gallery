from __future__ import annotations

from types import SimpleNamespace

from crawl_service.domain.documents.builder import ArtifactDocument, build_artifact_document


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
    description_lines: list[str] | None = None,
) -> ArtifactDocument:
    tokens = attributes or ["rPois"]
    raw_info = SimpleNamespace(
        source_name=source_name,
        source_url=source_url,
        line_no=line_no,
        visible_item_description=description_lines or ["rPois: It protects you from poison."],
        visible_description_labels=[],
        raw_text_block=name,
        item_location=None,
        item_source=None,
    )
    artifact_attributes = [
        SimpleNamespace(
            token=token,
            key=token.rstrip("+-0123456789") or token,
            value=True,
            description=None,
        )
        for token in tokens
    ]
    artifact_info = SimpleNamespace(
        raw_info=raw_info,
        attributes=artifact_attributes,
    )
    artifact = SimpleNamespace(
        artifact_info=artifact_info,
        name=name,
        base_item=base_item,
        enchantment=enchantment,
        brand=brand,
        base_subtype=base_subtype,
        item_class=item_class,
        item_subtype=item_subtype,
        weapon_subtype="ranged" if item_class == "weapon" and base_item in {"shortbow", "longbow"} else "melee" if item_class == "weapon" else None,
        armour_slot=armour_slot,
        jewellery_slot=jewellery_slot,
        all_attributes=tokens,
        base_attributes=[],
        random_attributes=tokens,
        all_attribute_text=" ".join(tokens),
        base_attribute_text="",
        random_attribute_text=" ".join(tokens),
    )
    evaluation = {
        "total": 42,
        "offense": 0,
        "defense": 8,
        "utility": 3,
        "penalty": 0,
        "base_fit": 12,
        "grade": "좋음",
    }
    return build_artifact_document(artifact, evaluation)
