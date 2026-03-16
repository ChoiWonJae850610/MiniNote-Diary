from ui.main_window_parts.main_window_work_order_image_logic import MainWindowWorkOrderImageLogic
from ui.main_window_parts.main_window_work_order_material_logic import MainWindowWorkOrderMaterialLogic
from ui.main_window_parts.main_window_work_order_postit_logic import MainWindowWorkOrderPostItLogic
from ui.main_window_parts.main_window_work_order_shared import MATERIAL_STACK_NAMES, MATERIAL_TARGET_CONFIGS


class MainWindowWorkOrderLogic:
    @staticmethod
    def reset_form(window) -> None:
        MainWindowWorkOrderPostItLogic.reset_form(window)

    @staticmethod
    def refresh_postits(window, *, force_rebuild: bool = False) -> None:
        MainWindowWorkOrderPostItLogic.refresh_postits(window, force_rebuild=force_rebuild)

    @staticmethod
    def refresh_basic_postit(window) -> None:
        MainWindowWorkOrderPostItLogic.refresh_basic_postit(window)

    @staticmethod
    def remove_material(window, target: str, idx: int) -> None:
        MainWindowWorkOrderMaterialLogic.remove_material(window, target, idx)

    @staticmethod
    def update_material(window, target: str, idx: int, patch: dict) -> None:
        MainWindowWorkOrderMaterialLogic.update_material(window, target, idx, patch)

    @staticmethod
    def add_material(window, target: str) -> None:
        MainWindowWorkOrderMaterialLogic.add_material(window, target)

    @staticmethod
    def upload_image(window) -> None:
        MainWindowWorkOrderImageLogic.upload_image(window)

    @staticmethod
    def delete_image(window) -> None:
        MainWindowWorkOrderImageLogic.delete_image(window)


__all__ = [
    "MATERIAL_STACK_NAMES",
    "MATERIAL_TARGET_CONFIGS",
    "MainWindowWorkOrderLogic",
]
