from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from services.common.field_keys import DbFilenames, PayloadKeys
from services.common.models import WorkOrderDocument
from services.common.schema import ORDER_RUNS_DB_FILENAME, PARTNERS_DB_FILENAME, PARTNER_TYPES_DB_FILENAME
from services.storage.storage import decrypt_payload, ensure_db_dir, save_work_order


@dataclass
class SaveResult:
    json_path: str
    image_path: str | None
    sha256_plain: str


@dataclass
class WorkOrderTemplateSummary:
    template_id: str
    json_path: str
    image_path: str | None
    name: str
    date: str
    factory_name: str
    cost_display: str
    labor_display: str
    sale_price_display: str
    change_note: str
    fabric_count: int
    trim_count: int
    saved_at: str


@dataclass
class WorkOrderTemplateDetail:
    summary: WorkOrderTemplateSummary
    document: WorkOrderDocument


class WorkOrderRepository:
    _SKIP_FILENAMES = {
        PARTNERS_DB_FILENAME,
        PARTNER_TYPES_DB_FILENAME,
        DbFilenames.UNITS,
        ORDER_RUNS_DB_FILENAME,
    }

    def __init__(self, base_dir: str | Path):
        self.base_dir = str(base_dir)

    def save_document(self, document: WorkOrderDocument, *, image_src_path: str | None = None) -> SaveResult:
        json_path, image_path, sha256_plain = save_work_order(
            base_dir=self.base_dir,
            data=document.to_dict(),
            image_src_path=image_src_path,
        )
        return SaveResult(json_path=json_path, image_path=image_path, sha256_plain=sha256_plain)

    def list_template_summaries(self) -> list[WorkOrderTemplateSummary]:
        items: list[WorkOrderTemplateSummary] = []
        db_dir = ensure_db_dir(self.base_dir)
        for path in self._iter_template_paths(db_dir):
            detail = self._load_template_detail(path)
            if detail is not None:
                items.append(detail.summary)
        items.sort(key=lambda item: (item.date or '', item.saved_at or '', item.template_id), reverse=True)
        return items

    def load_template_detail(self, template_id: str) -> WorkOrderTemplateDetail | None:
        db_dir = ensure_db_dir(self.base_dir)
        for path in self._iter_template_paths(db_dir):
            if os.path.splitext(os.path.basename(path))[0] == template_id:
                return self._load_template_detail(path)
        return None

    def _iter_template_paths(self, db_dir: str) -> Iterable[str]:
        try:
            filenames = sorted(os.listdir(db_dir))
        except FileNotFoundError:
            return []
        return [
            os.path.join(db_dir, name)
            for name in filenames
            if name.lower().endswith('.json') and name not in self._SKIP_FILENAMES
        ]

    def _load_template_detail(self, json_path: str) -> WorkOrderTemplateDetail | None:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            data = decrypt_payload(ensure_db_dir(self.base_dir), payload)
        except Exception:
            return None

        document = WorkOrderDocument.from_raw(
            header=data.get(PayloadKeys.HEADER),
            fabrics=data.get(PayloadKeys.FABRICS),
            trims=data.get(PayloadKeys.TRIMS),
            dyeings=data.get(PayloadKeys.DYEINGS),
            finishings=data.get(PayloadKeys.FINISHINGS),
            others=data.get(PayloadKeys.OTHERS),
            image_attached=bool(data.get(PayloadKeys.IMAGE_ATTACHED)),
        )
        header = document.header
        template_id = os.path.splitext(os.path.basename(json_path))[0]
        summary = WorkOrderTemplateSummary(
            template_id=template_id,
            json_path=json_path,
            image_path=self._find_image_path(json_path),
            name=(header.style_no or '').strip() or template_id,
            date=(header.date or '').strip(),
            factory_name=(header.factory or '').strip(),
            cost_display=(header.cost_display or '').strip(),
            labor_display=(header.labor_display or '').strip(),
            sale_price_display=(header.sale_price_display or '').strip(),
            change_note=(header.change_note or '').strip(),
            fabric_count=len([item for item in document.fabrics if item.has_any_value()]),
            trim_count=len([item for item in document.trims if item.has_any_value()]),
            saved_at=str(payload.get(PayloadKeys.SAVED_AT, '') or ''),
        )
        return WorkOrderTemplateDetail(summary=summary, document=document)

    @staticmethod
    def _find_image_path(json_path: str) -> str | None:
        stem, _ = os.path.splitext(json_path)
        for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
            candidate = stem + ext
            if os.path.isfile(candidate):
                return candidate
        return None
