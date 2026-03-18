
from __future__ import annotations

from typing import Iterable, Any

from services.product_type.repository import (
    ProductTypeNode,
    load_product_type_tree,
    save_product_type_tree,
)


class ProductTypeService:
    def __init__(self, project_root: str):
        self.project_root = project_root

    def get_tree(self) -> list[ProductTypeNode]:
        return load_product_type_tree(self.project_root)

    def save_tree(self, nodes: list[ProductTypeNode]) -> None:
        save_product_type_tree(nodes, self.project_root)

    def get_level_options(self, parent_path: Iterable[str] | None = None) -> list[str]:
        nodes = self.get_tree()
        path = [str(v).strip() for v in (parent_path or []) if str(v).strip()]
        for part in path:
            match = next((node for node in nodes if node.get('name') == part), None)
            if match is None:
                return []
            nodes = list(match.get('children') or [])
        return [str(node.get('name') or '').strip() for node in nodes if str(node.get('name') or '').strip()]

    def resolve_path(self, stored_value: str) -> list[str]:
        text = str(stored_value or '').strip()
        if not text:
            return []
        if '>' in text:
            parts = [part.strip() for part in text.split('>') if part.strip()]
            if parts:
                return parts[:3]
        found = self._find_first_path_by_name(text, self.get_tree())
        return found[:3] if found else [text]

    def encode_path(self, values: Iterable[str]) -> str:
        parts = [str(v).strip() for v in values if str(v).strip()]
        return ' > '.join(parts)

    def _find_first_path_by_name(self, target: str, nodes: list[ProductTypeNode], prefix: list[str] | None = None) -> list[str]:
        prefix = list(prefix or [])
        for node in nodes:
            name = str(node.get('name') or '').strip()
            current = prefix + [name]
            if name == target:
                return current
            found = self._find_first_path_by_name(target, list(node.get('children') or []), current)
            if found:
                return found
        return []
