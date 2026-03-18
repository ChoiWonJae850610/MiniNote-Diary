from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

from ui.messages import DialogTitles, UiTiming

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowFeedback:
    @staticmethod
    def initialize(window: "MainWindow") -> None:
        window._feedback_timer = QTimer(window)
        window._feedback_timer.setSingleShot(True)
        window._feedback_timer.timeout.connect(window._clear_feedback)

    @staticmethod
    def show_feedback(window: "MainWindow", message: str, timeout_ms: int = UiTiming.FEEDBACK_TIMEOUT_MS) -> None:
        label = getattr(window, "feedback_label", None)
        if label is None:
            return
        label.setText(message)
        label.setVisible(bool(message))
        window._feedback_timer.start(timeout_ms)

    @staticmethod
    def clear_feedback(window: "MainWindow") -> None:
        label = getattr(window, "feedback_label", None)
        if label is None:
            return
        label.clear()
        label.hide()

    @staticmethod
    def update_window_title(window: "MainWindow") -> None:
        suffix = ' *' if window.state.is_dirty else ''
        window.setWindowTitle(f'{DialogTitles.APP}{suffix}')

    @staticmethod
    def build_save_success_message(result) -> str:
        return "저장 완료"
