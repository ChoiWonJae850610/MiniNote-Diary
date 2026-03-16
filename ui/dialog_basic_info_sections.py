from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QWidget

from ui.dialog_form_fields import configure_text_field
from ui.dialog_value_widgets import MoneyLineEdit, build_partner_picker_row
from ui.layout_metrics import DialogLayout
from ui.messages import Labels, Tooltips
from ui.theme import THEME, field_label_style


def build_basic_text_fields(dialog, initial: dict):
    style_no = configure_text_field(QLineEdit(dialog))
    factory = configure_text_field(QLineEdit(dialog))
    for widget in (style_no, factory):
        widget.setFixedHeight(THEME.dialog_field_height)
    style_no.setText(initial.get('style_no', ''))
    factory.setText(initial.get('factory', ''))
    factory.setProperty('factory_partner_id', initial.get('factory_partner_id', ''))
    factory.textEdited.connect(lambda _text: factory.setProperty('factory_partner_id', ''))
    return style_no, factory


def build_factory_picker_row(dialog, factory, on_click):
    return build_partner_picker_row(
        dialog,
        factory,
        tooltip=Tooltips.PARTNER_MANAGE,
        icon_size=DialogLayout.BUTTON_ICON_SIZE,
        button_size=THEME.dialog_field_height,
        on_click=on_click,
        stretch=False,
    )


def build_price_row(dialog, initial: dict):
    price_row = QWidget(dialog)
    grid = QGridLayout(price_row)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(DialogLayout.PRICE_GRID_SPACING)

    cost = MoneyLineEdit(dialog)
    labor = MoneyLineEdit(dialog)
    loss = MoneyLineEdit(dialog)
    sale_price = MoneyLineEdit(dialog)
    cost.setText(initial.get('cost_display', ''))
    labor.setText(initial.get('labor_display', ''))
    loss.setText(initial.get('loss_display', ''))
    sale_price.setText(initial.get('sale_price_display', ''))
    cost.setReadOnly(True)
    cost.setFocusPolicy(Qt.NoFocus)

    for edit in (cost, labor, loss, sale_price):
        edit.setMinimumWidth(DialogLayout.PRICE_FIELD_MIN_WIDTH)
        edit.setMaximumWidth(DialogLayout.PRICE_FIELD_MAX_WIDTH)

    pairs = [(Labels.COST, cost), (Labels.LABOR, labor), (Labels.LOSS, loss), (Labels.SALE_PRICE, sale_price)]
    col = 0
    for label_text, edit in pairs:
        label = QLabel(label_text, dialog)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setStyleSheet(field_label_style())
        grid.addWidget(label, 0, col)
        grid.addWidget(edit, 0, col + 1)
        col += 2
    return price_row, (cost, labor, loss, sale_price)
