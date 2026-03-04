# ui/trims_table.py
from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGroupBox,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


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
    def createEditor(self, parent, option, index):  # noqa: N802
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(0, 2_147_483_647, editor))
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor

    def setEditorData(self, editor, index):  # noqa: N802
        text = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        editor.setText(_digits_only(str(text)))

    def setModelData(self, editor, model, index):  # noqa: N802
        raw = _digits_only(editor.text())
        model.setData(index, raw, Qt.EditRole)

    def displayText(self, value, locale):  # noqa: N802
        return _format_commas(str(value))


class NumberDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):  # noqa: N802
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(0, 2_147_483_647, editor))
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor

    def setEditorData(self, editor, index):  # noqa: N802
        text = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        editor.setText(_digits_only(str(text)))

    def setModelData(self, editor, model, index):  # noqa: N802
        raw = _digits_only(editor.text())
        model.setData(index, raw, Qt.EditRole)


class UnitComboDelegate(QStyledItemDelegate):
    def __init__(self, unit_items: list[dict], parent=None):
        super().__init__(parent)
        self.unit_items = unit_items

    def createEditor(self, parent, option, index):  # noqa: N802
        cb = QComboBox(parent)
        cb.setEditable(False)
        cb.setInsertPolicy(QComboBox.NoInsert)

        # 빈 값 1개 (삭제용)
        cb.addItem("", "")

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

        cb.installEventFilter(self)
        return cb

    def eventFilter(self, obj, event):  # noqa: N802
        if isinstance(obj, QComboBox) and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                obj.setCurrentIndex(0)
                return True
        return super().eventFilter(obj, event)

    def setEditorData(self, editor, index):  # noqa: N802
        unit = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        unit = str(unit).strip()

        for i in range(editor.count()):
            if str(editor.itemData(i)).strip() == unit:
                editor.setCurrentIndex(i)
                return
        editor.setCurrentIndex(0)

    def setModelData(self, editor, model, index):  # noqa: N802
        unit = editor.currentData()
        unit = "" if unit is None else str(unit)
        model.setData(index, unit, Qt.EditRole)

    def paint(self, painter, option, index):  # noqa: N802
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)


class TrimsTable(QGroupBox):
    VISIBLE_ROWS = 3

    COL_VENDOR = 0
    COL_ITEM = 1
    COL_QTY = 2
    COL_UNIT = 3
    COL_PRICE = 4
    COL_TOTAL = 5

    COLUMN_WIDTHS_FIXED = {
        COL_VENDOR: 150,
        COL_QTY: 80,
        COL_UNIT: 90,
        COL_PRICE: 110,
        COL_TOTAL: 110,
    }
    STRETCH_COLUMN = COL_ITEM

    def __init__(self, title: str = "부자재 + 외주작업", parent=None):
        super().__init__(title, parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 12)
        layout.setSpacing(8)

        self.table = QTableWidget(3, 6, self)
        self.table.setHorizontalHeaderLabels(["거래처", "품목", "수량", "단위", "단가", "토탈"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        vh = self.table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(28)

        self._apply_header_resize_policy()
        self.table.verticalScrollBar().setSingleStep(vh.defaultSectionSize() or 28)

        self._fix_table_height(self.VISIBLE_ROWS)

        self.unit_delegate = UnitComboDelegate(self._load_unit_items(), self.table)
        self.table.setItemDelegateForColumn(self.COL_UNIT, self.unit_delegate)
        self.table.setItemDelegateForColumn(self.COL_QTY, NumberDelegate(self.table))
        self.table.setItemDelegateForColumn(self.COL_PRICE, MoneyDelegate(self.table))
        self.table.setItemDelegateForColumn(self.COL_TOTAL, MoneyDelegate(self.table))

        self._init_cells()
        layout.addWidget(self.table)

        self.btn_add = QPushButton("+", self)
        self.btn_del = QPushButton("-", self)
        for b in (self.btn_add, self.btn_del):
            b.setFixedSize(34, 30)
            b.raise_()
        self.btn_add.setToolTip("행 추가")
        self.btn_del.setToolTip("선택 행 삭제")
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.delete_selected_row)

        self._sync_group_height()

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._position_buttons()

    def _position_buttons(self):
        margin_right = 12
        gap = 6
        y = 18
        bw = self.btn_add.width()
        x_del = self.width() - margin_right - bw
        x_add = x_del - gap - bw
        self.btn_add.move(x_add, y)
        self.btn_del.move(x_del, y)

    def _sync_group_height(self):
        title_h = 28
        top_bottom_margins = 14 + 12
        spacing = 8
        h = title_h + top_bottom_margins + spacing + self.table.height()
        self.setFixedHeight(h)

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
        row_h = vh.defaultSectionSize() or 28
        header_h = hh.sizeHint().height()
        frame = self.table.frameWidth() * 2
        target_h = header_h + (row_h * visible_rows) + frame + 4
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

    def delete_selected_row(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)

        if self.table.rowCount() < 3:
            while self.table.rowCount() < 3:
                self.table.insertRow(self.table.rowCount())
            self._init_cells()
