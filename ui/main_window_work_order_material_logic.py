from __future__ import annotations

from typing import TYPE_CHECKING

from ui.main_window_work_order_postit_logic import MainWindowWorkOrderPostItLogic
from ui.main_window_work_order_shared import MATERIAL_STACK_NAMES

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowWorkOrderMaterialLogic:
    @staticmethod
    def remove_material(window: "MainWindow", target: str, idx: int) -> None:
        if window.state.remove_material_item(target, idx):
            MainWindowWorkOrderPostItLogic.refresh_postits(window, force_rebuild=True)
            window._update_window_title()

    @staticmethod
    def update_material(window: "MainWindow", target: str, idx: int, patch: dict) -> None:
        window.state.update_material_patch(target, idx, patch)
        MainWindowWorkOrderPostItLogic.refresh_basic_postit(window)
        window._update_window_title()

    @staticmethod
    def add_material(window: "MainWindow", target: str) -> None:
        new_index = window.state.add_material_item(target)
        if new_index is None:
            return
        MainWindowWorkOrderPostItLogic.refresh_postits(window, force_rebuild=True)
        getattr(window.postit_bar, MATERIAL_STACK_NAMES[target]).set_active_card(new_index)
        window._update_window_title()
