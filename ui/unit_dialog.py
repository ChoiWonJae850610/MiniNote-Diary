import json
import os
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QAbstractItemView, QMessageBox, QHeaderView
)


class UnitDialog(QDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("단위 관리")
        self.resize(520, 420)

        self.project_root = project_root
        self.db_dir = os.path.join(self.project_root, "db")
        os.makedirs(self.db_dir, exist_ok=True)
        self.units_path = os.path.join(self.db_dir, "units.json")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.table = QTableWidget(20, 2)
        self.table.setHorizontalHeaderLabels(["단위", "표시 이름"])

        # 셀 단위 선택 + 클릭 즉시 입력
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.CurrentChanged |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )
        self.table.itemClicked.connect(lambda it: self.table.editItem(it))

        # 선택 하이라이트 최소화(입력칸 느낌)
        self.table.setStyleSheet("""
            QTableWidget::item:selected { background: transparent; color: inherit; }
            QTableWidget::item:focus { outline: none; }
        """)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.btn_save = QPushButton("저장")
        self.btn_delete = QPushButton("삭제")
        self.btn_close = QPushButton("닫기")

        for b in (self.btn_save, self.btn_delete, self.btn_close):
            b.setFixedHeight(30)

        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_close)

        layout.addLayout(btn_row)

        self.btn_save.clicked.connect(self.on_save)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_close.clicked.connect(self.close)

        self.load_units()

    def load_units(self):
        if not os.path.isfile(self.units_path):
            return

        try:
            with open(self.units_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        units: List[Dict[str, str]] = data.get("units", [])
        self.table.blockSignals(True)
        try:
            self.table.clearContents()
            for r, u in enumerate(units[: self.table.rowCount()]):
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

    def _cell_text(self, r: int, c: int) -> str:
        it = self.table.item(r, c)
        return it.text() if it else ""

    def _make_item(self, text: str):
        from PySide6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        return item