from __future__ import annotations

from PySide6.QtWidgets import QLineEdit, QSizePolicy

from services.unit.repository import load_units
from ui.dialogs.forms.fields import configure_text_field
from ui.dialogs.forms.value_widgets import ClearableComboBox, MoneyLineEdit, build_partner_picker_row
from ui.layout_metrics import DialogLayout
from ui.messages import Tooltips
from ui.theme import read_only_line_edit_style


def build_material_fields(dialog):
    vendor = configure_text_field(QLineEdit(dialog))
    item = configure_text_field(QLineEdit(dialog))
    qty = MoneyLineEdit(dialog, fixed_height=DialogLayout.FIELD_HEIGHT)
    unit = ClearableComboBox(dialog)
    unit.setMinimumHeight(DialogLayout.FIELD_HEIGHT)
    unit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
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
        widget.setMinimumHeight(DialogLayout.FIELD_HEIGHT)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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
