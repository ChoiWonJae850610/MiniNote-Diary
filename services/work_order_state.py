from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from services.formatters import format_commas_from_digits, int_from_any
from services.field_keys import HeaderKeys, MaterialKeys, MaterialTargets
from services.models import MaterialItem, WorkOrderDocument, WorkOrderHeader
from services.schema import MAX_MATERIAL_ITEMS


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
        return [item.to_dict() for item in self.fabrics]

    @fabric_items.setter
    def fabric_items(self, value: List[Dict[str, str]] | None) -> None:
        self.fabrics = self._coerce_items(value)
        self._recompute_sale_price()

    @property
    def trim_items(self) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.trims]

    @trim_items.setter
    def trim_items(self, value: List[Dict[str, str]] | None) -> None:
        self.trims = self._coerce_items(value)
        self._recompute_sale_price()


    @property
    def dyeing_items(self) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.dyeings]

    @dyeing_items.setter
    def dyeing_items(self, value: List[Dict[str, str]] | None) -> None:
        self.dyeings = self._coerce_items(value)
        self._recompute_sale_price()

    @property
    def finishing_items(self) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.finishings]

    @finishing_items.setter
    def finishing_items(self, value: List[Dict[str, str]] | None) -> None:
        self.finishings = self._coerce_items(value)
        self._recompute_sale_price()

    @property
    def other_items(self) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.others]

    @other_items.setter
    def other_items(self, value: List[Dict[str, str]] | None) -> None:
        self.others = self._coerce_items(value)
        self._recompute_sale_price()

    def reset(self) -> None:
        self.header = WorkOrderHeader()
        self.fabrics = [MaterialItem()]
        self.trims = [MaterialItem()]
        self.dyeings = [MaterialItem()]
        self.finishings = [MaterialItem()]
        self.others = [MaterialItem()]
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
            or self._items_have_value(self.fabrics)
            or self._items_have_value(self.trims)
            or self._items_have_value(self.dyeings)
            or self._items_have_value(self.finishings)
            or self._items_have_value(self.others)
        )

    def update_header(self, patch: Dict[str, str]) -> None:
        self.header.patch(patch)
        if self._needs_price_recompute(patch):
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

    def to_document(self) -> WorkOrderDocument:
        return WorkOrderDocument(
            header=WorkOrderHeader.from_dict(self.header.to_dict()),
            fabrics=[MaterialItem.from_dict(item.to_dict()) for item in self.fabrics],
            trims=[MaterialItem.from_dict(item.to_dict()) for item in self.trims],
            dyeings=[MaterialItem.from_dict(item.to_dict()) for item in self.dyeings],
            finishings=[MaterialItem.from_dict(item.to_dict()) for item in self.finishings],
            others=[MaterialItem.from_dict(item.to_dict()) for item in self.others],
            image_attached=bool(self.current_image_path),
        )

    def normalized_header(self) -> Dict[str, str]:
        return self.header.to_dict()

    def normalized_fabrics(self) -> List[Dict[str, str]]:
        return self.fabric_items

    def normalized_trims(self) -> List[Dict[str, str]]:
        return self.trim_items


    def normalized_dyeings(self) -> List[Dict[str, str]]:
        return self.dyeing_items

    def normalized_finishings(self) -> List[Dict[str, str]]:
        return self.finishing_items

    def normalized_others(self) -> List[Dict[str, str]]:
        return self.other_items

    def _target_items(self, target: str) -> List[MaterialItem]:
        mapping = {
            MaterialTargets.FABRIC: self.fabrics,
            MaterialTargets.TRIM: self.trims,
            MaterialTargets.DYEING: self.dyeings,
            MaterialTargets.FINISHING: self.finishings,
            MaterialTargets.OTHER: self.others,
        }
        return mapping.get(target, self.trims)

    @staticmethod
    def _coerce_items(items: List[Dict[str, str]] | None) -> List[MaterialItem]:
        coerced = [MaterialItem.from_dict(item) for item in (items or [])]
        return coerced or [MaterialItem()]


    def _recompute_sale_price(self) -> None:
        material_total = (
            self._sum_material_totals(self.fabrics)
            + self._sum_material_totals(self.trims)
            + self._sum_material_totals(self.dyeings)
            + self._sum_material_totals(self.finishings)
            + self._sum_material_totals(self.others)
        )
        material_text = str(material_total) if material_total else ''
        self.header.cost = material_text
        self.header.cost_display = format_commas_from_digits(material_text) if material_text else ''

        sale_total = material_total + int_from_any(self.header.labor) + int_from_any(self.header.loss)
        sale_text = str(sale_total) if sale_total else ''
        self.header.sale_price = sale_text
        self.header.sale_price_display = format_commas_from_digits(sale_text) if sale_text else ''


    @staticmethod
    def _needs_price_recompute(patch: Dict[str, str] | None) -> bool:
        if not isinstance(patch, dict) or not patch:
            return False
        watched_keys = {HeaderKeys.LABOR, HeaderKeys.LABOR_DISPLAY, HeaderKeys.LOSS, HeaderKeys.LOSS_DISPLAY}
        return any(key in watched_keys for key in patch)

    @staticmethod
    def _sum_material_totals(items: List[MaterialItem] | None) -> int:
        return sum(int_from_any(item.total) for item in (items or []))

    @staticmethod
    def _items_have_value(items: List[MaterialItem] | None) -> bool:
        return any(item.has_any_value() for item in (items or []))
