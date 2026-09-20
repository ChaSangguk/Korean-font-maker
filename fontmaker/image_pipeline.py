"""Deterministic preprocessing for a photographed fixed-layout worksheet."""

from PIL import Image, ImageOps


def extract_ink(image: Image.Image, threshold: int = 128) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Return a white-on-black-free mask and the bounding box of dark handwriting.

    The worksheet grid is intentionally light, so a conservative threshold rejects it.
    """
    grayscale = ImageOps.grayscale(image)
    mask = grayscale.point(lambda pixel: 255 if pixel < threshold else 0, mode="L")
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("그림에서 충분히 진한 획을 찾지 못했습니다.")
    # Components are persisted as ordinary black ink on a white background.
    return ImageOps.invert(mask).crop(bbox), bbox


def normalize_to_box(
    ink: Image.Image, target_size: tuple[int, int], padding: int = 8
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Fit an ink image inside a target box without changing its aspect ratio."""
    width, height = ink.size
    target_width, target_height = target_size
    if width <= 0 or height <= 0 or padding * 2 >= min(target_size):
        raise ValueError("정규화할 수 없는 이미지 또는 여백입니다.")
    scale = min((target_width - padding * 2) / width, (target_height - padding * 2) / height)
    placed_width = max(1, round(width * scale))
    placed_height = max(1, round(height * scale))
    resized = ink.resize((placed_width, placed_height), Image.Resampling.LANCZOS)
    x = (target_width - placed_width) // 2
    y = (target_height - placed_height) // 2
    canvas = Image.new("L", target_size, 255)
    canvas.paste(resized, (x, y))
    return canvas, (x, y, placed_width, placed_height)
