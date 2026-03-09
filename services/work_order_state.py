from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from services.models import MaterialItem, WorkOrderDocument, WorkOrderHeader
from services.work_order_defaults import default_fabric_items, default_trim_items, empty_header_data, empty_material_row


@dataclass
class WorkOrderState:
    header_data: Dict[str, str] = field(default_factory=empty_header_data)
    fabric_items: List[Dict[str, str]] = field(default_factory=default_fabric_items)
    trim_items: List[Dict[str, str]] = field(default_factory=default_trim_items)
    current_image_path: Optional[str] = None
    is_dirty: bool = False

    def reset(self) -> None:
        self.header_data = empty_header_data()
        self.fabric_items = default_fabric_items()
        self.trim_items = default_trim_items()
        self.current_image_path = None
        self.is_dirty = False

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def has_any_data(self) -> bool:
        if self.is_dirty or self.current_image_path:
            return True
        if self.header_data and any((value or "").strip() for value in self.header_data.values()):
            return True
        return self._items_have_value(self.fabric_items) or self._items_have_value(self.trim_items)

    def update_header(self, patch: Dict[str, str]) -> None:
        if not isinstance(patch, dict):
            return
        if not isinstance(self.header_data, dict):
            self.header_data = {}
        self.header_data.update(patch)
        self.mark_dirty()

    def update_change_note(self, text: str) -> None:
        self.update_header({"change_note": (text or "").rstrip()})

    def update_material_patch(self, target: str, idx: int, patch: Dict[str, str]) -> None:
        if idx < 0 or not isinstance(patch, dict):
            return
        items = self._target_items(target)
        while len(items) <= idx:
            items.append(empty_material_row())
        items[idx].update(patch)
        self.mark_dirty()

    def add_material_item(self, target: str, max_items: int = 9) -> int | None:
        items = self._target_items(target)
        if len(items) >= max_items:
            return None
        items.append(empty_material_row())
        self.mark_dirty()
        return len(items) - 1

    def remove_material_item(self, target: str, idx: int) -> bool:
        items = self._target_items(target)
        if 0 <= idx < len(items):
            del items[idx]
            self.mark_dirty()
            return True
        return False

    def to_document(self) -> WorkOrderDocument:
        return WorkOrderDocument.from_raw(
            header=self.header_data,
            fabrics=self.fabric_items,
            trims=self.trim_items,
            image_attached=bool(self.current_image_path),
        )

    def normalized_header(self) -> Dict[str, str]:
        return WorkOrderHeader.from_dict(self.header_data).to_dict()

    def normalized_fabrics(self) -> List[Dict[str, str]]:
        return [MaterialItem.from_dict(item).to_dict() for item in self.fabric_items]

    def normalized_trims(self) -> List[Dict[str, str]]:
        return [MaterialItem.from_dict(item).to_dict() for item in self.trim_items]

    def _target_items(self, target: str) -> List[Dict[str, str]]:
        if target == "fabric":
            if self.fabric_items is None:
                self.fabric_items = default_fabric_items()
            return self.fabric_items
        if self.trim_items is None:
            self.trim_items = default_trim_items()
        return self.trim_items

    @staticmethod
    def _items_have_value(items: List[Dict[str, str]] | None) -> bool:
        for row in items or []:
            if MaterialItem.from_dict(row).has_any_value():
                return True
        return False
