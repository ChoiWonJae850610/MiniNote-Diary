from __future__ import annotations

from typing import TYPE_CHECKING

from ui.dialogs import show_error, show_info
from ui.main_window_parts.main_window_navigation import MainWindowNavigationLogic
from ui.messages import DialogTitles

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowSaveLogic:
    @staticmethod
    def handle_back(window: "MainWindow") -> None:
        if not window.has_any_data():
            MainWindowNavigationLogic.go_menu(window)
            return
        dialog = window.create_back_confirm_dialog()
        result = dialog.exec()
        if result == window.dialog_accept_code():
            MainWindowNavigationLogic.go_menu(window)
        else:
            window.reset_work_order_form()
            MainWindowNavigationLogic.go_menu(window)

    @staticmethod
    def handle_save(window: "MainWindow") -> None:
        statuses = window.controller.get_save_requirement_statuses()
        if not all(ok for _, ok in statuses):
            window.show_validation_statuses(statuses)
            return
        try:
            result = window.controller.save()
        except Exception as exc:
            show_error(window, DialogTitles.SAVE_FAILED, str(exc))
            return
        window.reset_work_order_form()
        show_info(window, DialogTitles.SAVE, window.build_save_success_message(result))
