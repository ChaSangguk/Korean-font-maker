"""TTF export for the MVP's monochrome, pixel-style components."""

from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image

from .hangul import BASE, COUNT
from .project import CELL_SIZE, FontProject

UPM = 1024


def _empty_glyph():
    return TTGlyphPen(None).glyph()


def _bitmap_glyph(bitmap: Image.Image):
    """Turn black bitmap runs into square TrueType outlines."""
    image = bitmap.convert("L")
    pen = TTGlyphPen(None)
    scale = UPM / CELL_SIZE
    pixels = image.load()
    for y in range(image.height):
        x = 0
        while x < image.width:
            if pixels[x, y] >= 128:
                x += 1
                continue
            start = x
            while x < image.width and pixels[x, y] < 128:
                x += 1
            left, right = start * scale, x * scale
            top, bottom = UPM - y * scale, UPM - (y + 1) * scale
            pen.moveTo((left, bottom))
            pen.lineTo((left, top))
            pen.lineTo((right, top))
            pen.lineTo((right, bottom))
            pen.closePath()
    return pen.glyph()


def _postscript_name(name: str) -> str:
    ascii_name = "".join(character for character in name if character.isascii() and character.isalnum())
    return (ascii_name or "Fontmaker")[:40]


def export_ttf(project: FontProject, destination: Path) -> Path:
    """Export all 11,172 modern Hangul syllables as a valid TTF file."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    glyph_order = [".notdef"] + [f"uni{BASE + index:04X}" for index in range(COUNT)]
    glyphs = {".notdef": _empty_glyph()}
    cmap = {}
    metrics = {".notdef": (UPM, 0)}
    for index in range(COUNT):
        codepoint = BASE + index
        glyph_name = f"uni{codepoint:04X}"
        bitmap = project.render_syllable(chr(codepoint))
        glyphs[glyph_name] = _bitmap_glyph(bitmap)
        cmap[codepoint] = glyph_name
        metrics[glyph_name] = (UPM, 0)

    family_name = str(project.data.get("name", "My Hangul Font"))
    builder = FontBuilder(UPM, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=900, descent=-124)
    builder.setupNameTable(
        {
            "familyName": family_name,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"Fontmaker:{family_name}",
            "fullName": family_name,
            "psName": _postscript_name(family_name),
            "version": "Version 0.1",
        }
    )
    builder.setupOS2(sTypoAscender=900, sTypoDescender=-124, usWinAscent=900, usWinDescent=124)
    builder.setupPost()
    builder.setupMaxp()
    builder.save(destination)
    return destination
