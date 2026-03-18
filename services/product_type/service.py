
from __future__ import annotations

from typing import Iterable

from services.product_type.repository import load_product_types, save_product_types


class ProductTypeService:
    def __init__(self, project_root: str):
        self.project_root = project_root

    def list_types(self) -> list[str]:
        return load_product_types(self.project_root)

    def save_types(self, types: Iterable[str]) -> None:
        rows: list[str] = []
        for value in types:
            text = str(value or '').strip()
            if text and text not in rows:
                rows.append(text)
        save_product_types(rows, self.project_root)
