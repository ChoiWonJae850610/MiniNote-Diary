from __future__ import annotations

from PySide6.QtWidgets import QDialog

from services.field_keys import MaterialKeys
from ui.dialog_form_fields import build_hint_label
from ui.dialog_form_templates import add_action_row, add_form_to_root, setup_form_dialog
from ui.dialog_material_sections import build_material_fields, build_vendor_picker_row
from ui.layout_metrics import DialogLayout
from ui.messages import Buttons, InfoMessages, Labels
from ui.partner_ui_utils import PARTNER_PICKER_TYPE_OTHER, set_partner_line_edit, show_partner_picker


class MaterialItemDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        root, form = setup_form_dialog(self, title=title, min_width=DialogLayout.MIN_WIDTH_NARROW)

        self.vendor, self.item, self.qty, self.unit, self.unit_price, self.total = build_material_fields(self)
        self.btn_vendor_partner, vendor_row = build_vendor_picker_row(self, self.vendor, self._open_vendor_picker)

        form.addRow(Labels.VENDOR, vendor_row)
        form.addRow(Labels.ITEM, self.item)
        form.addRow(Labels.QTY, self.qty)
        form.addRow(Labels.UNIT, self.unit)
        form.addRow(Labels.UNIT_PRICE, self.unit_price)
        form.addRow(Labels.TOTAL, self.total)
        add_form_to_root(root, form)
        root.addWidget(build_hint_label(InfoMessages.MATERIAL_TOTAL_AUTO, self))
        self.btn_cancel, self.btn_ok = add_action_row(self, root, confirm_text=Buttons.ADD, cancel_text=Buttons.CANCEL)
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
            self.total.setText('')
            return
        try:
            self.total.setText(f"{int(qty) * int(price):,}")
        except (TypeError, ValueError):
            self.total.setText('')

    def _on_ok(self):
        if not (self.vendor.text().strip() or self.item.text().strip()):
            self.vendor.setFocus()
            return
        self.accept()

    def get_item(self) -> dict:
        unit_val = str(self.unit.currentData() or '').strip()
        return {
            MaterialKeys.VENDOR: self.vendor.text().strip(),
            MaterialKeys.VENDOR_ID: str(self.vendor.property('vendor_partner_id') or '').strip(),
            MaterialKeys.ITEM: self.item.text().strip(),
            MaterialKeys.QTY: self.qty.text().strip(),
            MaterialKeys.UNIT: unit_val,
            MaterialKeys.UNIT_PRICE: self.unit_price.text().strip(),
            MaterialKeys.TOTAL: self.total.text().strip(),
        }
