from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme import THEME
from ui.widget_factory import apply_button_metrics, make_action_button, make_page_title_label, make_hint_label


@dataclass
class MenuPageRefs:
    page: QWidget
    btn_template: QPushButton
    btn_job_start: QPushButton
    btn_receipt: QPushButton
    btn_complete: QPushButton
    btn_sale: QPushButton
    btn_inventory: QPushButton
    btn_partner_mgmt: QPushButton
    btn_unit_mgmt: QPushButton


class MenuPageBuilder:
    @staticmethod
    def _make_menu_card(title: str, subtitle: str) -> QPushButton:
        button = QPushButton(f'{title}\n{subtitle}')
        button.setObjectName('menuActionCard')
        apply_button_metrics(button, width=THEME.menu_button_width, height=THEME.menu_button_height + 18, font_px=THEME.base_font_px + 1)
        return button

    @staticmethod
    def build() -> MenuPageRefs:
        page = QWidget()
        page.setObjectName('workOrderPage')
        layout = QVBoxLayout(page)
        layout.setContentsMargins(THEME.page_padding_x + 4, 22, THEME.page_padding_x + 4, 18)
        layout.setSpacing(THEME.section_gap)

        title = make_page_title_label('업무 메뉴', page)
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName('menuHeroTitle')
        subtitle = make_hint_label('작업지시서 관리부터 작업 시작, 영수증 등록, 판매/재고 확인까지 흐름 기준으로 화면을 구성합니다.', page)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName('menuHeroSubtitle')
        layout.addWidget(title)
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(THEME.section_gap)
        grid.setVerticalSpacing(THEME.section_gap)

        btn_template = MenuPageBuilder._make_menu_card('작업지시서 관리', '기준 문서 생성 · 수정')
        btn_job_start = MenuPageBuilder._make_menu_card('발주', '템플릿 선택 후 발주 수량 입력')
        btn_receipt = MenuPageBuilder._make_menu_card('원단/부자재 등록', '영수증 첨부 · 실제 지출 기록')
        btn_complete = MenuPageBuilder._make_menu_card('작업 완료', '완료 수량 반영 · 재고 생성')
        btn_sale = MenuPageBuilder._make_menu_card('판매 등록', '판매 수량 · 수입 반영')
        btn_inventory = MenuPageBuilder._make_menu_card('재고 / 통계', '재고 현황 · 월별 흐름 확인')

        cards = [
            btn_template, btn_job_start, btn_receipt,
            btn_complete, btn_sale, btn_inventory,
        ]
        for index, button in enumerate(cards):
            grid.addWidget(button, index // 3, index % 3)

        layout.addLayout(grid)
        layout.addStretch(1)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        btn_partner_mgmt = make_action_button('거래처 관리', page, width=THEME.footer_button_width + 10, height=THEME.footer_button_height + 2)
        btn_unit_mgmt = make_action_button('단위 관리', page, width=THEME.footer_button_width, height=THEME.footer_button_height + 2)
        bottom_row.addWidget(btn_partner_mgmt)
        bottom_row.addSpacing(THEME.row_spacing)
        bottom_row.addWidget(btn_unit_mgmt)
        layout.addLayout(bottom_row)

        return MenuPageRefs(
            page=page,
            btn_template=btn_template,
            btn_job_start=btn_job_start,
            btn_receipt=btn_receipt,
            btn_complete=btn_complete,
            btn_sale=btn_sale,
            btn_inventory=btn_inventory,
            btn_partner_mgmt=btn_partner_mgmt,
            btn_unit_mgmt=btn_unit_mgmt,
        )