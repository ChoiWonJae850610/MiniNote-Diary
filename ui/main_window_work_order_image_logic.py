from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog

from ui.dialogs import show_error
from ui.messages import DialogTitles, FileDialogFilters, InfoMessages

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowWorkOrderImageLogic:
    @staticmethod
    def upload_image(window: "MainWindow") -> None:
        path, _ = QFileDialog.getOpenFileName(window, DialogTitles.IMAGE_SELECT, '', FileDialogFilters.IMAGES)
        if not path:
            return
        try:
            window.image_preview.set_image(path)
            window.state.current_image_path = path
            window.btn_delete_image.setEnabled(True)
            window.mark_dirty()
            window._show_feedback(InfoMessages.IMAGE_ATTACHED)
        except Exception as exc:
            show_error(window, DialogTitles.ERROR, str(exc))

    @staticmethod
    def delete_image(window: "MainWindow") -> None:
        window.image_preview.clear_image()
        window.state.current_image_path = None
        window.btn_delete_image.setEnabled(False)
        window.mark_dirty()
        window._show_feedback(InfoMessages.IMAGE_REMOVED)
