from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from services.field_keys import HeaderKeys, MaterialTargets
from services.models import MaterialItem, WorkOrderHeader
from services.schema import MAX_MATERIAL_ITEMS
from services.work_order_state_helpers import coerce_items, target_attr
from services.work_order_state_ops import add_material_item_to_state, recompute_sale_price, remove_material_item_from_state, reset_state, state_has_any_data, update_header_fields, update_material_patch_fields
from services.work_order_state_views import build_document, normalized_items_for_target


@dataclass
class WorkOrderState:
    header: WorkOrderHeader = field(default_factory=WorkOrderHeader)
    fabrics: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    trims: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    dyeings: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    finishings: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    others: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    current_image_path: Optional[str] = None
    is_dirty: bool = False

    @property
    def header_data(self) -> Dict[str, str]:
        return self.header.to_dict()

    @header_data.setter
    def header_data(self, value: Dict[str, str] | None) -> None:
        self.header = WorkOrderHeader.from_dict(value)
        recompute_sale_price(self)

    @property
    def fabric_items(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.FABRIC)

    @fabric_items.setter
    def fabric_items(self, value: List[Dict[str, str]] | None) -> None:
        self.fabrics = coerce_items(value)
        recompute_sale_price(self)

    @property
    def trim_items(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.TRIM)

    @trim_items.setter
    def trim_items(self, value: List[Dict[str, str]] | None) -> None:
        self.trims = coerce_items(value)
        recompute_sale_price(self)

    @property
    def dyeing_items(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.DYEING)

    @dyeing_items.setter
    def dyeing_items(self, value: List[Dict[str, str]] | None) -> None:
        self.dyeings = coerce_items(value)
        recompute_sale_price(self)

    @property
    def finishing_items(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.FINISHING)

    @finishing_items.setter
    def finishing_items(self, value: List[Dict[str, str]] | None) -> None:
        self.finishings = coerce_items(value)
        recompute_sale_price(self)

    @property
    def other_items(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.OTHER)

    @other_items.setter
    def other_items(self, value: List[Dict[str, str]] | None) -> None:
        self.others = coerce_items(value)
        recompute_sale_price(self)

    def reset(self) -> None:
        reset_state(self)

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def has_any_data(self) -> bool:
        return state_has_any_data(self)

    def update_header(self, patch: Dict[str, str]) -> None:
        update_header_fields(self, patch)

    def update_change_note(self, text: str) -> None:
        self.update_header({HeaderKeys.CHANGE_NOTE: (text or '').rstrip()})

    def update_material_patch(self, target: str, idx: int, patch: Dict[str, str]) -> None:
        update_material_patch_fields(self, target, idx, patch)

    def add_material_item(self, target: str, max_items: int = MAX_MATERIAL_ITEMS) -> int | None:
        return add_material_item_to_state(self, target, max_items=max_items)

    def remove_material_item(self, target: str, idx: int) -> bool:
        return remove_material_item_from_state(self, target, idx)

    def to_document(self):
        return build_document(self)

    def normalized_header(self) -> Dict[str, str]:
        return self.header.to_dict()

    def normalized_fabrics(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.FABRIC)

    def normalized_trims(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.TRIM)

    def normalized_dyeings(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.DYEING)

    def normalized_finishings(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.FINISHING)

    def normalized_others(self) -> List[Dict[str, str]]:
        return normalized_items_for_target(self, MaterialTargets.OTHER)

    def _target_items(self, target: str) -> List[MaterialItem]:
        return getattr(self, target_attr(target))
