import json
import os
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QAbstractItemView, QHeaderView

from ui.dialogs import show_info, show_warning
from ui.messages import DialogTitles, InfoMessages, Tooltips
from ui.theme import THEME, dialog_layout_margins, table_widget_style
from ui.widget_factory import make_dialog_button_row, make_icon_button


class UnitDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("단위 관리")
        self.resize(THEME.unit_dialog_width, THEME.unit_dialog_height)

        self.project_root = project_root
        self.db_dir = os.path.join(self.project_root, "db")
        os.makedirs(self.db_dir, exist_ok=True)
        self.units_path = os.path.join(self.db_dir, "units.json")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*dialog_layout_margins())
        layout.setSpacing(THEME.block_spacing)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["단위", "표시 이름"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.itemClicked.connect(lambda it: self.table.editItem(it))
        self.table.setStyleSheet(table_widget_style())
        self.table.verticalHeader().setDefaultSectionSize(THEME.table_row_height)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip=Tooltips.SAVE, text="✓", font_px=18)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.ADD, text="+", font_px=18)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip=Tooltips.DELETE, text="−", font_px=18)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.CLOSE, text="×", font_px=18)
        layout.addLayout(make_dialog_button_row([self.btn_save, self.btn_add, self.btn_delete, self.btn_close]))

        self.btn_save.clicked.connect(self.on_save)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_close.clicked.connect(self.close)

        self._ensure_empty_row_count(20)
        self.load_units()

    def load_units(self):
        units: List[Dict[str, str]] = []
        if os.path.isfile(self.units_path):
            try:
                with open(self.units_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                units = data.get("units", [])
                if not isinstance(units, list):
                    units = []
            except Exception:
                units = []

        self.table.blockSignals(True)
        try:
            self.table.clearContents()
            self.table.setRowCount(0)
            self._ensure_empty_row_count(max(20, len(units) + 1))
            for r, u in enumerate(units):
                if not isinstance(u, dict):
                    continue
                self.table.setItem(r, 0, self._make_item(u.get("unit", "")))
                self.table.setItem(r, 1, self._make_item(u.get("label", "")))
        finally:
            self.table.blockSignals(False)

    def on_save(self):
        units = []
        for r in range(self.table.rowCount()):
            unit = self._cell_text(r, 0).strip()
            label = self._cell_text(r, 1).strip()
            if not unit and not label:
                continue
            units.append({"unit": unit, "label": label})

        try:
            with open(self.units_path, "w", encoding="utf-8") as f:
                json.dump({"units": units}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            show_warning(self, DialogTitles.SAVE_FAILED, str(e))
            return

        show_info(self, DialogTitles.SAVE, InfoMessages.UNITS_SAVED)

    def on_add(self):
        for r in range(self.table.rowCount()):
            if not self._cell_text(r, 0).strip() and not self._cell_text(r, 1).strip():
                if self.table.item(r, 0) is None:
                    self.table.setItem(r, 0, self._make_item(""))
                if self.table.item(r, 1) is None:
                    self.table.setItem(r, 1, self._make_item(""))
                self.table.setCurrentCell(r, 0)
                self.table.editItem(self.table.item(r, 0))
                return
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setRowHeight(r, THEME.table_row_height)
        self.table.setItem(r, 0, self._make_item(""))
        self.table.setItem(r, 1, self._make_item(""))
        self.table.setCurrentCell(r, 0)
        self.table.editItem(self.table.item(r, 0))

    def on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.table.blockSignals(True)
        try:
            self.table.setItem(row, 0, self._make_item(""))
            self.table.setItem(row, 1, self._make_item(""))
        finally:
            self.table.blockSignals(False)

    def _ensure_empty_row_count(self, target_rows: int):
        while self.table.rowCount() < target_rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setRowHeight(r, THEME.table_row_height)

    def _cell_text(self, r: int, c: int) -> str:
        it = self.table.item(r, c)
        return it.text() if it else ""

    def _make_item(self, text: str):
        from PySide6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        return item
