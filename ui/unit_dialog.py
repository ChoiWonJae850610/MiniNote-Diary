from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QTableWidget, QAbstractItemView, QHeaderView

from services.unit_service import UnitService
from ui.dialogs import show_info, show_warning
from ui.layout_metrics import CommonSymbolsLayout, UnitDialogLayout
from ui.messages import DialogTitles, InfoMessages, Symbols, TableHeaders, Tooltips
from ui.theme import THEME, table_widget_style
from ui.widget_factory import make_dialog_button_row, make_icon_button
from ui.page_builders_common import make_dialog_root_layout


class UnitDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.UNIT_MANAGE)
        self.resize(THEME.unit_dialog_width, THEME.unit_dialog_height)

        self.project_root = project_root
        self.unit_service = UnitService(project_root)

        layout = make_dialog_root_layout(self)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(list(TableHeaders.UNIT))
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

        self.btn_save = make_icon_button(parent=self, object_name="iconPrimary", tooltip=Tooltips.SAVE, text=Symbols.SAVE, font_px=UnitDialogLayout.ICON_FONT_PX)
        self.btn_add = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.ADD, text=Symbols.ADD, font_px=UnitDialogLayout.ICON_FONT_PX)
        self.btn_delete = make_icon_button(parent=self, object_name="iconDanger", tooltip=Tooltips.DELETE, text=Symbols.DELETE, font_px=UnitDialogLayout.ICON_FONT_PX)
        self.btn_close = make_icon_button(parent=self, object_name="iconAction", tooltip=Tooltips.CLOSE, text=Symbols.CLOSE, font_px=UnitDialogLayout.ICON_FONT_PX)
        layout.addLayout(make_dialog_button_row([self.btn_save, self.btn_add, self.btn_delete, self.btn_close]))

        self.btn_save.clicked.connect(self.on_save)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_close.clicked.connect(self.close)

        self._ensure_empty_row_count(UnitDialogLayout.MIN_ROWS)
        self.load_units()

    def load_units(self):
        units: List[Dict[str, str]] = self.unit_service.list_units()

        self.table.blockSignals(True)
        try:
            self.table.clearContents()
            self.table.setRowCount(0)
            self._ensure_empty_row_count(max(UnitDialogLayout.MIN_ROWS, len(units) + 1))
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
            self.unit_service.save_units(units)
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
