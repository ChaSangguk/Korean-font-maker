"""Modern Hangul syllable decomposition and layout selection."""

from dataclasses import dataclass

INITIALS = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
MEDIALS = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
FINALS = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"
BASE = 0xAC00
COUNT = 11172

VERTICAL = set("ㅏㅐㅑㅒㅓㅔㅕㅖㅣ")
TOP = set("ㅗㅛㅡ")
TOP_RIGHT = set("ㅘㅙㅚㅢ")
BOTTOM = set("ㅜㅠ")
BOTTOM_RIGHT = set("ㅝㅞㅟ")


@dataclass(frozen=True)
class SyllableParts:
    initial: str
    medial: str
    final: str | None


def decompose_syllable(syllable: str) -> SyllableParts:
    if len(syllable) != 1 or not BASE <= ord(syllable) < BASE + COUNT:
        raise ValueError("현대 한글 완성형 한 글자만 입력할 수 있습니다.")
    offset = ord(syllable) - BASE
    initial = INITIALS[offset // 588]
    medial = MEDIALS[(offset % 588) // 28]
    final = None if offset % 28 == 0 else FINALS[offset % 28]
    return SyllableParts(initial, medial, final)


def compose_syllable(initial: str, medial: str, final: str | None = None) -> str:
    try:
        initial_index = INITIALS.index(initial)
        medial_index = MEDIALS.index(medial)
        final_index = FINALS.index(final or " ")
    except ValueError as error:
        raise ValueError("유효하지 않은 한글 자모입니다.") from error
    return chr(BASE + initial_index * 588 + medial_index * 28 + final_index)


def initial_form(medial: str, has_final: bool) -> str:
    if medial in VERTICAL:
        group = "vertical"
    elif medial in TOP:
        group = "top"
    elif medial in TOP_RIGHT:
        group = "top-right"
    elif medial in BOTTOM:
        group = "bottom"
    elif medial in BOTTOM_RIGHT:
        group = "bottom-right"
    else:
        raise ValueError("유효하지 않은 중성입니다.")
    return f"{group}-{'final' if has_final else 'open'}"


def final_form(medial: str) -> str:
    """Final consonants need only vertical-vowel and horizontal-vowel variants."""
    if medial in VERTICAL:
        return "vertical-final"
    if medial in TOP | TOP_RIGHT | BOTTOM | BOTTOM_RIGHT:
        return "horizontal-final"
    raise ValueError("유효하지 않은 중성입니다.")


def representative_syllables() -> list[str]:
    # Every vowel-layout group appears both without and with a final consonant.
    return ["가", "각", "고", "곡", "과", "광", "구", "국", "귀", "귁", "냐", "더"]
