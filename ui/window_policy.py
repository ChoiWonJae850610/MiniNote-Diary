from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtWidgets import QWidget


def _remove_maximize_button(window: QWidget) -> None:
    window.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
    if hasattr(window, "setSizeGripEnabled"):
        try:
            window.setSizeGripEnabled(False)
        except Exception:
            pass


def _locked_size(window: QWidget, width: int | None = None, height: int | None = None) -> QSize:
    base = window.sizeHint().expandedTo(window.minimumSizeHint())
    current = window.size().expandedTo(base)
    final_width = width if width is not None else max(base.width(), current.width())
    final_height = height if height is not None else max(base.height(), current.height())
    return QSize(final_width, final_height)


def lock_window_size(window: QWidget, *, width: int | None = None, height: int | None = None) -> None:
    _remove_maximize_button(window)
    size = _locked_size(window, width=width, height=height)
    window.setMinimumSize(size)
    window.setMaximumSize(size)
    window.resize(size)


class _LockOnShowFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show and isinstance(obj, QWidget):
            if not bool(obj.property("_fixed_size_applied")):
                width = obj.property("_fixed_width")
                height = obj.property("_fixed_height")
                lock_window_size(
                    obj,
                    width=int(width) if width is not None else None,
                    height=int(height) if height is not None else None,
                )
                obj.setProperty("_fixed_size_applied", True)
            obj.removeEventFilter(self)
        return False


def prepare_non_resizable_window(window: QWidget, *, width: int | None = None, height: int | None = None) -> None:
    _remove_maximize_button(window)
    window.setProperty("_fixed_width", width)
    window.setProperty("_fixed_height", height)
    if getattr(window, "_fixed_size_filter", None) is None:
        filt = _LockOnShowFilter(window)
        window._fixed_size_filter = filt
        window.installEventFilter(filt)


__all__ = ["lock_window_size", "prepare_non_resizable_window"]
