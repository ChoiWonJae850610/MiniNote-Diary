from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from services.common.project_paths import db_file_path, project_root_path

INBOUND_DB_FILENAME = 'inbound_records.json'


@dataclass
class InboundRecord:
    inbound_id: str
    order_id: str
    template_id: str
    template_name: str
    factory_name: str
    inbound_date: str
    inbound_qty: int
    defect_qty: int
    good_qty: int
    inspection_memo: str = ''
    source_memo: str = ''
    lead_days: int = 0
    created_at: str = ''


class InboundRepository:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else project_root_path(__file__)

    @property
    def file_path(self) -> Path:
        return db_file_path(INBOUND_DB_FILENAME, self.base_dir)

    def load_all(self) -> list[InboundRecord]:
        payload = self._read_payload()
        rows = payload.get('records', [])
        result: list[InboundRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                result.append(InboundRecord(**row))
            except TypeError:
                continue
        return result

    def create_record(
        self,
        *,
        order_id: str,
        template_id: str,
        template_name: str,
        factory_name: str,
        inbound_date: str,
        inbound_qty: int,
        defect_qty: int,
        good_qty: int,
        inspection_memo: str = '',
        source_memo: str = '',
        lead_days: int = 0,
    ) -> InboundRecord:
        now = datetime.now().isoformat(timespec='seconds')
        record = InboundRecord(
            inbound_id=f'inbound_{int(datetime.now().timestamp() * 1000)}',
            order_id=order_id,
            template_id=template_id,
            template_name=template_name,
            factory_name=factory_name,
            inbound_date=inbound_date,
            inbound_qty=max(0, int(inbound_qty or 0)),
            defect_qty=max(0, int(defect_qty or 0)),
            good_qty=max(0, int(good_qty or 0)),
            inspection_memo=(inspection_memo or '').strip(),
            source_memo=(source_memo or '').strip(),
            lead_days=max(0, int(lead_days or 0)),
            created_at=now,
        )
        rows = self.load_all()
        rows.append(record)
        self.save_all(rows)
        return record

    def list_by_order(self, order_id: str) -> list[InboundRecord]:
        return [row for row in self.load_all() if row.order_id == order_id]

    def save_all(self, records: list[InboundRecord]) -> None:
        payload = self._read_payload()
        payload['records'] = [asdict(record) for record in records]
        payload['updated_at'] = datetime.now().isoformat(timespec='seconds')
        self._write_payload(payload)

    def _read_payload(self) -> dict[str, Any]:
        path = self.file_path
        if not path.is_file():
            return {'version': 1, 'records': []}
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return {'version': 1, 'records': []}
        if not isinstance(payload, dict):
            return {'version': 1, 'records': []}
        if not isinstance(payload.get('records'), list):
            payload['records'] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        path = self.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
