from __future__ import annotations

from typing import Dict, Iterable, List

from services.field_keys import MaterialTargets
from services.models import MaterialItem, WorkOrderDocument, WorkOrderHeader
from services.work_order_state_helpers import clone_items, items_to_dicts


def build_document(header: WorkOrderHeader, *, fabrics: List[MaterialItem], trims: List[MaterialItem], dyeings: List[MaterialItem], finishings: List[MaterialItem], others: List[MaterialItem], image_attached: bool) -> WorkOrderDocument:
    return WorkOrderDocument(
        header=WorkOrderHeader.from_dict(header.to_dict()),
        fabrics=clone_items(fabrics),
        trims=clone_items(trims),
        dyeings=clone_items(dyeings),
        finishings=clone_items(finishings),
        others=clone_items(others),
        image_attached=image_attached,
    )


def normalized_items(items: List[MaterialItem]) -> List[Dict[str, str]]:
    return items_to_dicts(items)


def iter_material_groups(target_items) -> Iterable[List[MaterialItem]]:
    for target in MaterialTargets.ALL:
        yield target_items(target)
