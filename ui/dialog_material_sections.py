from __future__ import annotations

from PySide6.QtWidgets import QLineEdit

from services.unit.repository import load_units
from ui.dialog_form_fields import configure_text_field
from ui.dialog_value_widgets import ClearableComboBox, MoneyLineEdit, build_partner_picker_row
from ui.layout_metrics import DialogLayout
from ui.messages import Tooltips
from ui.theme import read_only_line_edit_style


def build_material_fields(dialog):
    vendor = configure_text_field(QLineEdit(dialog))
    item = configure_text_field(QLineEdit(dialog))
    qty = MoneyLineEdit(dialog, fixed_height=DialogLayout.FIELD_HEIGHT)
    unit = ClearableComboBox(dialog)
    unit.setFixedHeight(DialogLayout.FIELD_HEIGHT)
    unit.setMinimumWidth(DialogLayout.UNIT_COMBO_MIN_WIDTH)
    unit.addItem('', '')
    for value, label in load_units():
        if value or label:
            unit.addItem(label or value, value or label)
    unit_price = MoneyLineEdit(dialog, fixed_height=DialogLayout.FIELD_HEIGHT)
    total = MoneyLineEdit(dialog, fixed_height=DialogLayout.FIELD_HEIGHT)
    total.setReadOnly(True)
    total.setStyleSheet(read_only_line_edit_style())
    for widget in (vendor, item):
        widget.setFixedHeight(DialogLayout.FIELD_HEIGHT)
    vendor.textEdited.connect(lambda _text: vendor.setProperty('vendor_partner_id', ''))
    return vendor, item, qty, unit, unit_price, total


def build_vendor_picker_row(dialog, vendor, on_click):
    return build_partner_picker_row(
        dialog,
        vendor,
        tooltip=Tooltips.PARTNER_MANAGE,
        icon_size=DialogLayout.BUTTON_ICON_SIZE,
        button_size=DialogLayout.FIELD_HEIGHT,
        on_click=on_click,
        stretch=False,
    )
