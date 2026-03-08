# ui/main_window.py
import os
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QSize, QEvent, QTimer
from PySide6.QtGui import QColor, QIcon, QKeySequence, QPainter, QPen, QPixmap, QShortcut, QPainterPath
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
    QMessageBox,
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

from ui.image_preview import ImagePreview
from services.storage import save_work_order
from ui.unit_dialog import UnitDialog
from ui.basic_info_dialog import BasicInfoDialog
from ui.material_item_dialog import MaterialItemDialog
from ui.postit_widgets import PostItBar, ChangeNotePostIt, SectionContainer, SectionTitleBadge
from ui.theme import THEME, build_app_stylesheet, icon_button_override, image_preview_style, title_badge_style
from ui.dialogs import ConfirmActionDialog, ValidationStatusDialog




def _make_image_placeholder_pixmap(width: int = 240, height: int = 180) -> QPixmap:
    pix = QPixmap(width, height)
    pix.fill(Qt.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    border = QColor(THEME.color_border_hover)
    border.setAlpha(150)
    fill = QColor(THEME.color_surface_alt)
    fill.setAlpha(170)

    card_rect = pix.rect().adjusted(10, 10, -10, -10)
    path = QPainterPath()
    path.addRoundedRect(card_rect, 18, 18)
    p.fillPath(path, fill)

    pen = QPen(border, 2)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)

    dash_rect = card_rect.adjusted(20, 20, -20, -20)
    dash_pen = QPen(border, 2)
    dash_pen.setStyle(Qt.DashLine)
    dash_pen.setDashPattern([4, 4])
    dash_pen.setCapStyle(Qt.RoundCap)
    dash_pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(dash_pen)
    p.drawRoundedRect(dash_rect, 16, 16)

    p.setPen(pen)
    frame = dash_rect.adjusted(40, 28, -40, -46)
    p.drawRoundedRect(frame, 10, 10)
    p.drawEllipse(frame.right() - 34, frame.top() + 14, 12, 12)

    ridge = QPainterPath()
    ridge.moveTo(frame.left() + 14, frame.bottom() - 14)
    ridge.lineTo(frame.left() + 46, frame.center().y() + 6)
    ridge.lineTo(frame.left() + 72, frame.bottom() - 24)
    ridge.lineTo(frame.right() - 18, frame.top() + 34)
    p.drawPath(ridge)

    plus_x = dash_rect.center().x()
    plus_y = dash_rect.bottom() - 34
    p.drawLine(plus_x - 10, plus_y, plus_x + 10, plus_y)
    p.drawLine(plus_x, plus_y - 10, plus_x, plus_y + 10)

    p.end()
    return pix

def _make_image_outline_icon(size: int = 16) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    pen = QPen(QColor(THEME.color_icon), 1.8)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)

    inset = 2.0
    frame_w = size - inset * 2
    frame_h = size - inset * 2
    p.drawRoundedRect(inset, inset, frame_w, frame_h, 2.2, 2.2)
    p.drawEllipse(size * 0.63, size * 0.34, size * 0.14, size * 0.14)
    p.drawLine(size * 0.25, size * 0.73, size * 0.45, size * 0.50)
    p.drawLine(size * 0.45, size * 0.50, size * 0.57, size * 0.61)
    p.drawLine(size * 0.57, size * 0.61, size * 0.77, size * 0.39)
    p.end()
    return QIcon(pix)
class _ChangeNoteDialog(QDialog):
    def __init__(self, initial_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("메모")
        self.setModal(True)
        self.setMinimumSize(520, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.edit = QTextEdit(self)
        self.edit.setPlainText(initial_text or "")
        self.edit.setPlaceholderText("메모를 입력하세요.")
        layout.addWidget(self.edit, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_cancel = QPushButton("취소", self)
        btn_ok = QPushButton("확인", self)
        btn_cancel.setFixedHeight(34)
        btn_ok.setFixedHeight(34)
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_text(self) -> str:
        return self.edit.toPlainText().strip()



class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle("미니노트 다이어리")
        self.menuBar().hide()

        self.is_dirty = False
        self._suppress_dirty = False
        self.current_image_path: Optional[str] = None
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._clear_feedback)

        # 기본정보/원단/부자재는 모두 팝업 입력 → dict/list로 관리
        self.header_data: Dict[str, str] = {}
        self.fabric_items: List[Dict[str, str]] = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
        self.trim_items: List[Dict[str, str]] = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]

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

        # 이미지 중심 화면 느낌 (요청 반영)
        self.setMinimumSize(1080, 760)
        self.resize(1080, 760)
        self._apply_diary_theme()
        self._install_global_focus_clear()
        self._update_window_title()
        self._install_shortcuts()

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
        self.save_shortcut.activated.connect(self.on_save_clicked)

    # ===================== Menu Page ======================
    def _build_page_menu(self) -> QWidget:
        page = QWidget()
        page.setObjectName("workOrderPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        center_col = QVBoxLayout()
        center_col.setSpacing(14)

        title = QLabel("메인 메뉴")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: {THEME.menu_title_font_px}px; font-weight: bold;")

        btn_create = QPushButton("작업지시서 생성")
        btn_receipt = QPushButton("부자재 영수증 업로드")
        btn_status = QPushButton("제품 제작 현황")

        BTN_W, BTN_H = 360, 54
        for b in (btn_create, btn_receipt, btn_status):
            b.setFixedSize(BTN_W, BTN_H)

        btn_create.clicked.connect(self.go_work_order)

        center_col.addWidget(title)
        center_col.addSpacing(14)
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
        self.btn_vendor_mgmt.setFixedSize(140, 32)
        self.btn_unit_mgmt.setFixedSize(140, 32)

        self.btn_vendor_mgmt.clicked.connect(self.on_vendor_mgmt_clicked)
        self.btn_unit_mgmt.clicked.connect(self.on_unit_mgmt_clicked)

        bottom_row.addWidget(self.btn_vendor_mgmt)
        bottom_row.addSpacing(8)
        bottom_row.addWidget(self.btn_unit_mgmt)

        layout.addLayout(bottom_row)
        return page

    def on_vendor_mgmt_clicked(self):
        QMessageBox.information(self, "거래처 관리", "거래처 관리 화면은 추후 연결됩니다.")

    def on_unit_mgmt_clicked(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        dlg = UnitDialog(project_root=project_root, parent=self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec()

    # =================== Work Order Page ===================
    def _build_page_work_order(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(12, 12, 12, 12)
        page_layout.setSpacing(10)

        # 상단 버튼: 좌측 기능 버튼 + 이미지 영역 우측 상단의 사진 버튼
        self.btn_back = QPushButton("◀")
        self.btn_back.setObjectName("navButton")
        self.btn_reset = QPushButton("↻")
        self.btn_reset.setObjectName("iconAction")
        self.btn_save = QPushButton("✓")
        self.btn_save.setObjectName("iconPrimary")

        self.btn_upload = QPushButton("")
        self.btn_upload.setObjectName("iconAction")
        self.btn_delete_image = QPushButton("")
        self.btn_delete_image.setObjectName("iconDanger")
        self.btn_delete_image.setEnabled(False)

        for b in (self.btn_back, self.btn_reset, self.btn_save, self.btn_upload, self.btn_delete_image):
            b.setFixedSize(THEME.icon_button_size, THEME.icon_button_size)
            b.setContentsMargins(0, 0, 0, 0)
            f = b.font()
            f.setPointSize(THEME.icon_button_font_px + 2)
            f.setBold(True)
            b.setFont(f)

        self.btn_back.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))
        self.btn_reset.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))
        self.btn_save.setStyleSheet(icon_button_override(THEME.icon_button_font_px + 2))

        self.btn_back.setToolTip("뒤로가기")
        self.btn_reset.setToolTip("새로고침")
        self.btn_save.setToolTip("저장")
        self.btn_upload.setIcon(_make_image_outline_icon(THEME.icon_size_md))
        self.btn_upload.setIconSize(QSize(THEME.icon_size_md, THEME.icon_size_md))
        self.btn_upload.setToolTip("사진 업로드")

        delete_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        if delete_icon.isNull():
            delete_icon = self.style().standardIcon(QStyle.SP_DialogDiscardButton)
        self.btn_delete_image.setIcon(delete_icon)
        self.btn_delete_image.setToolTip("사진 삭제")

        self.btn_delete_image.setIconSize(QSize(THEME.icon_size_sm, THEME.icon_size_sm))
        self.btn_delete_image.setText("")

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        left_controls = QWidget()
        left_controls_layout = QHBoxLayout(left_controls)
        left_controls_layout.setContentsMargins(0, 0, 0, 0)
        left_controls_layout.setSpacing(6)
        left_controls_layout.addWidget(self.btn_back)
        left_controls_layout.addWidget(self.btn_reset)
        left_controls_layout.addWidget(self.btn_save)
        left_controls_layout.addStretch(1)

        image_controls = QWidget()
        image_controls_layout = QHBoxLayout(image_controls)
        image_controls_layout.setContentsMargins(0, 0, 0, 0)
        image_controls_layout.setSpacing(6)
        image_controls_layout.addStretch(1)
        image_controls_layout.addWidget(self.btn_upload)
        image_controls_layout.addWidget(self.btn_delete_image)

        self.feedback_label = QLabel("", self)
        self.feedback_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.feedback_label.setMinimumHeight(20)
        self.feedback_label.setMaximumHeight(20)
        self.feedback_label.setStyleSheet(
            "QLabel{background:transparent;border:none;padding:0 2px;color:#1F2933;font-weight:700;}"
        )

        # 이미지 영역(왼쪽) + 메모 포스트잇(오른쪽)
        self.image_preview = ImagePreview()
        self.image_preview.setMinimumHeight(520)
        self.image_preview.setStyleSheet(image_preview_style())
        self.image_preview.set_placeholder_pixmap(_make_image_placeholder_pixmap())

        self.image_shell = QWidget()
        self.image_shell.setObjectName("imageShell")
        image_shell_layout = QVBoxLayout(self.image_shell)
        image_shell_layout.setContentsMargins(18, 18, 18, 18)
        image_shell_layout.setSpacing(0)
        image_shell_layout.addWidget(self.image_preview)

        self.change_note_postit = ChangeNotePostIt()
        self.change_note_postit.text_changed.connect(self.on_change_note_changed)
        self.change_note_postit.setVisible(True)

        self.change_note_title = SectionTitleBadge(
            "메모",
            self,
            color=THEME.color_change_title,
            border_color=THEME.color_change_border,
        )
        self.change_note_wrap = SectionContainer(
            self.change_note_title,
            self.change_note_postit,
            spacing=6,
        )

        center_row = QWidget()
        center_layout = QGridLayout(center_row)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setHorizontalSpacing(14)
        center_layout.setVerticalSpacing(8)
        center_layout.setColumnStretch(0, 1)
        center_layout.setColumnStretch(1, 1)
        center_layout.setColumnStretch(2, 1)
        center_layout.setRowStretch(1, 1)

        center_layout.addWidget(left_controls, 0, 0, 1, 1)
        center_layout.addWidget(image_controls, 0, 1, 1, 1)
        center_layout.addWidget(self.change_note_wrap, 0, 2, 2, 1)
        center_layout.addWidget(self.image_shell, 1, 0, 1, 2)
        # 포스트잇(정보 확인용) — 이미지 중심 느낌을 위해 높이를 과하게 먹지 않도록 제한
        self.postit_bar = PostItBar()
        self.postit_bar.setMaximumHeight(232)
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
        if not hasattr(self, "feedback_label"):
            return
        self.feedback_label.setText(message)
        self._feedback_timer.start(timeout_ms)

    def _clear_feedback(self):
        if hasattr(self, "feedback_label"):
            self.feedback_label.clear()

    def _update_window_title(self):
        suffix = " *" if self.is_dirty else ""
        self.setWindowTitle(f"미니노트 다이어리{suffix}")

    # ===================== Navigation ======================
    def go_work_order(self):
        self._refresh_postits(force_rebuild=True)
        self.stack.setCurrentIndex(self.PAGE_WORK_ORDER)
        try:
            QTimer.singleShot(0, lambda: self.postit_bar.basic.style_no.activate_for_input())
        except Exception:
            pass

    def go_menu(self):
        self.stack.setCurrentIndex(self.PAGE_MENU)

    # ===================== Dirty/Reset ======================
    def mark_dirty(self):
        if self._suppress_dirty:
            return
        self.is_dirty = True
        self._update_window_title()

    def has_any_data(self) -> bool:
        if self.is_dirty:
            return True
        if self.current_image_path:
            return True
        if self.header_data and any((v or "").strip() for v in self.header_data.values()):
            return True

        def _has_real_rows(items) -> bool:
            for row in items:
                if any(str(v).strip() for v in row.values()):
                    return True
            return False

        if _has_real_rows(self.fabric_items) or _has_real_rows(self.trim_items):
            return True
        return False

    def reset_work_order_form(self):
        self._suppress_dirty = True
        try:
            self.header_data = {}
            self.fabric_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
            self.trim_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
            self.image_preview.clear_image()
            self.current_image_path = None
            self.btn_delete_image.setEnabled(False)
            self.is_dirty = False
            self._refresh_postits()
            self._clear_feedback()
            self._update_window_title()
            try:
                self.change_note_postit.set_text("")
            except Exception:
                pass
        finally:
            self._suppress_dirty = False

    # ===================== Post-its refresh ======================
    def _refresh_postits(self, force_rebuild: bool = False):
        self.postit_bar.set_data(
            header=self.header_data,
            fabrics=self.fabric_items,
            trims=self.trim_items,
            force_rebuild=force_rebuild,
        )
        if hasattr(self, "change_note_postit"):
            note = (self.header_data or {}).get("change_note", "")
            self.change_note_postit.set_text(note)

    # ===================== Basic/Fabric/Trim add/delete ======================
    def on_add_basic_clicked(self):
        dlg = BasicInfoDialog(initial=self.header_data, parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        self.header_data = dlg.get_data()
        self.mark_dirty()
        self._refresh_postits()



    def on_fabric_deleted(self, idx: int):
        if 0 <= idx < len(self.fabric_items):
            del self.fabric_items[idx]
            self.mark_dirty()
            self._refresh_postits()

    def on_trim_deleted(self, idx: int):
        if 0 <= idx < len(self.trim_items):
            del self.trim_items[idx]
            self.mark_dirty()
            self._refresh_postits()

    # ===================== Back/Reset/Save ======================
    def on_reset_clicked(self):
        self.reset_work_order_form()

    def on_back_clicked(self):
        if not self.has_any_data():
            self.go_menu()
            return

        dialog = ConfirmActionDialog(
            title="임시 저장",
            message="임시 저장 하시겠습니까?",
            confirm_text="예",
            cancel_text="아니요",
            parent=self,
        )
        result = dialog.exec()

        if result == QDialog.Accepted:
            self.go_menu()
        else:
            self.reset_work_order_form()
            self.go_menu()

    def _is_nonempty(self, value) -> bool:
        return bool(str(value or "").strip())

    def _row_has_all_fields(self, row: dict) -> bool:
        required_keys = ("거래처", "품목", "수량", "단가", "총액")
        if not isinstance(row, dict):
            return False
        return all(self._is_nonempty(row.get(key, "")) for key in required_keys)

    def _has_basic_info(self) -> bool:
        required_keys = (
            "date",
            "style_no",
            "factory",
            "cost_display",
            "labor_display",
            "loss_display",
            "sale_price_display",
        )
        if not isinstance(self.header_data, dict):
            return False
        return all(self._is_nonempty(self.header_data.get(key, "")) for key in required_keys)

    def _has_fabric_info(self) -> bool:
        return any(self._row_has_all_fields(row) for row in (self.fabric_items or []))

    def _has_trim_info(self) -> bool:
        return any(self._row_has_all_fields(row) for row in (self.trim_items or []))

    def _get_save_requirement_statuses(self):
        return [
            ("기본사항", self._has_basic_info()),
            ("원단정보 1개 이상", self._has_fabric_info()),
            ("부자재정보 1개 이상", self._has_trim_info()),
        ]

    def collect_work_order_data(self) -> dict:
        return {
            "header": self.header_data,
            "fabrics": self.fabric_items,
            "trims": self.trim_items,
            "image_attached": bool(self.current_image_path),
        }

    def on_save_clicked(self):
        statuses = self._get_save_requirement_statuses()
        if not all(ok for _, ok in statuses):
            ValidationStatusDialog("저장 불가", statuses, parent=self).exec()
            return

        data = self.collect_work_order_data()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        try:
            json_path, image_path, sha256_plain = save_work_order(
                base_dir=project_root,
                data=data,
                image_src_path=self.current_image_path,
            )
        except Exception as e:
            QMessageBox.warning(self, "저장 실패", str(e))
            return

        self.reset_work_order_form()

        msg = f"저장 완료\n\nJSON: {json_path}\nSHA256(평문): {sha256_plain}"
        if image_path:
            msg += f"\n이미지: {image_path}"
        QMessageBox.information(self, "저장", msg)


    # ===================== Inline post-it handlers ======================
    def on_basic_postit_changed(self, data: dict):
        if not isinstance(data, dict):
            return
        if not isinstance(self.header_data, dict):
            self.header_data = {}
        self.header_data.update(data)
        self.mark_dirty()

    def on_change_note_changed(self, text: str):
        if not isinstance(self.header_data, dict):
            self.header_data = {}
        self.header_data["change_note"] = (text or "").rstrip()
        self.mark_dirty()

    def on_fabric_postit_changed(self, idx: int, patch: dict):
        if not isinstance(patch, dict) or idx < 0:
            return
        if not hasattr(self, "fabric_items") or self.fabric_items is None:
            self.fabric_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
        while len(self.fabric_items) <= idx:
            self.fabric_items.append({"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""})
        self.fabric_items[idx].update(patch)
        self.mark_dirty()

    def on_trim_postit_changed(self, idx: int, patch: dict):
        if not isinstance(patch, dict) or idx < 0:
            return
        if not hasattr(self, "trim_items") or self.trim_items is None:
            self.trim_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
        while len(self.trim_items) <= idx:
            self.trim_items.append({"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""})
        self.trim_items[idx].update(patch)
        self.mark_dirty()

    # ===================== Image actions ======================
    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 선택",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not path:
            return
        try:
            self.image_preview.set_image(path)
            self.current_image_path = path
            if hasattr(self, "btn_delete_image"):
                self.btn_delete_image.setEnabled(True)
            self.mark_dirty()
            self._show_feedback("이미지 첨부됨")
        except Exception as e:
            QMessageBox.warning(self, "오류", str(e))

    def delete_image(self):
        try:
            self.image_preview.clear_image()
        except Exception:
            pass
        self.current_image_path = None
        if hasattr(self, "btn_delete_image"):
            self.btn_delete_image.setEnabled(False)
        self.mark_dirty()
        self._show_feedback("이미지 제거됨")

    # ===================== Add fabric/trim cards ======================
    def on_add_fabric_clicked(self):
        if not hasattr(self, "fabric_items") or self.fabric_items is None:
            self.fabric_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
        self.fabric_items = list(self.fabric_items)
        if len(self.fabric_items) >= 9:
            return
        self.fabric_items.append({"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""})
        try:
            self._refresh_postits()
            self.postit_bar.fabric.set_active_card(len(self.fabric_items) - 1)
        except Exception:
            pass
        self.mark_dirty()

    def on_add_trim_clicked(self):
        if not hasattr(self, "trim_items") or self.trim_items is None:
            self.trim_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
        self.trim_items = list(self.trim_items)
        if len(self.trim_items) >= 9:
            return
        self.trim_items.append({"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""})
        try:
            self._refresh_postits()
            self.postit_bar.trim.set_active_card(len(self.trim_items) - 1)
        except Exception:
            pass
        self.mark_dirty()
