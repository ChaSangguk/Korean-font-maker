"""Project persistence and a transparent composition preview."""

import json
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

from .hangul import decompose_syllable, final_form, initial_form
from .layout import Box, slots_for
from .syllable_split import split_syllable

CELL_SIZE = 64


def _file_safe(key: str) -> str:
    readable = re.sub(r"[^0-9A-Za-z_-]", "_", key)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return f"{readable}_{digest}"


@dataclass
class FontProject:
    path: Path
    data: dict
    _component_cache: dict[str, Image.Image | None] = field(default_factory=dict, init=False, repr=False)
    _resized_cache: dict[tuple[str, Box], Image.Image] = field(default_factory=dict, init=False, repr=False)
    _render_cache: dict[tuple[str, ...], Image.Image] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def create(cls, path: Path, name: str) -> "FontProject":
        path.mkdir(parents=True, exist_ok=True)
        (path / "components").mkdir(exist_ok=True)
        project = cls(path, {"name": name, "version": 1, "components": {}})
        project._write()
        return project

    def _write(self) -> None:
        (self.path / "project.json").write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def save_component(self, key: str, glyph: Image.Image) -> None:
        filename = f"{_file_safe(key)}.png"
        glyph.convert("L").save(self.path / "components" / filename)
        self.data["components"][key] = filename
        self._component_cache[key] = glyph.convert("L").copy()
        self._resized_cache = {
            cache_key: value for cache_key, value in self._resized_cache.items() if cache_key[0] != key
        }
        self._render_cache.clear()
        self._write()

    def save_syllable(self, syllable: str, image: Image.Image) -> list[str]:
        pieces = split_syllable(image, syllable)
        for key, piece in pieces.items():
            self.save_component(key, piece)
        return list(pieces)

    def _component(self, key: str) -> Image.Image | None:
        if key in self._component_cache:
            return self._component_cache[key]
        filename = self.data["components"].get(key)
        if not filename:
            self._component_cache[key] = None
            return None
        component = Image.open(self.path / "components" / filename).convert("L")
        self._component_cache[key] = component
        return component

    def render_syllable(self, syllable: str) -> Image.Image:
        parts = decompose_syllable(syllable)
        form = initial_form(parts.medial, parts.final is not None)
        keys = [
            f"initial:{parts.initial}:{form}",
            f"medial:{parts.medial}:{'final' if parts.final else 'open'}",
        ]
        if parts.final:
            keys.append(f"final:{parts.final}:{final_form(parts.medial)}")
        roles = ["initial", "medial"] + (["final"] if parts.final else [])
        layout = slots_for(parts.medial, parts.final is not None)
        loaded = [(role, key, self._component(key)) for role, key in zip(roles, keys)]
        # Missing components do not affect the bitmap, so do not prevent reuse.
        signature = tuple(key for _, key, component in loaded if component is not None)
        cached = self._render_cache.get(signature)
        if cached is not None:
            return cached
        glyph_canvas = Image.new("L", (CELL_SIZE, CELL_SIZE), 255)
        for role, key, component in loaded:
            if component is None:
                continue
            box = layout[role]
            cache_key = (key, box)
            placed = self._resized_cache.get(cache_key)
            if placed is None:
                placed = _fit_component(component, box)
                self._resized_cache[cache_key] = placed
            glyph_canvas = ImageChops.darker(glyph_canvas, placed)
        self._render_cache[signature] = glyph_canvas
        return glyph_canvas

    def render_text(self, text: str) -> Image.Image:
        canvas = Image.new("L", (max(1, len(text)) * CELL_SIZE, CELL_SIZE), 255)
        for index, character in enumerate(text):
            try:
                glyph_canvas = self.render_syllable(character)
            except ValueError:
                continue
            canvas.paste(glyph_canvas, (index * CELL_SIZE, 0))
        return canvas


def _fit_component(component: Image.Image, box: Box) -> Image.Image:
    """Crop surrounding whitespace, preserve aspect ratio, and place in a slot."""
    source = component.convert("L")
    ink_bbox = ImageOps.invert(source).getbbox()
    if ink_bbox is None:
        return Image.new("L", (CELL_SIZE, CELL_SIZE), 255)
    source = source.crop(ink_bbox)
    x, y, width, height = box
    scale = min(width / source.width, height / source.height)
    fitted_width = max(1, round(source.width * scale))
    fitted_height = max(1, round(source.height * scale))
    resized = source.resize((fitted_width, fitted_height), Image.Resampling.NEAREST)
    left = x + (width - fitted_width) // 2
    top = y + (height - fitted_height) // 2
    canvas = Image.new("L", (CELL_SIZE, CELL_SIZE), 255)
    canvas.paste(resized, (left, top))
    return canvas
