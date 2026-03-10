from __future__ import annotations

from typing import Iterable

PARTNER_TYPE_FACTORY = '공장'
PARTNER_TYPE_FABRIC = '원단'
PARTNER_TYPE_TRIM = '부자재'
PARTNER_TYPE_DYEING = '염색'
PARTNER_TYPE_FINISH = '마감'
PARTNER_TYPE_OTHER = '기타'

DEFAULT_PARTNER_TYPES: tuple[str, ...] = (
    PARTNER_TYPE_FACTORY,
    PARTNER_TYPE_FABRIC,
    PARTNER_TYPE_TRIM,
    PARTNER_TYPE_DYEING,
    PARTNER_TYPE_FINISH,
    PARTNER_TYPE_OTHER,
)

PARTNER_TYPE_COLORS: tuple[str, ...] = (
    '#778295',
    '#6F8F89',
    '#9A7A6C',
    '#8A7AA8',
    '#A08060',
    '#7D8794',
    '#6784A5',
    '#7FA071',
)

PARTNER_ROLE_HINTS: dict[str, str] = {
    'factory': PARTNER_TYPE_FACTORY,
    'fabric': PARTNER_TYPE_FABRIC,
    'trim': PARTNER_TYPE_TRIM,
    'partner': PARTNER_TYPE_OTHER,
}


def normalize_partner_types(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        name = str(item).strip()
        if name and name not in seen:
            result.append(name)
            seen.add(name)
    return result



def color_for_partner_type(index: int) -> str:
    return PARTNER_TYPE_COLORS[index % len(PARTNER_TYPE_COLORS)]



def fallback_partner_types() -> list[str]:
    return list(DEFAULT_PARTNER_TYPES)
