from __future__ import annotations

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import QCalendarWidget, QDialog, QVBoxLayout

from ui.common import (
    CARD_RADIUS,
    FIELD_H,
    MAX_POSTIT_CARDS,
    PENDING_TAB_FILTER,
    PendingTabFocusFilter,
    ensure_pending_tab_filter,
    make_down_icon,
    next_focusable_widget,
    prev_focusable_widget,
)
from ui.postit.layout_constants import POSTIT_POPUP_MARGIN


class InlineCalendarPopup(QDialog):
    datePicked = Signal(QDate)
    moveNextRequested = Signal()

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        root = QVBoxLayout(self)
        root.setContentsMargins(POSTIT_POPUP_MARGIN, POSTIT_POPUP_MARGIN, POSTIT_POPUP_MARGIN, POSTIT_POPUP_MARGIN)
        self.cal = QCalendarWidget(self)
        self.cal.setGridVisible(True)
        self.cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        if initial and initial.isValid():
            self.cal.setSelectedDate(initial)
        self.cal.activated.connect(self._on_activated)
        root.addWidget(self.cal)

    def _on_activated(self, date: QDate):
        if date and date.isValid():
            self.datePicked.emit(date)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            date = self.cal.selectedDate()
            if date and date.isValid():
                self.datePicked.emit(date)
            self.moveNextRequested.emit()
            self.close()
            event.accept()
            return
        if event.key() == Qt.Key_Backtab:
            date = self.cal.selectedDate()
            if date and date.isValid():
                self.datePicked.emit(date)
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)


__all__ = [
    "CARD_RADIUS",
    "FIELD_H",
    "InlineCalendarPopup",
    "MAX_POSTIT_CARDS",
    "PENDING_TAB_FILTER",
    "PendingTabFocusFilter",
    "ensure_pending_tab_filter",
    "make_down_icon",
    "next_focusable_widget",
    "prev_focusable_widget",
]
