from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QWidget

from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog
from ui.main_window_bootstrap import MainWindowBootstrap
from ui.main_window_constants import MainWindowPages
from ui.main_window_features import build_feature_page_configs
from ui.main_window_feedback import MainWindowFeedback
from ui.main_window_focus_logic import MainWindowFocusLogic
from ui.main_window_logic import (
    MainWindowDialogLogic,
    MainWindowEventBinder,
    MainWindowFeatureLogic,
    MainWindowNavigationLogic,
    MainWindowOrderLogic,
    MainWindowPageCoordinator,
    MainWindowSaveLogic,
    MainWindowWorkOrderLogic,
)
from ui.messages import Buttons, DialogTitles, Warnings


class MainWindow(QMainWindow):
    PAGE_MENU = MainWindowPages.MENU
    PAGE_WORK_ORDER = MainWindowPages.WORK_ORDER
    PAGE_JOB_START = MainWindowPages.JOB_START
    PAGE_RECEIPT = MainWindowPages.RECEIPT
    PAGE_COMPLETE = MainWindowPages.COMPLETE
    PAGE_SALE = MainWindowPages.SALE
    PAGE_INVENTORY = MainWindowPages.INVENTORY
    PAGE_PARTNER = MainWindowPages.PARTNER

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DialogTitles.APP)
        self.menuBar().hide()
        MainWindowBootstrap.initialize_services(self)
        MainWindowFeedback.initialize(self)
        MainWindowBootstrap.build_root(self)
        self._build_pages()
        self._bind_page_events()
        MainWindowBootstrap.apply_defaults(self)

    @property
    def is_dirty(self) -> bool:
        return self.state.is_dirty

    def _build_pages(self) -> None:
        MainWindowPageCoordinator.build_pages(self)

    def _bind_page_events(self) -> None:
        MainWindowEventBinder.bind(self)

    def _install_shortcuts(self):
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.save_shortcut.activated.connect(self._handle_save_shortcut)

    def _handle_save_shortcut(self):
        if self.stack.currentIndex() == self.PAGE_WORK_ORDER:
            self.on_save_clicked()

    def eventFilter(self, obj, event):
        MainWindowFocusLogic.handle_event_filter(self, obj, event)
        return super().eventFilter(obj, event)

    def on_partner_mgmt_clicked(self):
        MainWindowDialogLogic.open_partner_management(self)

    def on_unit_mgmt_clicked(self):
        MainWindowDialogLogic.open_unit_management(self)

    def _show_feedback(self, message: str, timeout_ms=None):
        if timeout_ms is None:
            MainWindowFeedback.show_feedback(self, message)
            return
        MainWindowFeedback.show_feedback(self, message, timeout_ms=timeout_ms)

    def _clear_feedback(self):
        MainWindowFeedback.clear_feedback(self)

    def _update_window_title(self):
        MainWindowFeedback.update_window_title(self)

    def build_feature_page_configs(self):
        return build_feature_page_configs()

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

    def on_feature_primary(self, page: QWidget) -> None:
        MainWindowFeatureLogic.show_primary(self, page)

    def on_feature_secondary(self, page: QWidget) -> None:
        MainWindowFeatureLogic.show_secondary(self, page)

    def _focus_style_input(self):
        MainWindowNavigationLogic.focus_style_input(self)

    def go_work_order(self):
        MainWindowNavigationLogic.go_work_order(self)

    def go_menu(self):
        MainWindowNavigationLogic.go_menu(self)

    def mark_dirty(self):
        if self._suppress_dirty:
            return
        self.state.mark_dirty()
        self._update_window_title()

    def has_any_data(self) -> bool:
        return self.state.has_any_data()

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

    @staticmethod
    def dialog_accept_code() -> int:
        return ConfirmActionDialog.Accepted

    def show_validation_statuses(self, statuses) -> None:
        ValidationStatusDialog(DialogTitles.SAVE_BLOCKED, statuses, parent=self).exec()

    @staticmethod
    def build_save_success_message(result) -> str:
        return MainWindowFeedback.build_save_success_message(result)

    def on_back_clicked(self):
        MainWindowSaveLogic.handle_back(self)

    def on_save_clicked(self):
        MainWindowSaveLogic.handle_save(self)

    def on_basic_postit_changed(self, data: dict):
        self.state.update_header(data)
        self._update_window_title()

    def on_change_note_changed(self, text: str):
        self.state.update_change_note(text)
        self._update_window_title()

    def on_material_changed(self, target: str, idx: int, patch: dict):
        MainWindowWorkOrderLogic.update_material(self, target, idx, patch)

    def upload_image(self):
        MainWindowWorkOrderLogic.upload_image(self)

    def delete_image(self):
        MainWindowWorkOrderLogic.delete_image(self)

    def on_add_material_clicked(self, target: str):
        MainWindowWorkOrderLogic.add_material(self, target)
