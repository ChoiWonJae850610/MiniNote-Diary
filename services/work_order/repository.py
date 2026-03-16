from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from services.common.field_keys import DbFilenames, PayloadKeys
from services.common.models import WorkOrderDocument
from services.common.project_paths import db_dir_path, project_root_path
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

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else project_root_path(__file__)

    @property
    def db_dir(self) -> Path:
        return db_dir_path(self.base_dir)

    def save_template(
        self,
        document: WorkOrderDocument,
        *,
        image_src_path: str | None = None,
        overwrite_template_id: str | None = None,
    ) -> SaveResult:
        json_path, image_path, sha256_plain = save_work_order(
            base_dir=str(self.base_dir),
            data=document.to_dict(),
            image_src_path=image_src_path,
            overwrite_template_id=overwrite_template_id,
        )
        return SaveResult(json_path=json_path, image_path=image_path, sha256_plain=sha256_plain)

    def save_document(
        self,
        document: WorkOrderDocument,
        *,
        image_src_path: str | None = None,
        overwrite_template_id: str | None = None,
    ) -> SaveResult:
        return self.save_template(document, image_src_path=image_src_path, overwrite_template_id=overwrite_template_id)

    def list_templates(self) -> list[WorkOrderTemplateSummary]:
        items: list[WorkOrderTemplateSummary] = []
        for path in self._iter_template_paths():
            detail = self._load_template_detail(path)
            if detail is not None:
                items.append(detail.summary)
        items.sort(key=lambda item: (item.date or '', item.saved_at or '', item.template_id), reverse=True)
        return items

    def list_template_summaries(self) -> list[WorkOrderTemplateSummary]:
        return self.list_templates()

    def load_template(self, template_id: str) -> WorkOrderTemplateDetail | None:
        for path in self._iter_template_paths():
            if path.stem == template_id:
                return self._load_template_detail(path)
        return None

    def load_template_detail(self, template_id: str) -> WorkOrderTemplateDetail | None:
        return self.load_template(template_id)

    def _iter_template_paths(self) -> Iterable[Path]:
        db_dir = self.db_dir
        try:
            filenames = sorted(db_dir.iterdir())
        except FileNotFoundError:
            return []
        return [
            path
            for path in filenames
            if path.is_file() and path.suffix.lower() == '.json' and path.name not in self._SKIP_FILENAMES
        ]

    def _load_template_detail(self, json_path: Path) -> WorkOrderTemplateDetail | None:
        try:
            payload = json.loads(json_path.read_text(encoding='utf-8'))
            data = decrypt_payload(ensure_db_dir(str(self.base_dir)), payload)
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
        template_id = json_path.stem
        summary = WorkOrderTemplateSummary(
            template_id=template_id,
            json_path=str(json_path),
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
    def _find_image_path(json_path: Path) -> str | None:
        stem = json_path.with_suffix('')
        for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
            candidate = Path(f'{stem}{ext}')
            if candidate.is_file():
                return str(candidate)
        return None
