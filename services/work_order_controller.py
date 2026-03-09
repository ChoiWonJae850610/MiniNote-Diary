from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from services.storage import save_work_order
from services.work_order_state import WorkOrderState
from services.work_order_validation import get_save_requirement_statuses


@dataclass
class SaveResult:
    json_path: str
    image_path: str | None
    sha256_plain: str


class WorkOrderController:
    def __init__(self, state: WorkOrderState, base_dir: str | Path):
        self.state = state
        self.base_dir = str(base_dir)

    def get_save_requirement_statuses(self) -> List[Tuple[str, bool]]:
        return get_save_requirement_statuses(
            self.state.normalized_header(),
            self.state.normalized_fabrics(),
            self.state.normalized_trims(),
        )

    def save(self) -> SaveResult:
        document = self.state.to_document()
        json_path, image_path, sha256_plain = save_work_order(
            base_dir=self.base_dir,
            data=document.to_dict(),
            image_src_path=self.state.current_image_path,
        )
        return SaveResult(json_path=json_path, image_path=image_path, sha256_plain=sha256_plain)
