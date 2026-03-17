from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.layout_metrics import MenuLayout
from ui.messages import DialogTitles, MenuPageTexts
from ui.pages.common import make_page_text_header, make_standard_page_layout
from ui.theme import THEME
from ui.widget_factory import apply_button_metrics, make_action_button, make_hint_label, make_panel_frame, make_panel_title_label


@dataclass
class MenuPageRefs:
    page: QWidget
    btn_template: QPushButton
    btn_job_start: QPushButton
    btn_receipt: QPushButton
    btn_complete: QPushButton
    btn_sale: QPushButton
    btn_inventory: QPushButton
    btn_data_reset: QPushButton
    btn_partner_mgmt: QPushButton
    btn_unit_mgmt: QPushButton
    metric_value_labels: dict[str, QLabel]
    recent_template_labels: list[tuple[QLabel, QLabel, QLabel]]
    recent_activity_labels: list[tuple[QLabel, QLabel, QLabel]]


class MenuPageBuilder:
    @staticmethod
    def _make_menu_card(title: str, subtitle: str) -> QPushButton:
        button = QPushButton(f'{title}\n{subtitle}')
        button.setObjectName('menuActionCard')
        apply_button_metrics(button, width=THEME.menu_button_width, height=THEME.menu_button_height + MenuLayout.CARD_HEIGHT_EXTRA, font_px=THEME.base_font_px + 1)
        return button

    @staticmethod
    def _make_metric_card(parent: QWidget, title: str) -> tuple[QFrame, QLabel]:
        card = make_panel_frame(parent, compact=False)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding - 2, THEME.page_section_padding, THEME.page_section_padding - 2)
        layout.setSpacing(6)

        title_label = make_hint_label(title, card, word_wrap=False)
        value_label = QLabel('0', card)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setObjectName('menuMetricValue')
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    @staticmethod
    def _make_line_item(parent: QWidget) -> tuple[QFrame, tuple[QLabel, QLabel, QLabel]]:
        card = make_panel_frame(parent, compact=True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        primary = QLabel('-', card)
        primary.setObjectName('menuListPrimary')
        secondary = QLabel('', card)
        secondary.setObjectName('menuListSecondary')
        secondary.setWordWrap(True)
        tertiary = QLabel('', card)
        tertiary.setObjectName('menuListTertiary')
        tertiary.setWordWrap(True)

        layout.addWidget(primary)
        layout.addWidget(secondary)
        layout.addWidget(tertiary)
        return card, (primary, secondary, tertiary)

    @staticmethod
    def build() -> MenuPageRefs:
        page = QWidget()
        page.setObjectName('workOrderPage')
        layout = make_standard_page_layout(page)
        layout.setContentsMargins(THEME.page_padding_x + MenuLayout.PAGE_MARGIN_X_OFFSET, MenuLayout.PAGE_MARGIN_TOP, THEME.page_padding_x + MenuLayout.PAGE_MARGIN_X_OFFSET, MenuLayout.PAGE_MARGIN_BOTTOM)

        hero_refs = make_page_text_header(
            page,
            title_text=MenuPageTexts.TITLE,
            subtitle_text='',
            title_object_name='menuHeroTitle',
            subtitle_object_name='menuHeroSubtitle',
            title_alignment=Qt.AlignCenter,
            subtitle_alignment=Qt.AlignCenter,
        )
        layout.addLayout(hero_refs.layout)

        metric_grid = QGridLayout()
        metric_grid.setHorizontalSpacing(THEME.section_gap)
        metric_grid.setVerticalSpacing(THEME.section_gap)
        metric_value_labels: dict[str, QLabel] = {}
        for index, title in enumerate(('총 작업지시서', '진행중 발주', '미검수 건수', '현재고 합계')):
            card, value_label = MenuPageBuilder._make_metric_card(page, title)
            metric_grid.addWidget(card, 0, index)
            metric_value_labels[title] = value_label
        layout.addLayout(metric_grid)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(THEME.section_gap)

        recent_template_panel = make_panel_frame(page)
        recent_template_layout = QVBoxLayout(recent_template_panel)
        recent_template_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        recent_template_layout.setSpacing(THEME.row_spacing)
        recent_template_layout.addWidget(make_panel_title_label('최근 작업지시서', recent_template_panel))
        recent_template_layout.addWidget(make_hint_label('최근 저장한 작업지시서 5건을 표시합니다.', recent_template_panel))
        recent_template_labels: list[tuple[QLabel, QLabel, QLabel]] = []
        for _ in range(5):
            item_card, item_labels = MenuPageBuilder._make_line_item(recent_template_panel)
            recent_template_layout.addWidget(item_card)
            recent_template_labels.append(item_labels)
        summary_row.addWidget(recent_template_panel, 1)

        recent_activity_panel = make_panel_frame(page)
        recent_activity_layout = QVBoxLayout(recent_activity_panel)
        recent_activity_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        recent_activity_layout.setSpacing(THEME.row_spacing)
        recent_activity_layout.addWidget(make_panel_title_label('최근 처리 내역', recent_activity_panel))
        recent_activity_layout.addWidget(make_hint_label('발주, 입고, 상품 수정 내역 중 최근 5건을 표시합니다.', recent_activity_panel))
        recent_activity_labels: list[tuple[QLabel, QLabel, QLabel]] = []
        for _ in range(5):
            item_card, item_labels = MenuPageBuilder._make_line_item(recent_activity_panel)
            recent_activity_layout.addWidget(item_card)
            recent_activity_labels.append(item_labels)
        summary_row.addWidget(recent_activity_panel, 1)

        layout.addLayout(summary_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(THEME.section_gap)
        grid.setVerticalSpacing(THEME.section_gap)

        btn_template = MenuPageBuilder._make_menu_card(MenuPageTexts.TEMPLATE_TITLE, MenuPageTexts.TEMPLATE_SUBTITLE)
        btn_job_start = MenuPageBuilder._make_menu_card(MenuPageTexts.ORDER_TITLE, MenuPageTexts.ORDER_SUBTITLE)
        btn_receipt = MenuPageBuilder._make_menu_card(MenuPageTexts.RECEIPT_TITLE, MenuPageTexts.RECEIPT_SUBTITLE)
        btn_receipt.hide()
        btn_complete = MenuPageBuilder._make_menu_card(MenuPageTexts.COMPLETE_TITLE, MenuPageTexts.COMPLETE_SUBTITLE)
        btn_sale = MenuPageBuilder._make_menu_card(MenuPageTexts.SALE_TITLE, MenuPageTexts.SALE_SUBTITLE)
        btn_inventory = MenuPageBuilder._make_menu_card(MenuPageTexts.INVENTORY_TITLE, MenuPageTexts.INVENTORY_SUBTITLE)

        for index, button in enumerate((btn_template, btn_job_start, btn_complete, btn_sale, btn_inventory)):
            grid.addWidget(button, index // 3, index % 3)

        layout.addLayout(grid)
        layout.addStretch(1)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        btn_data_reset = make_action_button(DialogTitles.DATA_RESET, page, width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA, height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA)
        btn_partner_mgmt = make_action_button(DialogTitles.PARTNER_MANAGE, page, width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA, height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA)
        btn_unit_mgmt = make_action_button(DialogTitles.UNIT_MANAGE, page, width=THEME.footer_button_width, height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA)
        bottom_row.addWidget(btn_data_reset)
        bottom_row.addSpacing(THEME.row_spacing)
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
            btn_data_reset=btn_data_reset,
            btn_partner_mgmt=btn_partner_mgmt,
            btn_unit_mgmt=btn_unit_mgmt,
            metric_value_labels=metric_value_labels,
            recent_template_labels=recent_template_labels,
            recent_activity_labels=recent_activity_labels,
        )
