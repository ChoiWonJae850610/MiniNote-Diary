from __future__ import annotations

import json
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QComboBox, QStyledItemDelegate, QLineEdit
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
    def __init__(self, units: list[str], parent=None):
        super().__init__(parent)
        self.units = units

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.setEditable(False)
        cb.addItems(self.units)
        cb.setMinimumWidth(140)
        try:
            cb.view().setMinimumWidth(280)
        except Exception:
            pass
        return cb

    def setEditorData(self, editor, index):
        val = index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""
        val = str(val)
        i = editor.findText(val)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)


class TrimsTable(QWidget):
    """
    부자재 + 외주작업
    컬럼: 거래처, 품목, 수량, 단위, 단가, 토탈
    """

    COL_VENDOR = 0
    COL_ITEM = 1
    COL_QTY = 2
    COL_UNIT = 3
    COL_PRICE = 4
    COL_TOTAL = 5

    # ===========================
    # ✅ 사용자가 여기 숫자만 바꿔서 조정 가능
    # ===========================
    COLUMN_WIDTHS_FIXED = {
        COL_VENDOR: 130,  # 거래처
        COL_QTY: 70,      # 수량
        COL_UNIT: 95,     # 단위
        COL_PRICE: 105,   # 단가
        COL_TOTAL: 105,   # 토탈
    }
    STRETCH_COLUMN = COL_ITEM  # ✅ 품목이 남는 폭을 먹거나 부족하면 줄어드는 역할

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

        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.CurrentChanged
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
        )

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        vh = self.table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(26)

        self._apply_header_resize_policy()

        # ✅ 단위 콤보 - db/units.json 로드
        self.unit_delegate = UnitComboDelegate(self._load_units(), self.table)
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

        # ✅ 품목 stretch
        hh.setSectionResizeMode(self.STRETCH_COLUMN, QHeaderView.Stretch)

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

    def _load_units(self) -> list[str]:
        """
        db/units.json의 units[].label을 콤보 항목으로 사용.
        - 실패 시 안전 기본값 fallback
        """
        default_units = [
            "EA (개)", "PCS (피스)", "SET (세트)", "PAIR (쌍)",
            "MM (밀리미터)", "CM (센티미터)", "M (미터)", "YD (야드)",
            "G (그램)", "KG (킬로그램)", "PACK (팩)", "BOX (박스)",
            "JOB (작업 1건)",
        ]

        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            units_path = os.path.join(project_root, "db", "units.json")
            if not os.path.isfile(units_path):
                return default_units

            with open(units_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            labels: list[str] = []
            for u in (data.get("units") or []):
                label = (u.get("label") or "").strip()
                if label:
                    labels.append(label)

            return labels or default_units
        except Exception:
            return default_units

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