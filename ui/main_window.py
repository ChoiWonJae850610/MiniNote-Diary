from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow

from services.common.db_reset_service import DbResetService
from ui.dialogs import ConfirmActionDialog, ask_confirm, show_warning
from ui.main_window_parts.main_window_bootstrap import MainWindowBootstrap
from ui.main_window_parts.main_window_constants import MainWindowPages
from ui.main_window_parts.main_window_dialog_logic import MainWindowDialogLogic
from ui.main_window_parts.main_window_event_binder import MainWindowEventBinder
from ui.main_window_parts.main_window_feature_logic import MainWindowFeatureLogic
from ui.main_window_parts.main_window_inbound_logic import MainWindowInboundLogic
from ui.main_window_parts.main_window_menu_logic import MainWindowMenuLogic
from ui.main_window_parts.main_window_features import build_feature_page_configs
from ui.main_window_parts.main_window_feedback import MainWindowFeedback
from ui.main_window_parts.main_window_focus_logic import MainWindowFocusLogic
from ui.main_window_parts.main_window_navigation import MainWindowNavigationLogic
from ui.main_window_parts.main_window_order_logic import MainWindowOrderLogic
from ui.main_window_parts.main_window_product_logic import MainWindowProductLogic
from ui.main_window_parts.main_window_pages import MainWindowPageCoordinator
from ui.main_window_parts.main_window_save_logic import MainWindowSaveLogic
from ui.main_window_parts.main_window_stats_logic import MainWindowStatsLogic
from ui.main_window_parts.main_window_work_order_logic import MainWindowWorkOrderLogic
from ui.messages import Buttons, DialogTitles, InfoMessages, Warnings
import ui.work_order_validation_ui as WorkOrderValidationUi


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
        self._validation_marks_active = False
        MainWindowBootstrap.initialize_services(self)
        MainWindowFeedback.initialize(self)
        MainWindowBootstrap.build_root(self)
        self._build_pages()
        self._bind_page_events()
        MainWindowBootstrap.apply_defaults(self)
        self.refresh_menu_page()
        self.refresh_stats_page()

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
        if MainWindowFocusLogic.handle_event_filter(self, obj, event):
            return True
        if event.type() == event.Type.MouseButtonPress and hasattr(event, "button"):
            if event.button() == Qt.MouseButton.BackButton:
                self._handle_mouse_back_navigation()
                return True
        return super().eventFilter(obj, event)

    def _handle_mouse_back_navigation(self) -> None:
        if QApplication.activeModalWidget() is not None:
            return
        current_index = self.stack.currentIndex()
        if current_index == self.PAGE_WORK_ORDER:
            self.on_back_clicked()
            return
        if current_index in {self.PAGE_JOB_START, self.PAGE_RECEIPT, self.PAGE_COMPLETE, self.PAGE_SALE, self.PAGE_INVENTORY, self.PAGE_PARTNER}:
            self.go_menu()

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

    def mark_dirty(self):
        if self._suppress_dirty:
            return
        self.state.mark_dirty()
        self._update_window_title()

    def has_any_data(self) -> bool:
        return self.state.has_any_data()

    def refresh_menu_page(self) -> None:
        MainWindowMenuLogic.refresh_menu_page(self)

    def refresh_stats_page(self) -> None:
        MainWindowStatsLogic.refresh_stats_page(self)

    def on_data_reset_clicked(self):
        confirmed = ask_confirm(
            self,
            DialogTitles.DATA_RESET,
            Warnings.DATA_RESET_CONFIRM,
            confirm_text=Buttons.YES,
            cancel_text=Buttons.NO,
        )
        if not confirmed:
            return
        DbResetService.reset_all(self.project_root)
        self.reset_work_order_form()
        self.refresh_order_page()
        self.refresh_inbound_page()
        self.refresh_product_page()
        self.refresh_menu_page()
        self.refresh_stats_page()
        self._show_feedback(InfoMessages.DATA_RESET_DONE)

    def on_partner_mgmt_clicked(self):
        MainWindowDialogLogic.open_partner_management(self)

    def on_unit_mgmt_clicked(self):
        MainWindowDialogLogic.open_unit_management(self)

    def on_product_type_mgmt_clicked(self):
        MainWindowDialogLogic.open_product_type_management(self)

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

    def open_inbound_page(self) -> None:
        self.refresh_inbound_page()
        self.stack.setCurrentIndex(self.PAGE_COMPLETE)

    def open_product_page(self) -> None:
        self.refresh_product_page()
        self.stack.setCurrentIndex(self.PAGE_SALE)

    def refresh_inbound_page(self) -> None:
        MainWindowInboundLogic.refresh_inbound_page(self)

    def on_inbound_order_selected(self, row: int) -> None:
        MainWindowInboundLogic.on_inbound_order_selected(self, row)

    def on_inbound_memo_toggled(self, checked: bool) -> None:
        MainWindowInboundLogic.toggle_order_memo(self, checked)

    def on_inbound_apply_clicked(self) -> None:
        MainWindowInboundLogic.show_apply_preview(self)

    def refresh_product_page(self) -> None:
        MainWindowProductLogic.refresh_product_page(self)

    def on_product_selected(self, row: int) -> None:
        MainWindowProductLogic.on_product_selected(self, row)

    def on_product_save_clicked(self) -> None:
        MainWindowProductLogic.save_product(self)

    def on_product_pending_apply_clicked(self) -> None:
        MainWindowProductLogic.apply_pending_inspection(self)

    def on_product_sale_clicked(self) -> None:
        MainWindowProductLogic.register_sale(self)

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
        WorkOrderValidationUi.deactivate(self)

    def _refresh_postits(self, force_rebuild: bool = False):
        MainWindowWorkOrderLogic.refresh_postits(self, force_rebuild=force_rebuild)

    def _refresh_basic_postit(self):
        MainWindowWorkOrderLogic.refresh_basic_postit(self)

    def on_material_deleted(self, target: str, idx: int):
        MainWindowWorkOrderLogic.remove_material(self, target, idx)
        WorkOrderValidationUi.refresh_if_active(self)

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
        del statuses
        show_warning(self, DialogTitles.SAVE_BLOCKED, "필수 요소가 입력되지 않았습니다.")

    @staticmethod
    def build_save_success_message(result) -> str:
        return MainWindowFeedback.build_save_success_message(result)

    def on_back_clicked(self):
        MainWindowSaveLogic.handle_back(self)

    def on_save_clicked(self):
        MainWindowSaveLogic.handle_save(self)

    def on_load_clicked(self):
        MainWindowWorkOrderLogic.open_load_dialog(self)

    def upload_image(self):
        MainWindowWorkOrderLogic.upload_image(self)

    def delete_image(self):
        MainWindowWorkOrderLogic.delete_image(self)

    def on_add_material_clicked(self, target: str):
        MainWindowWorkOrderLogic.add_material(self, target)
        WorkOrderValidationUi.refresh_if_active(self)

    def on_basic_postit_changed(self, data: dict):
        self.state.update_header(data)
        WorkOrderValidationUi.refresh_if_active(self)
        self._update_window_title()

    def on_change_note_changed(self, text: str):
        self.state.update_change_note(text)
        self._update_window_title()

    def on_material_changed(self, target: str, idx: int, patch: dict):
        MainWindowWorkOrderLogic.update_material(self, target, idx, patch)
        WorkOrderValidationUi.refresh_if_active(self)
