# ui/trims_table.py
from __future__ import annotations

import json
import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QComboBox,
    QStyledItemDelegate,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _format_commas(s: str) -> str:
    d = _digits_only(s)
    if not d:
        return ""
    try:
        return f"{int(d):,}"
    except Exception:
        return d


class MoneyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(0, 2_147_483_647, editor))
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor

    def setEditorData(self, editor, index):
        text = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        editor.setText(_digits_only(str(text)))

    def setModelData(self, editor, model, index):
        raw = _digits_only(editor.text())
        model.setData(index, raw, Qt.EditRole)

    def displayText(self, value, locale):
        return _format_commas(str(value))


class NumberDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(0, 2_147_483_647, editor))
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor

    def setEditorData(self, editor, index):
        text = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        editor.setText(_digits_only(str(text)))

    def setModelData(self, editor, model, index):
        raw = _digits_only(editor.text())
        model.setData(index, raw, Qt.EditRole)


class UnitComboDelegate(QStyledItemDelegate):
    """
    단위 콤보
    - 드롭다운 목록: label 표시
    - 선택 후 셀 값: unit 저장/표시
    """

    def __init__(self, unit_items: list[dict], parent=None):
        super().__init__(parent)
        self.unit_items = unit_items

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.setEditable(False)

        for it in self.unit_items:
            label = str(it.get("label", "")).strip()
            unit = str(it.get("unit", "")).strip()
            if label and unit:
                cb.addItem(label, unit)

        cb.setMinimumWidth(140)
        try:
            cb.view().setMinimumWidth(280)
        except Exception:
            pass
        return cb

    def setEditorData(self, editor, index):
        unit = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        unit = str(unit).strip()

        for i in range(editor.count()):
            if str(editor.itemData(i)).strip() == unit:
                editor.setCurrentIndex(i)
                return

        if editor.count() > 0:
            editor.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        unit = editor.currentData()
        unit = "" if unit is None else str(unit)
        model.setData(index, unit, Qt.EditRole)

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)


class TrimsTable(QWidget):
    """
    부자재 + 외주작업
    컬럼: 거래처, 품목, 수량, 단위, 단가, 토탈
    """

    VISIBLE_ROWS = 3

    COL_VENDOR = 0
    COL_ITEM = 1
    COL_QTY = 2
    COL_UNIT = 3
    COL_PRICE = 4
    COL_TOTAL = 5

    COLUMN_WIDTHS_FIXED = {
        COL_VENDOR: 130,
        COL_QTY: 70,
        COL_UNIT: 95,
        COL_PRICE: 105,
        COL_TOTAL: 105,
    }
    STRETCH_COLUMN = COL_ITEM

    def __init__(self, title: str = "부자재 + 외주작업", parent=None):
        super().__init__(parent)
        self.title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)

        self.btn_add = QPushButton("행 추가")
        self.btn_del = QPushButton("선택 삭제")
        self.btn_add.setFixedHeight(26)
        self.btn_del.setFixedHeight(26)

        top.addWidget(self.btn_add)
        top.addWidget(self.btn_del)
        top.addStretch(1)

        self.table = QTableWidget(3, 6)
        self.table.setHorizontalHeaderLabels(["거래처", "품목", "수량", "단위", "단가", "토탈"])

        # 테이블 미관 개선(줄무늬/그리드)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.CurrentChanged
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
        )

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        vh = self.table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(26)

        self._apply_header_resize_policy()

        self.table.verticalScrollBar().setSingleStep(vh.defaultSectionSize() or 26)
        self._fix_table_height(self.VISIBLE_ROWS)

        # 단위 콤보: db/units.json (label 표시 / unit 저장)
        self.unit_delegate = UnitComboDelegate(self._load_unit_items(), self.table)
        self.table.setItemDelegateForColumn(self.COL_UNIT, self.unit_delegate)

        self.table.setItemDelegateForColumn(self.COL_QTY, NumberDelegate(self.table))
        self.table.setItemDelegateForColumn(self.COL_PRICE, MoneyDelegate(self.table))
        self.table.setItemDelegateForColumn(self.COL_TOTAL, MoneyDelegate(self.table))

        self._init_cells()

        layout.addLayout(top)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.delete_selected_row)

    def _apply_header_resize_policy(self):
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(False)

        for c in range(self.table.columnCount()):
            hh.setSectionResizeMode(c, QHeaderView.Fixed)

        for c, w in self.COLUMN_WIDTHS_FIXED.items():
            self.table.setColumnWidth(c, w)

        hh.setSectionResizeMode(self.STRETCH_COLUMN, QHeaderView.Stretch)

    def _fix_table_height(self, visible_rows: int = 3):
        vh = self.table.verticalHeader()
        hh = self.table.horizontalHeader()
        row_h = vh.defaultSectionSize() or 26
        header_h = hh.sizeHint().height()
        frame = self.table.frameWidth() * 2
        target_h = header_h + (row_h * visible_rows) + frame + 2
        self.table.setFixedHeight(target_h)

    def _init_cells(self):
        self.table.blockSignals(True)
        try:
            for r in range(self.table.rowCount()):
                for c in range(self.table.columnCount()):
                    it = self.table.item(r, c)
                    if it is None:
                        it = QTableWidgetItem("")
                        self.table.setItem(r, c, it)

                    if c == self.COL_UNIT:
                        it.setTextAlignment(Qt.AlignCenter)
                    elif c in (self.COL_QTY, self.COL_PRICE, self.COL_TOTAL):
                        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    else:
                        it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        finally:
            self.table.blockSignals(False)

    def _load_unit_items(self) -> list[dict]:
        default_items = [
            {"unit": "EA", "label": "EA (개)"},
            {"unit": "PCS", "label": "PCS (피스)"},
            {"unit": "SET", "label": "SET (세트)"},
            {"unit": "PAIR", "label": "PAIR (쌍)"},
            {"unit": "PACK", "label": "PACK (팩)"},
            {"unit": "BOX", "label": "BOX (박스)"},
            {"unit": "JOB", "label": "JOB (작업 1건)"},
        ]

        def _read_units(path: str) -> list[dict]:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items: list[dict] = []
            for u in (data.get("units") or []):
                unit = str(u.get("unit", "")).strip()
                label = str(u.get("label", "")).strip()
                if unit and label:
                    items.append({"unit": unit, "label": label})
            return items

        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            candidates = [
                os.path.join(project_root, "db", "units.json"),
                os.path.join(project_root, "db", "unit.json"),
            ]

            for p in candidates:
                if os.path.isfile(p):
                    items = _read_units(p)
                    if items:
                        return items

            return default_items
        except Exception:
            return default_items

    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self._init_cells()
        self.table.setCurrentCell(r, 0)
        self.table.editItem(self.table.item(r, 0))

    def delete_selected_row(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)

        if self.table.rowCount() < 3:
            while self.table.rowCount() < 3:
                self.table.insertRow(self.table.rowCount())
            self._init_cells()