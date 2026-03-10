from __future__ import annotations

CHOSEONG = (
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
)


def chosung_string(text: str) -> str:
    result: list[str] = []
    for ch in str(text or ''):
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            result.append(CHOSEONG[(code - 0xAC00) // 588])
        else:
            result.append(ch)
    return ''.join(result)



def normalize_keyword(text: str) -> str:
    return ''.join(str(text or '').strip().lower().split())



def matches_keyword(keyword: str, *values: str) -> bool:
    needle = normalize_keyword(keyword)
    if not needle:
        return True
    for value in values:
        normalized = normalize_keyword(value)
        chosung = normalize_keyword(chosung_string(value))
        if needle in normalized or needle in chosung:
            return True
    return False
