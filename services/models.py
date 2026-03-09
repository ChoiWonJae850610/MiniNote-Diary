from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class WorkOrderHeader:
    date: str = ""
    style_no: str = ""
    factory: str = ""
    cost_display: str = ""
    labor_display: str = ""
    loss_display: str = ""
    sale_price_display: str = ""
    cost: str = ""
    labor: str = ""
    loss: str = ""
    sale_price: str = ""
    change_note: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, str] | None) -> "WorkOrderHeader":
        data = data or {}
        fields = cls.__dataclass_fields__
        payload = {name: str(data.get(name, "") or "") for name in fields}
        return cls(**payload)

    def to_dict(self) -> Dict[str, str]:
        return {name: str(getattr(self, name) or "") for name in self.__dataclass_fields__}


@dataclass
class MaterialItem:
    거래처: str = ""
    품목: str = ""
    수량: str = ""
    단위: str = ""
    단가: str = ""
    총액: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, str] | None) -> "MaterialItem":
        data = data or {}
        return cls(**{name: str(data.get(name, "") or "") for name in cls.__dataclass_fields__})

    def to_dict(self) -> Dict[str, str]:
        return {name: str(getattr(self, name) or "") for name in self.__dataclass_fields__}

    def has_any_value(self) -> bool:
        return any(str(getattr(self, name) or "").strip() for name in self.__dataclass_fields__)


@dataclass
class WorkOrderDocument:
    header: WorkOrderHeader = field(default_factory=WorkOrderHeader)
    fabrics: List[MaterialItem] = field(default_factory=list)
    trims: List[MaterialItem] = field(default_factory=list)
    image_attached: bool = False

    @classmethod
    def from_raw(cls, header: Dict[str, str] | None, fabrics: List[Dict[str, str]] | None, trims: List[Dict[str, str]] | None, image_attached: bool = False) -> "WorkOrderDocument":
        return cls(
            header=WorkOrderHeader.from_dict(header),
            fabrics=[MaterialItem.from_dict(item) for item in (fabrics or [])],
            trims=[MaterialItem.from_dict(item) for item in (trims or [])],
            image_attached=bool(image_attached),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "header": self.header.to_dict(),
            "fabrics": [item.to_dict() for item in self.fabrics],
            "trims": [item.to_dict() for item in self.trims],
            "image_attached": self.image_attached,
        }
