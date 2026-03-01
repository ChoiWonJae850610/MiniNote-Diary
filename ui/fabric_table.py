from __future__ import annotations

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
    """숫자만 입력 + 표시 시 천단위 콤마"""

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
    """숫자 입력(콤마 없음)"""

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
    """단위 콤보 + 가운데 정렬 + 팝업 폭 증가"""

    def __init__(self, units: list[str], parent=None):
        super().__init__(parent)
        self.units = units

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.setEditable(False)
        cb.addItems(self.units)

        # 콤보 자체/팝업 폭 키우기
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


class FabricTable(QWidget):
    """
    원단 테이블
    컬럼: 원단처, 원단이름, 요척, 단위, 단가, 토탈
    """

    COL_VENDOR = 0
    COL_NAME = 1
    COL_REQ = 2
    COL_UNIT = 3
    COL_PRICE = 4
    COL_TOTAL = 5

    # ===========================
    # ✅ 사용자가 여기 숫자만 바꿔서 조정 가능
    # (Stretch 컬럼은 폭을 강제로 지정하지 않음)
    # ===========================
    COLUMN_WIDTHS_FIXED = {
        COL_VENDOR: 130,  # 원단처 (늘리기 쉬움)
        COL_REQ: 70,      # 요척 (숫자)
        COL_UNIT: 95,     # 단위
        COL_PRICE: 105,   # 단가
        COL_TOTAL: 105    # 토탈
    }
    STRETCH_COLUMN = COL_NAME  # ✅ 원단이름이 남는 폭을 먹거나 부족하면 줄어드는 역할

    def __init__(self, title: str = "원단", parent=None):
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
        self.table.setHorizontalHeaderLabels(["원단처", "원단이름", "요척", "단위", "단가", "토탈"])

        # 셀 단위 선택 + 클릭 즉시 편집
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.CurrentChanged |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        # 스크롤: 세로만 필요시 표시, 가로는 없애되 "Stretch"로 해결
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        vh = self.table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(26)

        # ✅ 토탈이 가려지지 않게: fixed + stretch 조합
        self._apply_header_resize_policy()

        # 단위 콤보(가운데 정렬)
        self.unit_delegate = UnitComboDelegate(self._load_units(), self.table)
        self.table.setItemDelegateForColumn(self.COL_UNIT, self.unit_delegate)

        # 숫자/금액 delegate
        self.table.setItemDelegateForColumn(self.COL_REQ, NumberDelegate(self.table))
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

        # 기본은 Fixed
        for c in range(self.table.columnCount()):
            hh.setSectionResizeMode(c, QHeaderView.Fixed)

        # fixed 폭 적용
        for c, w in self.COLUMN_WIDTHS_FIXED.items():
            self.table.setColumnWidth(c, w)

        # ✅ 원단이름은 Stretch: 남는 폭 먹고, 부족하면 줄어서 토탈이 안 밀림
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
                    elif c in (self.COL_REQ, self.COL_PRICE, self.COL_TOTAL):
                        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    else:
                        it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        finally:
            self.table.blockSignals(False)

    def _load_units(self) -> list[str]:
        # 프로젝트에서 이미 units.json을 읽는 로더가 있다면 여기서 그걸 호출하는 게 정석.
        # 현재는 안전 기본값.
        return [
            "EA (개)", "PCS (피스)", "SET (세트)", "PAIR (쌍)",
            "MM (밀리미터)", "CM (센티미터)", "M (미터)", "YD (야드)",
            "G (그램)", "KG (킬로그램)", "ROLL (원단 롤)"
        ]

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