from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from services.common.project_paths import db_dir_path, db_file_path, project_root_path
from services.partner.utils import fallback_partner_types, normalize_partner_types
from services.common.schema import PARTNERS_DB_FILENAME, PARTNER_TYPES_DB_FILENAME


@dataclass
class PartnerRecord:
    id: str
    name: str
    owner: str = ''
    phone: str = ''
    address: str = ''
    memo: str = ''
    types: List[str] | None = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'phone': self.phone,
            'address': self.address,
            'memo': self.memo,
            'types': list(self.types or []),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PartnerRecord':
        return cls(
            id=str(data.get('id', '')),
            name=str(data.get('name', '')).strip(),
            owner=str(data.get('owner', '')).strip(),
            phone=str(data.get('phone', '')).strip(),
            address=str(data.get('address', '')).strip(),
            memo=str(data.get('memo', '')).strip(),
            types=normalize_partner_types(data.get('types', [])),
        )


class PartnerRepository:
    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root) if project_root is not None else project_root_path(__file__)
        self.db_dir = db_dir_path(self.project_root)
        self.partners_path = db_file_path(PARTNERS_DB_FILENAME, self.project_root)
        self.partner_types_path = db_file_path(PARTNER_TYPES_DB_FILENAME, self.project_root)

    def load_types(self) -> List[str]:
        payload = self._safe_read_json(self.partner_types_path, {'types': fallback_partner_types()})
        types = normalize_partner_types(payload.get('types', fallback_partner_types()))
        return types or fallback_partner_types()

    def save_types(self, types: Iterable[str]) -> None:
        cleaned = normalize_partner_types(types)
        if not cleaned:
            cleaned = fallback_partner_types()
        self._write_json(self.partner_types_path, {'types': cleaned})

    def load_all(self) -> List[PartnerRecord]:
        payload = self._safe_read_json(self.partners_path, {'partners': []})
        partners: List[PartnerRecord] = []
        for raw in payload.get('partners', []):
            if not isinstance(raw, dict):
                continue
            record = PartnerRecord.from_dict(raw)
            if record.name:
                partners.append(record)
        partners.sort(key=lambda x: x.name)
        return partners

    def save_all(self, partners: List[PartnerRecord]) -> None:
        sorted_rows = sorted(partners, key=lambda x: x.name)
        self._write_json(self.partners_path, {'partners': [row.to_dict() for row in sorted_rows]})

    def load_partners(self) -> List[PartnerRecord]:
        return self.load_all()

    def save_partners(self, partners: List[PartnerRecord]) -> None:
        self.save_all(partners)

    def load_partners_by_type(self, type_name: str) -> List[PartnerRecord]:
        type_name = str(type_name or '').strip()
        if not type_name:
            return self.load_all()
        return [row for row in self.load_all() if type_name in (row.types or [])]

    def next_partner_id(self, partners: List[PartnerRecord]) -> str:
        max_no = 0
        for item in partners:
            raw = str(item.id)
            if raw.startswith('PT-'):
                try:
                    max_no = max(max_no, int(raw.split('-', 1)[1]))
                except Exception:
                    continue
        return f'PT-{max_no + 1:04d}'

    def _safe_read_json(self, path: Path, fallback: dict) -> dict:
        if not path.is_file():
            return fallback
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            return data if isinstance(data, dict) else fallback
        except Exception:
            return fallback

    def _write_json(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
