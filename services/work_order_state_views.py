from __future__ import annotations

from services.field_keys import MaterialTargets
from services.models import WorkOrderDocument, WorkOrderHeader
from services.work_order_state_helpers import clone_items, get_target_items, items_to_dicts


def build_document(state) -> WorkOrderDocument:
    return WorkOrderDocument(
        header=WorkOrderHeader.from_dict(state.header.to_dict()),
        fabrics=clone_items(get_target_items(state, MaterialTargets.FABRIC)),
        trims=clone_items(get_target_items(state, MaterialTargets.TRIM)),
        dyeings=clone_items(get_target_items(state, MaterialTargets.DYEING)),
        finishings=clone_items(get_target_items(state, MaterialTargets.FINISHING)),
        others=clone_items(get_target_items(state, MaterialTargets.OTHER)),
        image_attached=bool(state.current_image_path),
    )


def normalized_items_for_target(state, target: str):
    return items_to_dicts(get_target_items(state, target))
