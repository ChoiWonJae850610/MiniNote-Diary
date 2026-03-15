from __future__ import annotations

from typing import Dict, Iterable, List

from services.formatters import format_commas_from_digits, int_from_any
from services.field_keys import HeaderKeys, MaterialTargets
from services.models import MaterialItem

_TARGET_ATTRS = {
    MaterialTargets.FABRIC: 'fabrics',
    MaterialTargets.TRIM: 'trims',
    MaterialTargets.DYEING: 'dyeings',
    MaterialTargets.FINISHING: 'finishings',
    MaterialTargets.OTHER: 'others',
}


def target_attr(target: str) -> str:
    return _TARGET_ATTRS.get(target, 'trims')


def items_to_dicts(items: List[MaterialItem]) -> List[Dict[str, str]]:
    return [item.to_dict() for item in items]


def clone_items(items: List[MaterialItem]) -> List[MaterialItem]:
    return [MaterialItem.from_dict(item.to_dict()) for item in items]


def coerce_items(items: List[Dict[str, str]] | None) -> List[MaterialItem]:
    coerced = [MaterialItem.from_dict(item) for item in (items or [])]
    return coerced or [MaterialItem()]


def items_have_value(items: List[MaterialItem] | None) -> bool:
    return any(item.has_any_value() for item in (items or []))


def sum_material_totals(items: List[MaterialItem] | None) -> int:
    return sum(int_from_any(item.total) for item in (items or []))


def needs_price_recompute(patch: Dict[str, str] | None) -> bool:
    if not isinstance(patch, dict) or not patch:
        return False
    watched_keys = {HeaderKeys.LABOR, HeaderKeys.LABOR_DISPLAY, HeaderKeys.LOSS, HeaderKeys.LOSS_DISPLAY}
    return any(key in watched_keys for key in patch)


def recompute_header_prices(header, material_groups: Iterable[List[MaterialItem]]) -> None:
    material_total = sum(sum_material_totals(items) for items in material_groups)
    material_text = str(material_total) if material_total else ''
    header.cost = material_text
    header.cost_display = format_commas_from_digits(material_text) if material_text else ''

    sale_total = material_total + int_from_any(header.labor) + int_from_any(header.loss)
    sale_text = str(sale_total) if sale_total else ''
    header.sale_price = sale_text
    header.sale_price_display = format_commas_from_digits(sale_text) if sale_text else ''
