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
)

from ui.image_preview import ImagePreview
from services.storage import save_work_order
from ui.unit_dialog import UnitDialog

from ui.basic_info_dialog import BasicInfoDialog
from ui.material_item_dialog import MaterialItemDialog
from ui.postit_widgets import PostItBar


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
        self.fabric_items: List[Dict[str, str]] = []
        self.trim_items: List[Dict[str, str]] = []

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

        # 화면을 전체적으로 줄임(요청: 이미지 중심 단일 화면)
        self.setMinimumSize(980, 720)
        self.resize(980, 720)

    # ===================== Menu Page ======================
    def _build_page_menu(self) -> QWidget:
        page = QWidget()
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
        page_layout.setContentsMargins(18, 18, 18, 18)
        page_layout.setSpacing(12)

        # 1) 이미지 영역 "위" 버튼들: 뒤로가기/초기화/저장/사진업로드/사진삭제
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.btn_back = QPushButton("← 뒤로가기")
        self.btn_reset = QPushButton("초기화")
        self.btn_save = QPushButton("저장")
        self.btn_upload = QPushButton("사진 업로드")
        self.btn_delete_image = QPushButton("사진 삭제")
        self.btn_delete_image.setEnabled(False)

        for b in (self.btn_back, self.btn_reset, self.btn_save, self.btn_upload, self.btn_delete_image):
            b.setFixedHeight(32)

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        top_bar.addWidget(self.btn_back)
        top_bar.addWidget(self.btn_reset)
        top_bar.addWidget(self.btn_save)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.btn_upload)
        top_bar.addWidget(self.btn_delete_image)
        top_bar.addStretch(1)

        # 2) 이미지 영역
        self.image_preview = ImagePreview()
        self.image_preview.setMinimumHeight(440)

        # 3) 이미지 영역 "아래" 버튼들: 기본/원단/부자재 추가
        bottom_btn_row = QHBoxLayout()
        bottom_btn_row.setSpacing(10)

        self.btn_add_basic = QPushButton("기본정보 추가/수정")
        self.btn_add_fabric = QPushButton("원단정보 추가")
        self.btn_add_trim = QPushButton("부자재정보 추가")

        for b in (self.btn_add_basic, self.btn_add_fabric, self.btn_add_trim):
            b.setFixedHeight(36)

        self.btn_add_basic.clicked.connect(self.on_add_basic_clicked)
        self.btn_add_fabric.clicked.connect(self.on_add_fabric_clicked)
        self.btn_add_trim.clicked.connect(self.on_add_trim_clicked)

        bottom_btn_row.addWidget(self.btn_add_basic)
        bottom_btn_row.addWidget(self.btn_add_fabric)
        bottom_btn_row.addWidget(self.btn_add_trim)
        bottom_btn_row.addStretch(1)

        # 4) 포스트잇 바(기본/원단/부자재)
        self.postit_bar = PostItBar()
        self.postit_bar.fabric_deleted.connect(self.on_fabric_deleted)
        self.postit_bar.trim_deleted.connect(self.on_trim_deleted)
        self.postit_bar.basic_edit_requested.connect(self.on_add_basic_clicked)

        page_layout.addLayout(top_bar)
        page_layout.addWidget(self.image_preview, 1)
        page_layout.addLayout(bottom_btn_row)
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
            self.fabric_items = []
            self.trim_items = []

            self.image_preview.clear()
            self.image_preview.setText("이미지 업로드 영역")
            self.current_image_path = None
            self.btn_delete_image.setEnabled(False)

            self.is_dirty = False
            self._refresh_postits()
        finally:
            self._suppress_dirty = False

    # ===================== Post-its refresh ======================
    def _refresh_postits(self):
        self.postit_bar.set_data(
            header=self.header_data,
            fabrics=self.fabric_items,
            trims=self.trim_items,
        )

    # ===================== Basic/Fabric/Trim add/delete ======================
    def on_add_basic_clicked(self):
        dlg = BasicInfoDialog(initial=self.header_data, parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        self.header_data = dlg.get_data()
        self.mark_dirty()
        self._refresh_postits()

    def on_add_fabric_clicked(self):
        dlg = MaterialItemDialog(title="원단 정보 추가", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        self.fabric_items.append(dlg.get_item())
        self.mark_dirty()
        self._refresh_postits()

    def on_add_trim_clicked(self):
        dlg = MaterialItemDialog(title="부자재 정보 추가", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        self.trim_items.append(dlg.get_item())
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

    def collect_work_order_data(self) -> dict:
        return {
            "header": self.header_data,
            "fabrics": self.fabric_items,
            "trims": self.trim_items,
            "image_attached": bool(self.current_image_path),
        }

    def on_save_clicked(self):
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

    # ===================== Image actions ======================
    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return
        try:
            self.image_preview.set_image(path)
            self.current_image_path = path
            self.btn_delete_image.setEnabled(True)
            self.mark_dirty()
        except Exception as e:
            QMessageBox.warning(self, "오류", str(e))

    def delete_image(self):
        self.image_preview.clear()
        self.image_preview.setText("이미지 업로드 영역")
        self.current_image_path = None
        self.btn_delete_image.setEnabled(False)
        self.mark_dirty()