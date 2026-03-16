from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog

from ui.dialog_basic_info_sections import build_basic_text_fields, build_factory_picker_row, build_price_row
from ui.dialog_form_templates import add_action_row, add_form_to_root, setup_form_dialog
from ui.dialog_value_widgets import build_calendar_row, show_calendar_popup
from ui.layout_metrics import DialogLayout
from ui.messages import Buttons, DialogTitles, Labels
from ui.partners.ui_utils import PARTNER_PICKER_TYPE_FACTORY, set_partner_line_edit, show_partner_picker


class BasicInfoDialog(QDialog):
    def __init__(self, initial: Dict[str, str] | None = None, parent=None):
        super().__init__(parent)
        initial = initial or {}
        root, form = setup_form_dialog(self, title=DialogTitles.BASIC_INFO_INPUT, min_width=DialogLayout.MIN_WIDTH_STANDARD)

        initial_date = QDate.fromString(initial.get('date', ''), 'yyyy-MM-dd')
        self._date_value = initial_date if initial_date.isValid() else QDate.currentDate()
        self.date_text, self.btn_calendar, date_row = build_calendar_row(self, self._date_value, self._open_calendar)
        self.style_no, self.factory = build_basic_text_fields(self, initial)
        self.btn_factory_partner, factory_row = build_factory_picker_row(self, self.factory, self._open_factory_picker)
        price_row, fields = build_price_row(self, initial)
        self.cost, self.labor, self.loss, self.sale_price = fields

        form.addRow(Labels.DATE, date_row)
        form.addRow(Labels.STYLE_NO, self.style_no)
        form.addRow(Labels.FACTORY, factory_row)
        form.addRow('', price_row)
        add_form_to_root(root, form)
        btn_cancel, btn_ok = add_action_row(self, root, confirm_text=Buttons.OK, cancel_text=Buttons.CANCEL)
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)

    def _open_calendar(self):
        if getattr(self, '_calendar_popup', None) is not None:
            self._calendar_popup.close()
            self._calendar_popup = None

        def _apply(date: QDate):
            if date and date.isValid():
                self._date_value = date
                self.date_text.setText(self._date_value.toString('yyyy-MM-dd'))

        self._calendar_popup = show_calendar_popup(self, self.date_text, self._date_value, _apply)

    def _open_factory_picker(self):
        show_partner_picker(
            self.btn_factory_partner,
            partner_type=PARTNER_PICKER_TYPE_FACTORY,
            on_selected=lambda partner: set_partner_line_edit(self.factory, partner, id_property='factory_partner_id'),
        )

    def get_data(self) -> Dict[str, str]:
        return {
            'date': self._date_value.toString('yyyy-MM-dd'),
            'style_no': self.style_no.text().strip(),
            'factory': self.factory.text().strip(),
            'factory_partner_id': str(self.factory.property('factory_partner_id') or '').strip(),
            'cost_display': self.cost.text(),
            'labor_display': self.labor.text(),
            'loss_display': self.loss.text(),
            'sale_price_display': self.sale_price.text(),
            'cost': self.cost.value_digits(),
            'labor': self.labor.value_digits(),
            'loss': self.loss.value_digits(),
            'sale_price': self.sale_price.value_digits(),
        }
