from __future__ import annotations

from typing import TYPE_CHECKING

from services.stats import StatsNoteItem, StatsService, StyleStatsRow
from ui.pages.stats_page import fill_stats_table

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowStatsLogic:
    @staticmethod
    def refresh_stats_page(window: 'MainWindow') -> None:
        refs = window.stats_page_refs
        period_key = refs.period_combo.currentData()
        data = StatsService(window.project_root).build_stats_page(period_key=period_key)

        for metric in data.metrics:
            label = refs.metric_value_labels.get(metric.label)
            if label is not None:
                label.setText(metric.value)

        fill_stats_table(
            refs.style_table,
            [
                [
                    row.template_name,
                    str(row.ordered_qty),
                    str(row.inbound_qty),
                    str(row.sold_qty),
                    str(row.current_stock_qty),
                    row.status_text,
                ]
                for row in data.style_rows
            ] or [['표시할 데이터가 없습니다.', '-', '-', '-', '-', '-']],
        )
        fill_stats_table(
            refs.factory_table,
            [
                [
                    row.factory_name,
                    str(row.order_count),
                    str(row.ordered_qty),
                ]
                for row in data.factory_rows
            ] or [['표시할 데이터가 없습니다.', '-', '-']],
        )
        MainWindowStatsLogic._fill_notes(refs.note_labels, data.notes)

    @staticmethod
    def _fill_notes(label_rows, items: tuple[StatsNoteItem, ...]) -> None:
        for index, labels in enumerate(label_rows):
            title_label, detail_label = labels
            if index < len(items):
                item = items[index]
                title_label.setText(item.title or '-')
                detail_label.setText(item.detail or '')
            else:
                title_label.setText('-')
                detail_label.setText('표시할 항목이 없습니다.')
