from __future__ import annotations

from copy import deepcopy
from typing import Iterable, List

from services.common.models import MaterialItem, WorkOrderHeader


def empty_material_item() -> MaterialItem:
    return MaterialItem()


def empty_material_row() -> dict[str, str]:
    return empty_material_item().to_dict()


def default_fabric_items() -> List[dict[str, str]]:
    return [empty_material_row()]


def default_trim_items() -> List[dict[str, str]]:
    return [empty_material_row()]


def empty_header_model() -> WorkOrderHeader:
    return WorkOrderHeader()


def empty_header_data() -> dict[str, str]:
    return empty_header_model().to_dict()


def clone_material_items(items: Iterable[dict[str, str]] | None) -> List[dict[str, str]]:
    if not items:
        return [empty_material_row()]
    rows: List[dict[str, str]] = []
    for item in items:
        if isinstance(item, dict):
            rows.append(deepcopy(MaterialItem.from_dict(item).to_dict()))
        else:
            rows.append(empty_material_row())
    return rows or [empty_material_row()]
