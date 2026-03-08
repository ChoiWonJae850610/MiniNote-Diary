import json
import os
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QAbstractItemView, QMessageBox, QHeaderView, QTableWidgetItem
)

from ui.theme import THEME, build_app_stylesheet, icon_button_override


class UnitDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("단위 관리")
        self.resize(520, 420)
        self.setStyleSheet(build_app_stylesheet())

        self.project_root = project_root
        self.db_dir = os.path.join(self.project_root, "db")
        os.makedirs(self.db_dir, exist_ok=True)
        self.units_path = os.path.join(self.db_dir, "units.json")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["단위", "표시 이름"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )
        self.table.itemClicked.connect(lambda it: self.table.editItem(it))
        self.table.setStyleSheet(
            "QTableWidget{"
            "background:#FFFFFF;"
            "border:1px solid #D7DCE3;"
            "border-radius:12px;"
            "gridline-color:transparent;"
            "selection-background-color:transparent;"
            "selection-color:#1F2933;"
            "padding:4px;"
            "}"
            "QHeaderView::section{"
            "background:#FAFAFB;"
            "color:#364152;"
            "border:none;"
            "border-bottom:1px solid #E7EBF0;"
            "padding:8px 10px;"
            "font-weight:600;"
            "}"
            "QTableWidget::item{"
            "border:1px solid transparent;"
            "padding:4px 6px;"
            "}"
            "QTableWidget::item:selected{"
            "background:#F5F6F8;"
            "color:#1F2933;"
            "border:1px solid #E7EBF0;"
            "}"
            "QTableWidget::item:focus{outline:none;}"
            "QTableWidget QLineEdit{"
            "background:#F5F6F8;"
            "border:1px solid transparent;"
            "border-radius:8px;"
            "padding:0 6px;"
            "color:#1F2933;"
            "selection-background-color:#E9EDF2;"
            "selection-color:#1F2933;"
            "}"
            "QTableWidget QLineEdit:focus{"
            "background:#FFFFFF;"
            "border:1px solid rgba(98,107,119,0.28);"
            "}"
        )
        self.table.verticalHeader().setDefaultSectionSize(30)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.btn_save = QPushButton("✓")
        self.btn_add = QPushButton("+")
        self.btn_delete = QPushButton("−")
        self.btn_close = QPushButton("×")

        self.btn_save.setObjectName("iconPrimary")
        self.btn_add.setObjectName("iconAction")
        self.btn_delete.setObjectName("iconDanger")
        self.btn_close.setObjectName("iconAction")

        for b in (self.btn_save, self.btn_add, self.btn_delete, self.btn_close):
            b.setFixedSize(THEME.icon_button_size, THEME.icon_button_size)
            b.setContentsMargins(0, 0, 0, 0)
            b.setCursor(Qt.PointingHandCursor)
            f = b.font()
            f.setPointSize(THEME.icon_button_font_px + 2)
            f.setBold(True)
            b.setFont(f)

        self.btn_save.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))
        self.btn_add.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))
        self.btn_delete.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))
        self.btn_close.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))

        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_close)

        layout.addLayout(btn_row)

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

        payload = {"units": units}

        try:
            with open(self.units_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "저장 실패", str(e))
            return

        QMessageBox.information(self, "저장", "단위 목록이 저장되었습니다.")

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
        self.table.setRowHeight(r, 30)
        self.table.setItem(r, 0, self._make_item(""))
        self.table.setItem(r, 1, self._make_item(""))
        self.table.setCurrentCell(r, 0)
        self.table.editItem(self.table.item(r, 0))

    def on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return

        # 현재 행 셀 비우기(행 삭제 대신 UX 안정적)
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
            self.table.setRowHeight(r, 30)

    def _cell_text(self, r: int, c: int) -> str:
        it = self.table.item(r, c)
        return it.text() if it else ""

    def _make_item(self, text: str):
        from PySide6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        return item