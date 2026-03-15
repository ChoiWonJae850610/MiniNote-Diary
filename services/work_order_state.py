from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from services.field_keys import HeaderKeys, MaterialTargets
from services.models import MaterialItem, WorkOrderHeader
from services.schema import MAX_MATERIAL_ITEMS
from services.work_order_state_helpers import (
    coerce_items,
    items_have_value,
    needs_price_recompute,
    recompute_header_prices,
    target_attr,
)
from services.work_order_state_views import build_document, iter_material_groups, normalized_items


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
        self._recompute_sale_price()

    @property
    def fabric_items(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.FABRIC)

    @fabric_items.setter
    def fabric_items(self, value: List[Dict[str, str]] | None) -> None:
        self._set_items(MaterialTargets.FABRIC, value)

    @property
    def trim_items(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.TRIM)

    @trim_items.setter
    def trim_items(self, value: List[Dict[str, str]] | None) -> None:
        self._set_items(MaterialTargets.TRIM, value)

    @property
    def dyeing_items(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.DYEING)

    @dyeing_items.setter
    def dyeing_items(self, value: List[Dict[str, str]] | None) -> None:
        self._set_items(MaterialTargets.DYEING, value)

    @property
    def finishing_items(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.FINISHING)

    @finishing_items.setter
    def finishing_items(self, value: List[Dict[str, str]] | None) -> None:
        self._set_items(MaterialTargets.FINISHING, value)

    @property
    def other_items(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.OTHER)

    @other_items.setter
    def other_items(self, value: List[Dict[str, str]] | None) -> None:
        self._set_items(MaterialTargets.OTHER, value)

    def reset(self) -> None:
        self.header = WorkOrderHeader()
        for attr in MaterialTargets.ATTRS.values():
            setattr(self, attr, [MaterialItem()])
        self.current_image_path = None
        self._recompute_sale_price()
        self.is_dirty = False

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def has_any_data(self) -> bool:
        return bool(
            self.is_dirty
            or self.current_image_path
            or self.header.has_any_value()
            or any(items_have_value(self._target_items(target)) for target in MaterialTargets.ALL)
        )

    def update_header(self, patch: Dict[str, str]) -> None:
        self.header.patch(patch)
        if needs_price_recompute(patch):
            self._recompute_sale_price()
        self.mark_dirty()

    def update_change_note(self, text: str) -> None:
        self.update_header({HeaderKeys.CHANGE_NOTE: (text or '').rstrip()})

    def update_material_patch(self, target: str, idx: int, patch: Dict[str, str]) -> None:
        if idx < 0 or not isinstance(patch, dict):
            return
        items = self._target_items(target)
        while len(items) <= idx:
            items.append(MaterialItem())
        items[idx].patch(patch)
        self._recompute_sale_price()
        self.mark_dirty()

    def add_material_item(self, target: str, max_items: int = MAX_MATERIAL_ITEMS) -> int | None:
        items = self._target_items(target)
        if len(items) >= max_items:
            return None
        items.append(MaterialItem())
        self._recompute_sale_price()
        self.mark_dirty()
        return len(items) - 1

    def remove_material_item(self, target: str, idx: int) -> bool:
        items = self._target_items(target)
        if 0 <= idx < len(items):
            del items[idx]
            if not items:
                items.append(MaterialItem())
            self._recompute_sale_price()
            self.mark_dirty()
            return True
        return False

    def to_document(self):
        return build_document(
            self.header,
            fabrics=self.fabrics,
            trims=self.trims,
            dyeings=self.dyeings,
            finishings=self.finishings,
            others=self.others,
            image_attached=bool(self.current_image_path),
        )

    def normalized_header(self) -> Dict[str, str]:
        return self.header.to_dict()

    def normalized_fabrics(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.FABRIC)

    def normalized_trims(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.TRIM)

    def normalized_dyeings(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.DYEING)

    def normalized_finishings(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.FINISHING)

    def normalized_others(self) -> List[Dict[str, str]]:
        return self._normalized_items(MaterialTargets.OTHER)

    def _set_items(self, target: str, value: List[Dict[str, str]] | None) -> None:
        setattr(self, target_attr(target), coerce_items(value))
        self._recompute_sale_price()

    def _target_items(self, target: str) -> List[MaterialItem]:
        return getattr(self, target_attr(target))

    def _normalized_items(self, target: str) -> List[Dict[str, str]]:
        return normalized_items(self._target_items(target))

    def _recompute_sale_price(self) -> None:
        recompute_header_prices(self.header, iter_material_groups(self._target_items))
