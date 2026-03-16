from __future__ import annotations

from PySide6.QtWidgets import QDialog

from ui.dialogs import ConfirmActionDialog, show_info, show_warning
from ui.messages import Buttons, DialogTitles, InfoMessages, WarningMessages
from ui.partners.dialogs.edit_dialog import PartnerEditDialog
from ui.partners.dialogs.type_dialog import PartnerTypeDialog
from ui.partners.browser.selection import find_by_id, reload_all, select_partner


def on_add(dialog) -> None:
    edit = PartnerEditDialog(dialog._type_order, parent=dialog)
    if edit.exec() != QDialog.Accepted:
        return
    created = dialog.partner_service.create_partner(dialog._partners, edit.to_record())
    reload_all(dialog)
    select_partner(dialog, created.id)
    show_info(dialog, DialogTitles.SAVE, InfoMessages.PARTNER_SAVED)


def on_edit(dialog) -> None:
    record = find_by_id(dialog, dialog._current_partner_id)
    if record is None:
        show_warning(dialog, DialogTitles.EDIT, WarningMessages.PARTNER_SELECT_TO_EDIT)
        return
    edit = PartnerEditDialog(dialog._type_order, partner=record, parent=dialog)
    if edit.exec() != QDialog.Accepted:
        return
    updated = dialog.partner_service.update_partner(dialog._partners, record.id, edit.to_record())
    reload_all(dialog)
    select_partner(dialog, updated.id)
    show_info(dialog, DialogTitles.SAVE, InfoMessages.PARTNER_UPDATED)


def on_delete(dialog) -> None:
    record = find_by_id(dialog, dialog._current_partner_id)
    if record is None:
        return
    confirm = ConfirmActionDialog(
        Buttons.DELETE,
        f"'{record.name}' {WarningMessages.PARTNER_DELETE_CONFIRM}",
        confirm_text=Buttons.DELETE,
        cancel_text=Buttons.CANCEL,
        parent=dialog,
    )
    if confirm.exec() != QDialog.Accepted:
        return
    dialog.partner_service.delete_partner(dialog._partners, record.id)
    reload_all(dialog)


def on_manage_types(dialog) -> None:
    type_dialog = PartnerTypeDialog(dialog.partner_service, parent=dialog)
    if type_dialog.exec() != QDialog.Accepted:
        return
    dialog.partner_service.prune_partners_to_active_types(dialog._partners)
    reload_all(dialog)
