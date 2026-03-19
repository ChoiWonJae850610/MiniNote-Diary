from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowNavigationLogic:
    @staticmethod
    def open_order_page(window: "MainWindow") -> None:
        window.refresh_order_page()
        window.stack.setCurrentIndex(window.PAGE_JOB_START)

    @staticmethod
    def open_feature_page(window: "MainWindow", page_index: int) -> None:
        if page_index == window.PAGE_INVENTORY:
            window.refresh_stats_page()
        window.stack.setCurrentIndex(page_index)

    @staticmethod
    def focus_style_input(window: "MainWindow") -> None:
        QTimer.singleShot(0, lambda: window.postit_bar.basic.style_no.activate_for_input())

    @staticmethod
    def go_work_order(window: "MainWindow") -> None:
        window._refresh_postits(force_rebuild=True)
        if hasattr(window, 'set_work_order_diary_page'):
            window.set_work_order_diary_page(0)
        window.stack.setCurrentIndex(window.PAGE_WORK_ORDER)
        MainWindowNavigationLogic.focus_style_input(window)

    @staticmethod
    def go_menu(window: "MainWindow") -> None:
        window.refresh_menu_page()
        window.stack.setCurrentIndex(window.PAGE_MENU)
