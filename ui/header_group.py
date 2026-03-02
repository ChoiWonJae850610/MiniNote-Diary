# ui/header_group.py
from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QFormLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QDateEdit,
    QSizePolicy,
    QGridLayout,
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setFixedHeight(30)

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
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(12)
        layout.setContentsMargins(12, 14, 12, 12)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setFixedHeight(30)
        self.date.setDate(QDate.currentDate())

        self.style_no = QLineEdit()
        self.factory = QLineEdit()
        for w in (self.style_no, self.factory):
            w.setFixedHeight(30)

        # ✅ 원가/공임/로스/판매가: 한 줄에 (라벨+필드) x4
        price_row = QWidget()
        grid = QGridLayout(price_row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(0)

        self.cost = MoneyLineEdit()
        self.labor = MoneyLineEdit()
        self.loss = MoneyLineEdit()
        self.sale_price = MoneyLineEdit()

        # 필드 폭을 줄여서 4개가 한 줄에 들어가게
        for e in (self.cost, self.labor, self.loss, self.sale_price):
            e.setMinimumWidth(90)
            e.setMaximumWidth(140)

        pairs = [
            ("원가", self.cost),
            ("공임", self.labor),
            ("로스", self.loss),
            ("판매가", self.sale_price),
        ]

        col = 0
        for label_text, edit in pairs:
            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            grid.addWidget(lbl, 0, col)
            grid.addWidget(edit, 0, col + 1)

            grid.setColumnStretch(col, 0)
            grid.setColumnStretch(col + 1, 1)
            col += 2

        layout.addRow("날 짜", self.date)
        layout.addRow("제품명", self.style_no)
        layout.addRow("공 장", self.factory)
        layout.addRow("", price_row)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMinimumHeight(180)

    def get_data(self):
        return {
            "date": self.date.date().toString("yyyy-MM-dd"),
            "style_no": self.style_no.text(),
            "factory": self.factory.text(),
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.value_digits(),
            "labor": self.labor.value_digits(),
            "loss": self.loss.value_digits(),
            "sale_price": self.sale_price.value_digits(),
        }