# ui/header_group.py
from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QDateEdit,
    QSizePolicy,
)
from PySide6.QtCore import QDate, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _format_commas_from_digits(digits: str) -> str:
    if not digits:
        return ""
    try:
        return f"{int(digits):,}"
    except Exception:
        return digits


class MoneyLineEdit(QLineEdit):
    """
    - 숫자만 입력(붙여넣기 포함) -> 내부적으로 digits만 유지
    - 표시: 천단위 콤마
    - text()는 콤마 포함, value_digits()는 콤마 제거 digits
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 콤마가 들어간 상태로 setText를 해도 validator가 막지 않도록 [0-9,] 허용
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setFixedHeight(26)

        self._in_format = False
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        if self._in_format:
            return

        digits = _digits_only(text)
        formatted = _format_commas_from_digits(digits)

        if formatted == text:
            return

        self._in_format = True
        try:
            # 커서는 끝으로 보내는 단순 정책(안정적)
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
        finally:
            self._in_format = False

    def value_digits(self) -> str:
        return _digits_only(self.text())


class HeaderGroup(QGroupBox):
    def __init__(self):
        super().__init__("제품 정보")

        layout = QFormLayout(self)
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setFixedHeight(26)
        self.date.setDate(QDate.currentDate())  # ✅ 오늘 날짜로

        self.style_no = QLineEdit()
        self.factory = QLineEdit()

        for w in (self.style_no, self.factory):
            w.setFixedHeight(26)

        # ✅ 매장(store) 삭제 -> 원가/공임/판매가 3등분
        price_row = QWidget()
        h = QHBoxLayout(price_row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        self.cost = MoneyLineEdit()
        self.labor = MoneyLineEdit()
        self.sale_price = MoneyLineEdit()

        # 라벨 + 입력을 한 묶음으로 3개 배치
        def pack(label_text: str, editor: QLineEdit) -> QWidget:
            w = QWidget()
            hh = QHBoxLayout(w)
            hh.setContentsMargins(0, 0, 0, 0)
            hh.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setFixedWidth(36)  # 간단 고정(원가/공임/판매가 정렬용)
            hh.addWidget(lbl)
            hh.addWidget(editor, 1)
            return w

        h.addWidget(pack("원가", self.cost), 1)
        h.addWidget(pack("공임", self.labor), 1)
        h.addWidget(pack("판매가", self.sale_price), 1)

        layout.addRow("날   짜", self.date)
        layout.addRow("제품명", self.style_no)
        layout.addRow("공   장", self.factory)
        layout.addRow("", price_row)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def get_data(self):
        # header는 기존처럼 dict 반환하되 store 대신 금액 3종 추가
        return {
            "date": self.date.date().toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),

            # 표시(콤마 포함)
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "sale_price_display": self.sale_price.text(),

            # 저장/계산용(콤마 제거 digits)
            "cost": self.cost.value_digits(),
            "labor": self.labor.value_digits(),
            "sale_price": self.sale_price.value_digits(),
        }