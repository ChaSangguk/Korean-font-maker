import unittest

from fontmaker.layout import layout_type, slots_for


class LayoutSlotTests(unittest.TestCase):
    def test_all_five_requested_layout_types_are_distinct(self):
        self.assertEqual(layout_type("ㅏ"), "type-1")
        self.assertEqual(layout_type("ㅗ"), "type-2-1")
        self.assertEqual(layout_type("ㅘ"), "type-2-2")
        self.assertEqual(layout_type("ㅜ"), "type-3-1")
        self.assertEqual(layout_type("ㅝ"), "type-3-2")

    def test_vertical_vowel_without_final_uses_left_and_right_slots(self):
        self.assertEqual(
            slots_for("ㅏ", False),
            {"initial": (2, 4, 36, 56), "medial": (40, 4, 22, 56)},
        )

    def test_vertical_vowel_with_final_reserves_bottom_slot(self):
        self.assertEqual(
            slots_for("ㅏ", True),
            {
                "initial": (2, 2, 36, 36),
                "medial": (40, 2, 22, 36),
                "final": (8, 42, 48, 20),
            },
        )

    def test_horizontal_vowel_without_final_uses_top_and_bottom_slots(self):
        self.assertEqual(
            slots_for("ㅗ", False),
            {"initial": (6, 2, 52, 36), "medial": (6, 40, 52, 22)},
        )

    def test_horizontal_vowel_with_final_uses_three_rows(self):
        self.assertEqual(
            slots_for("ㅜ", True),
            {
                "initial": (8, 2, 48, 24),
                "medial": (6, 28, 52, 14),
                "final": (8, 44, 48, 18),
            },
        )

    def test_type_2_2_compound_vowel_uses_full_l_shaped_area(self):
        self.assertEqual(
            slots_for("ㅘ", False),
            {"initial": (4, 4, 28, 28), "medial": (2, 2, 60, 60)},
        )

    def test_type_3_2_compound_vowel_has_its_own_layout(self):
        self.assertEqual(
            slots_for("ㅝ", False),
            {"initial": (4, 2, 28, 30), "medial": (2, 2, 60, 60)},
        )
