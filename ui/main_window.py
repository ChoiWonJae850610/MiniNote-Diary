# ui/main_window.py
import os
from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
    QStackedWidget,
    QDialog,
    QTextEdit,
    QStyle,
)

from ui.image_preview import ImagePreview
from services.storage import save_work_order
from ui.unit_dialog import UnitDialog
from ui.basic_info_dialog import BasicInfoDialog
from ui.material_item_dialog import MaterialItemDialog
from ui.postit_widgets import PostItBar, ChangeNotePostIt
class _ChangeNoteDialog(QDialog):
    def __init__(self, initial_text: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("수정사항")
        self.setModal(True)
        self.setMinimumSize(520, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.edit = QTextEdit(self)
        self.edit.setPlainText(initial_text or "")
        self.edit.setPlaceholderText("수정사항을 입력하세요.")
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

    def _apply_diary_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #F7F2EA;
                color: #4B4036;
                font-size: 12px;
            }
            QWidget#workOrderPage {
                background: #F7F2EA;
            }
            QLabel {
                color: #4B4036;
            }
            QPushButton {
                background: #FFF9F1;
                color: #5A4B40;
                border: 1px solid #DCCBBB;
                border-radius: 14px;
                padding: 0 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #FFF4E6;
                border-color: #CDB9A6;
            }
            QPushButton:pressed {
                background: #F3E4D4;
            }
            QPushButton:disabled {
                background: #EEE7DE;
                color: #A39587;
                border-color: #E1D7CC;
            }
            QPushButton#navButton {
                min-width: 44px;
                max-width: 44px;
                border-radius: 16px;
                padding: 0;
                background: #FFF9F1;
            }
            QPushButton#primaryAction {
                background: #EEDCCB;
                border-color: #D4BBA5;
                color: #5E4A3C;
            }
            QPushButton#primaryAction:hover {
                background: #E7D1BD;
            }
            QPushButton#dangerSoft {
                background: #F5F0EB;
                color: #9B8674;
            }
            QWidget#imageShell {
                background: #F3ECE4;
                border: 1px solid #E2D6C9;
                border-radius: 22px;
            }
            QWidget#noteShell {
                background: transparent;
                border: none;
            }
        """)

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
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

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

        # 상단 바: 왼쪽(뒤로/초기화/저장), 오른쪽(사진 업로드/삭제)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.btn_back = QPushButton("")
        self.btn_back.setObjectName("navButton")
        self.btn_reset = QPushButton("초기화")
        self.btn_save = QPushButton("저장")
        self.btn_save.setObjectName("primaryAction")

        self.btn_upload = QPushButton("사진 업로드")
        self.btn_delete_image = QPushButton("사진 삭제")
        self.btn_delete_image.setObjectName("dangerSoft")
        self.btn_delete_image.setEnabled(False)

        for b in (self.btn_back, self.btn_reset, self.btn_save, self.btn_upload, self.btn_delete_image):
            b.setFixedHeight(32)

        # 뒤로가기: 아이콘-only 버튼
        self.btn_back.setFixedWidth(44)
        back_icon = self.style().standardIcon(QStyle.SP_ArrowBack)
        self.btn_back.setIcon(back_icon)
        self.btn_back.setToolTip("뒤로가기")

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        top_bar.addWidget(self.btn_back)
        top_bar.addWidget(self.btn_reset)
        top_bar.addWidget(self.btn_save)
        top_bar.addStretch(1)  # ✅ 오른쪽 상단 구석 정렬
        top_bar.addWidget(self.btn_upload)
        top_bar.addWidget(self.btn_delete_image)

        # 이미지 영역(왼쪽) + 수정사항 포스트잇(오른쪽)
        self.image_preview = ImagePreview()
        self.image_preview.setMinimumHeight(520)
        self.image_preview.setStyleSheet("background: transparent; border: none; color: #8F7F72;")

        self.image_shell = QWidget()
        self.image_shell.setObjectName("imageShell")
        image_shell_layout = QVBoxLayout(self.image_shell)
        image_shell_layout.setContentsMargins(18, 18, 18, 18)
        image_shell_layout.setSpacing(0)
        image_shell_layout.addWidget(self.image_preview)

        self.change_note_postit = ChangeNotePostIt()
        self.change_note_postit.text_changed.connect(self.on_change_note_changed)
        self.change_note_postit.setVisible(True)

        center_row = QWidget()
        center_layout = QHBoxLayout(center_row)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(12)

        center_layout.addWidget(self.image_shell, 3)
        center_layout.addWidget(self.change_note_postit, 1)
        # 포스트잇(정보 확인용) — 이미지 중심 느낌을 위해 높이를 과하게 먹지 않도록 제한
        self.postit_bar = PostItBar()
        self.postit_bar.setMaximumHeight(220)
        self.postit_bar.fabric_deleted.connect(self.on_fabric_deleted)
        self.postit_bar.trim_deleted.connect(self.on_trim_deleted)
        self.postit_bar.fabric_item_changed.connect(self.on_fabric_postit_changed)
        self.postit_bar.trim_item_changed.connect(self.on_trim_postit_changed)
        self.postit_bar.fabric_item_added.connect(self.on_add_fabric_clicked)
        self.postit_bar.trim_item_added.connect(self.on_add_trim_clicked)
        self.postit_bar.basic_data_changed.connect(self.on_basic_postit_changed)

        page_layout.addLayout(top_bar)
        page_layout.addWidget(center_row, 1)
        page_layout.addWidget(self.postit_bar, 0)

        self._refresh_postits()
        return page

    # ===================== Navigation ======================
    def go_work_order(self):
        self.stack.setCurrentIndex(self.PAGE_WORK_ORDER)

    def go_menu(self):
        self.stack.setCurrentIndex(self.PAGE_MENU)

    # ===================== Dirty/Reset ======================
    def mark_dirty(self):
        if self._suppress_dirty:
            return
        self.is_dirty = True

    def has_any_data(self) -> bool:
        if self.is_dirty:
            return True
        if self.current_image_path:
            return True
        if self.header_data and any((v or "").strip() for v in self.header_data.values()):
            return True
        if self.fabric_items or self.trim_items:
            return True
        return False

    def reset_work_order_form(self):
        self._suppress_dirty = True
        try:
            self.header_data = {}
            self.fabric_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
            self.trim_items = [{"거래처":"", "품목":"", "수량":"", "단위":"", "단가":"", "총액":""}]
            self.image_preview.clear()
            self.image_preview.setText("이미지 업로드 영역")
            self.current_image_path = None
            self.btn_delete_image.setEnabled(False)
            self.is_dirty = False
            self._refresh_postits()
            try:
                self.change_note_postit.set_text("")
            except Exception:
                pass
        finally:
            self._suppress_dirty = False

    # ===================== Post-its refresh ======================
    def _refresh_postits(self):
        self.postit_bar.set_data(
            header=self.header_data,
            fabrics=self.fabric_items,
            trims=self.trim_items,
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

        box = QMessageBox(self)
        box.setWindowTitle("임시 저장")
        box.setText("임시 저장 하시겠습니까?")
        yes_btn = box.addButton("예", QMessageBox.YesRole)
        no_btn = box.addButton("아니요", QMessageBox.NoRole)
        box.setIcon(QMessageBox.Question)
        box.exec()

        clicked = box.clickedButton()
        if clicked == yes_btn:
            self.go_menu()
        elif clicked == no_btn:
            self.reset_work_order_form()
            self.go_menu()

    def _has_basic_info(self) -> bool:
        return bool(self.header_data) and any((v or "").strip() for v in self.header_data.values())

    def _has_fabric_info(self) -> bool:
        return len(self.fabric_items) > 0

    def _has_trim_info(self) -> bool:
        return len(self.trim_items) > 0

    def collect_work_order_data(self) -> dict:
        return {
            "header": self.header_data,
            "fabrics": self.fabric_items,
            "trims": self.trim_items,
            "image_attached": bool(self.current_image_path),
        }

    def on_save_clicked(self):
        # ✅ 저장 조건: 기본정보/원단/부자재가 모두 있을 때만
        if not (self._has_basic_info() and self._has_fabric_info() and self._has_trim_info()):
            QMessageBox.warning(
                self,
                "저장 불가",
                "기본정보 / 원단 정보 / 부자재 정보가 모두 입력된 경우에만 저장할 수 있습니다.",
            )
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
        except Exception as e:
            QMessageBox.warning(self, "오류", str(e))

    def delete_image(self):
        try:
            self.image_preview.clear()
            self.image_preview.setText("이미지 업로드 영역")
        except Exception:
            pass
        self.current_image_path = None
        if hasattr(self, "btn_delete_image"):
            self.btn_delete_image.setEnabled(False)
        self.mark_dirty()

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

