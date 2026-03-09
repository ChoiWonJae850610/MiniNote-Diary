import os

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QStackedWidget,
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QDialog,
)

from services.schema import DEFAULT_FEEDBACK_TIMEOUT_MS, SUPPORTED_IMAGE_FILTER
from services.work_order_controller import WorkOrderController
from services.work_order_state import WorkOrderState
from ui.basic_info_dialog import BasicInfoDialog
from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog, show_error, show_info
from ui.menu_page import MenuPageBuilder
from ui.theme import THEME, build_app_stylesheet
from ui.unit_dialog import UnitDialog
from ui.work_order_page import WorkOrderPageBuilder


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle('미니노트 다이어리')
        self.menuBar().hide()

        self.state = WorkOrderState()
        self.controller = WorkOrderController(self.state, self._project_root())
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
        menu_refs = MenuPageBuilder.build()
        work_refs = WorkOrderPageBuilder.build(self)

        self.page_menu = menu_refs.page
        self.page_work_order = work_refs.page

        self.btn_create = menu_refs.btn_create
        self.btn_vendor_mgmt = menu_refs.btn_vendor_mgmt
        self.btn_unit_mgmt = menu_refs.btn_unit_mgmt

        self.btn_back = work_refs.btn_back
        self.btn_reset = work_refs.btn_reset
        self.btn_save = work_refs.btn_save
        self.btn_upload = work_refs.btn_upload
        self.btn_delete_image = work_refs.btn_delete_image
        self.feedback_label = work_refs.feedback_label
        self.image_preview = work_refs.image_preview
        self.change_note_postit = work_refs.change_note_postit
        self.postit_bar = work_refs.postit_bar

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_work_order)
        self.stack.setCurrentIndex(self.PAGE_MENU)

    def _bind_page_events(self) -> None:
        self.btn_create.clicked.connect(self.go_work_order)
        self.btn_vendor_mgmt.clicked.connect(self.on_vendor_mgmt_clicked)
        self.btn_unit_mgmt.clicked.connect(self.on_unit_mgmt_clicked)

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        self.change_note_postit.text_changed.connect(self.on_change_note_changed)
        self.postit_bar.fabric_deleted.connect(self.on_fabric_deleted)
        self.postit_bar.trim_deleted.connect(self.on_trim_deleted)
        self.postit_bar.fabric_item_changed.connect(self.on_fabric_postit_changed)
        self.postit_bar.trim_item_changed.connect(self.on_trim_postit_changed)
        self.postit_bar.fabric_item_added.connect(self.on_add_fabric_clicked)
        self.postit_bar.trim_item_added.connect(self.on_add_trim_clicked)
        self.postit_bar.basic_data_changed.connect(self.on_basic_postit_changed)

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

    def on_vendor_mgmt_clicked(self):
        show_info(self, '거래처 관리', '거래처 관리 화면은 추후 연결됩니다.')

    def on_unit_mgmt_clicked(self):
        dlg = UnitDialog(project_root=self._project_root(), parent=self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec()

    def _show_feedback(self, message: str, timeout_ms: int = DEFAULT_FEEDBACK_TIMEOUT_MS):
        self.feedback_label.setText(message)
        self._feedback_timer.start(timeout_ms)

    def _clear_feedback(self):
        self.feedback_label.clear()

    def _update_window_title(self):
        suffix = ' *' if self.state.is_dirty else ''
        self.setWindowTitle(f'미니노트 다이어리{suffix}')

    def _focus_style_input(self):
        QTimer.singleShot(0, lambda: self.postit_bar.basic.style_no.activate_for_input())

    def go_work_order(self):
        self._refresh_postits(force_rebuild=True)
        self.stack.setCurrentIndex(self.PAGE_WORK_ORDER)
        self._focus_style_input()

    def go_menu(self):
        self.stack.setCurrentIndex(self.PAGE_MENU)

    def mark_dirty(self):
        if self._suppress_dirty:
            return
        self.state.mark_dirty()
        self._update_window_title()

    def has_any_data(self) -> bool:
        return self.state.has_any_data()

    def reset_work_order_form(self):
        self._suppress_dirty = True
        try:
            self.state.reset()
            self.image_preview.clear_image()
            self.btn_delete_image.setEnabled(False)
            self._refresh_postits(force_rebuild=True)
            self._clear_feedback()
            self._update_window_title()
        finally:
            self._suppress_dirty = False

    def _refresh_postits(self, force_rebuild: bool = False):
        self.postit_bar.set_data(
            header=self.state.header_data,
            fabrics=self.state.fabric_items,
            trims=self.state.trim_items,
            force_rebuild=force_rebuild,
        )
        self.change_note_postit.set_text(self.state.header.change_note)

    def on_add_basic_clicked(self):
        dlg = BasicInfoDialog(initial=self.state.header_data, parent=self)
        if dlg.exec() == dlg.Accepted:
            self.state.header_data = dlg.get_data()
            self.mark_dirty()
            self._refresh_postits(force_rebuild=True)

    def on_fabric_deleted(self, idx: int):
        if self.state.remove_material_item('fabric', idx):
            self._refresh_postits(force_rebuild=True)
            self._update_window_title()

    def on_trim_deleted(self, idx: int):
        if self.state.remove_material_item('trim', idx):
            self._refresh_postits(force_rebuild=True)
            self._update_window_title()

    def on_reset_clicked(self):
        self.reset_work_order_form()

    def on_back_clicked(self):
        if not self.has_any_data():
            self.go_menu()
            return
        dialog = ConfirmActionDialog(title='임시 저장', message='임시 저장 하시겠습니까?', confirm_text='예', cancel_text='아니요', parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.go_menu()
        else:
            self.reset_work_order_form()
            self.go_menu()

    def on_save_clicked(self):
        statuses = self.controller.get_save_requirement_statuses()
        if not all(ok for _, ok in statuses):
            ValidationStatusDialog('저장 불가', statuses, parent=self).exec()
            return
        try:
            result = self.controller.save()
        except Exception as exc:
            show_error(self, '저장 실패', str(exc))
            return
        self.reset_work_order_form()
        message = f'저장 완료\n\nJSON: {result.json_path}\nSHA256(평문): {result.sha256_plain}'
        if result.image_path:
            message += f'\n이미지: {result.image_path}'
        show_info(self, '저장', message)

    def on_basic_postit_changed(self, data: dict):
        self.state.update_header(data)
        self._update_window_title()

    def on_change_note_changed(self, text: str):
        self.state.update_change_note(text)
        self._update_window_title()

    def on_fabric_postit_changed(self, idx: int, patch: dict):
        self.state.update_material_patch('fabric', idx, patch)
        self._update_window_title()

    def on_trim_postit_changed(self, idx: int, patch: dict):
        self.state.update_material_patch('trim', idx, patch)
        self._update_window_title()

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(self, '이미지 선택', '', SUPPORTED_IMAGE_FILTER)
        if not path:
            return
        try:
            self.image_preview.set_image(path)
            self.state.current_image_path = path
            self.btn_delete_image.setEnabled(True)
            self.mark_dirty()
            self._show_feedback('이미지 첨부됨')
        except Exception as exc:
            show_error(self, '오류', str(exc))

    def delete_image(self):
        self.image_preview.clear_image()
        self.state.current_image_path = None
        self.btn_delete_image.setEnabled(False)
        self.mark_dirty()
        self._show_feedback('이미지 제거됨')

    def on_add_fabric_clicked(self):
        new_index = self.state.add_material_item('fabric')
        if new_index is None:
            return
        self._refresh_postits(force_rebuild=True)
        self.postit_bar.fabric.set_active_card(new_index)
        self._update_window_title()

    def on_add_trim_clicked(self):
        new_index = self.state.add_material_item('trim')
        if new_index is None:
            return
        self._refresh_postits(force_rebuild=True)
        self.postit_bar.trim.set_active_card(new_index)
        self._update_window_title()
