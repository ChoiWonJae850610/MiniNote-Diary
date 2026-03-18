from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from services.common.field_keys import MaterialKeys, PayloadKeys
from services.common.model_utils import to_text
from services.common.schema import HEADER_FIELDS, MATERIAL_FIELDS, REQUIRED_HEADER_FIELDS, REQUIRED_MATERIAL_FIELDS


@dataclass
class WorkOrderHeader:
    date: str = ''
    style_no: str = ''
    factory: str = ''
    cost_display: str = '0'
    labor_display: str = '0'
    loss_display: str = '0'
    sale_price_display: str = '0'
    cost: str = '0'
    labor: str = '0'
    loss: str = '0'
    sale_price: str = '0'
    change_note: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> 'WorkOrderHeader':
        data = data or {}
        defaults = cls().to_dict()
        payload = {name: (to_text(data.get(name, defaults[name])) or defaults[name]) for name in HEADER_FIELDS}
        return cls(**payload)

    def to_dict(self) -> Dict[str, str]:
        return {name: to_text(getattr(self, name, '')) for name in HEADER_FIELDS}

    def patch(self, patch: Dict[str, Any] | None) -> None:
        if not isinstance(patch, dict):
            return
        for name in HEADER_FIELDS:
            if name in patch:
                setattr(self, name, to_text(patch.get(name, '')))

    def has_required_fields(self) -> bool:
        data = self.to_dict()
        return all(data.get(key, '').strip() for key in REQUIRED_HEADER_FIELDS)

    def has_any_value(self) -> bool:
        text_keys = ('date', 'style_no', 'factory', 'change_note')
        if any(str(getattr(self, key, '') or '').strip() for key in text_keys):
            return True
        numeric_keys = ('cost', 'labor', 'loss', 'sale_price')
        return any(str(getattr(self, key, '') or '').replace(',', '').strip() not in ('', '0') for key in numeric_keys)


@dataclass
class MaterialItem:
    거래처: str = ''
    품목: str = ''
    수량: str = '0'
    단위: str = ''
    단가: str = '0'
    총액: str = '0'

    @property
    def vendor(self) -> str:
        return getattr(self, MaterialKeys.VENDOR)

    @property
    def item(self) -> str:
        return getattr(self, MaterialKeys.ITEM)

    @property
    def qty(self) -> str:
        return getattr(self, MaterialKeys.QTY)

    @property
    def unit(self) -> str:
        return getattr(self, MaterialKeys.UNIT)

    @property
    def unit_price(self) -> str:
        return getattr(self, MaterialKeys.UNIT_PRICE)

    @property
    def total(self) -> str:
        return getattr(self, MaterialKeys.TOTAL)

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> 'MaterialItem':
        data = data or {}
        defaults = cls().to_dict()
        return cls(**{name: (to_text(data.get(name, defaults[name])) or defaults[name]) for name in MATERIAL_FIELDS})

    def to_dict(self) -> Dict[str, str]:
        return {name: to_text(getattr(self, name, '')) for name in MATERIAL_FIELDS}

    def patch(self, patch: Dict[str, Any] | None) -> None:
        if not isinstance(patch, dict):
            return
        for name in MATERIAL_FIELDS:
            if name in patch:
                setattr(self, name, to_text(patch.get(name, '')))

    def has_any_value(self) -> bool:
        text_keys = (MaterialKeys.VENDOR, MaterialKeys.ITEM, MaterialKeys.UNIT)
        if any(str(getattr(self, key) or '').strip() for key in text_keys):
            return True
        numeric_keys = (MaterialKeys.QTY, MaterialKeys.UNIT_PRICE, MaterialKeys.TOTAL)
        return any(str(getattr(self, key) or '').replace(',', '').strip() not in ('', '0') for key in numeric_keys)

    def has_required_fields(self) -> bool:
        data = self.to_dict()
        return all(data.get(key, '').strip() for key in REQUIRED_MATERIAL_FIELDS)


@dataclass
class WorkOrderDocument:
    header: WorkOrderHeader = field(default_factory=WorkOrderHeader)
    fabrics: List[MaterialItem] = field(default_factory=list)
    trims: List[MaterialItem] = field(default_factory=list)
    dyeings: List[MaterialItem] = field(default_factory=list)
    finishings: List[MaterialItem] = field(default_factory=list)
    others: List[MaterialItem] = field(default_factory=list)
    image_attached: bool = False

    @classmethod
    def from_raw(
        cls,
        header: Dict[str, Any] | WorkOrderHeader | None,
        fabrics: Iterable[Dict[str, Any] | MaterialItem] | None,
        trims: Iterable[Dict[str, Any] | MaterialItem] | None,
        dyeings: Iterable[Dict[str, Any] | MaterialItem] | None = None,
        finishings: Iterable[Dict[str, Any] | MaterialItem] | None = None,
        others: Iterable[Dict[str, Any] | MaterialItem] | None = None,
        image_attached: bool = False,
    ) -> 'WorkOrderDocument':
        return cls(
            header=header if isinstance(header, WorkOrderHeader) else WorkOrderHeader.from_dict(header),
            fabrics=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (fabrics or [])],
            trims=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (trims or [])],
            dyeings=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (dyeings or [])],
            finishings=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (finishings or [])],
            others=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (others or [])],
            image_attached=bool(image_attached),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            PayloadKeys.HEADER: self.header.to_dict(),
            PayloadKeys.FABRICS: [item.to_dict() for item in self.fabrics],
            PayloadKeys.TRIMS: [item.to_dict() for item in self.trims],
            PayloadKeys.DYEINGS: [item.to_dict() for item in self.dyeings],
            PayloadKeys.FINISHINGS: [item.to_dict() for item in self.finishings],
            PayloadKeys.OTHERS: [item.to_dict() for item in self.others],
            PayloadKeys.IMAGE_ATTACHED: self.image_attached,
        }
