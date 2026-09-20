import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

from fontmaker.font_export import export_ttf
from fontmaker.project import FontProject


class FontExportTests(unittest.TestCase):
    def test_exports_a_valid_font_with_the_modern_hangul_range(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory) / "project", "내 게임 폰트")
            target = Path(directory) / "my-game-font.ttf"

            export_ttf(project, target)

            font = TTFont(target)
            cmap = font.getBestCmap()
            self.assertTrue(target.exists())
            self.assertEqual(len([code for code in cmap if 0xAC00 <= code <= 0xD7A3]), 11172)
            self.assertIn(ord("가"), cmap)

    def test_exports_drawn_component_as_a_nonempty_glyph(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory) / "project", "테스트")
            glyph = Image.new("L", (64, 64), 255)
            ImageDraw.Draw(glyph).rectangle((4, 4, 40, 12), fill=0)
            project.save_component("initial:ㄱ:vertical-open", glyph)
            target = Path(directory) / "font.ttf"

            export_ttf(project, target)

            font = TTFont(target)
            glyph_name = font.getBestCmap()[ord("가")]
            self.assertGreater(font["glyf"][glyph_name].numberOfContours, 0)
