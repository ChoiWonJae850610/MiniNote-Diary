from __future__ import annotations

from services.common.field_keys import MaterialKeys
from services.work_order.validation import row_has_any_meaningful_value, row_is_save_complete


def _repolish(widget):
    if widget is None:
        return
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def set_invalid(widget, invalid: bool):
    if widget is None:
        return
    widget.setProperty("validationError", bool(invalid))
    _repolish(widget)


def clear_all(window):
    basic = getattr(window.postit_bar, "basic", None)
    if basic is not None:
        for widget in (getattr(basic, "style_no", None), getattr(basic, "factory", None)):
            set_invalid(widget, False)
    partner = getattr(window.postit_bar, "partner", None)
    if partner is not None and hasattr(partner, "tab_header"):
        partner.tab_header.clear_invalid_tabs()
        for stack in partner._tab_stacks.values():
            for card in getattr(stack, "cards", []):
                _clear_card(card)


def _clear_card(card):
    for widget_name in ("vendor", "item", "qty", "unit_btn", "price", "total"):
        set_invalid(getattr(card, widget_name, None), False)


def _apply_basic(window):
    header = window.state.header_data
    basic = window.postit_bar.basic
    set_invalid(basic.style_no, not bool(str(header.get("style_no", "") or "").strip()))
    set_invalid(basic.factory, not bool(str(header.get("factory", "") or "").strip()))


def _apply_card(card, row):
    row = row or {}
    any_value = row_has_any_meaningful_value(row)
    complete = row_is_save_complete(row)
    if not any_value or complete:
        _clear_card(card)
        return False
    set_invalid(card.vendor, not bool(str(row.get(MaterialKeys.VENDOR, "") or "").strip()))
    set_invalid(card.item, not bool(str(row.get(MaterialKeys.ITEM, "") or "").strip()))
    set_invalid(card.unit_btn, not bool(str(row.get(MaterialKeys.UNIT, "") or "").strip()))
    set_invalid(card.qty, str(row.get(MaterialKeys.QTY, "") or "").replace(",", "").strip() == "")
    set_invalid(card.price, str(row.get(MaterialKeys.UNIT_PRICE, "") or "").replace(",", "").strip() == "")
    set_invalid(card.total, str(row.get(MaterialKeys.TOTAL, "") or "").replace(",", "").strip() == "")
    return True


def _apply_material_tabs(window):
    partner = window.postit_bar.partner
    state_map = {
        partner.TAB_FABRIC: window.state.fabric_items,
        partner.TAB_TRIM: window.state.trim_items,
        partner.TAB_DYEING: window.state.dyeing_items,
        partner.TAB_OTHER: window.state.other_items,
    }
    for tab_key, rows in state_map.items():
        stack = partner._tab_stacks.get(tab_key)
        if stack is None:
            continue
        invalid_tab = False
        cards = list(getattr(stack, "cards", []))
        for idx, card in enumerate(cards):
            row = rows[idx] if idx < len(rows) else getattr(card, "data", {})
            invalid_tab = _apply_card(card, row) or invalid_tab
        partner.tab_header.set_invalid_tab(tab_key, invalid_tab)


def apply(window):
    _apply_basic(window)
    _apply_material_tabs(window)


def activate(window):
    window._validation_marks_active = True
    apply(window)


def refresh_if_active(window):
    if not getattr(window, "_validation_marks_active", False):
        return
    apply(window)


def deactivate(window):
    window._validation_marks_active = False
    clear_all(window)
