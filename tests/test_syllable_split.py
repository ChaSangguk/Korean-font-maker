import unittest

from PIL import Image, ImageDraw

from fontmaker.syllable_split import component_keys_for, split_syllable


class SyllableSplitTests(unittest.TestCase):
    def test_ga_is_split_into_initial_and_medial_components(self):
        image = Image.new("L", (64, 64), 255)
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 12, 30, 48), fill=0)
        draw.rectangle((44, 10, 55, 52), fill=0)

        pieces = split_syllable(image, "가")

        self.assertEqual(
            set(pieces),
            {"initial:ㄱ:vertical-open", "medial:ㅏ:open"},
        )
        self.assertLess(pieces["initial:ㄱ:vertical-open"].getextrema()[0], 128)
        self.assertLess(pieces["medial:ㅏ:open"].getextrema()[0], 128)

    def test_gak_is_split_into_three_components(self):
        image = Image.new("L", (64, 64), 255)
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 8, 28, 30), fill=0)
        draw.rectangle((45, 8, 54, 30), fill=0)
        draw.rectangle((16, 48, 48, 56), fill=0)

        pieces = split_syllable(image, "각")

        self.assertEqual(
            set(pieces),
            {
                "initial:ㄱ:vertical-final",
                "medial:ㅏ:final",
                "final:ㄱ:vertical-final",
            },
        )

    def test_compound_vowel_excludes_initial_region_from_medial_piece(self):
        image = Image.new("L", (64, 64), 255)
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 8, 24, 24), fill=0)
        draw.rectangle((50, 4, 58, 58), fill=0)
        draw.rectangle((4, 50, 58, 58), fill=0)

        pieces = split_syllable(image, "과")
        medial = pieces["medial:ㅘ:open"]

        self.assertEqual(medial.getpixel((10, 10)), 255)
        self.assertEqual(medial.getpixel((52, 10)), 0)
        self.assertEqual(medial.getpixel((10, 52)), 0)

    def test_component_keys_cover_type_3_2(self):
        self.assertEqual(
            component_keys_for("궈"),
            {
                "initial": "initial:ㄱ:bottom-right-open",
                "medial": "medial:ㅝ:open",
            },
        )

