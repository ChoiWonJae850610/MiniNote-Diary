from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from ui.partner_dialog import PartnerBrowserDialog
from ui.unit_dialog import UnitDialog

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowDialogLogic:
    @staticmethod
    def open_modal_dialog(window: "MainWindow", dialog_cls) -> int:
        dialog = dialog_cls(project_root=window.project_root, parent=window)
        dialog.setWindowModality(Qt.ApplicationModal)
        return dialog.exec()

    @staticmethod
    def open_partner_management(window: "MainWindow") -> int:
        return MainWindowDialogLogic.open_modal_dialog(window, PartnerDialog)

    @staticmethod
    def open_unit_management(window: "MainWindow") -> int:
        return MainWindowDialogLogic.open_modal_dialog(window, UnitDialog)
