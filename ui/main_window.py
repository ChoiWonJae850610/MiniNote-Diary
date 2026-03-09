import os
from typing import Optional

from PySide6.QtCore import Qt, QSize, QEvent, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QSizePolicy,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QStackedWidget,
    QDialog,
    QTextEdit,
    QLineEdit,
    QPlainTextEdit,
    QComboBox,
    QAbstractSpinBox,
    QStyle,
)

from services.work_order_controller import WorkOrderController
from services.work_order_state import WorkOrderState
from ui.image_preview import ImagePreview
from ui.unit_dialog import UnitDialog
from ui.basic_info_dialog import BasicInfoDialog
from ui.material_item_dialog import MaterialItemDialog
from ui.postit_widgets import PostItBar, ChangeNotePostIt, SectionContainer, SectionTitleBadge
from ui.theme import THEME, build_app_stylesheet, image_preview_style
from ui.icon_factory import make_image_outline_icon, make_save_icon, standard_icon
from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog, show_error, show_info
from ui.widget_factory import apply_button_metrics, apply_icon_button_metrics, make_dialog_button, make_dialog_button_row


class _ChangeNoteDialog(QDialog):
    def __init__(self, initial_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("메모")
        self.setModal(True)
        self.setMinimumSize(THEME.note_dialog_min_width, THEME.note_dialog_min_height)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(THEME.page_padding, THEME.page_padding, THEME.page_padding, THEME.page_padding)
        layout.setSpacing(THEME.block_spacing)
        self.edit = QTextEdit(self)
        self.edit.setPlainText(initial_text or "")
        self.edit.setPlaceholderText("메모를 입력하세요.")
        layout.addWidget(self.edit, 1)
        btn_cancel = make_dialog_button("취소", self, role="cancel")
        btn_ok = make_dialog_button("확인", self, role="confirm")
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        layout.addLayout(make_dialog_button_row([btn_cancel, btn_ok]))

    def get_text(self) -> str:
        return self.edit.toPlainText().strip()


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle("미니노트 다이어리")
        self.menuBar().hide()

        self.state = WorkOrderState()
        self.controller = WorkOrderController(self.state, self._project_root())
        self._suppress_dirty = False
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._clear_feedback)

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)
        self.page_menu = self._build_page_menu()
        self.page_work_order = self._build_page_work_order()
        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_work_order)
        self.stack.setCurrentIndex(self.PAGE_MENU)

        self.setMinimumSize(THEME.window_min_width, THEME.window_min_height)
        self.resize(THEME.window_min_width, THEME.window_min_height)
        self._apply_diary_theme()
        self._install_global_focus_clear()
        self._update_window_title()
        self._install_shortcuts()

    @staticmethod
    def _project_root() -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @property
    def is_dirty(self) -> bool:
        return self.state.is_dirty

    def _apply_diary_theme(self):
        self.setStyleSheet(build_app_stylesheet())

    def _install_global_focus_clear(self):
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

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

    def _install_shortcuts(self):
        self.save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.save_shortcut.activated.connect(self._handle_save_shortcut)

    def _handle_save_shortcut(self):
        if self.stack.currentIndex() == self.PAGE_WORK_ORDER:
            self.on_save_clicked()

    def _build_page_menu(self) -> QWidget:
        page = QWidget()
        page.setObjectName("workOrderPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(THEME.page_padding_x + 4, THEME.page_padding_y + 4, THEME.page_padding_x + 4, THEME.page_padding_y + 4)
        layout.setSpacing(0)

        center_col = QVBoxLayout()
        center_col.setSpacing(THEME.section_gap)
        title = QLabel("메인 메뉴")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: {THEME.menu_title_font_px}px; font-weight: bold;")

        btn_create = QPushButton("작업지시서 생성")
        btn_receipt = QPushButton("부자재 영수증 업로드")
        btn_status = QPushButton("제품 제작 현황")
        for button in (btn_create, btn_receipt, btn_status):
            button.setFixedSize(THEME.menu_button_width, THEME.menu_button_height)
        btn_create.clicked.connect(self.go_work_order)

        center_col.addWidget(title)
        center_col.addSpacing(THEME.section_gap)
        center_col.addWidget(btn_create, alignment=Qt.AlignHCenter)
        center_col.addWidget(btn_receipt, alignment=Qt.AlignHCenter)
        center_col.addWidget(btn_status, alignment=Qt.AlignHCenter)
        layout.addStretch(1)
        layout.addLayout(center_col)
        layout.addStretch(1)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        self.btn_vendor_mgmt = QPushButton("거래처 관리")
        self.btn_unit_mgmt = QPushButton("단위 추가(관리)")
        apply_button_metrics(self.btn_vendor_mgmt, width=THEME.footer_button_width, height=THEME.footer_button_height)
        apply_button_metrics(self.btn_unit_mgmt, width=THEME.footer_button_width, height=THEME.footer_button_height)
        self.btn_vendor_mgmt.clicked.connect(self.on_vendor_mgmt_clicked)
        self.btn_unit_mgmt.clicked.connect(self.on_unit_mgmt_clicked)
        bottom_row.addWidget(self.btn_vendor_mgmt)
        bottom_row.addSpacing(THEME.row_spacing)
        bottom_row.addWidget(self.btn_unit_mgmt)
        layout.addLayout(bottom_row)
        return page

    def on_vendor_mgmt_clicked(self):
        show_info(self, "거래처 관리", "거래처 관리 화면은 추후 연결됩니다.")

    def on_unit_mgmt_clicked(self):
        dlg = UnitDialog(project_root=self._project_root(), parent=self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec()

    def _build_page_work_order(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(THEME.page_padding_x, THEME.page_padding_y, THEME.page_padding_x, THEME.page_padding_y)
        page_layout.setSpacing(THEME.block_spacing)

        self.btn_back = QPushButton("◀")
        apply_icon_button_metrics(self.btn_back, font_px=THEME.icon_button_font_px + 2, object_name="navButton", tooltip="뒤로가기")
        self.btn_reset = QPushButton("")
        apply_icon_button_metrics(self.btn_reset, font_px=THEME.reset_button_font_px, object_name="iconAction", tooltip="새로고침")
        self.btn_reset.setIcon(standard_icon(self, [QStyle.SP_BrowserReload, QStyle.SP_FileDialogDetailedView]))
        self.btn_reset.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        self.btn_save = QPushButton("")
        apply_icon_button_metrics(self.btn_save, font_px=THEME.save_button_font_px, object_name="iconPrimary", tooltip="저장")
        save_icon = standard_icon(self, [QStyle.SP_DialogSaveButton], fallback=make_save_icon(THEME.icon_size_md, THEME.color_text_on_primary))
        self.btn_save.setIcon(save_icon)
        self.btn_save.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        self.btn_upload = QPushButton("")
        apply_icon_button_metrics(self.btn_upload, font_px=THEME.icon_button_font_px + 2, object_name="iconAction", tooltip="사진 업로드")
        self.btn_upload.setIcon(make_image_outline_icon(THEME.icon_size_md))
        self.btn_upload.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        self.btn_delete_image = QPushButton("")
        apply_icon_button_metrics(self.btn_delete_image, font_px=THEME.icon_button_font_px + 2, object_name="iconDanger", tooltip="사진 삭제")
        delete_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        if delete_icon.isNull():
            delete_icon = self.style().standardIcon(QStyle.SP_DialogDiscardButton)
        self.btn_delete_image.setIcon(delete_icon)
        self.btn_delete_image.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        self.btn_delete_image.setEnabled(False)

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        left_controls = QWidget()
        left_controls_layout = QHBoxLayout(left_controls)
        left_controls_layout.setContentsMargins(0, 0, 0, 0)
        left_controls_layout.setSpacing(THEME.top_button_spacing)
        left_controls_layout.addWidget(self.btn_back)
        left_controls_layout.addWidget(self.btn_reset)
        left_controls_layout.addWidget(self.btn_save)
        left_controls_layout.addStretch(1)

        image_controls = QWidget()
        image_controls_layout = QHBoxLayout(image_controls)
        image_controls_layout.setContentsMargins(0, 0, 0, 0)
        image_controls_layout.setSpacing(THEME.top_button_spacing)
        image_controls_layout.addStretch(1)
        image_controls_layout.addWidget(self.btn_upload)
        image_controls_layout.addWidget(self.btn_delete_image)

        self.feedback_label = QLabel("", self)
        self.feedback_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.feedback_label.setMinimumHeight(THEME.feedback_label_height)
        self.feedback_label.setMaximumHeight(THEME.feedback_label_height)
        self.feedback_label.setStyleSheet(f"QLabel{{background:transparent;border:none;padding:0 {THEME.label_padding_x}px;color:{THEME.color_text};font-weight:700;}}")

        self.image_preview = ImagePreview()
        self.image_preview.setMinimumHeight(THEME.image_preview_min_height)
        self.image_preview.setStyleSheet(image_preview_style())
        self.image_shell = QWidget()
        self.image_shell.setObjectName("imageShell")
        image_shell_layout = QVBoxLayout(self.image_shell)
        image_shell_layout.setContentsMargins(THEME.image_shell_margin, THEME.image_shell_margin, THEME.image_shell_margin, THEME.image_shell_margin)
        image_shell_layout.setSpacing(0)
        image_shell_layout.addWidget(self.image_preview)

        self.change_note_postit = ChangeNotePostIt()
        self.change_note_postit.text_changed.connect(self.on_change_note_changed)
        self.change_note_title = SectionTitleBadge("메모", self, color=THEME.color_change_title, border_color=THEME.color_change_border)
        self.change_note_wrap = SectionContainer(self.change_note_title, self.change_note_postit, spacing=THEME.top_button_spacing)

        center_row = QWidget()
        center_layout = QGridLayout(center_row)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setHorizontalSpacing(THEME.section_gap)
        center_layout.setVerticalSpacing(THEME.row_spacing)
        center_layout.setColumnStretch(0, 1)
        center_layout.setColumnStretch(1, 1)
        center_layout.setColumnStretch(2, 1)
        center_layout.setRowStretch(1, 1)
        center_layout.addWidget(left_controls, 0, 0, 1, 1)
        center_layout.addWidget(image_controls, 0, 1, 1, 1)
        center_layout.addWidget(self.change_note_wrap, 0, 2, 2, 1)
        center_layout.addWidget(self.image_shell, 1, 0, 1, 2)

        self.postit_bar = PostItBar()
        self.postit_bar.setMaximumHeight(THEME.postit_bar_max_height)
        self.postit_bar.fabric_deleted.connect(self.on_fabric_deleted)
        self.postit_bar.trim_deleted.connect(self.on_trim_deleted)
        self.postit_bar.fabric_item_changed.connect(self.on_fabric_postit_changed)
        self.postit_bar.trim_item_changed.connect(self.on_trim_postit_changed)
        self.postit_bar.fabric_item_added.connect(self.on_add_fabric_clicked)
        self.postit_bar.trim_item_added.connect(self.on_add_trim_clicked)
        self.postit_bar.basic_data_changed.connect(self.on_basic_postit_changed)

        page_layout.addWidget(center_row, 1)
        page_layout.addWidget(self.postit_bar, 0)
        page_layout.addWidget(self.feedback_label, 0)

        self._refresh_postits()
        QTimer.singleShot(0, lambda: self.postit_bar.basic.style_no.activate_for_input())
        return page

    def _show_feedback(self, message: str, timeout_ms: int = 2200):
        self.feedback_label.setText(message)
        self._feedback_timer.start(timeout_ms)

    def _clear_feedback(self):
        self.feedback_label.clear()

    def _update_window_title(self):
        suffix = " *" if self.state.is_dirty else ""
        self.setWindowTitle(f"미니노트 다이어리{suffix}")

    def go_work_order(self):
        self._refresh_postits(force_rebuild=True)
        self.stack.setCurrentIndex(self.PAGE_WORK_ORDER)
        QTimer.singleShot(0, lambda: self.postit_bar.basic.style_no.activate_for_input())

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
            self._refresh_postits()
            self._clear_feedback()
            self._update_window_title()
            self.change_note_postit.set_text("")
        finally:
            self._suppress_dirty = False

    def _refresh_postits(self, force_rebuild: bool = False):
        self.postit_bar.set_data(
            header=self.state.header_data,
            fabrics=self.state.fabric_items,
            trims=self.state.trim_items,
            force_rebuild=force_rebuild,
        )
        self.change_note_postit.set_text((self.state.header_data or {}).get("change_note", ""))

    def on_add_basic_clicked(self):
        dlg = BasicInfoDialog(initial=self.state.header_data, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.state.header_data = dlg.get_data()
            self.mark_dirty()
            self._refresh_postits()

    def on_fabric_deleted(self, idx: int):
        if self.state.remove_material_item("fabric", idx):
            self._refresh_postits()
            self._update_window_title()

    def on_trim_deleted(self, idx: int):
        if self.state.remove_material_item("trim", idx):
            self._refresh_postits()
            self._update_window_title()

    def on_reset_clicked(self):
        self.reset_work_order_form()

    def on_back_clicked(self):
        if not self.has_any_data():
            self.go_menu()
            return
        dialog = ConfirmActionDialog(title="임시 저장", message="임시 저장 하시겠습니까?", confirm_text="예", cancel_text="아니요", parent=self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.go_menu()
        else:
            self.reset_work_order_form()
            self.go_menu()

    def on_save_clicked(self):
        statuses = self.controller.get_save_requirement_statuses()
        if not all(ok for _, ok in statuses):
            ValidationStatusDialog("저장 불가", statuses, parent=self).exec()
            return
        try:
            result = self.controller.save()
        except Exception as exc:
            show_error(self, "저장 실패", str(exc))
            return
        self.reset_work_order_form()
        message = f"저장 완료\n\nJSON: {result.json_path}\nSHA256(평문): {result.sha256_plain}"
        if result.image_path:
            message += f"\n이미지: {result.image_path}"
        show_info(self, "저장", message)

    def on_basic_postit_changed(self, data: dict):
        self.state.update_header(data)
        self._update_window_title()

    def on_change_note_changed(self, text: str):
        self.state.update_change_note(text)
        self._update_window_title()

    def on_fabric_postit_changed(self, idx: int, patch: dict):
        self.state.update_material_patch("fabric", idx, patch)
        self._update_window_title()

    def on_trim_postit_changed(self, idx: int, patch: dict):
        self.state.update_material_patch("trim", idx, patch)
        self._update_window_title()

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        try:
            self.image_preview.set_image(path)
            self.state.current_image_path = path
            self.btn_delete_image.setEnabled(True)
            self.mark_dirty()
            self._show_feedback("이미지 첨부됨")
        except Exception as exc:
            show_error(self, "오류", str(exc))

    def delete_image(self):
        self.image_preview.clear_image()
        self.state.current_image_path = None
        self.btn_delete_image.setEnabled(False)
        self.mark_dirty()
        self._show_feedback("이미지 제거됨")

    def on_add_fabric_clicked(self):
        new_index = self.state.add_material_item("fabric")
        if new_index is None:
            return
        self._refresh_postits()
        self.postit_bar.fabric.set_active_card(new_index)
        self._update_window_title()

    def on_add_trim_clicked(self):
        new_index = self.state.add_material_item("trim")
        if new_index is None:
            return
        self._refresh_postits()
        self.postit_bar.trim.set_active_card(new_index)
        self._update_window_title()
