from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowNavigationLogic:
    @staticmethod
    def open_order_page(window: "MainWindow") -> None:
        window.refresh_order_page()
        window.stack.setCurrentIndex(window.PAGE_JOB_START)

    @staticmethod
    def open_feature_page(window: "MainWindow", page_index: int) -> None:
        window.stack.setCurrentIndex(page_index)

    @staticmethod
    def go_work_order(window: "MainWindow") -> None:
        window._refresh_postits(force_rebuild=True)
        window.stack.setCurrentIndex(window.PAGE_WORK_ORDER)
        window._focus_style_input()

    @staticmethod
    def go_menu(window: "MainWindow") -> None:
        window.stack.setCurrentIndex(window.PAGE_MENU)
