from __future__ import annotations

from ui.partners.browser.helpers import (
    clear_partner_detail,
    filter_partners,
    find_partner_by_id,
    populate_partner_list,
    select_partner_in_list,
    show_partner_detail,
)


def reload_all(dialog) -> None:
    dialog._type_order = dialog.partner_service.list_types()
    dialog._partners = dialog.partner_service.list_partners()
    apply_filter(dialog, dialog.search_edit.text())


def apply_filter(dialog, text: str) -> None:
    dialog._filtered = filter_partners(dialog._partners, text)
    populate_list(dialog)


def populate_list(dialog) -> None:
    populate_partner_list(dialog.list_widget, dialog._filtered, dialog._type_order)
    if dialog._filtered:
        dialog.list_widget.setCurrentRow(0)
    else:
        clear_detail(dialog)


def find_by_id(dialog, partner_id: str):
    return find_partner_by_id(dialog._partners, partner_id)


def show_partner(dialog, partner) -> None:
    show_partner_detail(dialog, partner)


def clear_detail(dialog) -> None:
    clear_partner_detail(dialog)


def select_partner(dialog, partner_id: str) -> None:
    select_partner_in_list(dialog.list_widget, partner_id)
