from __future__ import annotations

import unittest

from crawl_service.morgue.types import MorgueRawText
from crawl_service.core.processor import ArtifactProcessor


class ArtifactProcessorTest(unittest.TestCase):
    def test_processor_builds_sorted_artifact_documents(self) -> None:
        raw_text = MorgueRawText(
            name="morgue-wiiwiwi-20260101-000001.txt",
            url="https://example.test/morgue.txt",
            extension="txt",
            text="\n".join(
                [
                    "Inventory:",
                    ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
                    ' b - the ring "Miracles" {rCorr AC+4}',
                    "     [ring of protection]",
                    "     AC+4: It affects your AC (+4).",
                    "   Skills:",
                ]
            ),
        )

        documents = ArtifactProcessor().documents_from_raw_text(raw_text)

        self.assertEqual(len(documents), 2)
        self.assertGreaterEqual(
            documents[0].evaluation.total,
            documents[1].evaluation.total,
        )
        self.assertTrue(all(document.source.file == raw_text.name for document in documents))
        ring = next(document for document in documents if document.base_item == "ring")
        self.assertEqual(ring.base_attributes, ["AC+4"])
        self.assertEqual(ring.random_attributes, ["rCorr"])


if __name__ == "__main__":
    unittest.main()
