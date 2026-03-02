# ui/basic_info_dialog.py
from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QPushButton,
    QWidget,
    QGridLayout,
)


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


class BasicInfoDialog(QDialog):
    def __init__(self, initial: Dict[str, str] | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("기본정보 입력")
        self.setModal(True)
        self.setMinimumWidth(460)

        initial = initial or {}

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setFixedHeight(30)
        self.date.setDate(QDate.fromString(initial.get("date", ""), "yyyy-MM-dd") or QDate.currentDate())

        self.style_no = QLineEdit()
        self.factory = QLineEdit()
        for w in (self.style_no, self.factory):
            w.setFixedHeight(30)

        self.style_no.setText(initial.get("style_no", ""))
        self.factory.setText(initial.get("factory", ""))

        # 금액 4개 한줄
        price_row = QWidget()
        grid = QGridLayout(price_row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)

        self.cost = MoneyLineEdit()
        self.labor = MoneyLineEdit()
        self.loss = MoneyLineEdit()
        self.sale_price = MoneyLineEdit()

        self.cost.setText(initial.get("cost_display", ""))
        self.labor.setText(initial.get("labor_display", ""))
        self.loss.setText(initial.get("loss_display", ""))
        self.sale_price.setText(initial.get("sale_price_display", ""))

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
            col += 2

        form.addRow("날짜", self.date)
        form.addRow("제품명", self.style_no)
        form.addRow("공장", self.factory)
        form.addRow("", price_row)

        root.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_cancel = QPushButton("취소")
        btn_ok = QPushButton("확인")
        btn_cancel.setFixedHeight(34)
        btn_ok.setFixedHeight(34)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        root.addLayout(btn_row)

        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)

    def get_data(self) -> Dict[str, str]:
        return {
            "date": self.date.date().toString("yyyy-MM-dd"),
            "style_no": self.style_no.text().strip(),
            "factory": self.factory.text().strip(),
            "cost_display": self.cost.text(),
            "labor_display": self.labor.text(),
            "loss_display": self.loss.text(),
            "sale_price_display": self.sale_price.text(),
            "cost": self.cost.value_digits(),
            "labor": self.labor.value_digits(),
            "loss": self.loss.value_digits(),
            "sale_price": self.sale_price.value_digits(),
        }