from __future__ import annotations

import os
from collections.abc import Callable

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QLineEdit, QMenu, QWidget

from services.partner_repository import PartnerRepository, PartnerRecord
from services.partner_utils import PARTNER_TYPE_FACTORY, PARTNER_TYPE_FABRIC, PARTNER_TYPE_OTHER, PARTNER_TYPE_TRIM
from ui.messages import InfoMessages
from ui.partner_dialog import PartnerDialog
from ui.theme import menu_style

PARTNER_PICKER_TYPE_FACTORY = PARTNER_TYPE_FACTORY
PARTNER_PICKER_TYPE_FABRIC = PARTNER_TYPE_FABRIC
PARTNER_PICKER_TYPE_OTHER = PARTNER_TYPE_OTHER


def project_root_from_widget(widget: QWidget | None) -> str:
    current = widget
    while current is not None:
        path = getattr(current, 'project_root', None)
        if isinstance(path, str) and path:
            return path
        current = current.parentWidget()
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))



def open_partner_management(widget: QWidget | None) -> int:
    dialog = PartnerDialog(project_root=project_root_from_widget(widget), parent=widget)
    return dialog.exec()



def _repository_for(widget: QWidget | None) -> PartnerRepository:
    return PartnerRepository(project_root_from_widget(widget))



def _partners_for_type(widget: QWidget | None, partner_type: str) -> list[PartnerRecord]:
    repository = _repository_for(widget)
    if partner_type == PARTNER_TYPE_OTHER:
        excluded = {PARTNER_TYPE_FACTORY, PARTNER_TYPE_FABRIC, PARTNER_TYPE_TRIM}
        return [
            row
            for row in repository.load_partners()
            if not any(partner_type_name in excluded for partner_type_name in (row.types or []))
        ]
    return repository.load_partners_by_type(partner_type)



def set_partner_line_edit(line_edit: QLineEdit, partner: PartnerRecord, *, id_property: str = 'partner_id') -> None:
    line_edit.setText(partner.name)
    line_edit.setProperty(id_property, partner.id)



def show_partner_picker(anchor: QWidget, *, partner_type: str, on_selected: Callable[[PartnerRecord], None]) -> bool:
    partners = _partners_for_type(anchor, partner_type)
    menu = QMenu(anchor)
    menu.setStyleSheet(menu_style())
    if not partners:
        empty = menu.addAction(InfoMessages.PARTNER_EMPTY_LIST)
        empty.setEnabled(False)
    else:
        for partner in partners:
            action = menu.addAction(partner.name)
            action.setData(partner.id)
    chosen = menu.exec(anchor.mapToGlobal(QPoint(0, anchor.height() + 2)))
    if chosen is None or not chosen.isEnabled():
        return False
    chosen_id = str(chosen.data() or '')
    if not chosen_id:
        return False
    partner = next((row for row in partners if row.id == chosen_id), None)
    if partner is None:
        return False
    on_selected(partner)
    return True
