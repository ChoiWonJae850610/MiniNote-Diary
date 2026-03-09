from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from services.work_order_repository import SaveResult, WorkOrderRepository
from services.work_order_state import WorkOrderState
from services.work_order_validation import get_document_save_requirement_statuses


class WorkOrderController:
    def __init__(self, state: WorkOrderState, base_dir: str | Path):
        self.state = state
        self.repository = WorkOrderRepository(base_dir)

    def get_save_requirement_statuses(self) -> List[Tuple[str, bool]]:
        return get_document_save_requirement_statuses(self.state.to_document())

    def save(self) -> SaveResult:
        document = self.state.to_document()
        return self.repository.save_document(document, image_src_path=self.state.current_image_path)
