from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.layout_metrics import MenuLayout
from ui.messages import DialogTitles, MenuPageTexts
from ui.pages.common import make_standard_page_layout
from ui.theme import THEME
from ui.widget_factory import apply_button_metrics, make_hint_label, make_panel_frame, make_panel_title_label


@dataclass
class MenuPageRefs:
    page: QWidget
    btn_template: QPushButton
    btn_job_start: QPushButton
    btn_receipt: QPushButton
    btn_complete: QPushButton
    btn_sale: QPushButton
    btn_inventory: QPushButton
    btn_settings: QPushButton
    metric_value_labels: dict[str, QLabel] = field(default_factory=dict)
    recent_template_labels: list[tuple[QLabel, QLabel, QLabel]] = field(default_factory=list)
    recent_activity_labels: list[tuple[QLabel, QLabel, QLabel]] = field(default_factory=list)


class MenuPageBuilder:
    _WEEKDAY_MAP = {
        1: '월요일',
        2: '화요일',
        3: '수요일',
        4: '목요일',
        5: '금요일',
        6: '토요일',
        7: '일요일',
    }

    @staticmethod
    def _today_text() -> str:
        today = QDate.currentDate()
        weekday = MenuPageBuilder._WEEKDAY_MAP.get(today.dayOfWeek(), '')
        return f"{MenuPageTexts.DATE_PREFIX} · {today.toString('yyyy.MM.dd')} {weekday}"

    @staticmethod
    def _make_section_label(text: str, parent: QWidget) -> QLabel:
        label = QLabel(text, parent)
        label.setObjectName('menuSectionLabel')
        return label

    @staticmethod
    def _make_section_hint(text: str, parent: QWidget) -> QLabel:
        label = make_hint_label(text, parent, word_wrap=True)
        label.setObjectName('menuSectionHint')
        return label

    @staticmethod
    def _make_menu_card(title: str, subtitle: str, *, utility: bool = False) -> QPushButton:
        button = QPushButton(f'{title}\n{subtitle}')
        button.setObjectName('menuUtilityCard' if utility else 'menuActionCard')
        button.setMinimumHeight(THEME.menu_action_card_min_height)
        button.setCursor(Qt.PointingHandCursor)
        apply_button_metrics(button, font_px=THEME.base_font_px + 1, bold=True)
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
    def _make_recent_panel(page: QWidget, title: str, empty_text: str) -> tuple[QFrame, list[tuple[QLabel, QLabel, QLabel]]]:
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
        for _ in range(THEME.menu_recent_row_count):
            row = QWidget(panel)
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(THEME.dashboard_recent_item_spacing)

            primary = QLabel('-', row)
            primary.setObjectName('menuListPrimary')
            secondary = QLabel(empty_text, row)
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
    def _make_section_panel(page: QWidget, title: str, subtitle: str) -> tuple[QFrame, QVBoxLayout]:
        panel = make_panel_frame(page, object_name='menuSectionPanel')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            THEME.menu_section_padding,
            THEME.menu_section_padding,
            THEME.menu_section_padding,
            THEME.menu_section_padding,
        )
        layout.setSpacing(THEME.menu_section_spacing)
        layout.addWidget(MenuPageBuilder._make_section_label(title, panel))
        layout.addWidget(MenuPageBuilder._make_section_hint(subtitle, panel))
        return panel, layout

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
        layout.setSpacing(THEME.section_gap)

        hero_panel = make_panel_frame(page, object_name='menuHeroPanel')
        hero_layout = QVBoxLayout(hero_panel)
        hero_layout.setContentsMargins(
            THEME.menu_hero_padding_x,
            THEME.menu_hero_padding_y,
            THEME.menu_hero_padding_x,
            THEME.menu_hero_padding_y,
        )
        hero_layout.setSpacing(THEME.menu_hero_spacing)

        hero_title = QLabel(MenuPageTexts.TITLE, hero_panel)
        hero_title.setObjectName('menuHeroTitle')
        hero_date = QLabel(MenuPageBuilder._today_text(), hero_panel)
        hero_date.setObjectName('menuHeroDate')
        hero_subtitle = QLabel(MenuPageTexts.SUBTITLE, hero_panel)
        hero_subtitle.setWordWrap(True)
        hero_subtitle.setObjectName('menuHeroSubtitle')

        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_date)
        hero_layout.addWidget(hero_subtitle)
        layout.addWidget(hero_panel)

        overview_row = QGridLayout()
        overview_row.setHorizontalSpacing(THEME.section_gap)
        overview_row.setVerticalSpacing(THEME.section_gap)

        flow_panel, flow_layout = MenuPageBuilder._make_section_panel(page, MenuPageTexts.FLOW_TITLE, MenuPageTexts.FLOW_SUBTITLE)
        flow_grid = QGridLayout()
        flow_grid.setHorizontalSpacing(THEME.section_gap)
        flow_grid.setVerticalSpacing(THEME.section_gap)

        btn_template = MenuPageBuilder._make_menu_card(MenuPageTexts.TEMPLATE_TITLE, MenuPageTexts.TEMPLATE_SUBTITLE)
        btn_job_start = MenuPageBuilder._make_menu_card(MenuPageTexts.ORDER_TITLE, MenuPageTexts.ORDER_SUBTITLE)
        btn_receipt = MenuPageBuilder._make_menu_card(MenuPageTexts.RECEIPT_TITLE, MenuPageTexts.RECEIPT_SUBTITLE)
        btn_receipt.hide()
        btn_complete = MenuPageBuilder._make_menu_card(MenuPageTexts.COMPLETE_TITLE, MenuPageTexts.COMPLETE_SUBTITLE)
        btn_sale = MenuPageBuilder._make_menu_card(MenuPageTexts.SALE_TITLE, MenuPageTexts.SALE_SUBTITLE)
        btn_inventory = MenuPageBuilder._make_menu_card(MenuPageTexts.INVENTORY_TITLE, MenuPageTexts.INVENTORY_SUBTITLE)

        menu_buttons = (btn_template, btn_job_start, btn_complete, btn_sale, btn_inventory)
        for index, button in enumerate(menu_buttons):
            flow_grid.addWidget(button, index // 3, index % 3)
        flow_layout.addLayout(flow_grid)
        flow_layout.addStretch(1)

        status_panel, status_layout = MenuPageBuilder._make_section_panel(page, MenuPageTexts.STATUS_TITLE, MenuPageTexts.STATUS_SUBTITLE)
        metric_titles = ('총 작업지시서', '진행중 발주', '미검수 건수', '현재고 합계')
        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(THEME.section_gap)
        metrics_grid.setVerticalSpacing(THEME.section_gap)
        metric_value_labels: dict[str, QLabel] = {}
        for index, title in enumerate(metric_titles):
            card, value_label = MenuPageBuilder._make_metric_card(page, title)
            metrics_grid.addWidget(card, index // 2, index % 2)
            metric_value_labels[title] = value_label
        status_layout.addLayout(metrics_grid)

        utility_panel, utility_layout = MenuPageBuilder._make_section_panel(page, MenuPageTexts.UTILITIES_TITLE, MenuPageTexts.UTILITIES_SUBTITLE)
        btn_settings = MenuPageBuilder._make_menu_card(MenuPageTexts.SETTINGS_TITLE, MenuPageTexts.SETTINGS_SUBTITLE, utility=True)
        utility_layout.addWidget(btn_settings)
        utility_layout.addStretch(1)

        status_layout.addWidget(utility_panel)

        overview_row.addWidget(flow_panel, 0, 0, 2, 1)
        overview_row.addWidget(status_panel, 0, 1)
        overview_row.setColumnStretch(0, 3)
        overview_row.setColumnStretch(1, 2)
        layout.addLayout(overview_row)

        recent_row = QGridLayout()
        recent_row.setHorizontalSpacing(THEME.section_gap)
        recent_row.setVerticalSpacing(THEME.section_gap)
        recent_templates_panel, recent_template_labels = MenuPageBuilder._make_recent_panel(page, MenuPageTexts.RECENT_TEMPLATE_TITLE, MenuPageTexts.RECENT_TEMPLATE_EMPTY)
        recent_activity_panel, recent_activity_labels = MenuPageBuilder._make_recent_panel(page, MenuPageTexts.RECENT_ACTIVITY_TITLE, MenuPageTexts.RECENT_ACTIVITY_EMPTY)
        recent_row.addWidget(recent_templates_panel, 0, 0)
        recent_row.addWidget(recent_activity_panel, 0, 1)
        recent_row.setColumnStretch(0, 1)
        recent_row.setColumnStretch(1, 1)
        layout.addLayout(recent_row)
        layout.addStretch(1)

        return MenuPageRefs(
            page=page,
            btn_template=btn_template,
            btn_job_start=btn_job_start,
            btn_receipt=btn_receipt,
            btn_complete=btn_complete,
            btn_sale=btn_sale,
            btn_inventory=btn_inventory,
            btn_settings=btn_settings,
            metric_value_labels=metric_value_labels,
            recent_template_labels=recent_template_labels,
            recent_activity_labels=recent_activity_labels,
        )
