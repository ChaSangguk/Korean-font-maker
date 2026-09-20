import unittest

from PIL import Image, ImageDraw

from fontmaker.image_pipeline import extract_ink, normalize_to_box


class ImagePipelineTests(unittest.TestCase):
    def test_extract_ink_removes_light_grid_and_returns_ink_bbox(self):
        image = Image.new("RGB", (100, 100), "white")
        draw = ImageDraw.Draw(image)
        draw.line((0, 20, 99, 20), fill=(220, 220, 220), width=1)
        draw.rectangle((30, 35, 55, 70), fill="black")

        ink, bbox = extract_ink(image)

        self.assertEqual(bbox, (30, 35, 56, 71))
        self.assertEqual(ink.mode, "L")

    def test_normalization_preserves_aspect_ratio_and_padding(self):
        image = Image.new("L", (20, 40), 0)
        normalized, placement = normalize_to_box(image, (100, 100), padding=10)

        self.assertEqual(normalized.size, (100, 100))
        self.assertEqual(placement[2:], (40, 80))
        self.assertEqual(placement[:2], (30, 10))

