from __future__ import annotations

from crawl_service.artifacts.models import (
    ArtifactDocument,
    ArtifactDocumentAttribute,
    ArtifactDocumentEvaluation,
    ArtifactDocumentSource,
)


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
    artifact_attributes = [
        ArtifactDocumentAttribute(
            token=token,
            key=token.rstrip("+-0123456789") or token,
            value=True,
            description=None,
        )
        for token in tokens
    ]
    return ArtifactDocument(
        id="the-1-cloak-rain-rpois-testid",
        name=name,
        base_item=base_item,
        base_subtype=base_subtype,
        item_class=item_class,
        item_subtype=item_subtype,
        weapon_subtype="ranged" if item_class == "weapon" and base_item in {"shortbow", "longbow"} else "melee" if item_class == "weapon" else None,
        armour_slot=armour_slot,
        jewellery_slot=jewellery_slot,
        enchantment=enchantment,
        brand=brand,
        source=ArtifactDocumentSource(
            player="wiiwiwi",
            file=source_name,
            url=source_url,
            line=line_no,
        ),
        attributes=artifact_attributes,
        all_attributes=tokens,
        base_attributes=[],
        random_attributes=tokens,
        all_attribute_text=" ".join(tokens),
        base_attribute_text="",
        random_attribute_text=" ".join(tokens),
        evaluation=ArtifactDocumentEvaluation(
            total=42,
            offense=0,
            defense=8,
            utility=3,
            penalty=0,
            base_fit=12,
            grade="좋음",
        ),
        visible_item_description=description_lines or ["rPois: It protects you from poison."],
        visible_description_labels=[],
        raw_text_block=name,
        item_location=None,
        item_source=None,
    )
