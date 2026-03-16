from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from services.common.project_paths import db_file_path, project_root_path

PRODUCT_DB_FILENAME = 'products.json'


@dataclass
class ProductRecord:
    template_id: str
    template_name: str
    sale_price: int = 0
    note: str = ''
    updated_at: str = ''


class ProductRepository:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else project_root_path(__file__)

    @property
    def file_path(self) -> Path:
        return db_file_path(PRODUCT_DB_FILENAME, self.base_dir)

    def load_all(self) -> list[ProductRecord]:
        payload = self._read_payload()
        rows = payload.get('products', [])
        result: list[ProductRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                result.append(ProductRecord(**row))
            except TypeError:
                continue
        return result

    def get(self, template_id: str) -> ProductRecord | None:
        for row in self.load_all():
            if row.template_id == template_id:
                return row
        return None

    def upsert(self, *, template_id: str, template_name: str, sale_price: int, note: str = '') -> ProductRecord:
        rows = self.load_all()
        now = datetime.now().isoformat(timespec='seconds')
        record = ProductRecord(
            template_id=template_id,
            template_name=(template_name or '').strip(),
            sale_price=max(0, int(sale_price or 0)),
            note=(note or '').strip(),
            updated_at=now,
        )
        updated = False
        for index, row in enumerate(rows):
            if row.template_id == template_id:
                rows[index] = record
                updated = True
                break
        if not updated:
            rows.append(record)
        self.save_all(rows)
        return record

    def save_all(self, rows: list[ProductRecord]) -> None:
        payload = self._read_payload()
        payload['products'] = [asdict(row) for row in rows]
        payload['updated_at'] = datetime.now().isoformat(timespec='seconds')
        self._write_payload(payload)

    def _read_payload(self) -> dict[str, Any]:
        path = self.file_path
        if not path.is_file():
            return {'version': 1, 'products': []}
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return {'version': 1, 'products': []}
        if not isinstance(payload, dict):
            return {'version': 1, 'products': []}
        if not isinstance(payload.get('products'), list):
            payload['products'] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        path = self.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
