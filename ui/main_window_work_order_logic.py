from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog

from services.field_keys import MaterialTargets
from ui.messages import DefaultTexts, FileDialogFilters, DialogTitles, InfoMessages

if TYPE_CHECKING:
    from ui.main_window import MainWindow


MATERIAL_TARGET_CONFIGS = {
    MaterialTargets.FABRIC: ('fabric_deleted', 'fabric_item_changed', 'fabric_item_added', 'fabric'),
    MaterialTargets.TRIM: ('trim_deleted', 'trim_item_changed', 'trim_item_added', 'trim'),
    MaterialTargets.DYEING: ('dyeing_deleted', 'dyeing_item_changed', 'dyeing_item_added', 'dyeing'),
    MaterialTargets.FINISHING: ('finishing_deleted', 'finishing_item_changed', 'finishing_item_added', 'finishing'),
    MaterialTargets.OTHER: ('other_deleted', 'other_item_changed', 'other_item_added', 'other'),
}

MATERIAL_STACK_NAMES = {target: stack_name for target, (_, _, _, stack_name) in MATERIAL_TARGET_CONFIGS.items()}


class MainWindowWorkOrderLogic:
    @staticmethod
    def reset_form(window: "MainWindow") -> None:
        window._suppress_dirty = True
        try:
            window.state.reset()
            window.image_preview.clear_image()
            window.btn_delete_image.setEnabled(False)
            MainWindowWorkOrderLogic.refresh_postits(window, force_rebuild=True)
            window._clear_feedback()
            window._update_window_title()
        finally:
            window._suppress_dirty = False

    @staticmethod
    def refresh_postits(window: "MainWindow", *, force_rebuild: bool = False) -> None:
        window.postit_bar.set_data(
            header=window.state.header_data,
            fabrics=window.state.fabric_items,
            trims=window.state.trim_items,
            dyeings=window.state.dyeing_items,
            finishings=window.state.finishing_items,
            others=window.state.other_items,
            force_rebuild=force_rebuild,
        )
        window.change_note_postit.set_text(window.state.header.change_note)

    @staticmethod
    def refresh_basic_postit(window: "MainWindow") -> None:
        window.postit_bar.basic.set_header_data(window.state.header_data)

    @staticmethod
    def remove_material(window: "MainWindow", target: str, idx: int) -> None:
        if window.state.remove_material_item(target, idx):
            MainWindowWorkOrderLogic.refresh_postits(window, force_rebuild=True)
            window._update_window_title()

    @staticmethod
    def update_material(window: "MainWindow", target: str, idx: int, patch: dict) -> None:
        window.state.update_material_patch(target, idx, patch)
        MainWindowWorkOrderLogic.refresh_basic_postit(window)
        window._update_window_title()

    @staticmethod
    def add_material(window: "MainWindow", target: str) -> None:
        new_index = window.state.add_material_item(target)
        if new_index is None:
            return
        MainWindowWorkOrderLogic.refresh_postits(window, force_rebuild=True)
        getattr(window.postit_bar, MATERIAL_STACK_NAMES[target]).set_active_card(new_index)
        window._update_window_title()

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
