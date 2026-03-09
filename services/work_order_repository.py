from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.models import WorkOrderDocument
from services.storage import save_work_order


@dataclass
class SaveResult:
    json_path: str
    image_path: str | None
    sha256_plain: str


class WorkOrderRepository:
    def __init__(self, base_dir: str | Path):
        self.base_dir = str(base_dir)

    def save_document(self, document: WorkOrderDocument, *, image_src_path: str | None = None) -> SaveResult:
        json_path, image_path, sha256_plain = save_work_order(
            base_dir=self.base_dir,
            data=document.to_dict(),
            image_src_path=image_src_path,
        )
        return SaveResult(json_path=json_path, image_path=image_path, sha256_plain=sha256_plain)
