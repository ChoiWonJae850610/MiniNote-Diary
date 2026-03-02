# ui/material_item_dialog.py
from __future__ import annotations

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
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


class CommaIntEdit(QLineEdit):
    """
    - 숫자만 입력 허용 (0-9, 콤마만)
    - 입력 중 자동으로 3자리 콤마 포맷 적용
    """

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


class MoneyEdit(CommaIntEdit):
    """단가/총액 입력용(콤마 + 숫자만)."""
    pass


class MaterialItemDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.vendor = QLineEdit()
        self.item = QLineEdit()

        # ✅ 요청: 수량/단가도 원가/공임처럼 콤마 + 숫자만
        self.qty = CommaIntEdit()
        self.unit = QLineEdit()
        self.unit_price = MoneyEdit()
        self.total = MoneyEdit()
        self.total.setReadOnly(True)

        for w in (self.vendor, self.item, self.unit):
            w.setFixedHeight(30)

        form.addRow("거래처", self.vendor)
        form.addRow("품목", self.item)
        form.addRow("수량", self.qty)
        form.addRow("단위", self.unit)
        form.addRow("단가", self.unit_price)
        form.addRow("총액", self.total)

        root.addLayout(form)

        # (기존 안내 문구는 팝업 내라서 유지)
        tip = QLabel("수량·단가를 입력하면 총액이 자동 계산됩니다.")
        tip.setStyleSheet("color:#666;")
        root.addWidget(tip)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_cancel = QPushButton("취소")
        self.btn_ok = QPushButton("추가")
        self.btn_cancel.setFixedHeight(34)
        self.btn_ok.setFixedHeight(34)
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_ok)
        root.addLayout(btn_row)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._on_ok)

        self.qty.textChanged.connect(self._recalc_total)
        self.unit_price.textChanged.connect(self._recalc_total)

    def _recalc_total(self):
        q = self.qty.value_digits()
        p = self.unit_price.value_digits()
        if not q or not p:
            self.total.setText("")
            return
        try:
            total = int(q) * int(p)
            self.total.setText(f"{total:,}")
        except Exception:
            self.total.setText("")

    def _on_ok(self):
        if not (self.vendor.text().strip() or self.item.text().strip()):
            self.vendor.setFocus()
            return
        self.accept()

    def get_item(self) -> dict:
        return {
            "거래처": self.vendor.text().strip(),
            "품목": self.item.text().strip(),
            "수량": self.qty.text().strip(),
            "단위": self.unit.text().strip(),
            "단가": self.unit_price.text().strip(),
            "총액": self.total.text().strip(),
        }