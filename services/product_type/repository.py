
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Iterable

from services.common.project_paths import db_file_path, project_root_path


ProductTypeNode = dict[str, Any]


class ProductTypeRepository:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else project_root_path(__file__)

    @property
    def file_path(self) -> Path:
        return db_file_path('product_types.json', self.base_dir)

    def load_tree(self) -> list[ProductTypeNode]:
        path = self.file_path
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return []
        rows = data.get('types', data) if isinstance(data, dict) else data
        if not isinstance(rows, list):
            return []
        return _normalize_nodes(rows)

    def save_tree(self, nodes: list[ProductTypeNode]) -> None:
        path = self.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'types': _normalize_nodes(nodes)}, ensure_ascii=False, indent=2), encoding='utf-8')

    def load_all(self) -> list[str]:
        return _flatten_paths(self.load_tree())

    def save_all(self, values: list[str]) -> None:
        self.save_tree(_tree_from_paths(values))


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _normalize_node(node: Any) -> ProductTypeNode | None:
    if isinstance(node, str):
        text = node.strip()
        if not text:
            return None
        return {'id': _new_id(), 'name': text, 'children': []}
    if not isinstance(node, dict):
        return None
    name = str(node.get('name') or '').strip()
    if not name:
        return None
    raw_children = node.get('children', [])
    children = _normalize_nodes(raw_children if isinstance(raw_children, list) else [])
    return {'id': str(node.get('id') or _new_id()), 'name': name, 'children': children}


def _normalize_nodes(nodes: Iterable[Any]) -> list[ProductTypeNode]:
    out: list[ProductTypeNode] = []
    seen: set[tuple[str, str]] = set()
    for node in nodes:
        normalized = _normalize_node(node)
        if not normalized:
            continue
        key = (normalized['id'], normalized['name'])
        if key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    return out


def _flatten_paths(nodes: list[ProductTypeNode], prefix: tuple[str, ...] = ()) -> list[str]:
    out: list[str] = []
    for node in nodes:
        path = prefix + (node['name'],)
        out.append(' > '.join(path))
        out.extend(_flatten_paths(node.get('children', []) or [], path))
    return out


def _tree_from_paths(values: Iterable[str]) -> list[ProductTypeNode]:
    roots: list[ProductTypeNode] = []
    for raw in values:
        parts = [part.strip() for part in str(raw or '').split('>') if part.strip()]
        if not parts:
            continue
        current_list = roots
        for part in parts:
            existing = next((node for node in current_list if node['name'] == part), None)
            if existing is None:
                existing = {'id': _new_id(), 'name': part, 'children': []}
                current_list.append(existing)
            current_list = existing['children']
    return roots


def load_product_type_tree(base_dir: str | Path | None = None) -> list[ProductTypeNode]:
    return ProductTypeRepository(base_dir).load_tree()


def save_product_type_tree(nodes: list[ProductTypeNode], base_dir: str | Path | None = None) -> None:
    ProductTypeRepository(base_dir).save_tree(nodes)


def load_product_types(base_dir: str | Path | None = None) -> list[str]:
    return ProductTypeRepository(base_dir).load_all()


def save_product_types(values: list[str], base_dir: str | Path | None = None) -> None:
    ProductTypeRepository(base_dir).save_all(values)
