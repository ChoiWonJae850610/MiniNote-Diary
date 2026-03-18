
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from services.common.project_paths import db_file_path, project_root_path


class ProductTypeRepository:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else project_root_path(__file__)

    @property
    def file_path(self) -> Path:
        return db_file_path('product_types.json', self.base_dir)

    def load_all(self) -> List[str]:
        path = self.file_path
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return []
        rows = data.get('types', data) if isinstance(data, dict) else data
        out: list[str] = []
        for value in rows if isinstance(rows, list) else []:
            text = str(value or '').strip()
            if text and text not in out:
                out.append(text)
        return out

    def save_all(self, values: List[str]) -> None:
        path = self.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        rows: list[str] = []
        for value in values:
            text = str(value or '').strip()
            if text and text not in rows:
                rows.append(text)
        path.write_text(json.dumps({'types': rows}, ensure_ascii=False, indent=2), encoding='utf-8')


def load_product_types(base_dir: str | Path | None = None) -> List[str]:
    return ProductTypeRepository(base_dir).load_all()


def save_product_types(values: List[str], base_dir: str | Path | None = None) -> None:
    ProductTypeRepository(base_dir).save_all(values)
