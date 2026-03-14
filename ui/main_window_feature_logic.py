from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ui.dialogs import show_info
from ui.messages import DialogTitles, InfoMessages

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowFeatureLogic:
    PRIMARY_MESSAGE_BY_PAGE = {
        'page_partner': (DialogTitles.PARTNER_MANAGE, InfoMessages.FEATURE_PARTNER_PENDING),
        'page_inventory': (DialogTitles.INVENTORY, InfoMessages.FEATURE_INVENTORY_PENDING),
    }
    SECONDARY_MESSAGE_BY_PAGE = {
        'page_receipt': (DialogTitles.RECEIPT, InfoMessages.FEATURE_RECEIPT_EXTEND),
    }

    @staticmethod
    def show_primary(window: "MainWindow", page: QWidget) -> None:
        title, message = MainWindowFeatureLogic.PRIMARY_MESSAGE_BY_PAGE.get(
            MainWindowFeatureLogic._page_name(window, page),
            (DialogTitles.COMING_SOON, InfoMessages.FEATURE_GENERIC_PENDING),
        )
        show_info(window, title, message)

    @staticmethod
    def show_secondary(window: "MainWindow", page: QWidget) -> None:
        title, message = MainWindowFeatureLogic.SECONDARY_MESSAGE_BY_PAGE.get(
            MainWindowFeatureLogic._page_name(window, page),
            (DialogTitles.SCREEN_REVIEW, InfoMessages.FEATURE_SCREEN_REVIEW),
        )
        show_info(window, title, message)

    @staticmethod
    def _page_name(window: "MainWindow", page: QWidget) -> str:
        for name, current_page in window.pages.items():
            if current_page is page:
                return name
        return ''
