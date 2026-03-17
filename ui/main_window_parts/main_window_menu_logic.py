from __future__ import annotations

from typing import TYPE_CHECKING

from services.stats import DashboardListItem, DashboardService

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowMenuLogic:
    @staticmethod
    def refresh_menu_page(window: 'MainWindow') -> None:
        refs = window.menu_page_refs
        dashboard = DashboardService(window.project_root).build_dashboard()

        for metric in dashboard.metrics:
            label = refs.metric_value_labels.get(metric.label)
            if label is not None:
                label.setText(metric.value)

        MainWindowMenuLogic._fill_items(refs.recent_template_labels, dashboard.recent_templates)
        MainWindowMenuLogic._fill_items(refs.recent_activity_labels, dashboard.recent_activity)

    @staticmethod
    def _fill_items(label_rows, items: tuple[DashboardListItem, ...]) -> None:
        for index, labels in enumerate(label_rows):
            primary_label, secondary_label, tertiary_label = labels
            if index < len(items):
                item = items[index]
                primary_label.setText(item.primary or '-')
                secondary_label.setText(item.secondary or '')
                tertiary_label.setText(item.tertiary or '')
                primary_label.parentWidget().show()
            else:
                primary_label.setText('-')
                secondary_label.setText('표시할 데이터가 없습니다.')
                tertiary_label.setText('')
                primary_label.parentWidget().show()
