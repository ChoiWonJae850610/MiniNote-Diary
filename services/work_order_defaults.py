from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

EMPTY_MATERIAL_ROW: Dict[str, str] = {
    "거래처": "",
    "품목": "",
    "수량": "",
    "단위": "",
    "단가": "",
    "총액": "",
}


def empty_material_row() -> Dict[str, str]:
    return dict(EMPTY_MATERIAL_ROW)


def default_fabric_items() -> List[Dict[str, str]]:
    return [empty_material_row()]


def default_trim_items() -> List[Dict[str, str]]:
    return [empty_material_row()]


def empty_header_data() -> Dict[str, str]:
    return {}


def clone_material_items(items: List[Dict[str, str]] | None) -> List[Dict[str, str]]:
    if not items:
        return [empty_material_row()]
    return [deepcopy(it) if isinstance(it, dict) else empty_material_row() for it in items]
