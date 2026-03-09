from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

REQUIRED_HEADER_KEYS: tuple[str, ...] = (
    "date",
    "style_no",
    "factory",
    "cost_display",
    "labor_display",
    "loss_display",
    "sale_price_display",
)

REQUIRED_MATERIAL_KEYS: tuple[str, ...] = (
    "거래처",
    "품목",
    "수량",
    "단가",
    "총액",
)


def is_nonempty(value) -> bool:
    return bool(str(value or "").strip())


def row_has_required_fields(row: dict, required_keys: Iterable[str] = REQUIRED_MATERIAL_KEYS) -> bool:
    if not isinstance(row, dict):
        return False
    return all(is_nonempty(row.get(key, "")) for key in required_keys)


def has_basic_info(header_data: Dict[str, str] | None) -> bool:
    if not isinstance(header_data, dict):
        return False
    return all(is_nonempty(header_data.get(key, "")) for key in REQUIRED_HEADER_KEYS)


def has_completed_material(items: Iterable[dict] | None) -> bool:
    return any(row_has_required_fields(row) for row in (items or []))


def get_save_requirement_statuses(header_data: Dict[str, str] | None, fabrics: Iterable[dict] | None, trims: Iterable[dict] | None) -> List[Tuple[str, bool]]:
    return [
        ("기본사항", has_basic_info(header_data)),
        ("원단정보 1개 이상", has_completed_material(fabrics)),
        ("부자재정보 1개 이상", has_completed_material(trims)),
    ]
