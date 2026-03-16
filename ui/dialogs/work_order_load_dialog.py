from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QTextEdit, QVBoxLayout, QWidget

from services.order.repository import OrderRepository
from services.work_order.repository import WorkOrderRepository, WorkOrderTemplateDetail
from services.work_order.summary_service import build_work_order_summary_view
from ui.dialogs.base import _BaseThemedDialog
from ui.messages import Buttons, DefaultTexts, DialogTitles, PageDescriptions, SectionTitles
from ui.widget_factory import make_action_button, make_hint_label, make_panel_frame, make_panel_title_label, make_section_title_label


@dataclass(frozen=True)
class WorkOrderLoadResult:
    template_id: str
    detail: WorkOrderTemplateDetail


class WorkOrderLoadDialog(_BaseThemedDialog):
    def __init__(self, repository: WorkOrderRepository, order_repository: OrderRepository, parent=None):
        super().__init__(DialogTitles.LOAD_TEMPLATE, parent=parent)
        self.repository = repository
        self.order_repository = order_repository
        self.selected_result: WorkOrderLoadResult | None = None
        self._detail_by_id: dict[str, WorkOrderTemplateDetail] = {}
        self.resize(980, 680)
        self._build_ui()
        self._load_templates()

    def _build_ui(self) -> None:
        root = self.body
        root.setSpacing(14)

        header = QWidget(self)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        header_layout.addWidget(make_panel_title_label(DialogTitles.LOAD_TEMPLATE, header))
        header_layout.addWidget(make_hint_label(PageDescriptions.WORK_ORDER_LOAD, header))
        root.addWidget(header)

        body = QHBoxLayout()
        body.setSpacing(14)

        left_panel = make_panel_frame(self)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)
        left_layout.addWidget(make_section_title_label(SectionTitles.ORDER_TEMPLATE_LIST, left_panel))
        self.template_list = QListWidget(left_panel)
        self.template_list.currentRowChanged.connect(self._on_row_changed)
        self.template_list.itemActivated.connect(self._on_item_activated)
        left_layout.addWidget(self.template_list, 1)

        right_panel = make_panel_frame(self)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)
        right_layout.addWidget(make_section_title_label(SectionTitles.WORK_ORDER_LOAD_PREVIEW, right_panel))
        self.preview = QTextEdit(right_panel)
        self.preview.setReadOnly(True)
        right_layout.addWidget(self.preview, 1)

        body.addWidget(left_panel, 4)
        body.addWidget(right_panel, 6)
        root.addLayout(body, 1)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.btn_cancel = make_action_button(Buttons.CANCEL, self)
        self.btn_load = make_action_button(Buttons.LOAD_TO_EDIT, self, primary=True)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_load.clicked.connect(self._accept_selected)
        button_row.addWidget(self.btn_cancel)
        button_row.addWidget(self.btn_load)
        root.addLayout(button_row)

    def _load_templates(self) -> None:
        self.template_list.clear()
        self._detail_by_id.clear()
        summaries = self.repository.list_templates()
        for summary in summaries:
            detail = self.repository.load_template_detail(summary.template_id)
            if detail is None:
                continue
            self._detail_by_id[summary.template_id] = detail
            subtitle = f"{summary.factory_name or DefaultTexts.EMPTY_VALUE} · {summary.date or DefaultTexts.EMPTY_VALUE}"
            item = QListWidgetItem(f"{summary.name}\n{subtitle}")
            item.setData(Qt.UserRole, summary.template_id)
            self.template_list.addItem(item)
        if self.template_list.count() > 0:
            self.template_list.setCurrentRow(0)
        else:
            self.preview.setPlainText(DefaultTexts.NO_SAVED_WORK_ORDER)
            self.btn_load.setEnabled(False)

    def _on_row_changed(self, row: int) -> None:
        item = self.template_list.item(row) if row >= 0 else None
        if item is None:
            self.selected_result = None
            self.preview.clear()
            self.btn_load.setEnabled(False)
            return
        template_id = item.data(Qt.UserRole)
        detail = self._detail_by_id.get(template_id)
        if detail is None:
            self.selected_result = None
            self.preview.setPlainText(DefaultTexts.WORK_ORDER_LOAD_FAILED)
            self.btn_load.setEnabled(False)
            return
        stats = self.order_repository.aggregate_for_template(template_id)
        summary_view = build_work_order_summary_view(detail, order_stats=stats)
        self.preview.setHtml(summary_view.to_detail_html())
        self.selected_result = WorkOrderLoadResult(template_id=template_id, detail=detail)
        self.btn_load.setEnabled(True)

    def _on_item_activated(self, _item: QListWidgetItem) -> None:
        self._accept_selected()

    def _accept_selected(self) -> None:
        if self.selected_result is None:
            return
        self.accept()


__all__ = ["WorkOrderLoadDialog", "WorkOrderLoadResult"]
