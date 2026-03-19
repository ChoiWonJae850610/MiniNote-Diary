from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolButton, QSizePolicy

from services.common.field_keys import MaterialKeys
from services.unit.repository import load_units, unit_label_for_value
from ui.icon_factory import make_partner_link_icon
from ui.messages import Labels, PostItTexts, Tooltips
from ui.partners.ui_utils import (
    PARTNER_PICKER_TYPE_DYEING,
    PARTNER_PICKER_TYPE_FABRIC,
    PARTNER_PICKER_TYPE_FINISH,
    PARTNER_PICKER_TYPE_OTHER,
    PARTNER_PICKER_TYPE_TRIM,
    show_partner_picker,
)
from ui.postit.common import CheckedPopupSelector, FIELD_H
from ui.postit.editor_fields import _ClickToEditLineEdit, _MoneyLineEdit, _QtyClickToEditLineEdit
from ui.postit.forms import make_field_label, make_form_row
from ui.postit.layout import POSTIT_ROW_ACTION_GAP, PostItLayout
from ui.theme import delete_button_style, tool_button_style, THEME, input_line_edit_style
from ui.widget_factory import set_widget_tooltip
from ui.work_order_validation_ui import set_invalid


def configure_delete_button(card) -> None:
    card.btn_delete = QToolButton(card)
    card.btn_delete.setText("×")
    card.btn_delete.setCursor(Qt.PointingHandCursor)
    card.btn_delete.setFixedSize(THEME.delete_button_size, THEME.delete_button_size)
    card.btn_delete.setStyleSheet(delete_button_style())
    card.btn_delete.clicked.connect(lambda: card.delete_clicked.emit(card.index))


def build_vendor_rows(card, root) -> None:
    card.vendor = _ClickToEditLineEdit(card)
    card.item = _ClickToEditLineEdit(card)
    card.btn_vendor_partner = QToolButton(card)
    card.btn_vendor_partner.setIcon(make_partner_link_icon(PostItLayout.PARTNER_LINK_ICON_SIZE))
    card.btn_vendor_partner.setIconSize(QSize(PostItLayout.PARTNER_LINK_ICON_SIZE, PostItLayout.PARTNER_LINK_ICON_SIZE))
    card.btn_vendor_partner.setFixedSize(FIELD_H, FIELD_H)
    card.btn_vendor_partner.setCursor(Qt.PointingHandCursor)
    set_widget_tooltip(card.btn_vendor_partner, Tooltips.PARTNER_MANAGE)
    card.btn_vendor_partner.setStyleSheet(tool_button_style())
    card.btn_vendor_partner.clicked.connect(card._open_vendor_picker)
    card.vendor.set_edit_enabled(False)
    card.vendor.setFocusPolicy(Qt.NoFocus)
    card.vendor.set_text_silent(card.data.get(MaterialKeys.VENDOR, ""))
    card.data[MaterialKeys.VENDOR_ID] = card.data.get(MaterialKeys.VENDOR_ID, "")
    card.item.set_text_silent(card.data.get(MaterialKeys.ITEM, ""))
    vendor_label = Labels.VENDOR
    vendor_row = make_form_row(make_field_label(vendor_label, card), (card.vendor, 1), card.btn_vendor_partner)
    vendor_row.setSpacing(POSTIT_ROW_ACTION_GAP)
    root.addLayout(vendor_row)
    root.addLayout(make_form_row(make_field_label(Labels.ITEM, card), (card.item, 1)))


def _apply_unit_button_text(card) -> None:
    idx = card.unit_btn.findData(card._unit_value)
    card.unit_btn.setCurrentIndex(idx if idx >= 0 else 0)


def configure_unit_controls(card) -> None:
    card._units = load_units()
    card._unit_value = (card.data.get(MaterialKeys.UNIT) or "").strip()
    card._unit_label = unit_label_for_value(card._unit_value, card._units)
    card.unit_btn = CheckedPopupSelector(card, clear_text=PostItTexts.CLEAR_UNIT)
    card.unit_btn.setMinimumWidth(max(32, THEME.postit_unit_button_width))
    card.unit_btn.setMaximumWidth(max(32, THEME.postit_unit_button_width))
    card.unit_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    card.unit_btn.addItem(PostItTexts.CLEAR_UNIT, "")
    for unit, label in card._units:
        card.unit_btn.addItem(label, unit)
    card.unit_btn.currentIndexChanged.connect(lambda _i: card._set_unit(str(card.unit_btn.currentData() or ""), unit_label_for_value(str(card.unit_btn.currentData() or ""), card._units)))
    card.unit_btn.installEventFilter(card)
    card._apply_unit_button_text = lambda: _apply_unit_button_text(card)
    _apply_unit_button_text(card)


def build_amount_rows(card, root) -> None:
    card.qty = _QtyClickToEditLineEdit(card)
    card.qty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    card.qty.set_text_silent(card.data.get(MaterialKeys.QTY, ""))
    configure_unit_controls(card)
    card.price = _MoneyLineEdit(card)
    card.total = _MoneyLineEdit(card)
    for widget in (card.price, card.total):
        widget.setStyleSheet(input_line_edit_style())
    card.price.setText(card.data.get(MaterialKeys.UNIT_PRICE, ""))
    card.total.set_edit_enabled(False)
    card.total.setFocusPolicy(Qt.NoFocus)
    card.total.setText(card.data.get(MaterialKeys.TOTAL, ""))
    card.qty.setMinimumWidth(0)
    card.qty.setMaximumWidth(16777215)
    card.qty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    card.unit_btn.setMinimumWidth(0)
    card.unit_btn.setMaximumWidth(16777215)
    card.unit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    qty_label = make_field_label(Labels.QTY, card)
    qty_label.setMinimumWidth(0)
    qty_label.setMaximumWidth(16777215)
    qty_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    unit_label = make_field_label(Labels.UNIT, card)
    unit_label.setMinimumWidth(0)
    unit_label.setMaximumWidth(16777215)
    unit_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    root.addLayout(
        make_form_row(
            (qty_label, 1),
            (card.qty, 1),
            (unit_label, 1),
            (card.unit_btn, 1),
        )
    )
    root.addLayout(make_form_row(make_field_label(Labels.UNIT_PRICE, card), (card.price, 1)))
    root.addLayout(make_form_row(make_field_label(Labels.TOTAL, card), (card.total, 1)))


def connect_material_signals(card) -> None:
    card.item.textChanged.connect(lambda text: set_invalid(card.item, not bool((text or "").strip()) and bool(card.item.property("validationError"))))
    card.item.committed.connect(lambda value: card._commit(MaterialKeys.ITEM, value))
    card.qty.textChanged.connect(lambda text: set_invalid(card.qty, (str(text or "").replace(",", "").strip() == "") and bool(card.qty.property("validationError"))))
    card.qty.committed.connect(card._on_qty_committed)
    card.qty.textChanged.connect(lambda _t: card._recalc_total())
    card.price.textChanged.connect(lambda text: set_invalid(card.price, (str(text or "").replace(",", "").strip() == "") and bool(card.price.property("validationError"))))
    card.price.textChanged.connect(lambda _t: card._on_price_changed())
    card.total.textChanged.connect(lambda _t: None if card._block_total else card._commit(MaterialKeys.TOTAL, card.total.text()))


def configure_material_tab_order(card) -> None:
    card.setTabOrder(card.btn_vendor_partner, card.item)
    card.setTabOrder(card.item, card.qty)
    card.setTabOrder(card.qty, card.unit_btn)
    card.setTabOrder(card.unit_btn, card.price)
    card.price._pending_prev_widget = card.unit_btn


def picker_partner_type(kind: str) -> str:
    if kind == "fabric":
        return PARTNER_PICKER_TYPE_FABRIC
    if kind == "trim":
        return PARTNER_PICKER_TYPE_TRIM
    if kind == "dyeing":
        return PARTNER_PICKER_TYPE_DYEING
    if kind == "finishing":
        return PARTNER_PICKER_TYPE_FINISH
    return PARTNER_PICKER_TYPE_OTHER


def open_vendor_picker(card) -> None:
    def _apply(partner):
        card.vendor.set_text_silent(partner.name)
        card.data[MaterialKeys.VENDOR_ID] = partner.id
        card._commit(MaterialKeys.VENDOR, partner.name)

    def _clear():
        card.vendor.set_text_silent("")
        card.data[MaterialKeys.VENDOR_ID] = ""
        card._commit(MaterialKeys.VENDOR, "")

    show_partner_picker(card.btn_vendor_partner, partner_type=picker_partner_type(card.kind), on_selected=_apply, on_cleared=_clear)
