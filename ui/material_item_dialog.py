from __future__ import annotations

from PySide6.QtCore import Qt, QRegularExpression, QEvent
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QComboBox, QDialog, QLineEdit

from services.field_keys import MaterialKeys
from services.formatters import digits_only, format_commas_from_digits
from services.unit_repository import load_units
from ui.dialog_form_fields import build_hint_label, configure_text_field
from ui.theme import combo_box_style, input_line_edit_style, read_only_line_edit_style
from ui.icon_factory import make_partner_link_icon
from ui.messages import Buttons, InfoMessages, Labels, Tooltips
from ui.widget_factory import make_inline_icon_button
from ui.dialog_form_templates import add_dialog_action_row, setup_form_dialog, wire_dialog_reject
from ui.dialog_layout_utils import make_dialog_inline_row
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
        root, form = setup_form_dialog(
            self,
            title=title,
            min_width=DialogLayout.MIN_WIDTH_NARROW,
        )

        self.vendor = configure_text_field(QLineEdit(self))
        self.item = configure_text_field(QLineEdit(self))
        self.qty = CommaIntEdit(self)
        self.unit = ClearableComboBox(self)
        self.unit.setFixedHeight(DialogLayout.FIELD_HEIGHT)
        self.unit.setMinimumWidth(DialogLayout.UNIT_COMBO_MIN_WIDTH)
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
        self.vendor.textEdited.connect(lambda _text: self.vendor.setProperty("vendor_partner_id", ""))

        self.btn_vendor_partner = make_inline_icon_button(
            parent=self,
            tooltip=Tooltips.PARTNER_MANAGE,
            icon=make_partner_link_icon(DialogLayout.BUTTON_ICON_SIZE),
            size=DialogLayout.FIELD_HEIGHT,
        )
        self.btn_vendor_partner.clicked.connect(self._open_vendor_picker)
        vendor_row = make_dialog_inline_row(self, self.vendor, self.btn_vendor_partner, stretch=False)

        form.addRow(Labels.VENDOR, vendor_row)
        form.addRow(Labels.ITEM, self.item)
        form.addRow(Labels.QTY, self.qty)
        form.addRow(Labels.UNIT, self.unit)
        form.addRow(Labels.UNIT_PRICE, self.unit_price)
        form.addRow(Labels.TOTAL, self.total)
        root.addLayout(form)
        root.addWidget(build_hint_label(InfoMessages.MATERIAL_TOTAL_AUTO, self))

        self.btn_cancel, self.btn_ok = add_dialog_action_row(
            self,
            root,
            confirm_text=Buttons.ADD,
            cancel_text=Buttons.CANCEL,
        )
        wire_dialog_reject([self.btn_cancel], self.reject)
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
