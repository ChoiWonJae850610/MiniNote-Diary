from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from services.common.models import MaterialItem, WorkOrderDocument, WorkOrderHeader


def is_nonempty(value) -> bool:
    return bool(str(value or '').strip())


def row_has_required_fields(row: dict | MaterialItem) -> bool:
    item = row if isinstance(row, MaterialItem) else MaterialItem.from_dict(row)
    return item.has_required_fields()


def has_basic_info(header_data: Dict[str, str] | WorkOrderHeader | None) -> bool:
    header = header_data if isinstance(header_data, WorkOrderHeader) else WorkOrderHeader.from_dict(header_data)
    return header.has_required_fields()


def has_completed_material(items: Iterable[dict | MaterialItem] | None) -> bool:
    return any(row_has_required_fields(row) for row in (items or []))


def get_save_requirement_statuses(
    header_data: Dict[str, str] | WorkOrderHeader | None,
    fabrics: Iterable[dict | MaterialItem] | None,
    trims: Iterable[dict | MaterialItem] | None,
) -> List[Tuple[str, bool]]:
    return [
        ('기본사항', has_basic_info(header_data)),
        ('원단정보 1개 이상', has_completed_material(fabrics)),
        ('부자재정보 1개 이상', has_completed_material(trims)),
    ]


def get_document_save_requirement_statuses(document: WorkOrderDocument) -> List[Tuple[str, bool]]:
    return get_save_requirement_statuses(document.header, document.fabrics, document.trims)
