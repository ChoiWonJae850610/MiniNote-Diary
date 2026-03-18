from datetime import datetime
from ui.main_window_parts.main_window_work_order_image_logic import MainWindowWorkOrderImageLogic
from ui.dialogs import show_error
from ui.dialogs.work_order_load_dialog import WorkOrderLoadDialog
from ui.messages import DialogTitles, InfoMessages, Warnings
from ui.main_window_parts.main_window_work_order_material_logic import MainWindowWorkOrderMaterialLogic
from ui.main_window_parts.main_window_work_order_postit_logic import MainWindowWorkOrderPostItLogic
from ui.main_window_parts.main_window_work_order_shared import MATERIAL_STACK_NAMES, MATERIAL_TARGET_CONFIGS
import ui.work_order_validation_ui as WorkOrderValidationUi


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

    @staticmethod
    def open_load_dialog(window) -> None:
        dialog = WorkOrderLoadDialog(window.controller.repository, window.order_repository, parent=window)
        if dialog.exec() != WorkOrderLoadDialog.DialogCode.Accepted or dialog.selected_result is None:
            return
        try:
            MainWindowWorkOrderLogic.load_template_into_form(window, dialog.selected_result.detail)
        except Exception as exc:
            show_error(window, DialogTitles.LOAD_TEMPLATE, str(exc) or Warnings.WORK_ORDER_LOAD_FAILED)

    @staticmethod
    def load_template_into_form(window, detail) -> None:
        document = detail.document
        window._suppress_dirty = True
        try:
            window.state.reset()
            header_data = document.header.to_dict()
            header_data['date'] = datetime.now().strftime('%Y-%m-%d')
            window.state.header_data = header_data
            window.state.fabric_items = [item.to_dict() for item in document.fabrics] or [dict()]
            window.state.trim_items = [item.to_dict() for item in document.trims] or [dict()]
            window.state.dyeing_items = [item.to_dict() for item in document.dyeings] or [dict()]
            window.state.finishing_items = [item.to_dict() for item in document.finishings] or [dict()]
            window.state.other_items = [item.to_dict() for item in document.others] or [dict()]
            window.state.current_image_path = detail.summary.image_path
            window.state.loaded_template_id = detail.summary.template_id
            stats = window.order_repository.aggregate_for_template(detail.summary.template_id)
            window.state.loaded_has_order_history = stats.order_count > 0
            MainWindowWorkOrderPostItLogic.refresh_postits(window, force_rebuild=True)
            if detail.summary.image_path:
                window.image_preview.set_image(detail.summary.image_path)
                window.btn_delete_image.setEnabled(True)
            else:
                window.image_preview.clear_image()
                window.btn_delete_image.setEnabled(False)
            WorkOrderValidationUi.deactivate(window)
            window._show_feedback(InfoMessages.WORK_ORDER_LOADED)
        finally:
            window._suppress_dirty = False
        window.state.is_dirty = False
        window._update_window_title()


__all__ = [
    "MATERIAL_STACK_NAMES",
    "MATERIAL_TARGET_CONFIGS",
    "MainWindowWorkOrderLogic",
]
