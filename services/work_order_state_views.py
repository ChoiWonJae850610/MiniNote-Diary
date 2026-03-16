from __future__ import annotations

from services.field_keys import MaterialTargets
from services.models import WorkOrderDocument, WorkOrderHeader
from services.work_order_state_helpers import clone_items, items_to_dicts


def build_document(state) -> WorkOrderDocument:
    return WorkOrderDocument(
        header=WorkOrderHeader.from_dict(state.header.to_dict()),
        fabrics=clone_items(state.fabrics),
        trims=clone_items(state.trims),
        dyeings=clone_items(state.dyeings),
        finishings=clone_items(state.finishings),
        others=clone_items(state.others),
        image_attached=bool(state.current_image_path),
    )


def normalized_items_for_target(state, target: str):
    return items_to_dicts(getattr(state, MaterialTargets.ATTRS.get(target, MaterialTargets.DEFAULT_ATTR)))
