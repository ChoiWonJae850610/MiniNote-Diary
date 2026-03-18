from __future__ import annotations

from PySide6.QtCore import QDate, QEvent, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QCalendarWidget, QDialog, QMenu, QSizePolicy, QToolButton, QVBoxLayout

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
from ui.postit.layout import PostItLayout
from ui.postit.layout_constants import POSTIT_POPUP_MARGIN
from ui.theme import menu_style, unit_button_style
from ui.window_policy import prepare_non_resizable_window


class CheckedPopupSelector(QToolButton):
    currentIndexChanged = Signal(int)
    currentTextChanged = Signal(str)
    currentDataChanged = Signal(object)
    activated = Signal(int)

    def __init__(self, parent=None, *, clear_text: str):
        super().__init__(parent)
        self._clear_text = clear_text
        self._items: list[tuple[str, object]] = []
        self._actions: list[QAction] = []
        self._current_index = -1

        self.setCursor(Qt.PointingHandCursor)
        self.setPopupMode(QToolButton.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setIcon(make_down_icon(PostItLayout.UNIT_ICON_SIZE))
        self.setIconSize(self.iconSize())
        self.setFixedHeight(FIELD_H)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(unit_button_style())

        menu = QMenu(self)
        menu.setStyleSheet(menu_style())
        menu.aboutToShow.connect(self._sync_menu_checks)
        self.setMenu(menu)
        self._apply_display_text()

    def clear(self):
        self.menu().clear()
        self._items.clear()
        self._actions.clear()
        self._current_index = -1
        self._apply_display_text()

    def addItem(self, text: str, user_data=None):
        index = len(self._items)
        self._items.append((str(text), user_data))
        action = self.menu().addAction(str(text))
        action.setCheckable(True)
        action.triggered.connect(lambda _checked=False, idx=index: self._on_action_triggered(idx))
        self._actions.append(action)
        if self._current_index < 0:
            self.setCurrentIndex(0)

    def count(self) -> int:
        return len(self._items)

    def currentIndex(self) -> int:
        return self._current_index

    def currentData(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][1]
        return None

    def currentText(self) -> str:
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][0]
        return ''

    def itemData(self, index: int):
        return self._items[index][1] if 0 <= index < len(self._items) else None

    def itemText(self, index: int) -> str:
        return self._items[index][0] if 0 <= index < len(self._items) else ''

    def findData(self, data) -> int:
        for idx, (_text, item_data) in enumerate(self._items):
            if item_data == data:
                return idx
        return -1

    def setCurrentIndex(self, index: int):
        if not (0 <= index < len(self._items)):
            index = -1
        changed = index != self._current_index
        self._current_index = index
        self._apply_display_text()
        if changed:
            self.currentIndexChanged.emit(self._current_index)
            self.currentTextChanged.emit(self.currentText())
            self.currentDataChanged.emit(self.currentData())

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self.count() > 0:
                self.setCurrentIndex(0)
                event.accept()
                return
        if event.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Down):
            self.showMenu()
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_action_triggered(self, index: int):
        self.setCurrentIndex(index)
        self.activated.emit(index)

    def _display_text_for_index(self, index: int) -> str:
        if not (0 <= index < len(self._items)):
            return ''
        text, data = self._items[index]
        if not str(data or '').strip() and text == self._clear_text:
            return ''
        return text

    def _apply_display_text(self):
        self.setText(self._display_text_for_index(self._current_index))

    def _sync_menu_checks(self):
        for idx, action in enumerate(self._actions):
            action.setChecked(idx == self._current_index)


class CheckedClearableComboBox(CheckedPopupSelector):
    pass


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
        prepare_non_resizable_window(self)

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
    "CheckedClearableComboBox",
    "CheckedPopupSelector",
    "InlineCalendarPopup",
    "MAX_POSTIT_CARDS",
    "PENDING_TAB_FILTER",
    "PendingTabFocusFilter",
    "ensure_pending_tab_filter",
    "make_down_icon",
    "next_focusable_widget",
    "prev_focusable_widget",
]
