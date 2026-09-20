"""Split a handwritten complete syllable into reusable jamo components."""

from PIL import Image, ImageDraw, ImageOps

from .hangul import decompose_syllable, final_form, initial_form
from .layout import layout_type, slots_for


def component_keys_for(syllable: str) -> dict[str, str]:
    parts = decompose_syllable(syllable)
    state = "final" if parts.final else "open"
    keys = {
        "initial": f"initial:{parts.initial}:{initial_form(parts.medial, parts.final is not None)}",
        "medial": f"medial:{parts.medial}:{state}",
    }
    if parts.final:
        keys["final"] = f"final:{parts.final}:{final_form(parts.medial)}"
    return keys


def split_syllable(image: Image.Image, syllable: str) -> dict[str, Image.Image]:
    """Cut an already aligned 64×64 syllable using its known layout slots."""
    parts = decompose_syllable(syllable)
    if image.size != (64, 64):
        image = image.resize((64, 64), Image.Resampling.LANCZOS)
    grayscale = ImageOps.grayscale(image)
    # Ignore pale printed/canvas guides and keep only the user's dark strokes.
    clean = grayscale.point(lambda value: 0 if value < 128 else 255, mode="L")
    slots = slots_for(parts.medial, parts.final is not None)
    keys = component_keys_for(syllable)
    pieces: dict[str, Image.Image] = {}
    kind = layout_type(parts.medial)

    for role, key in keys.items():
        x, y, width, height = slots[role]
        piece = clean.crop((x, y, x + width, y + height))
        if role == "medial" and kind in {"type-2-2", "type-3-2"}:
            # The compound-medial canvas surrounds the initial. Remove the
            # overlapping initial slot so its strokes cannot leak into ㅘ/ㅝ.
            initial_x, initial_y, initial_width, initial_height = slots["initial"]
            local_box = (
                max(0, initial_x - x),
                max(0, initial_y - y),
                min(width, initial_x - x + initial_width),
                min(height, initial_y - y + initial_height),
            )
            ImageDraw.Draw(piece).rectangle(local_box, fill=255)
        if ImageOps.invert(piece).getbbox() is None:
            raise ValueError(f"{syllable}에서 {role} 획을 찾지 못했습니다.")
        pieces[key] = piece
    return pieces

