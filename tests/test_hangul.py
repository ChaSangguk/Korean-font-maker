import unittest

from fontmaker.hangul import (
    decompose_syllable,
    compose_syllable,
    initial_form,
    representative_syllables,
)


class HangulCompositionTests(unittest.TestCase):
    def test_decomposes_and_recomposes_a_syllable_without_final(self):
        parts = decompose_syllable("가")
        self.assertEqual(parts.initial, "ㄱ")
        self.assertEqual(parts.medial, "ㅏ")
        self.assertIsNone(parts.final)
        self.assertEqual(compose_syllable(parts.initial, parts.medial, parts.final), "가")

    def test_decomposes_and_recomposes_a_syllable_with_final(self):
        parts = decompose_syllable("광")
        self.assertEqual((parts.initial, parts.medial, parts.final), ("ㄱ", "ㅘ", "ㅇ"))
        self.assertEqual(compose_syllable(parts.initial, parts.medial, parts.final), "광")

    def test_late_final_consonants_follow_unicode_order(self):
        parts = decompose_syllable("갗")
        self.assertEqual(parts.final, "ㅊ")
        self.assertEqual(compose_syllable("ㄱ", "ㅏ", "ㅊ"), "갗")

    def test_initial_form_changes_by_vowel_group_and_final(self):
        self.assertEqual(initial_form("ㅏ", False), "vertical-open")
        self.assertEqual(initial_form("ㅏ", True), "vertical-final")
        self.assertEqual(initial_form("ㅘ", False), "top-right-open")
        self.assertEqual(initial_form("ㅜ", True), "bottom-final")

    def test_representative_sheet_covers_every_layout_group(self):
        samples = representative_syllables()
        self.assertIn("가", samples)
        self.assertIn("각", samples)
        self.assertIn("광", samples)
        self.assertEqual(len(samples), len(set(samples)))
