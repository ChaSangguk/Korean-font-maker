import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from fontmaker.project import FontProject


class FontProjectTests(unittest.TestCase):
    def test_saves_a_component_and_generates_a_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "내 게임 폰트")
            glyph = Image.new("L", (32, 32), 0)
            project.save_component("initial:ㄱ:vertical-open", glyph)

            preview = project.render_text("가각")

            self.assertEqual(preview.size, (128, 64))
            self.assertTrue((project.path / "project.json").exists())

    def test_vertical_open_components_are_placed_left_and_right(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "슬롯 테스트")
            project.save_component("initial:ㄱ:vertical-open", Image.new("L", (36, 56), 0))
            project.save_component("medial:ㅏ:open", Image.new("L", (22, 56), 0))

            glyph = project.render_syllable("가")

            self.assertEqual(glyph.getpixel((10, 16)), 0)
            self.assertEqual(glyph.getpixel((50, 16)), 0)
            self.assertEqual(glyph.getpixel((39, 16)), 255)

    def test_vertical_final_components_reserve_a_bottom_row(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "슬롯 테스트")
            project.save_component("initial:ㄱ:vertical-final", Image.new("L", (36, 36), 0))
            project.save_component("medial:ㅏ:final", Image.new("L", (22, 36), 0))
            project.save_component("final:ㄱ:vertical-final", Image.new("L", (48, 20), 0))

            glyph = project.render_syllable("각")

            self.assertEqual(glyph.getpixel((10, 12)), 0)
            self.assertEqual(glyph.getpixel((50, 12)), 0)
            self.assertEqual(glyph.getpixel((32, 52)), 0)
            self.assertEqual(glyph.getpixel((32, 40)), 255)

    def test_horizontal_open_components_are_placed_top_and_bottom(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "슬롯 테스트")
            project.save_component("initial:ㄱ:top-open", Image.new("L", (52, 36), 0))
            project.save_component("medial:ㅗ:open", Image.new("L", (52, 22), 0))

            glyph = project.render_syllable("고")

            self.assertEqual(glyph.getpixel((24, 12)), 0)
            self.assertEqual(glyph.getpixel((24, 50)), 0)
            self.assertEqual(glyph.getpixel((24, 39)), 255)

    def test_horizontal_final_uses_shared_horizontal_final_component(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "슬롯 테스트")
            project.save_component("final:ㄱ:horizontal-final", Image.new("L", (48, 18), 0))

            glyph = project.render_syllable("곡")

            self.assertEqual(glyph.getpixel((32, 52)), 0)

    def test_type_2_2_vowel_preserves_its_l_shape_around_the_initial(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "복합 모음 테스트")
            project.save_component("initial:ㄱ:top-right-open", Image.new("L", (28, 28), 0))
            vowel = Image.new("L", (60, 60), 255)
            draw = ImageDraw.Draw(vowel)
            draw.rectangle((48, 0, 59, 59), fill=0)
            draw.rectangle((0, 48, 59, 59), fill=0)
            project.save_component("medial:ㅘ:open", vowel)

            glyph = project.render_syllable("과")

            self.assertEqual(glyph.getpixel((12, 12)), 0)   # 초성
            self.assertEqual(glyph.getpixel((54, 12)), 0)   # 중성 오른쪽 획
            self.assertEqual(glyph.getpixel((12, 54)), 0)   # 중성 아래 획
            self.assertEqual(glyph.getpixel((36, 20)), 255) # 두 조각 사이의 빈 공간

    def test_type_3_2_vowel_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "복합 모음 테스트")
            project.save_component("initial:ㄱ:bottom-right-open", Image.new("L", (28, 30), 0))
            vowel = Image.new("L", (60, 60), 255)
            draw = ImageDraw.Draw(vowel)
            draw.rectangle((48, 0, 59, 59), fill=0)
            draw.rectangle((0, 48, 59, 59), fill=0)
            project.save_component("medial:ㅝ:open", vowel)

            glyph = project.render_syllable("궈")

            self.assertEqual(glyph.getpixel((12, 12)), 0)
            self.assertEqual(glyph.getpixel((54, 12)), 0)
            self.assertEqual(glyph.getpixel((12, 54)), 0)

    def test_complete_syllable_is_split_and_saved_as_components(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "완성형 입력 테스트")
            image = Image.new("L", (64, 64), 255)
            draw = ImageDraw.Draw(image)
            draw.rectangle((8, 12, 30, 48), fill=0)
            draw.rectangle((44, 10, 55, 52), fill=0)

            saved = project.save_syllable("가", image)

            self.assertEqual(saved, ["initial:ㄱ:vertical-open", "medial:ㅏ:open"])
            self.assertTrue(all(key in project.data["components"] for key in saved))

    def test_compatibility_jamo_keys_use_distinct_component_files(self):
        with tempfile.TemporaryDirectory() as directory:
            project = FontProject.create(Path(directory), "파일명 테스트")
            first = Image.new("L", (8, 8), 0)
            second = Image.new("L", (8, 8), 255)

            project.save_component("initial:ㄱ:vertical-open", first)
            project.save_component("initial:ㄲ:vertical-open", second)

            first_file = project.data["components"]["initial:ㄱ:vertical-open"]
            second_file = project.data["components"]["initial:ㄲ:vertical-open"]
            self.assertNotEqual(first_file, second_file)
            self.assertEqual(Image.open(project.path / "components" / first_file).getpixel((0, 0)), 0)
            self.assertEqual(Image.open(project.path / "components" / second_file).getpixel((0, 0)), 255)
