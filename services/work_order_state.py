from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from services.models import MaterialItem, WorkOrderDocument, WorkOrderHeader
from services.schema import MAX_MATERIAL_ITEMS


@dataclass
class WorkOrderState:
    header: WorkOrderHeader = field(default_factory=WorkOrderHeader)
    fabrics: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    trims: List[MaterialItem] = field(default_factory=lambda: [MaterialItem()])
    current_image_path: Optional[str] = None
    is_dirty: bool = False

    @property
    def header_data(self) -> Dict[str, str]:
        return self.header.to_dict()

    @header_data.setter
    def header_data(self, value: Dict[str, str] | None) -> None:
        self.header = WorkOrderHeader.from_dict(value)

    @property
    def fabric_items(self) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.fabrics]

    @fabric_items.setter
    def fabric_items(self, value: List[Dict[str, str]] | None) -> None:
        self.fabrics = self._coerce_items(value)

    @property
    def trim_items(self) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.trims]

    @trim_items.setter
    def trim_items(self, value: List[Dict[str, str]] | None) -> None:
        self.trims = self._coerce_items(value)

    def reset(self) -> None:
        self.header = WorkOrderHeader()
        self.fabrics = [MaterialItem()]
        self.trims = [MaterialItem()]
        self.current_image_path = None
        self.is_dirty = False

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def has_any_data(self) -> bool:
        return bool(
            self.is_dirty
            or self.current_image_path
            or self.header.has_any_value()
            or self._items_have_value(self.fabrics)
            or self._items_have_value(self.trims)
        )

    def update_header(self, patch: Dict[str, str]) -> None:
        self.header.patch(patch)
        self.mark_dirty()

    def update_change_note(self, text: str) -> None:
        self.update_header({'change_note': (text or '').rstrip()})

    def update_material_patch(self, target: str, idx: int, patch: Dict[str, str]) -> None:
        if idx < 0 or not isinstance(patch, dict):
            return
        items = self._target_items(target)
        while len(items) <= idx:
            items.append(MaterialItem())
        items[idx].patch(patch)
        self.mark_dirty()

    def add_material_item(self, target: str, max_items: int = MAX_MATERIAL_ITEMS) -> int | None:
        items = self._target_items(target)
        if len(items) >= max_items:
            return None
        items.append(MaterialItem())
        self.mark_dirty()
        return len(items) - 1

    def remove_material_item(self, target: str, idx: int) -> bool:
        items = self._target_items(target)
        if 0 <= idx < len(items):
            del items[idx]
            if not items:
                items.append(MaterialItem())
            self.mark_dirty()
            return True
        return False

    def to_document(self) -> WorkOrderDocument:
        return WorkOrderDocument(
            header=WorkOrderHeader.from_dict(self.header.to_dict()),
            fabrics=[MaterialItem.from_dict(item.to_dict()) for item in self.fabrics],
            trims=[MaterialItem.from_dict(item.to_dict()) for item in self.trims],
            image_attached=bool(self.current_image_path),
        )

    def normalized_header(self) -> Dict[str, str]:
        return self.header.to_dict()

    def normalized_fabrics(self) -> List[Dict[str, str]]:
        return self.fabric_items

    def normalized_trims(self) -> List[Dict[str, str]]:
        return self.trim_items

    def _target_items(self, target: str) -> List[MaterialItem]:
        return self.fabrics if target == 'fabric' else self.trims

    @staticmethod
    def _coerce_items(items: List[Dict[str, str]] | None) -> List[MaterialItem]:
        coerced = [MaterialItem.from_dict(item) for item in (items or [])]
        return coerced or [MaterialItem()]

    @staticmethod
    def _items_have_value(items: List[MaterialItem] | None) -> bool:
        return any(item.has_any_value() for item in (items or []))
