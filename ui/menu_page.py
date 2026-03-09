from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme import THEME
from ui.widget_factory import apply_button_metrics


@dataclass
class MenuPageRefs:
    page: QWidget
    btn_create: QPushButton
    btn_receipt: QPushButton
    btn_status: QPushButton
    btn_vendor_mgmt: QPushButton
    btn_unit_mgmt: QPushButton


class MenuPageBuilder:
    @staticmethod
    def build() -> MenuPageRefs:
        page = QWidget()
        page.setObjectName('workOrderPage')
        layout = QVBoxLayout(page)
        layout.setContentsMargins(THEME.page_padding_x + 4, THEME.page_padding_y + 4, THEME.page_padding_x + 4, THEME.page_padding_y + 4)
        layout.setSpacing(0)

        center_col = QVBoxLayout()
        center_col.setSpacing(THEME.section_gap)
        title = QLabel('메인 메뉴')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f'font-size: {THEME.menu_title_font_px}px; font-weight: bold;')

        btn_create = QPushButton('작업지시서 생성')
        btn_receipt = QPushButton('부자재 영수증 업로드')
        btn_status = QPushButton('제품 제작 현황')
        for button in (btn_create, btn_receipt, btn_status):
            button.setFixedSize(THEME.menu_button_width, THEME.menu_button_height)

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
        btn_vendor_mgmt = QPushButton('거래처 관리')
        btn_unit_mgmt = QPushButton('단위 추가(관리)')
        apply_button_metrics(btn_vendor_mgmt, width=THEME.footer_button_width, height=THEME.footer_button_height)
        apply_button_metrics(btn_unit_mgmt, width=THEME.footer_button_width, height=THEME.footer_button_height)
        bottom_row.addWidget(btn_vendor_mgmt)
        bottom_row.addSpacing(THEME.row_spacing)
        bottom_row.addWidget(btn_unit_mgmt)
        layout.addLayout(bottom_row)

        return MenuPageRefs(
            page=page,
            btn_create=btn_create,
            btn_receipt=btn_receipt,
            btn_status=btn_status,
            btn_vendor_mgmt=btn_vendor_mgmt,
            btn_unit_mgmt=btn_unit_mgmt,
        )
