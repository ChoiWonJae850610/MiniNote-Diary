
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QComboBox, QToolButton, QSizePolicy

from ui.icon_factory import make_calendar_icon, make_partner_link_icon
from services.product_type.service import ProductTypeService
from ui.messages import Labels, Tooltips
from ui.partners.ui_utils import PARTNER_PICKER_TYPE_FACTORY, project_root_from_widget, show_partner_picker
from ui.postit.common import FIELD_H
from ui.postit.editor_fields import _ClickToEditLineEdit, _MoneyLineEdit
from ui.postit.forms import make_field_label, make_form_row
from ui.postit.layout import PostItLayout
from ui.theme import THEME, combo_box_style, display_field_style, input_line_edit_style, tool_button_style
from ui.widget_factory import set_widget_tooltip
from ui.work_order_validation_ui import set_invalid


def _make_type_combo(card):
    combo = QComboBox(card)
    combo.setFixedHeight(FIELD_H)
    combo.addItem('(비움)', '')
    combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    combo.setStyleSheet(combo_box_style())
    return combo


def build_date_row(card, root) -> None:
    card.date_text.setFixedHeight(FIELD_H)
    card.date_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    card.date_text.setStyleSheet(display_field_style())
    card.date_text.setMinimumWidth(THEME.calendar_display_width + PostItLayout.DATE_MIN_WIDTH_EXTRA)
    card.btn_calendar = QToolButton(card)
    card.btn_calendar.setIcon(make_calendar_icon(PostItLayout.CALENDAR_ICON_SIZE))
    card.btn_calendar.setIconSize(QSize(PostItLayout.CALENDAR_ICON_SIZE, PostItLayout.CALENDAR_ICON_SIZE))
    card.btn_calendar.setFixedSize(FIELD_H, FIELD_H)
    card.btn_calendar.setCursor(Qt.PointingHandCursor)
    set_widget_tooltip(card.btn_calendar, Tooltips.OPEN_CALENDAR)
    card.btn_calendar.setStyleSheet(tool_button_style())
    card.btn_calendar.clicked.connect(card._open_calendar)
    date_row = make_form_row(make_field_label(Labels.DATE, card), card.date_text, card.btn_calendar)
    date_row.addStretch(1)
    root.addLayout(date_row)



def build_partner_rows(card, root) -> None:
    card.style_no = _ClickToEditLineEdit(card)
    card.product_type_1 = _make_type_combo(card)
    card.product_type_2 = _make_type_combo(card)
    card.product_type_3 = _make_type_combo(card)
    card.product_type_1.setMinimumWidth(THEME.basic_type_field_width)
    card.product_type_2.setMinimumWidth(THEME.basic_type_field_width)
    card.product_type_3.setMinimumWidth(THEME.basic_type_field_width)
    card.product_type_1.setMaximumWidth(16777215)
    card.product_type_2.setMaximumWidth(16777215)
    card.product_type_3.setMaximumWidth(16777215)
    card.factory = _ClickToEditLineEdit(card)
    card.btn_factory_partner = QToolButton(card)
    card.btn_factory_partner.setIcon(make_partner_link_icon(PostItLayout.PARTNER_LINK_ICON_SIZE))
    card.btn_factory_partner.setIconSize(QSize(PostItLayout.PARTNER_LINK_ICON_SIZE, PostItLayout.PARTNER_LINK_ICON_SIZE))
    card.btn_factory_partner.setFixedSize(FIELD_H, FIELD_H)
    card.btn_factory_partner.setCursor(Qt.PointingHandCursor)
    set_widget_tooltip(card.btn_factory_partner, Tooltips.PARTNER_MANAGE)
    card.btn_factory_partner.setStyleSheet(tool_button_style())
    card.btn_factory_partner.clicked.connect(card._open_factory_picker)
    card.factory.set_edit_enabled(False)
    card.factory.setFocusPolicy(Qt.NoFocus)
    card.style_no.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    card.style_no.setMinimumWidth(THEME.basic_style_field_extra_width)
    card.style_no.setMaximumWidth(16777215)

    card._refresh_product_type_options()
    style_row = make_form_row(make_field_label(Labels.STYLE_NO, card), (card.style_no, 1))
    type_row = make_form_row(
        make_field_label(Labels.TYPE, card),
        (card.product_type_1, 1),
        (card.product_type_2, 1),
        (card.product_type_3, 1),
    )
    root.addLayout(style_row)
    root.addLayout(type_row)
    root.addLayout(make_form_row(make_field_label(Labels.FACTORY, card), (card.factory, 1), card.btn_factory_partner))


def build_price_rows(card, root) -> None:
    card.cost = _MoneyLineEdit(card)
    card.labor = _MoneyLineEdit(card)
    card.loss = _MoneyLineEdit(card)
    card.sale_price = _MoneyLineEdit(card)
    for widget in (card.cost, card.labor, card.loss, card.sale_price):
        widget.setStyleSheet(input_line_edit_style())
    card.cost.set_edit_enabled(False)
    card.cost.setFocusPolicy(Qt.NoFocus)
    card.sale_price.set_edit_enabled(False)
    card.sale_price.setFocusPolicy(Qt.NoFocus)
    root.addLayout(make_form_row(make_field_label(Labels.LABOR, card), (card.labor, 1), make_field_label(Labels.LOSS, card), (card.loss, 1)))
    root.addLayout(make_form_row(make_field_label(Labels.COST, card), (card.cost, 1), make_field_label(Labels.SALE_PRICE, card), (card.sale_price, 1)))


def connect_basic_info_signals(card) -> None:
    def _clear_type_invalid_if_selected():
        has_type = bool(card._current_product_type_path().strip())
        if has_type:
            for combo in (card.product_type_1, card.product_type_2, card.product_type_3):
                set_invalid(combo, False)

    card.style_no.textChanged.connect(lambda text: set_invalid(card.style_no, not bool((text or '').strip()) and bool(card.style_no.property('validationError'))))
    card.style_no.committed.connect(lambda _v: card._emit_basic_fields())
    card.product_type_1.currentIndexChanged.connect(lambda _i: (card._on_product_type_level_changed(1), _clear_type_invalid_if_selected()))
    card.product_type_2.currentIndexChanged.connect(lambda _i: (card._on_product_type_level_changed(2), _clear_type_invalid_if_selected()))
    card.product_type_3.currentIndexChanged.connect(lambda _i: (card._emit_basic_fields(), _clear_type_invalid_if_selected()))
    card.labor.textChanged.connect(card._on_price_component_changed)
    card.loss.textChanged.connect(card._on_price_component_changed)
    card.sale_price.textChanged.connect(card._on_sale_price_changed)


def configure_basic_info_tab_order(card) -> None:
    card.setTabOrder(card.btn_calendar, card.style_no)
    card.setTabOrder(card.style_no, card.product_type_1)
    card.setTabOrder(card.product_type_1, card.product_type_2)
    card.setTabOrder(card.product_type_2, card.product_type_3)
    card.setTabOrder(card.product_type_3, card.btn_factory_partner)
    card.setTabOrder(card.btn_factory_partner, card.labor)
    card.setTabOrder(card.labor, card.loss)
    card.setTabOrder(card.loss, card.cost)
    card.setTabOrder(card.cost, card.sale_price)
    card.labor._pending_prev_widget = card.btn_factory_partner
    card.labor._pending_next_widget = card.loss
    card.loss._pending_prev_widget = card.labor
    card.loss._pending_next_widget = card.cost
    card.cost._pending_prev_widget = card.loss


def open_factory_picker(card) -> None:
    def _apply(partner):
        card.factory.set_text_silent(partner.name)
        card.factory.setProperty('factory_partner_id', partner.id)
        card._emit_basic_fields()

    def _clear():
        card.factory.set_text_silent('')
        card.factory.setProperty('factory_partner_id', '')
        card._emit_basic_fields()

    show_partner_picker(card.btn_factory_partner, partner_type=PARTNER_PICKER_TYPE_FACTORY, on_selected=_apply, on_cleared=_clear)
