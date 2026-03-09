from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from services.schema import HEADER_FIELDS, MATERIAL_FIELDS, REQUIRED_HEADER_FIELDS, REQUIRED_MATERIAL_FIELDS


def _to_text(value: Any) -> str:
    return '' if value is None else str(value)


@dataclass
class WorkOrderHeader:
    date: str = ''
    style_no: str = ''
    factory: str = ''
    cost_display: str = ''
    labor_display: str = ''
    loss_display: str = ''
    sale_price_display: str = ''
    cost: str = ''
    labor: str = ''
    loss: str = ''
    sale_price: str = ''
    change_note: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> 'WorkOrderHeader':
        data = data or {}
        payload = {name: _to_text(data.get(name, '')) for name in HEADER_FIELDS}
        return cls(**payload)

    def to_dict(self) -> Dict[str, str]:
        return {name: _to_text(getattr(self, name, '')) for name in HEADER_FIELDS}

    def patch(self, patch: Dict[str, Any] | None) -> None:
        if not isinstance(patch, dict):
            return
        for name in HEADER_FIELDS:
            if name in patch:
                setattr(self, name, _to_text(patch.get(name, '')))

    def has_required_fields(self) -> bool:
        data = self.to_dict()
        return all(data.get(key, '').strip() for key in REQUIRED_HEADER_FIELDS)

    def has_any_value(self) -> bool:
        return any(value.strip() for value in self.to_dict().values())


@dataclass
class MaterialItem:
    거래처: str = ''
    품목: str = ''
    수량: str = ''
    단위: str = ''
    단가: str = ''
    총액: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> 'MaterialItem':
        data = data or {}
        return cls(**{name: _to_text(data.get(name, '')) for name in MATERIAL_FIELDS})

    def to_dict(self) -> Dict[str, str]:
        return {name: _to_text(getattr(self, name, '')) for name in MATERIAL_FIELDS}

    def patch(self, patch: Dict[str, Any] | None) -> None:
        if not isinstance(patch, dict):
            return
        for name in MATERIAL_FIELDS:
            if name in patch:
                setattr(self, name, _to_text(patch.get(name, '')))

    def has_any_value(self) -> bool:
        return any(value.strip() for value in self.to_dict().values())

    def has_required_fields(self) -> bool:
        data = self.to_dict()
        return all(data.get(key, '').strip() for key in REQUIRED_MATERIAL_FIELDS)


@dataclass
class WorkOrderDocument:
    header: WorkOrderHeader = field(default_factory=WorkOrderHeader)
    fabrics: List[MaterialItem] = field(default_factory=list)
    trims: List[MaterialItem] = field(default_factory=list)
    image_attached: bool = False

    @classmethod
    def from_raw(
        cls,
        header: Dict[str, Any] | WorkOrderHeader | None,
        fabrics: Iterable[Dict[str, Any] | MaterialItem] | None,
        trims: Iterable[Dict[str, Any] | MaterialItem] | None,
        image_attached: bool = False,
    ) -> 'WorkOrderDocument':
        return cls(
            header=header if isinstance(header, WorkOrderHeader) else WorkOrderHeader.from_dict(header),
            fabrics=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (fabrics or [])],
            trims=[item if isinstance(item, MaterialItem) else MaterialItem.from_dict(item) for item in (trims or [])],
            image_attached=bool(image_attached),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            'header': self.header.to_dict(),
            'fabrics': [item.to_dict() for item in self.fabrics],
            'trims': [item.to_dict() for item in self.trims],
            'image_attached': self.image_attached,
        }
