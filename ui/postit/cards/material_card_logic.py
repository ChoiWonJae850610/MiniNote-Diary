from __future__ import annotations

from typing import Dict

from services.common.field_keys import MaterialKeys
from services.common.formatters import digits_only, format_commas_from_digits
from services.unit.repository import unit_label_for_value


def sync_unit_menu_checks(card) -> None:
    current = (card._unit_value or "").strip()
    card._act_clear_unit.setChecked(not bool(current))
    for unit, action in card._unit_actions.items():
        action.setChecked(bool(current) and unit == current)


def set_unit(card, unit: str, label: str) -> None:
    card._unit_value = unit or ""
    card._unit_label = label or ""
    card._apply_unit_button_text()
    card._commit(MaterialKeys.UNIT, card._unit_value)


def update_material_card_data(card, data: Dict[str, str]) -> None:
    card._syncing_data = True
    try:
        card.data = dict(data or {})
        card._unit_value = (card.data.get(MaterialKeys.UNIT) or "").strip()
        card._unit_label = unit_label_for_value(card._unit_value, card._units)
        widgets = (card.vendor, card.item, card.qty, card.price, card.total)
        blocked = [(widget, widget.blockSignals(True)) for widget in widgets]
        try:
            card.vendor.set_text_silent(card.data.get(MaterialKeys.VENDOR, ""))
            card.data[MaterialKeys.VENDOR_ID] = card.data.get(MaterialKeys.VENDOR_ID, "")
            card.item.set_text_silent(card.data.get(MaterialKeys.ITEM, ""))
            card.qty.set_text_silent(digits_only(card.data.get(MaterialKeys.QTY, "")))
            card.price.setText(card.data.get(MaterialKeys.UNIT_PRICE, ""))
            card.total.setText(card.data.get(MaterialKeys.TOTAL, ""))
            card._apply_unit_button_text()
        finally:
            for widget, old in blocked:
                widget.blockSignals(old)
        recalc_material_total(card, commit=False)
    finally:
        card._syncing_data = False


def commit_material_value(card, key: str, value: str) -> None:
    value = (value or "").strip()
    card.data[key] = value
    if card._syncing_data:
        return
    payload = {key: value}
    if key == MaterialKeys.VENDOR:
        payload[MaterialKeys.VENDOR_ID] = str(card.data.get(MaterialKeys.VENDOR_ID, "") or "")
    card.data_changed.emit(card.index, payload)


def on_qty_committed(card, value: str) -> None:
    commit_material_value(card, MaterialKeys.QTY, value)
    recalc_material_total(card)


def on_price_changed(card) -> None:
    commit_material_value(card, MaterialKeys.UNIT_PRICE, card.price.text())
    recalc_material_total(card)


def recalc_material_total(card, *, commit: bool = True) -> None:
    if card._block_total:
        return
    qty_digits = digits_only(card.qty.text())
    price_digits = digits_only(card.price.text())
    if not qty_digits or not price_digits:
        card._block_total = True
        try:
            card.total.setText("")
        finally:
            card._block_total = False
        if commit:
            commit_material_value(card, MaterialKeys.TOTAL, "")
        return
    try:
        total = int(qty_digits) * int(price_digits)
    except (TypeError, ValueError):
        total = 0
    card._block_total = True
    try:
        card.total.setText(format_commas_from_digits(str(total)))
    finally:
        card._block_total = False
    if commit:
        commit_material_value(card, MaterialKeys.TOTAL, card.total.text())
