from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from services.work_order.repository import SaveResult, WorkOrderTemplateDetail, WorkOrderTemplateSummary
from services.work_order.service import WorkOrderService
from services.work_order.state import WorkOrderState


class WorkOrderController:
    def __init__(self, state: WorkOrderState, base_dir: str | Path | None = None):
        self.state = state
        self.service = WorkOrderService(state, base_dir)
        self.repository = self.service.repository

    def get_save_requirement_statuses(self) -> List[Tuple[str, bool]]:
        return self.service.validate_current()

    def save(self) -> SaveResult:
        return self.service.save_current()

    def list_templates(self) -> list[WorkOrderTemplateSummary]:
        return self.service.list_templates()

    def load_template(self, template_id: str) -> WorkOrderTemplateDetail | None:
        return self.service.load_template(template_id)
