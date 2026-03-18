from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from services.stats import StatsService
from ui.pages.common import apply_secondary_button_metrics, apply_table_widget_metrics, apply_toolbar_field_metrics, make_compact_toolbar_panel, make_standard_body_row, make_standard_page_header, make_standard_page_layout
from ui.theme import THEME
from ui.widget_factory import make_action_button, make_hint_label, make_panel_frame, make_panel_title_label


@dataclass
class StatsPageRefs:
    page: QWidget
    btn_back: QPushButton
    btn_refresh: QPushButton
    period_combo: QComboBox
    metric_value_labels: dict[str, QLabel]
    style_table: QTableWidget
    factory_table: QTableWidget
    note_labels: list[tuple[QLabel, QLabel]]


class StatsPageBuilder:
    PERIOD_OPTIONS = (
        ('전체', StatsService.PERIOD_ALL),
        ('이번 달', StatsService.PERIOD_THIS_MONTH),
        ('최근 30일', StatsService.PERIOD_LAST_30_DAYS),
    )

    @staticmethod
    def _make_metric_card(parent: QWidget, title: str) -> tuple[QFrame, QLabel]:
        card = make_panel_frame(parent, compact=False)
        card.setMinimumHeight(THEME.dashboard_metric_card_min_height)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        layout.setSpacing(THEME.dashboard_metric_spacing)

        title_label = make_hint_label(title, card, word_wrap=False)
        title_label.setObjectName('menuMetricTitle')
        value_label = QLabel('0', card)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setObjectName('menuMetricValue')
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    @staticmethod
    def _build_table(parent: QWidget, headers: list[str]) -> QTableWidget:
        table = QTableWidget(parent)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        apply_table_widget_metrics(table, min_height=260)
        return table

    @staticmethod
    def _make_note_item(parent: QWidget) -> tuple[QFrame, tuple[QLabel, QLabel]]:
        frame = make_panel_frame(parent, compact=True)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(
            THEME.stats_note_item_padding_x,
            THEME.stats_note_item_padding_y,
            THEME.stats_note_item_padding_x,
            THEME.stats_note_item_padding_y,
        )
        layout.setSpacing(THEME.stats_note_item_spacing)
        title = QLabel('-', frame)
        title.setObjectName('menuListPrimary')
        detail = QLabel('', frame)
        detail.setObjectName('menuListSecondary')
        detail.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(detail)
        return frame, (title, detail)

    @staticmethod
    def build() -> StatsPageRefs:
        page = QWidget()
        page.setObjectName('featurePage')
        root = make_standard_page_layout(page)

        header_refs = make_standard_page_header(page, title_text='재고 / 통계', subtitle_text='')
        root.addLayout(header_refs.row)

        filter_panel, filter_row = make_compact_toolbar_panel(page, object_name='statsToolbarPanel')
        filter_row.addWidget(make_hint_label('조회 기간', filter_panel, word_wrap=False), 0)

        period_combo = QComboBox(filter_panel)
        for text, key in StatsPageBuilder.PERIOD_OPTIONS:
            period_combo.addItem(text, key)
        apply_toolbar_field_metrics(period_combo)
        filter_row.addWidget(period_combo, 0)
        filter_row.addStretch(1)
        btn_refresh = make_action_button('새로고침', filter_panel, width=THEME.secondary_button_width, height=THEME.primary_button_height)
        apply_secondary_button_metrics(btn_refresh)
        filter_row.addWidget(btn_refresh, 0)
        root.addWidget(filter_panel)

        metric_grid = QGridLayout()
        metric_grid.setContentsMargins(0, 0, 0, 0)
        metric_grid.setHorizontalSpacing(THEME.section_gap)
        metric_grid.setVerticalSpacing(THEME.section_gap)
        metric_value_labels: dict[str, QLabel] = {}
        for index, title in enumerate(('총 발주 수량', '총 입고 수량', '총 판매 수량', '현재고 합계')):
            card, value_label = StatsPageBuilder._make_metric_card(page, title)
            metric_grid.addWidget(card, 0, index)
            metric_value_labels[title] = value_label
        root.addLayout(metric_grid)

        body_row = make_standard_body_row()

        left_panel = make_panel_frame(page)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        left_layout.setSpacing(THEME.section_gap)
        left_layout.addWidget(make_panel_title_label('스타일별 현황', left_panel))
        style_table = StatsPageBuilder._build_table(left_panel, ['스타일', '발주', '입고', '판매', '현재고', '상태'])
        left_layout.addWidget(style_table, 1)
        body_row.addWidget(left_panel, THEME.page_master_detail_detail_stretch)

        right_column = QVBoxLayout()
        right_column.setSpacing(THEME.section_gap)

        factory_panel = make_panel_frame(page)
        factory_layout = QVBoxLayout(factory_panel)
        factory_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        factory_layout.setSpacing(THEME.section_gap)
        factory_layout.addWidget(make_panel_title_label('거래처별 발주', factory_panel))
        factory_table = StatsPageBuilder._build_table(factory_panel, ['거래처', '건수', '수량'])
        factory_table.setMinimumHeight(220)
        factory_layout.addWidget(factory_table, 1)
        right_column.addWidget(factory_panel, 3)

        note_panel = make_panel_frame(page)
        note_layout = QVBoxLayout(note_panel)
        note_layout.setContentsMargins(THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding, THEME.page_section_padding)
        note_layout.setSpacing(THEME.row_spacing)
        note_layout.addWidget(make_panel_title_label('주의 / 참고', note_panel))
        note_labels: list[tuple[QLabel, QLabel]] = []
        for _ in range(4):
            item_frame, item_labels = StatsPageBuilder._make_note_item(note_panel)
            note_layout.addWidget(item_frame)
            note_labels.append(item_labels)
        note_layout.addStretch(1)
        right_column.addWidget(note_panel, 2)

        body_row.addLayout(right_column, THEME.page_master_detail_list_stretch)
        root.addLayout(body_row, 1)

        return StatsPageRefs(
            page=page,
            btn_back=header_refs.back_button,
            btn_refresh=btn_refresh,
            period_combo=period_combo,
            metric_value_labels=metric_value_labels,
            style_table=style_table,
            factory_table=factory_table,
            note_labels=note_labels,
        )


def _make_center_item(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignCenter)
    return item


def fill_stats_table(table: QTableWidget, rows: list[list[str]]) -> None:
    table.setRowCount(len(rows))
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            item = _make_center_item(value) if col_index > 0 else QTableWidgetItem(value)
            table.setItem(row_index, col_index, item)
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)
