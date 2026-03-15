from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QLabel

from services.partner_repository import PartnerRecord
from services.search_utils import matches_keyword
from ui.partner_dialog_common import PartnerListItem, detail_value_fallback


def filter_partners(partners: Iterable[PartnerRecord], text: str) -> list[PartnerRecord]:
    return [
        row
        for row in partners
        if matches_keyword(text, row.name, row.owner, row.phone, row.address, ' '.join(row.types or []))
    ]


def populate_partner_list(list_widget: QListWidget, partners: list[PartnerRecord], type_order: list[str]) -> None:
    list_widget.clear()
    for partner in partners:
        item = QListWidgetItem(list_widget)
        item.setData(Qt.UserRole, partner.id)
        widget = PartnerListItem(partner, type_order, list_widget)
        item.setSizeHint(widget.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, widget)


def find_partner_by_id(partners: Iterable[PartnerRecord], partner_id: str) -> PartnerRecord | None:
    for row in partners:
        if row.id == partner_id:
            return row
    return None


def show_partner_detail(dialog, partner: PartnerRecord) -> None:
    fallback = detail_value_fallback()
    dialog.detail_name.setText(partner.name or fallback)
    dialog.detail_owner.setText(partner.owner or fallback)
    dialog.detail_phone.setText(partner.phone or fallback)
    dialog.detail_address.setText(partner.address or fallback)
    dialog.detail_memo.setText(partner.memo or fallback)
    dialog.type_indicator_grid.set_types(dialog._type_order, partner.types or [])


def clear_partner_detail(dialog) -> None:
    dialog._current_partner_id = ""
    fallback = detail_value_fallback()
    for label in [dialog.detail_name, dialog.detail_owner, dialog.detail_phone, dialog.detail_address, dialog.detail_memo]:
        label.setText(fallback)
    dialog.type_indicator_grid.set_types(dialog._type_order, [])


def select_partner_in_list(list_widget: QListWidget, partner_id: str) -> None:
    for row in range(list_widget.count()):
        item = list_widget.item(row)
        if item and item.data(Qt.UserRole) == partner_id:
            list_widget.setCurrentRow(row)
            return
