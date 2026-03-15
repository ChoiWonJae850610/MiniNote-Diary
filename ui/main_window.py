from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QWidget

from ui.main_window_bootstrap import MainWindowBootstrap
from ui.main_window_constants import MainWindowPages
from ui.main_window_features import build_feature_page_configs
from ui.main_window_feedback import MainWindowFeedback
from ui.main_window_focus_logic import MainWindowFocusLogic
from ui.main_window_handlers import (
    _clear_order_template_detail,
    _focus_style_input,
    _refresh_basic_postit,
    _refresh_postits,
    build_save_success_message,
    create_back_confirm_dialog,
    delete_image,
    dialog_accept_code,
    go_menu,
    go_work_order,
    on_add_material_clicked,
    on_back_clicked,
    on_feature_primary,
    on_feature_secondary,
    on_material_deleted,
    on_order_create_clicked,
    on_order_template_selected,
    on_partner_mgmt_clicked,
    on_reset_clicked,
    on_save_clicked,
    on_unit_mgmt_clicked,
    open_feature_page,
    open_order_page,
    refresh_order_page,
    reset_work_order_form,
    show_validation_statuses,
    upload_image,
)
from ui.main_window_logic import MainWindowEventBinder, MainWindowPageCoordinator
from ui.messages import DialogTitles


class MainWindow(QMainWindow):
    PAGE_MENU = MainWindowPages.MENU
    PAGE_WORK_ORDER = MainWindowPages.WORK_ORDER
    PAGE_JOB_START = MainWindowPages.JOB_START
    PAGE_RECEIPT = MainWindowPages.RECEIPT
    PAGE_COMPLETE = MainWindowPages.COMPLETE
    PAGE_SALE = MainWindowPages.SALE
    PAGE_INVENTORY = MainWindowPages.INVENTORY
    PAGE_PARTNER = MainWindowPages.PARTNER

    on_partner_mgmt_clicked = on_partner_mgmt_clicked
    on_unit_mgmt_clicked = on_unit_mgmt_clicked
    open_order_page = open_order_page
    refresh_order_page = refresh_order_page
    on_order_template_selected = on_order_template_selected
    _clear_order_template_detail = _clear_order_template_detail
    on_order_create_clicked = on_order_create_clicked
    open_feature_page = open_feature_page
    on_feature_primary = on_feature_primary
    on_feature_secondary = on_feature_secondary
    _focus_style_input = _focus_style_input
    go_work_order = go_work_order
    go_menu = go_menu
    reset_work_order_form = reset_work_order_form
    _refresh_postits = _refresh_postits
    _refresh_basic_postit = _refresh_basic_postit
    on_material_deleted = on_material_deleted
    on_reset_clicked = on_reset_clicked
    create_back_confirm_dialog = create_back_confirm_dialog
    dialog_accept_code = staticmethod(dialog_accept_code)
    show_validation_statuses = show_validation_statuses
    build_save_success_message = staticmethod(build_save_success_message)
    on_back_clicked = on_back_clicked
    on_save_clicked = on_save_clicked
    upload_image = upload_image
    delete_image = delete_image
    on_add_material_clicked = on_add_material_clicked

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

    def on_basic_postit_changed(self, data: dict):
        self.state.update_header(data)
        self._update_window_title()

    def on_change_note_changed(self, text: str):
        self.state.update_change_note(text)
        self._update_window_title()

    def on_material_changed(self, target: str, idx: int, patch: dict):
        from ui.main_window_logic import MainWindowWorkOrderLogic
        MainWindowWorkOrderLogic.update_material(self, target, idx, patch)
