#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ai_review_cli


class IdentityStabilityTests(unittest.TestCase):
    def test_existing_eof_block_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = root / "note.md"
            original = (
                "# Title\n\n"
                "body\n\n"
                "<!-- ai-review:start unit=ru000001 -->\n"
                "> [!question]- AI Review `ru000001`\n"
                "> - 待审查\n"
                "> `2026-05-06` · identity\n"
                "^ru000001\n"
                "<!-- ai-review:end -->\n"
            )
            note.write_text(original, encoding="utf-8")

            ledger = {"version": 1, "next_unit_id": 2, "by_locator": {}, "by_hash": {}}
            units = ai_review_cli.split_units(note, root, ledger, {})
            updated, created = ai_review_cli.replace_identity_blocks_for_file(note, units)

            self.assertEqual(created, 0)
            self.assertEqual(updated, original)

    def test_missing_identity_is_inserted_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = root / "note.md"
            note.write_text("# Title\n\nbody\n", encoding="utf-8")
            ledger = {"version": 1, "next_unit_id": 1, "by_locator": {}, "by_hash": {}}

            units = ai_review_cli.split_units(note, root, ledger, {})
            updated, created = ai_review_cli.replace_identity_blocks_for_file(note, units)
            self.assertEqual(created, 1)
            self.assertEqual(updated.count("<!-- ai-review:start unit="), 1)

            note.write_text(updated, encoding="utf-8")
            units = ai_review_cli.split_units(note, root, ledger, {})
            rerun, created = ai_review_cli.replace_identity_blocks_for_file(note, units)
            self.assertEqual(created, 0)
            self.assertEqual(rerun, updated)

    def test_obsidian_tag_is_not_markdown_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = root / "note.md"
            note.write_text(
                "#tag\n"
                "#中文标签\n"
                "#\u3000not-heading\n\n"
                "# Real Heading\n\n"
                "body\n",
                encoding="utf-8",
            )
            ledger = {"version": 1, "next_unit_id": 1, "by_locator": {}, "by_hash": {}}

            units = ai_review_cli.split_units(note, root, ledger, {})

            self.assertEqual(len(units), 2)
            self.assertEqual(units[0].heading, "_preamble")
            self.assertIn("#tag", units[0].content)
            self.assertIn("#中文标签", units[0].content)
            self.assertIn("#\u3000not-heading", units[0].content)
            self.assertEqual(units[1].heading, "Real Heading")

    def test_duplicate_existing_ids_are_remapped_after_first_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.md"
            second = root / "second.md"
            text = (
                "# Same\n\n"
                "body\n\n"
                "<!-- ai-review:start unit=ru000001 -->\n"
                "> [!question]- AI Review `ru000001`\n"
                "> - 待审查\n"
                "> `2026-05-06` · identity\n"
                "^ru000001\n"
                "<!-- ai-review:end -->\n"
            )
            first.write_text(text, encoding="utf-8")
            second.write_text(text, encoding="utf-8")
            ledger = {"version": 1, "next_unit_id": 2, "by_locator": {}, "by_hash": {}}
            claimed: dict[str, str] = {}

            first_units = ai_review_cli.split_units(first, root, ledger, claimed)
            second_units = ai_review_cli.split_units(second, root, ledger, claimed)

            self.assertEqual(first_units[0].unit_id, "ru000001")
            self.assertEqual(second_units[0].existing_unit_id, "ru000001")
            self.assertNotEqual(second_units[0].unit_id, "ru000001")

            updated, created = ai_review_cli.replace_identity_blocks_for_file(second, second_units)
            self.assertEqual(created, 0)
            self.assertIn(f"unit={second_units[0].unit_id}", updated)
            self.assertNotIn("unit=ru000001", updated)


if __name__ == "__main__":
    unittest.main()
