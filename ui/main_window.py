# ui/main_window.py
import os
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
    QStackedWidget,
)

from ui.header_group import HeaderGroup
from ui.image_preview import ImagePreview
from services.storage import save_work_order
from ui.unit_dialog import UnitDialog

from ui.material_item_dialog import MaterialItemDialog
from ui.postit_widgets import BasicInfoPostIt, PostItStack


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1

    def __init__(self):
        super().__init__()

        # ✅ 앱 타이틀 변경
        self.setWindowTitle("미니노트 다이어리")
        self.menuBar().hide()

        self.is_dirty = False
        self._suppress_dirty = False
        self.current_image_path: Optional[str] = None

        # ✅ 테이블 대신 리스트로 관리
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

        self.setMinimumSize(1280, 820)
        self.resize(1280, 820)

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

        # Top bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.btn_back = QPushButton("← 뒤로가기")
        self.btn_reset = QPushButton("초기화")
        self.btn_save = QPushButton("저장")

        for b in (self.btn_back, self.btn_reset, self.btn_save):
            b.setFixedHeight(32)

        self.btn_back.clicked.connect(self.on_back_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)

        top_bar.addWidget(self.btn_back)
        top_bar.addWidget(self.btn_reset)
        top_bar.addWidget(self.btn_save)
        top_bar.addStretch(1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)

        # Left
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(12)

        self.header = HeaderGroup()

        # ✅ 테이블 대신 버튼 + 설명
        self.btn_add_fabric = QPushButton("+ 원단 정보 추가")
        self.btn_add_trim = QPushButton("+ 부자재 정보 추가")
        self.btn_add_fabric.setFixedHeight(36)
        self.btn_add_trim.setFixedHeight(36)

        hint = QLabel("원단/부자재는 추가 버튼을 눌러 팝업에서 입력합니다.\n입력된 항목은 오른쪽 이미지 아래 포스트잇으로 쌓입니다.")
        hint.setStyleSheet("color: #666;")
        hint.setWordWrap(True)

        left_layout.addWidget(self.header)
        left_layout.addWidget(self.btn_add_fabric)
        left_layout.addWidget(self.btn_add_trim)
        left_layout.addWidget(hint)
        left_layout.addStretch(1)

        # Right
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_upload = QPushButton("사진 업로드")
        self.btn_delete_image = QPushButton("사진 삭제")
        self.btn_delete_image.setEnabled(False)
        self.btn_upload.setFixedHeight(32)
        self.btn_delete_image.setFixedHeight(32)
        btn_row.addWidget(self.btn_upload)
        btn_row.addWidget(self.btn_delete_image)
        btn_row.addStretch(1)

        self.image_preview = ImagePreview()
        self.image_preview.setMinimumHeight(520)

        # ✅ 포스트잇 영역(1열)
        self.postit_basic = BasicInfoPostIt()
        self.postit_fabric_stack = PostItStack(kind="fabric")
        self.postit_trim_stack = PostItStack(kind="trim")

        right_layout.addLayout(btn_row)
        right_layout.addWidget(self.image_preview, 1)
        right_layout.addWidget(self.postit_basic, 0)
        right_layout.addWidget(self.postit_fabric_stack, 0)
        right_layout.addWidget(self.postit_trim_stack, 0)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([780, 500])
        left.setMinimumWidth(720)
        right.setMinimumWidth(420)

        page_layout.addLayout(top_bar)
        page_layout.addWidget(splitter, 1)

        # signals
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)
        self.btn_add_fabric.clicked.connect(self.on_add_fabric_clicked)
        self.btn_add_trim.clicked.connect(self.on_add_trim_clicked)

        self._wire_dirty_signals()

        self.header.date.setDate(QDate.currentDate())
        self._refresh_postits()

        # delete handlers from stacks
        self.postit_fabric_stack.item_deleted.connect(self.on_fabric_deleted)
        self.postit_trim_stack.item_deleted.connect(self.on_trim_deleted)

        return page

    def _wire_dirty_signals(self):
        self.header.style_no.textChanged.connect(self.mark_dirty)
        self.header.factory.textChanged.connect(self.mark_dirty)
        self.header.cost.textChanged.connect(self.mark_dirty)
        self.header.labor.textChanged.connect(self.mark_dirty)
        self.header.loss.textChanged.connect(self.mark_dirty)
        self.header.sale_price.textChanged.connect(self.mark_dirty)
        self.header.date.dateChanged.connect(self.on_header_changed)

    def on_header_changed(self, *args):
        self.mark_dirty()
        self._refresh_postits()

    # ===================== Navigation ======================
    def go_work_order(self):
        self.stack.setCurrentIndex(self.PAGE_WORK_ORDER)

    def go_menu(self):
        self.stack.setCurrentIndex(self.PAGE_MENU)

    # ===================== Dirty/Reset ======================
    def mark_dirty(self, *args):
        if self._suppress_dirty:
            return
        self.is_dirty = True

    def has_any_data(self) -> bool:
        if self.is_dirty:
            return True
        if self.current_image_path:
            return True

        # header
        if (
            self.header.style_no.text().strip()
            or self.header.factory.text().strip()
            or self.header.cost.text().strip()
            or self.header.labor.text().strip()
            or self.header.loss.text().strip()
            or self.header.sale_price.text().strip()
        ):
            return True

        # materials
        if self.fabric_items or self.trim_items:
            return True

        return False

    def reset_work_order_form(self):
        self._suppress_dirty = True
        try:
            self.header.style_no.clear()
            self.header.factory.clear()
            self.header.cost.clear()
            self.header.labor.clear()
            self.header.loss.clear()
            self.header.sale_price.clear()
            self.header.date.setDate(QDate.currentDate())

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
        header = self.header.get_data()
        self.postit_basic.set_header_data(header)
        self.postit_fabric_stack.set_items(self.fabric_items)
        self.postit_trim_stack.set_items(self.trim_items)

    # ===================== Materials add/delete ======================
    def on_add_fabric_clicked(self):
        dlg = MaterialItemDialog(title="원단 정보 추가", parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        item = dlg.get_item()
        self.fabric_items.append(item)
        self.mark_dirty()
        self._refresh_postits()

    def on_add_trim_clicked(self):
        dlg = MaterialItemDialog(title="부자재 정보 추가", parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        item = dlg.get_item()
        self.trim_items.append(item)
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
            # 현재 프로젝트는 임시저장을 실제로 저장하지 않음(기존 동작 유지)
            self.go_menu()
        elif clicked == no_btn:
            self.reset_work_order_form()
            self.go_menu()

    def collect_work_order_data(self) -> dict:
        header = self.header.get_data()
        return {
            "header": header,
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