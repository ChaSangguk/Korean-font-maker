"""Fixed component slots for composing a 64×64 Hangul syllable cell."""

from .hangul import BOTTOM, BOTTOM_RIGHT, TOP, TOP_RIGHT, VERTICAL

Box = tuple[int, int, int, int]


def layout_type(medial: str) -> str:
    if medial in VERTICAL:
        return "type-1"
    if medial in TOP:
        return "type-2-1"
    if medial in TOP_RIGHT:
        return "type-2-2"
    if medial in BOTTOM:
        return "type-3-1"
    if medial in BOTTOM_RIGHT:
        return "type-3-2"
    raise ValueError("지원하지 않는 중성입니다.")


def slots_for(medial: str, has_final: bool) -> dict[str, Box]:
    """Return x, y, width, height boxes inspired by traditional Hangul blocks."""
    kind = layout_type(medial)
    if kind == "type-1":
        if has_final:
            return {
                "initial": (2, 2, 36, 36),
                "medial": (40, 2, 22, 36),
                "final": (8, 42, 48, 20),
            }
        return {"initial": (2, 4, 36, 56), "medial": (40, 4, 22, 56)}

    if kind == "type-2-1":
        if has_final:
            return {
                "initial": (8, 2, 48, 24),
                "medial": (6, 28, 52, 14),
                "final": (8, 44, 48, 18),
            }
        return {"initial": (6, 2, 52, 36), "medial": (6, 40, 52, 22)}

    if kind == "type-2-2":
        if has_final:
            return {
                "initial": (4, 2, 28, 24),
                "medial": (2, 2, 60, 40),
                "final": (8, 44, 48, 18),
            }
        return {"initial": (4, 4, 28, 28), "medial": (2, 2, 60, 60)}

    if kind == "type-3-1":
        if has_final:
            return {
                "initial": (8, 2, 48, 24),
                "medial": (6, 28, 52, 14),
                "final": (8, 44, 48, 18),
            }
        return {"initial": (6, 2, 52, 36), "medial": (6, 40, 52, 22)}

    if kind == "type-3-2":
        if has_final:
            return {
                "initial": (4, 2, 28, 26),
                "medial": (2, 2, 60, 40),
                "final": (8, 44, 48, 18),
            }
        return {"initial": (4, 2, 28, 30), "medial": (2, 2, 60, 60)}

    raise ValueError("지원하지 않는 중성입니다.")
