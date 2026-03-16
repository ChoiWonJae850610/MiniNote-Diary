from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from services.work_order.repository import SaveResult, WorkOrderRepository, WorkOrderTemplateDetail, WorkOrderTemplateSummary
from services.work_order.state import WorkOrderState
from services.work_order.validation import get_document_save_requirement_statuses


class WorkOrderService:
    def __init__(self, state: WorkOrderState, base_dir: str | Path | None = None):
        self.state = state
        self.repository = WorkOrderRepository(base_dir)

    def current_document(self):
        return self.state.to_document()

    def validate_current(self) -> List[Tuple[str, bool]]:
        return get_document_save_requirement_statuses(self.current_document())

    def save_current(self) -> SaveResult:
        overwrite_template_id = None
        if self.state.loaded_template_id and not self.state.loaded_has_order_history:
            overwrite_template_id = self.state.loaded_template_id
        return self.repository.save_template(
            self.current_document(),
            image_src_path=self.state.current_image_path,
            overwrite_template_id=overwrite_template_id,
        )

    def list_templates(self) -> list[WorkOrderTemplateSummary]:
        return self.repository.list_templates()

    def load_template(self, template_id: str) -> WorkOrderTemplateDetail | None:
        return self.repository.load_template(template_id)
