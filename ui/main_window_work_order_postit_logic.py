from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowWorkOrderPostItLogic:
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
    def reset_form(window: "MainWindow") -> None:
        window._suppress_dirty = True
        try:
            window.state.reset()
            window.image_preview.clear_image()
            window.btn_delete_image.setEnabled(False)
            MainWindowWorkOrderPostItLogic.refresh_postits(window, force_rebuild=True)
            window._clear_feedback()
            window._update_window_title()
        finally:
            window._suppress_dirty = False
