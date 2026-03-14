import os

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QStackedWidget,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

from services.order_repository import OrderRepository
from services.partner_lookup_service import PartnerLookupService
from services.work_order_controller import WorkOrderController
from services.work_order_state import WorkOrderState
from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog
from ui.main_window_features import build_feature_page_configs
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
from ui.messages import Buttons, DialogTitles, UiTiming, Warnings
from ui.theme import THEME, build_app_stylesheet


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1
    PAGE_JOB_START = 2
    PAGE_RECEIPT = 3
    PAGE_COMPLETE = 4
    PAGE_SALE = 5
    PAGE_INVENTORY = 6
    PAGE_PARTNER = 7

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DialogTitles.APP)
        self.menuBar().hide()

        self.project_root = self._project_root()
        self.state = WorkOrderState()
        self.controller = WorkOrderController(self.state, self.project_root)
        self.order_repository = OrderRepository(self.project_root)
        self.partner_lookup_service = PartnerLookupService(self.project_root)
        self._suppress_dirty = False
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._clear_feedback)

        self._build_root()
        self._build_pages()
        self._bind_page_events()
        self._apply_window_defaults()

    @staticmethod
    def _project_root() -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    @property
    def is_dirty(self) -> bool:
        return self.state.is_dirty

    def _build_root(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

    def _build_pages(self) -> None:
        MainWindowPageCoordinator.build_pages(self)

    def _bind_page_events(self) -> None:
        MainWindowEventBinder.bind(self)

    def _apply_window_defaults(self) -> None:
        self.setMinimumSize(THEME.window_min_width, THEME.window_min_height)
        self.resize(THEME.window_min_width, THEME.window_min_height)
        self.setStyleSheet(build_app_stylesheet())
        self._install_global_focus_clear()
        self._install_shortcuts()
        self._refresh_postits(force_rebuild=True)
        self._update_window_title()

    def _install_global_focus_clear(self):
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _install_shortcuts(self):
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.save_shortcut.activated.connect(self._handle_save_shortcut)

    def _handle_save_shortcut(self):
        if self.stack.currentIndex() == self.PAGE_WORK_ORDER:
            self.on_save_clicked()

    def _is_text_input_widget(self, widget) -> bool:
        return isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QAbstractSpinBox))

    def _has_input_ancestor(self, widget) -> bool:
        current = widget
        while current is not None:
            if self._is_text_input_widget(current):
                return True
            current = current.parentWidget()
        return False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            focused = QApplication.focusWidget()
            target = obj if isinstance(obj, QWidget) else None
            if focused is not None and target is not None and self._is_text_input_widget(focused):
                if target is not focused and not focused.isAncestorOf(target) and not self._has_input_ancestor(target):
                    focused.clearFocus()
        return super().eventFilter(obj, event)

    def on_partner_mgmt_clicked(self):
        MainWindowDialogLogic.open_partner_management(self)

    def on_unit_mgmt_clicked(self):
        MainWindowDialogLogic.open_unit_management(self)

    def _show_feedback(self, message: str, timeout_ms: int = UiTiming.FEEDBACK_TIMEOUT_MS):
        self.feedback_label.setText(message)
        self._feedback_timer.start(timeout_ms)

    def _clear_feedback(self):
        self.feedback_label.clear()

    def _update_window_title(self):
        suffix = ' *' if self.state.is_dirty else ''
        self.setWindowTitle(f'{DialogTitles.APP}{suffix}')

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
        QTimer.singleShot(0, lambda: self.postit_bar.basic.style_no.activate_for_input())

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
        message = f"저장 완료\n\nJSON: {result.json_path}\nSHA256(평문): {result.sha256_plain}"
        if result.image_path:
            message += f"\n이미지: {result.image_path}"
        return message

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
