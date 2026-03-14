from __future__ import annotations

from PySide6.QtWidgets import QAbstractItemView, QDialog, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout

from services.partner_repository import PartnerRepository
from ui.dialogs import show_info
from ui.messages import DialogTitles, InfoMessages, Tooltips
from ui.theme import THEME, dialog_layout_margins
from ui.widget_factory import make_dialog_button_row, make_icon_button


class PartnerTypeDialog(QDialog):
    def __init__(self, repo: PartnerRepository, parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.PARTNER_TYPE_MANAGE)
        self.resize(540, 420)
        self.repo = repo

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        self.table = QTableWidget(0, 1, self)
        self.table.setHorizontalHeaderLabels([DialogTitles.PARTNER_TYPE])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.itemClicked.connect(lambda it: self.table.editItem(it))
        self.table.setStyleSheet(
            f"QTableWidget{{background:{THEME.color_window};border:1px solid {THEME.color_border};border-radius:12px;padding:4px;}}"
            f"QHeaderView::section{{background:{THEME.color_surface};border:none;border-bottom:1px solid {THEME.color_border_soft};padding:8px 10px;font-weight:600;color:{THEME.color_text_soft};}}"
        )
        self.table.verticalHeader().setDefaultSectionSize(THEME.table_row_height)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        root.addWidget(self.table)

        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip=Tooltips.SAVE, text="✓", font_px=18)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.ADD, text="+", font_px=18)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip=Tooltips.DELETE, text="−", font_px=18)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.CLOSE, text="×", font_px=18)
        root.addLayout(make_dialog_button_row([self.btn_save, self.btn_add, self.btn_delete, self.btn_close]))

        self.btn_save.clicked.connect(self.on_save)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_close.clicked.connect(self.reject)

        self._ensure_rows(16)
        self.load_types()

    def _ensure_rows(self, target: int) -> None:
        while self.table.rowCount() < target:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, THEME.table_row_height)

    def load_types(self) -> None:
        types = self.repo.load_types()
        self.table.clearContents()
        self.table.setRowCount(0)
        self._ensure_rows(max(16, len(types) + 1))
        for row, type_name in enumerate(types):
            self.table.setItem(row, 0, QTableWidgetItem(type_name))

    def on_add(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is None or not item.text().strip():
                if item is None:
                    item = QTableWidgetItem("")
                    self.table.setItem(row, 0, item)
                self.table.setCurrentCell(row, 0)
                self.table.editItem(item)
                return

    def on_delete(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        self.table.setItem(row, 0, QTableWidgetItem(""))

    def on_save(self) -> None:
        values: list[str] = []
        seen: set[str] = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            text = item.text().strip() if item else ""
            if text and text not in seen:
                values.append(text)
                seen.add(text)
        self.repo.save_types(values)
        show_info(self, DialogTitles.SAVE, InfoMessages.PARTNER_TYPES_SAVED)
        self.accept()
