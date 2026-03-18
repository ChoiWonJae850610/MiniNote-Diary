from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from services.common.field_keys import MaterialKeys
from services.common.models import MaterialItem, WorkOrderDocument, WorkOrderHeader


def is_nonempty(value) -> bool:
    return bool(str(value or '').strip())


def _material_item(row: dict | MaterialItem) -> MaterialItem:
    return row if isinstance(row, MaterialItem) else MaterialItem.from_dict(row)


def _digits_text(value: str) -> str:
    return str(value or '').replace(',', '').strip()


def row_has_required_fields(row: dict | MaterialItem) -> bool:
    item = _material_item(row)
    return item.has_required_fields()


def row_has_any_meaningful_value(row: dict | MaterialItem) -> bool:
    item = _material_item(row)
    return item.has_any_value()


def row_is_save_complete(row: dict | MaterialItem) -> bool:
    item = _material_item(row)
    data = item.to_dict()
    required_text_keys = (MaterialKeys.VENDOR, MaterialKeys.ITEM, MaterialKeys.UNIT)
    if not all(str(data.get(key, '') or '').strip() for key in required_text_keys):
        return False
    required_numeric_keys = (MaterialKeys.QTY, MaterialKeys.UNIT_PRICE, MaterialKeys.TOTAL)
    return all(_digits_text(data.get(key, '')) != '' for key in required_numeric_keys)


def has_invalid_partial_material(items: Iterable[dict | MaterialItem] | None) -> bool:
    for row in (items or []):
        if row_has_any_meaningful_value(row) and not row_is_save_complete(row):
            return True
    return False


def has_basic_info(header_data: Dict[str, str] | WorkOrderHeader | None) -> bool:
    header = header_data if isinstance(header_data, WorkOrderHeader) else WorkOrderHeader.from_dict(header_data)
    return header.has_required_fields()


def has_completed_material(items: Iterable[dict | MaterialItem] | None) -> bool:
    return any(row_is_save_complete(row) for row in (items or []))


def has_any_completed_material_group(*groups: Iterable[dict | MaterialItem] | None) -> bool:
    return any(has_completed_material(group) for group in groups)


def has_any_invalid_material_group(*groups: Iterable[dict | MaterialItem] | None) -> bool:
    return any(has_invalid_partial_material(group) for group in groups)


def get_save_requirement_statuses(
    header_data: Dict[str, str] | WorkOrderHeader | None,
    fabrics: Iterable[dict | MaterialItem] | None,
    trims: Iterable[dict | MaterialItem] | None,
    dyeings: Iterable[dict | MaterialItem] | None = None,
    finishings: Iterable[dict | MaterialItem] | None = None,
    others: Iterable[dict | MaterialItem] | None = None,
) -> List[Tuple[str, bool]]:
    return [
        ('기본사항', has_basic_info(header_data)),
        ('외주작업 입력', not has_any_invalid_material_group(fabrics, trims, dyeings, finishings, others)),
    ]


def get_document_save_requirement_statuses(document: WorkOrderDocument) -> List[Tuple[str, bool]]:
    return get_save_requirement_statuses(
        document.header,
        document.fabrics,
        document.trims,
        document.dyeings,
        document.finishings,
        document.others,
    )
