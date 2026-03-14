from __future__ import annotations

from PySide6.QtCore import Qt, QRegularExpression, QEvent
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget, QHBoxLayout

from services.field_keys import MaterialKeys
from services.formatters import digits_only, format_commas_from_digits
from services.unit_repository import load_units
from ui.theme import THEME, combo_box_style, dialog_layout_margins, hint_label_style, input_line_edit_style, read_only_line_edit_style
from ui.icon_factory import make_partner_link_icon
from ui.messages import Buttons, InfoMessages, Labels, Tooltips, Warnings
from ui.widget_factory import make_dialog_button, make_dialog_button_row, make_inline_icon_button
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_OTHER, set_partner_line_edit, show_partner_picker
from ui.layout_metrics import DialogLayout


class ClearableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(False)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.installEventFilter(self)
        self.setStyleSheet(combo_box_style())

    def eventFilter(self, obj, event):
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
        self.setFixedHeight(DialogLayout.FIELD_HEIGHT)
        self.setStyleSheet(input_line_edit_style())
        self._in_format = False
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        if self._in_format:
            return
        formatted = format_commas_from_digits(text)
        if formatted == text:
            return
        self._in_format = True
        try:
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
        finally:
            self._in_format = False

    def value_digits(self) -> str:
        return digits_only(self.text())


class MoneyEdit(CommaIntEdit):
    pass


class MaterialItemDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(DialogLayout.MIN_WIDTH_NARROW)

        root = QVBoxLayout(self)
        root.setContentsMargins(*dialog_layout_margins())
        root.setSpacing(THEME.block_spacing)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(DialogLayout.FORM_HORIZONTAL_SPACING)
        form.setVerticalSpacing(DialogLayout.FORM_VERTICAL_SPACING)

        self.vendor = QLineEdit(self)
        self.item = QLineEdit(self)
        self.qty = CommaIntEdit(self)
        self.unit = ClearableComboBox(self)
        self.unit.setFixedHeight(DialogLayout.FIELD_HEIGHT)
        self.unit.setMinimumWidth(160)
        self.unit.addItem("", "")
        for unit, label in load_units():
            if unit or label:
                self.unit.addItem(label or unit, unit or label)

        self.unit_price = MoneyEdit(self)
        self.total = MoneyEdit(self)
        self.total.setReadOnly(True)
        self.total.setStyleSheet(read_only_line_edit_style())

        for widget in (self.vendor, self.item):
            widget.setFixedHeight(DialogLayout.FIELD_HEIGHT)
            widget.setStyleSheet(input_line_edit_style())
        self.vendor.textEdited.connect(lambda _text: self.vendor.setProperty("vendor_partner_id", ""))

        self.btn_vendor_partner = make_inline_icon_button(
            parent=self,
            tooltip=Tooltips.PARTNER_MANAGE,
            icon=make_partner_link_icon(DialogLayout.BUTTON_ICON_SIZE),
            size=DialogLayout.FIELD_HEIGHT,
        )
        self.btn_vendor_partner.clicked.connect(self._open_vendor_picker)
        vendor_row = QWidget(self)
        vendor_h = QHBoxLayout(vendor_row)
        vendor_h.setContentsMargins(0, 0, 0, 0)
        vendor_h.setSpacing(DialogLayout.INLINE_ROW_SPACING)
        vendor_h.addWidget(self.vendor, 1)
        vendor_h.addWidget(self.btn_vendor_partner, 0)

        form.addRow(Labels.VENDOR, vendor_row)
        form.addRow(Labels.ITEM, self.item)
        form.addRow(Labels.QTY, self.qty)
        form.addRow(Labels.UNIT, self.unit)
        form.addRow(Labels.UNIT_PRICE, self.unit_price)
        form.addRow(Labels.TOTAL, self.total)
        root.addLayout(form)

        tip = QLabel(InfoMessages.MATERIAL_TOTAL_AUTO, self)
        tip.setStyleSheet(hint_label_style())
        root.addWidget(tip)

        self.btn_cancel = make_dialog_button(Buttons.CANCEL, self, role="cancel")
        self.btn_ok = make_dialog_button(Buttons.ADD, self, role="confirm")
        root.addLayout(make_dialog_button_row([self.btn_cancel, self.btn_ok]))
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._on_ok)
        self.qty.textChanged.connect(self._recalc_total)
        self.unit_price.textChanged.connect(self._recalc_total)


    def _open_vendor_picker(self):
        show_partner_picker(
            self.btn_vendor_partner,
            partner_type=PARTNER_PICKER_TYPE_OTHER,
            on_selected=lambda partner: set_partner_line_edit(self.vendor, partner, id_property='vendor_partner_id'),
        )

    def _recalc_total(self):
        qty = self.qty.value_digits()
        price = self.unit_price.value_digits()
        if not qty or not price:
            self.total.setText("")
            return
        try:
            self.total.setText(f"{int(qty) * int(price):,}")
        except (TypeError, ValueError):
            self.total.setText("")

    def _on_ok(self):
        if not (self.vendor.text().strip() or self.item.text().strip()):
            self.vendor.setFocus()
            return
        self.accept()

    def get_item(self) -> dict:
        unit_val = str(self.unit.currentData() or "").strip()
        return {
            MaterialKeys.VENDOR: self.vendor.text().strip(),
            MaterialKeys.VENDOR_ID: str(self.vendor.property("vendor_partner_id") or "").strip(),
            MaterialKeys.ITEM: self.item.text().strip(),
            MaterialKeys.QTY: self.qty.text().strip(),
            MaterialKeys.UNIT: unit_val,
            MaterialKeys.UNIT_PRICE: self.unit_price.text().strip(),
            MaterialKeys.TOTAL: self.total.text().strip(),
        }
