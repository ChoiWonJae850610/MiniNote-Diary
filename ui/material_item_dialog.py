# ui/material_item_dialog.py
from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt, QRegularExpression, QEvent
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QLabel, QLineEdit, QVBoxLayout

from ui.theme import THEME, combo_box_style, dialog_layout_margins, hint_label_style, input_line_edit_style, read_only_line_edit_style
from ui.widget_factory import make_dialog_button, make_dialog_button_row


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _format_commas_from_digits(digits: str) -> str:
    if not digits:
        return ""
    try:
        return f"{int(digits):,}"
    except Exception:
        return digits


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_units() -> list[dict]:
    path = os.path.join(_project_root(), "db", "units.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        units = data.get("units", [])
        out: list[dict] = []
        if isinstance(units, list):
            for u in units:
                if not isinstance(u, dict):
                    continue
                unit = str(u.get("unit", "")).strip()
                label = str(u.get("label", "")).strip()
                if unit or label:
                    out.append({"unit": unit, "label": label})
        return out
    except Exception:
        return []


class ClearableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(False)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.installEventFilter(self)
        self.setStyleSheet(combo_box_style())

    def eventFilter(self, obj, event):  # noqa: N802
        if obj is self and event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self.count() > 0:
                self.setCurrentIndex(0)
                return True
        return super().eventFilter(obj, event)


class CommaIntEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(r"[0-9,]*"), self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setFixedHeight(30)
        self.setStyleSheet(input_line_edit_style())
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
    pass


class MaterialItemDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.vendor = QLineEdit(self)
        self.item = QLineEdit(self)
        self.qty = CommaIntEdit(self)
        self.unit = ClearableComboBox(self)
        self.unit.setFixedHeight(30)
        self.unit.setMinimumWidth(160)
        self.unit.addItem("", "")
        for u in _load_units():
            unit = str(u.get("unit", "")).strip()
            label = str(u.get("label", "")).strip()
            if not unit and not label:
                continue
            display = label if label else unit
            self.unit.addItem(display, unit if unit else display)

        self.unit_price = MoneyEdit(self)
        self.total = MoneyEdit(self)
        self.total.setReadOnly(True)
        self.total.setStyleSheet(read_only_line_edit_style())

        for w in (self.vendor, self.item):
            w.setFixedHeight(30)
            w.setStyleSheet(input_line_edit_style())

        form.addRow("거래처", self.vendor)
        form.addRow("품목", self.item)
        form.addRow("수량", self.qty)
        form.addRow("단위", self.unit)
        form.addRow("단가", self.unit_price)
        form.addRow("총액", self.total)
        root.addLayout(form)

        tip = QLabel("수량·단가를 입력하면 총액이 자동 계산됩니다.", self)
        tip.setStyleSheet(hint_label_style())
        root.addWidget(tip)

        self.btn_cancel = make_dialog_button("취소", self, role="cancel")
        self.btn_ok = make_dialog_button("추가", self, role="confirm")
        root.addLayout(make_dialog_button_row([self.btn_cancel, self.btn_ok]))

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
            self.total.setText(f"{int(q) * int(p):,}")
        except Exception:
            self.total.setText("")

    def _on_ok(self):
        if not (self.vendor.text().strip() or self.item.text().strip()):
            self.vendor.setFocus()
            return
        self.accept()

    def get_item(self) -> dict:
        unit_val = str(self.unit.currentData() or "").strip()
        return {
            "거래처": self.vendor.text().strip(),
            "품목": self.item.text().strip(),
            "수량": self.qty.text().strip(),
            "단위": unit_val,
            "단가": self.unit_price.text().strip(),
            "총액": self.total.text().strip(),
        }
