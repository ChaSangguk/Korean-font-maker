"""A minimal complete-syllable writing plan covering all 286 input pieces."""

from .hangul import (
    BOTTOM,
    BOTTOM_RIGHT,
    FINALS,
    INITIALS,
    MEDIALS,
    TOP,
    TOP_RIGHT,
    VERTICAL,
    compose_syllable,
    decompose_syllable,
    final_form,
    initial_form,
)
from .layout import layout_type

GROUPS = [
    ("형태 1", tuple(vowel for vowel in MEDIALS if vowel in VERTICAL)),
    ("형태 2-1", tuple(vowel for vowel in MEDIALS if vowel in TOP)),
    ("형태 2-2", tuple(vowel for vowel in MEDIALS if vowel in TOP_RIGHT)),
    ("형태 3-1", tuple(vowel for vowel in MEDIALS if vowel in BOTTOM)),
    ("형태 3-2", tuple(vowel for vowel in MEDIALS if vowel in BOTTOM_RIGHT)),
]


def required_component_keys() -> set[str]:
    keys: set[str] = set()
    for initial in INITIALS:
        for _, vowels in GROUPS:
            for has_final in (False, True):
                keys.add(f"initial:{initial}:{initial_form(vowels[0], has_final)}")
    for medial in MEDIALS:
        keys.add(f"medial:{medial}:open")
        keys.add(f"medial:{medial}:final")
    for final in FINALS[1:]:
        keys.add(f"final:{final}:vertical-final")
        keys.add(f"final:{final}:horizontal-final")
    return keys


def minimal_sample_syllables() -> list[str]:
    """Return 198 syllables, the lower bound imposed by initial/final variants.

    Every syllable covers one of 190 initial variants. Eight additional
    type-1-final syllables are necessary because 27 vertical-final components
    cannot be covered by the 19 type-1-final initial variants alone.
    """
    samples: list[str] = []
    horizontal_final_index = 0
    for group_index, (_, vowels) in enumerate(GROUPS):
        for index, initial in enumerate(INITIALS):
            samples.append(compose_syllable(initial, vowels[index % len(vowels)]))

        final_sample_count = 27 if group_index == 0 else len(INITIALS)
        for index in range(final_sample_count):
            initial = INITIALS[index % len(INITIALS)]
            medial = vowels[index % len(vowels)]
            if group_index == 0:
                final = FINALS[index + 1]
            else:
                final = FINALS[horizontal_final_index % 27 + 1]
                horizontal_final_index += 1
            samples.append(compose_syllable(initial, medial, final))
    return samples


def describe_sample(syllable: str) -> str:
    parts = decompose_syllable(syllable)
    type_names = {
        "type-1": "형태 1",
        "type-2-1": "형태 2-1",
        "type-2-2": "형태 2-2",
        "type-3-1": "형태 3-1",
        "type-3-2": "형태 3-2",
    }
    final_label = "받침 있음" if parts.final else "받침 없음"
    return f"{type_names[layout_type(parts.medial)]} · {final_label}"

