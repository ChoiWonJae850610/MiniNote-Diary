from __future__ import annotations

from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog
from ui.main_window_feedback import MainWindowFeedback
from ui.main_window_logic import (
    MainWindowDialogLogic,
    MainWindowFeatureLogic,
    MainWindowNavigationLogic,
    MainWindowOrderLogic,
    MainWindowSaveLogic,
    MainWindowWorkOrderLogic,
)
from ui.messages import Buttons, DialogTitles, Warnings


def on_partner_mgmt_clicked(self):
    MainWindowDialogLogic.open_partner_management(self)


def on_unit_mgmt_clicked(self):
    MainWindowDialogLogic.open_unit_management(self)


def open_order_page(self) -> None:
    MainWindowNavigationLogic.open_order_page(self)


def refresh_order_page(self) -> None:
    MainWindowOrderLogic.refresh_order_page(self)


def on_order_template_selected(self, row: int) -> None:
    MainWindowOrderLogic.on_order_template_selected(self, row)


def _clear_order_template_detail(self) -> None:
    MainWindowOrderLogic.clear_order_template_detail(self)


def on_order_create_clicked(self) -> None:
    MainWindowOrderLogic.on_order_create_clicked(self)


def open_feature_page(self, page_index: int) -> None:
    MainWindowNavigationLogic.open_feature_page(self, page_index)


def on_feature_primary(self, page) -> None:
    MainWindowFeatureLogic.show_primary(self, page)


def on_feature_secondary(self, page) -> None:
    MainWindowFeatureLogic.show_secondary(self, page)


def _focus_style_input(self):
    MainWindowNavigationLogic.focus_style_input(self)


def go_work_order(self):
    MainWindowNavigationLogic.go_work_order(self)


def go_menu(self):
    MainWindowNavigationLogic.go_menu(self)


def reset_work_order_form(self):
    MainWindowWorkOrderLogic.reset_form(self)


def _refresh_postits(self, force_rebuild: bool = False):
    MainWindowWorkOrderLogic.refresh_postits(self, force_rebuild=force_rebuild)


def _refresh_basic_postit(self):
    MainWindowWorkOrderLogic.refresh_basic_postit(self)


def on_material_deleted(self, target: str, idx: int):
    MainWindowWorkOrderLogic.remove_material(self, target, idx)


def on_reset_clicked(self):
    self.reset_work_order_form()


def create_back_confirm_dialog(self):
    return ConfirmActionDialog(
        title=DialogTitles.TEMP_SAVE,
        message=Warnings.TEMP_SAVE_CONFIRM,
        confirm_text=Buttons.YES,
        cancel_text=Buttons.NO,
        parent=self,
    )


def dialog_accept_code() -> int:
    return ConfirmActionDialog.Accepted


def show_validation_statuses(self, statuses) -> None:
    ValidationStatusDialog(DialogTitles.SAVE_BLOCKED, statuses, parent=self).exec()


def build_save_success_message(result) -> str:
    return MainWindowFeedback.build_save_success_message(result)


def on_back_clicked(self):
    MainWindowSaveLogic.handle_back(self)


def on_save_clicked(self):
    MainWindowSaveLogic.handle_save(self)


def upload_image(self):
    MainWindowWorkOrderLogic.upload_image(self)


def delete_image(self):
    MainWindowWorkOrderLogic.delete_image(self)


def on_add_material_clicked(self, target: str):
    MainWindowWorkOrderLogic.add_material(self, target)


__all__ = [name for name in globals() if not name.startswith('_') or name in {'_clear_order_template_detail', '_focus_style_input', '_refresh_postits', '_refresh_basic_postit'}]
