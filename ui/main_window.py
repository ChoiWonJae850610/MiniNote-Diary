# ui/main_window.py
import os

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
    QTableWidget,
)
from PySide6.QtCore import Qt, QDate

from ui.header_group import HeaderGroup
from ui.fabric_table import FabricTable
from ui.trims_table import TrimsTable
from ui.image_preview import ImagePreview
from services.storage import save_work_order
from ui.unit_dialog import UnitDialog


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORK_ORDER = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle("작업지시서 관리 시스템")

        # ✅ maximize 제거 + resize 금지(고정 사이즈)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.menuBar().hide()

        self.is_dirty = False
        self._suppress_dirty = False
        self.current_image_path = None

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

        # ✅ 시작은 메뉴
        self.stack.setCurrentIndex(self.PAGE_MENU)

        # ✅ 강제 고정 사이즈 (테이블 줄인 버전 기준)
        W, H = 1100, 600
        self.page_menu.setMinimumSize(W, H)
        self.page_work_order.setMinimumSize(W, H)
        self.resize(W, H)
        self.setFixedSize(W, H)

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
        page_layout.setContentsMargins(16, 16, 16, 16)
        page_layout.setSpacing(10)

        top_bar = QHBoxLayout()

        self.btn_back = QPushButton("← 뒤로가기")
        self.btn_back.setFixedHeight(30)
        self.btn_back.clicked.connect(self.on_back_clicked)

        self.btn_reset = QPushButton("초기화")
        self.btn_reset.setFixedHeight(30)
        self.btn_reset.clicked.connect(self.on_reset_clicked)

        self.btn_save = QPushButton("저장")
        self.btn_save.setFixedHeight(30)
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
        left_layout.setSpacing(10)

        self.header = HeaderGroup()
        self.fabric = FabricTable("원단")
        self.trims = TrimsTable("부자재 + 외주작업")

        left_layout.addWidget(self.header)
        left_layout.addWidget(self.fabric)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.trims)

        # Right
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(8)

        self.image_preview = ImagePreview()
        self.image_preview.setMinimumHeight(260)

        btn_row = QHBoxLayout()
        self.btn_upload = QPushButton("사진 업로드")
        self.btn_delete_image = QPushButton("사진 삭제")
        self.btn_delete_image.setEnabled(False)
        self.btn_upload.setFixedHeight(28)
        self.btn_delete_image.setFixedHeight(28)

        btn_row.addWidget(self.btn_upload)
        btn_row.addWidget(self.btn_delete_image)
        btn_row.addStretch(1)

        right_layout.addLayout(btn_row)
        right_layout.addWidget(self.image_preview, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([660, 360])

        page_layout.addLayout(top_bar)
        page_layout.addWidget(splitter, 1)

        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_delete_image.clicked.connect(self.delete_image)

        self._wire_dirty_signals()

        # ✅ 최초 진입 시 오늘 날짜
        self.header.date.setDate(QDate.currentDate())
        return page

    def _wire_dirty_signals(self):
        self.header.style_no.textChanged.connect(self.mark_dirty)
        self.header.factory.textChanged.connect(self.mark_dirty)

        # ✅ 금액 4종 dirty 연결 (원가/공임/로스/판매가)
        self.header.cost.textChanged.connect(self.mark_dirty)
        self.header.labor.textChanged.connect(self.mark_dirty)
        self.header.loss.textChanged.connect(self.mark_dirty)
        self.header.sale_price.textChanged.connect(self.mark_dirty)

        self.header.date.dateChanged.connect(self.mark_dirty)
        self.fabric.table.itemChanged.connect(self.mark_dirty)
        self.trims.table.itemChanged.connect(self.mark_dirty)

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

        # ✅ store 제거, cost/labor/loss/sale_price 추가
        if (
            self.header.style_no.text().strip()
            or self.header.factory.text().strip()
            or self.header.cost.text().strip()
            or self.header.labor.text().strip()
            or self.header.loss.text().strip()
            or self.header.sale_price.text().strip()
        ):
            return True

        if self._table_has_any_text(self.fabric.table) or self._table_has_any_text(
            self.trims.table
        ):
            return True
        return False

    def _table_has_any_text(self, table: QTableWidget) -> bool:
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                it = table.item(r, c)
                if it and it.text().strip():
                    return True
        return False

    def _clear_table_items(self, table: QTableWidget):
        table.blockSignals(True)
        try:
            table.clearContents()
        finally:
            table.blockSignals(False)

    def reset_work_order_form(self):
        self._suppress_dirty = True
        try:
            self.header.style_no.clear()
            self.header.factory.clear()

            # ✅ 금액 4종 초기화
            self.header.cost.clear()
            self.header.labor.clear()
            self.header.loss.clear()
            self.header.sale_price.clear()

            self.header.date.setDate(QDate.currentDate())

            self._clear_table_items(self.fabric.table)
            self._clear_table_items(self.trims.table)

            self.image_preview.clear()
            self.image_preview.setText("이미지 업로드 영역")
            self.current_image_path = None
            self.btn_delete_image.setEnabled(False)

            self.is_dirty = False
        finally:
            self._suppress_dirty = False

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
        header = self.header.get_data()
        fabric_cols = ["원단처", "원단이름", "요척", "단위", "단가", "토탈"]
        trims_cols = ["거래처", "품목", "수량", "단위", "단가", "토탈"]

        fabrics = self._table_to_dicts(self.fabric.table, fabric_cols)
        trims = self._table_to_dicts(self.trims.table, trims_cols)

        return {
            "header": header,
            "fabrics": fabrics,
            "trims": trims,
            "image_attached": bool(self.current_image_path),
        }

    def _table_to_dicts(self, table: QTableWidget, col_names):
        rows = []
        for r in range(table.rowCount()):
            row = {}
            empty = True
            for c, key in enumerate(col_names):
                it = table.item(r, c)
                val = it.text().strip() if it else ""
                if val:
                    empty = False
                row[key] = val
            if not empty:
                rows.append(row)
        return rows

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