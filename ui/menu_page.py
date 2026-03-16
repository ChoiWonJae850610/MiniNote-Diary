from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QWidget

from ui.layout_metrics import MenuLayout
from ui.messages import DialogTitles, MenuPageTexts
from ui.pages.common import make_page_text_header, make_standard_page_layout
from ui.theme import THEME
from ui.widget_factory import apply_button_metrics, make_action_button


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
        apply_button_metrics(button, width=THEME.menu_button_width, height=THEME.menu_button_height + MenuLayout.CARD_HEIGHT_EXTRA, font_px=THEME.base_font_px + 1)
        return button

    @staticmethod
    def build() -> MenuPageRefs:
        page = QWidget()
        page.setObjectName('workOrderPage')
        layout = make_standard_page_layout(page)
        layout.setContentsMargins(THEME.page_padding_x + MenuLayout.PAGE_MARGIN_X_OFFSET, MenuLayout.PAGE_MARGIN_TOP, THEME.page_padding_x + MenuLayout.PAGE_MARGIN_X_OFFSET, MenuLayout.PAGE_MARGIN_BOTTOM)

        hero_refs = make_page_text_header(
            page,
            title_text=MenuPageTexts.TITLE,
            subtitle_text=MenuPageTexts.SUBTITLE,
            title_object_name='menuHeroTitle',
            subtitle_object_name='menuHeroSubtitle',
            title_alignment=Qt.AlignCenter,
            subtitle_alignment=Qt.AlignCenter,
        )
        layout.addLayout(hero_refs.layout)

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
        btn_partner_mgmt = make_action_button(DialogTitles.PARTNER_MANAGE, page, width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA, height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA)
        btn_unit_mgmt = make_action_button(DialogTitles.UNIT_MANAGE, page, width=THEME.footer_button_width, height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA)
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
