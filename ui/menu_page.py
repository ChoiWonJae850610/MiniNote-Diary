from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QDate, Qt, QSize
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QToolButton,
    QStyle,
    QAbstractButton,
    QVBoxLayout,
    QWidget,
)

from ui.layout_metrics import MenuLayout
from ui.messages import MenuPageTexts
from ui.pages.common import make_standard_page_layout
from ui.button_icon_utils import apply_glyph_icon
from ui.widget_factory_buttons import make_icon_button
from ui.theme import THEME
from ui.widget_factory import apply_button_metrics, make_panel_frame


@dataclass
class MenuPageRefs:
    page: QWidget
    btn_template: QAbstractButton
    btn_job_start: QAbstractButton
    btn_receipt: QAbstractButton
    btn_complete: QAbstractButton
    btn_sale: QAbstractButton
    btn_inventory: QAbstractButton
    btn_partner_mgmt: QAbstractButton
    btn_unit_mgmt: QAbstractButton
    btn_product_type_mgmt: QAbstractButton
    btn_material_mgmt: QAbstractButton
    btn_settings: QAbstractButton
    btn_help: QAbstractButton
    checklist_input: QLineEdit
    checklist_list: QListWidget
    metric_value_labels: dict[str, QLabel] = field(default_factory=dict)
    recent_template_labels: list[tuple[QLabel, QLabel, QLabel]] = field(default_factory=list)
    recent_activity_labels: list[tuple[QLabel, QLabel, QLabel]] = field(default_factory=list)


class MenuChecklistStore:
    DEFAULT_ITEMS = (
        '원단 발주 확인',
        '공장 연락',
        '배송 일정 체크',
    )

    @staticmethod
    def path_for(project_root: str | None) -> Path:
        base = Path(project_root) if project_root else Path.cwd()
        return base / 'data' / 'memo' / 'checklist.json'

    @staticmethod
    def load(project_root: str | None) -> list[dict[str, object]]:
        path = MenuChecklistStore.path_for(project_root)
        if not path.exists():
            return [{'text': text, 'checked': False} for text in MenuChecklistStore.DEFAULT_ITEMS]
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
            items = payload.get('items', []) if isinstance(payload, dict) else []
            normalized: list[dict[str, object]] = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                text = str(item.get('text', '')).strip()
                if not text:
                    continue
                normalized.append({'text': text, 'checked': bool(item.get('checked', False))})
            return normalized or [{'text': text, 'checked': False} for text in MenuChecklistStore.DEFAULT_ITEMS]
        except Exception:
            return [{'text': text, 'checked': False} for text in MenuChecklistStore.DEFAULT_ITEMS]

    @staticmethod
    def save(project_root: str | None, items: list[dict[str, object]]) -> None:
        path = MenuChecklistStore.path_for(project_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {'items': items}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


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
    def _make_header_icon_button(glyph: str, tooltip: str, parent: QWidget) -> QPushButton:
        button = make_icon_button(parent=parent, object_name='iconAction', tooltip=tooltip, font_px=THEME.icon_button_font_px + 1)
        button.setFixedSize(THEME.icon_button_size + 10, THEME.icon_button_size + 10)
        apply_glyph_icon(button, glyph, font_px=THEME.icon_button_font_px + 3, color=THEME.color_icon)
        return button

    @staticmethod
    def _make_metric_card(page: QWidget, title: str) -> tuple[QFrame, QLabel]:
        card = make_panel_frame(page, object_name='menuMetricCard')
        card.setMinimumHeight(THEME.dashboard_metric_card_min_height)
        card.setMaximumHeight(THEME.dashboard_metric_card_min_height)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            THEME.dashboard_metric_padding_x,
            THEME.dashboard_metric_padding_y,
            THEME.dashboard_metric_padding_x,
            THEME.dashboard_metric_padding_y,
        )
        layout.setSpacing(THEME.dashboard_metric_spacing)

        title_label = QLabel(title, card)
        title_label.setObjectName('menuMetricTitle')
        value_label = QLabel('--', card)
        value_label.setObjectName('menuMetricValue')
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    @staticmethod
    def _make_checklist_panel(page: QWidget, project_root: str | None) -> tuple[QFrame, QLineEdit, QListWidget]:
        panel = make_panel_frame(page, object_name='menuChecklistPanel')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = MenuPageBuilder._make_section_label('오늘 할 일', panel)
        subtitle = QLabel('Enter로 바로 추가하고 체크해서 관리합니다.', panel)
        subtitle.setObjectName('menuSectionHint')

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(10)
        checklist_input = QLineEdit(panel)
        checklist_input.setObjectName('menuChecklistInput')
        checklist_input.setPlaceholderText('예: 원단 발주 확인')
        apply_button_metrics(checklist_input, font_px=THEME.base_font_px + 1)

        add_button = QPushButton('추가', panel)
        add_button.setObjectName('primaryAction')
        add_button.setMinimumHeight(44)
        add_button.setMinimumWidth(84)

        checklist_list = QListWidget(panel)
        checklist_list.setObjectName('menuChecklistList')
        checklist_list.setAlternatingRowColors(False)
        checklist_list.setSpacing(6)

        def snapshot_items() -> list[dict[str, object]]:
            items: list[dict[str, object]] = []
            for row in range(checklist_list.count()):
                item = checklist_list.item(row)
                if item is None:
                    continue
                text = item.text().strip()
                if not text:
                    continue
                items.append({'text': text, 'checked': item.checkState() == Qt.Checked})
            return items

        def save_items() -> None:
            MenuChecklistStore.save(project_root, snapshot_items())

        def add_check_item(text: str, checked: bool = False) -> None:
            normalized = text.strip()
            if not normalized:
                return
            item = QListWidgetItem(normalized)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            checklist_list.addItem(item)

        def commit_input() -> None:
            text = checklist_input.text().strip()
            if not text:
                return
            add_check_item(text)
            checklist_input.clear()
            save_items()

        add_button.clicked.connect(commit_input)
        checklist_input.returnPressed.connect(commit_input)
        checklist_list.itemChanged.connect(lambda _item: save_items())

        for entry in MenuChecklistStore.load(project_root):
            add_check_item(str(entry.get('text', '')), bool(entry.get('checked', False)))

        input_row.addWidget(checklist_input, 1)
        input_row.addWidget(add_button, 0)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(input_row)
        layout.addWidget(checklist_list, 1)
        return panel, checklist_input, checklist_list

    @staticmethod
    def _make_menu_button(title: str, glyph: str, accent_name: str, icon_kind: QStyle.StandardPixmap) -> QToolButton:
        button = QToolButton()
        button.setText(f'{glyph}\n{title}')
        button.setObjectName('menuIconCard')
        button.setProperty('accent', accent_name)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setCursor(Qt.PointingHandCursor)
        button.setAutoRaise(False)
        button.setIcon(button.style().standardIcon(icon_kind))
        button.setIconSize(QSize(*THEME.menu_button_icon_size))
        button.setMinimumHeight(THEME.menu_button_min_height)
        button.setMinimumWidth(THEME.menu_button_min_width)
        apply_button_metrics(button, font_px=THEME.base_font_px, bold=True)
        return button

    @staticmethod
    def build(project_root: str | None = None) -> MenuPageRefs:
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

        hero_top_row = QHBoxLayout()
        hero_top_row.setContentsMargins(0, 0, 0, 0)
        hero_top_row.setSpacing(THEME.section_gap)

        hero_title = QLabel(MenuPageTexts.TITLE, hero_panel)
        hero_title.setObjectName('menuHeroTitle')
        hero_date = QLabel(MenuPageBuilder._today_text(), hero_panel)
        hero_date.setObjectName('menuHeroDate')

        hero_text_col = QVBoxLayout()
        hero_text_col.setContentsMargins(0, 0, 0, 0)
        hero_text_col.setSpacing(6)
        hero_text_col.addWidget(hero_title)
        hero_text_col.addWidget(hero_date)

        hero_action_row = QHBoxLayout()
        hero_action_row.setContentsMargins(0, 0, 0, 0)
        hero_action_row.setSpacing(10)
        btn_help = MenuPageBuilder._make_header_icon_button('?', '도움말', hero_panel)
        btn_settings = MenuPageBuilder._make_header_icon_button('⚙', '환경설정', hero_panel)
        hero_action_row.addWidget(btn_help)
        hero_action_row.addWidget(btn_settings)

        hero_top_row.addLayout(hero_text_col, 1)
        hero_top_row.addLayout(hero_action_row, 0)
        hero_layout.addLayout(hero_top_row)
        layout.addWidget(hero_panel)

        content_row = QGridLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setHorizontalSpacing(THEME.section_gap)
        content_row.setVerticalSpacing(THEME.section_gap)

        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(THEME.section_gap)

        checklist_panel, checklist_input, checklist_list = MenuPageBuilder._make_checklist_panel(page, project_root)
        left_col.addWidget(checklist_panel, 1)

        menu_panel = make_panel_frame(page, object_name='menuActionPanel')
        menu_layout = QVBoxLayout(menu_panel)
        menu_layout.setContentsMargins(20, 20, 20, 20)
        menu_layout.setSpacing(12)
        menu_layout.addWidget(MenuPageBuilder._make_section_label(MenuPageTexts.FLOW_TITLE, menu_panel))

        menu_grid = QGridLayout()
        menu_grid.setContentsMargins(0, 0, 0, 0)
        menu_grid.setHorizontalSpacing(12)
        menu_grid.setVerticalSpacing(12)

        btn_template = MenuPageBuilder._make_menu_button(MenuPageTexts.TEMPLATE_TITLE, '📝', 'peach', QStyle.SP_FileIcon)
        btn_job_start = MenuPageBuilder._make_menu_button(MenuPageTexts.ORDER_TITLE, '📦', 'lavender', QStyle.SP_DialogOpenButton)
        btn_receipt = MenuPageBuilder._make_menu_button(MenuPageTexts.RECEIPT_TITLE, '🧵', 'mint', QStyle.SP_DialogApplyButton)
        btn_complete = MenuPageBuilder._make_menu_button(MenuPageTexts.COMPLETE_TITLE, '✅', 'sky', QStyle.SP_DialogYesButton)
        btn_sale = MenuPageBuilder._make_menu_button(MenuPageTexts.SALE_TITLE, '🏷', 'peach', QStyle.SP_ComputerIcon)
        btn_inventory = MenuPageBuilder._make_menu_button(MenuPageTexts.INVENTORY_TITLE, '📊', 'lavender', QStyle.SP_DriveHDIcon)
        btn_partner_mgmt = MenuPageBuilder._make_menu_button(MenuPageTexts.PARTNER_TITLE, '🏭', 'sky', QStyle.SP_DirHomeIcon)
        btn_unit_mgmt = MenuPageBuilder._make_menu_button(MenuPageTexts.UNIT_TITLE, '📏', 'mint', QStyle.SP_DialogResetButton)
        btn_product_type_mgmt = MenuPageBuilder._make_menu_button(MenuPageTexts.PRODUCT_TYPE_TITLE, '🪪', 'peach', QStyle.SP_DriveFDIcon)
        btn_material_mgmt = MenuPageBuilder._make_menu_button(MenuPageTexts.MATERIAL_MGMT_TITLE, '🧶', 'lavender', QStyle.SP_DirIcon)

        menu_buttons = (
            btn_template,
            btn_job_start,
            btn_complete,
            btn_sale,
            btn_inventory,
            btn_partner_mgmt,
            btn_unit_mgmt,
            btn_product_type_mgmt,
            btn_material_mgmt,
            btn_receipt,
        )
        for index, button in enumerate(menu_buttons):
            menu_grid.addWidget(button, index // 5, index % 5)
        for col in range(5):
            menu_grid.setColumnStretch(col, 1)

        menu_layout.addLayout(menu_grid)
        left_col.addWidget(menu_panel, 0)

        right_panel = make_panel_frame(page, object_name='menuStatusPanel')
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(12)
        right_layout.addWidget(MenuPageBuilder._make_section_label(MenuPageTexts.STATUS_TITLE, right_panel))

        metric_titles = ('총 작업지시서', '진행중 발주', '미검수 건수', '현재고 합계')
        metrics_grid = QGridLayout()
        metrics_grid.setContentsMargins(0, 0, 0, 0)
        metrics_grid.setHorizontalSpacing(12)
        metrics_grid.setVerticalSpacing(12)
        metric_value_labels: dict[str, QLabel] = {}
        for index, title in enumerate(metric_titles):
            card, value_label = MenuPageBuilder._make_metric_card(page, title)
            metrics_grid.addWidget(card, index // 2, index % 2)
            metric_value_labels[title] = value_label
        metrics_grid.setColumnStretch(0, 1)
        metrics_grid.setColumnStretch(1, 1)
        right_layout.addLayout(metrics_grid)

        content_row.addLayout(left_col, 0, 0)
        content_row.addWidget(right_panel, 0, 1)
        content_row.setColumnStretch(0, 5)
        content_row.setColumnStretch(1, 2)
        layout.addLayout(content_row, 1)

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
            btn_product_type_mgmt=btn_product_type_mgmt,
            btn_material_mgmt=btn_material_mgmt,
            btn_settings=btn_settings,
            btn_help=btn_help,
            checklist_input=checklist_input,
            checklist_list=checklist_list,
            metric_value_labels=metric_value_labels,
            recent_template_labels=[],
            recent_activity_labels=[],
        )
