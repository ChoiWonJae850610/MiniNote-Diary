from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List


DEFAULT_PARTNER_TYPES = ["공장", "원단", "부자재", "염색", "마감", "기타"]


@dataclass
class PartnerRecord:
    id: str
    name: str
    owner: str = ""
    phone: str = ""
    address: str = ""
    memo: str = ""
    types: List[str] | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "phone": self.phone,
            "address": self.address,
            "memo": self.memo,
            "types": list(self.types or []),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PartnerRecord":
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")).strip(),
            owner=str(data.get("owner", "")).strip(),
            phone=str(data.get("phone", "")).strip(),
            address=str(data.get("address", "")).strip(),
            memo=str(data.get("memo", "")).strip(),
            types=[str(x).strip() for x in data.get("types", []) if str(x).strip()],
        )


class PartnerRepository:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.db_dir = os.path.join(project_root, "db")
        os.makedirs(self.db_dir, exist_ok=True)
        self.partners_path = os.path.join(self.db_dir, "partners.json")
        self.partner_types_path = os.path.join(self.db_dir, "partner_types.json")

    def load_types(self) -> List[str]:
        payload = self._safe_read_json(self.partner_types_path, {"types": DEFAULT_PARTNER_TYPES})
        raw = payload.get("types", DEFAULT_PARTNER_TYPES)
        types = []
        seen = set()
        for item in raw:
            name = str(item).strip()
            if name and name not in seen:
                types.append(name)
                seen.add(name)
        if not types:
            types = list(DEFAULT_PARTNER_TYPES)
        return types

    def save_types(self, types: List[str]) -> None:
        cleaned = []
        seen = set()
        for item in types:
            name = str(item).strip()
            if name and name not in seen:
                cleaned.append(name)
                seen.add(name)
        if not cleaned:
            cleaned = list(DEFAULT_PARTNER_TYPES)
        self._write_json(self.partner_types_path, {"types": cleaned})

    def load_partners(self) -> List[PartnerRecord]:
        payload = self._safe_read_json(self.partners_path, {"partners": []})
        partners: List[PartnerRecord] = []
        for raw in payload.get("partners", []):
            if not isinstance(raw, dict):
                continue
            record = PartnerRecord.from_dict(raw)
            if record.name:
                partners.append(record)
        partners.sort(key=lambda x: x.name)
        return partners

    def save_partners(self, partners: List[PartnerRecord]) -> None:
        sorted_rows = sorted(partners, key=lambda x: x.name)
        self._write_json(self.partners_path, {"partners": [row.to_dict() for row in sorted_rows]})

    def next_partner_id(self, partners: List[PartnerRecord]) -> str:
        max_no = 0
        for item in partners:
            raw = str(item.id)
            if raw.startswith("PT-"):
                try:
                    max_no = max(max_no, int(raw.split("-", 1)[1]))
                except Exception:
                    continue
        return f"PT-{max_no + 1:04d}"

    def _safe_read_json(self, path: str, fallback: dict) -> dict:
        if not os.path.isfile(path):
            return fallback
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else fallback
        except Exception:
            return fallback

    def _write_json(self, path: str, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
