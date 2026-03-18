from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.layout_metrics import MenuLayout
from ui.messages import DialogTitles, MenuPageTexts
from ui.pages.common import (
    apply_secondary_button_metrics,
    make_page_text_header,
    make_standard_action_row,
    make_standard_body_row,
    make_standard_page_layout,
)
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
    metric_value_labels: dict[str, QLabel] = field(default_factory=dict)
    recent_template_labels: list[tuple[QLabel, QLabel, QLabel]] = field(default_factory=list)
    recent_activity_labels: list[tuple[QLabel, QLabel, QLabel]] = field(default_factory=list)


class MenuPageBuilder:
    @staticmethod
    def _make_menu_card(title: str, subtitle: str) -> QPushButton:
        button = QPushButton(f'{title}\n{subtitle}')
        button.setObjectName('menuActionCard')
        apply_button_metrics(
            button,
            width=THEME.menu_button_width,
            height=THEME.menu_button_height + MenuLayout.CARD_HEIGHT_EXTRA,
            font_px=THEME.base_font_px + 1,
        )
        return button

    @staticmethod
    def _make_metric_card(page: QWidget, title: str) -> tuple[QFrame, QLabel]:
        card = make_panel_frame(page, object_name='menuMetricCard')
        card.setMinimumHeight(THEME.dashboard_metric_card_min_height)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            THEME.dashboard_metric_padding_x,
            THEME.dashboard_metric_padding_y,
            THEME.dashboard_metric_padding_x,
            THEME.dashboard_metric_padding_y,
        )
        layout.setSpacing(THEME.dashboard_metric_spacing)

        title_label = make_hint_label(title, card, word_wrap=False)
        title_label.setObjectName('menuMetricTitle')
        value_label = QLabel('0', card)
        value_label.setObjectName('menuMetricValue')
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    @staticmethod
    def _make_recent_panel(page: QWidget, title: str) -> tuple[QFrame, list[tuple[QLabel, QLabel, QLabel]]]:
        panel = make_panel_frame(page, object_name='menuRecentPanel')
        panel.setMinimumHeight(THEME.dashboard_recent_panel_min_height)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            THEME.dashboard_recent_padding,
            THEME.dashboard_recent_padding,
            THEME.dashboard_recent_padding,
            THEME.dashboard_recent_padding,
        )
        layout.setSpacing(THEME.dashboard_recent_spacing)

        layout.addWidget(make_panel_title_label(title, panel))

        rows: list[tuple[QLabel, QLabel, QLabel]] = []
        for _ in range(5):
            row = QWidget(panel)
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(THEME.dashboard_recent_item_spacing)

            primary = QLabel('-', row)
            primary.setObjectName('menuListPrimary')
            secondary = QLabel('표시할 데이터가 없습니다.', row)
            secondary.setObjectName('menuListSecondary')
            tertiary = QLabel('', row)
            tertiary.setObjectName('menuListTertiary')

            row_layout.addWidget(primary)
            row_layout.addWidget(secondary)
            row_layout.addWidget(tertiary)
            layout.addWidget(row)
            rows.append((primary, secondary, tertiary))

        layout.addStretch(1)
        return panel, rows

    @staticmethod
    def build() -> MenuPageRefs:
        page = QWidget()
        page.setObjectName('workOrderPage')
        layout = make_standard_page_layout(page)
        layout.setContentsMargins(
            THEME.page_padding_x + MenuLayout.PAGE_MARGIN_X_OFFSET,
            MenuLayout.PAGE_MARGIN_TOP,
            THEME.page_padding_x + MenuLayout.PAGE_MARGIN_X_OFFSET,
            MenuLayout.PAGE_MARGIN_BOTTOM,
        )

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

        metric_titles = ('총 작업지시서', '진행중 발주', '미검수 건수', '현재고 합계')
        metrics_row = QGridLayout()
        metrics_row.setHorizontalSpacing(THEME.section_gap)
        metrics_row.setVerticalSpacing(THEME.section_gap)
        metric_value_labels: dict[str, QLabel] = {}
        for index, title in enumerate(metric_titles):
            card, value_label = MenuPageBuilder._make_metric_card(page, title)
            metrics_row.addWidget(card, 0, index)
            metric_value_labels[title] = value_label
        layout.addLayout(metrics_row)

        recent_row = make_standard_body_row()
        recent_templates_panel, recent_template_labels = MenuPageBuilder._make_recent_panel(page, '최근 작업지시서')
        recent_activity_panel, recent_activity_labels = MenuPageBuilder._make_recent_panel(page, '최근 처리 내역')
        recent_row.addWidget(recent_templates_panel, 1)
        recent_row.addWidget(recent_activity_panel, 1)
        layout.addLayout(recent_row)

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

        bottom_row = make_standard_action_row()
        bottom_row.addStretch(1)
        btn_data_reset = make_action_button(
            DialogTitles.DATA_RESET,
            page,
            width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA,
            height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA,
        )
        btn_partner_mgmt = make_action_button(
            DialogTitles.PARTNER_MANAGE,
            page,
            width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA,
            height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA,
        )
        btn_unit_mgmt = make_action_button(
            DialogTitles.UNIT_MANAGE,
            page,
            width=THEME.footer_button_width,
            height=THEME.footer_button_height + MenuLayout.FOOTER_BUTTON_HEIGHT_EXTRA,
        )
        apply_secondary_button_metrics(btn_data_reset, width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA)
        apply_secondary_button_metrics(btn_partner_mgmt, width=THEME.footer_button_width + MenuLayout.FOOTER_PRIMARY_WIDTH_EXTRA)
        apply_secondary_button_metrics(btn_unit_mgmt, width=THEME.footer_button_width)

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
