from __future__ import annotations

from PySide6.QtCore import QDate, QEvent, QObject, QPoint, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QCalendarWidget, QDialog, QWidget

from services.formatters import digits_only, format_commas_from_digits, int_from_any
from services.unit_repository import load_units, unit_label_for_value
from services.schema import MAX_MATERIAL_ITEMS
from ui.theme import THEME

FIELD_H = THEME.field_height
CARD_RADIUS = THEME.card_radius
MAX_POSTIT_CARDS = MAX_MATERIAL_ITEMS


class PendingTabFocusFilter(QObject):
    def __init__(self):
        super().__init__()
        self.anchor = None

    def set_pending(self, anchor=None):
        self.anchor = anchor

    def clear_pending(self):
        self.anchor = None

    def eventFilter(self, obj, event):
        if self.anchor is None:
            return False
        if event.type() == QEvent.MouseButtonPress:
            self.clear_pending()
            return False
        if event.type() != QEvent.KeyPress:
            return False

        key = event.key()
        if key == Qt.Key_Tab:
            anchor = self.anchor
            self.clear_pending()
            if anchor is not None:
                target = getattr(anchor, "_pending_next_widget", None) or next_focusable_widget(anchor)
                if target is not None:
                    target.setFocus(Qt.TabFocusReason)
                    event.accept()
                    return True
            return False

        if key == Qt.Key_Backtab:
            anchor = self.anchor
            self.clear_pending()
            if anchor is not None:
                target = getattr(anchor, "_pending_prev_widget", None) or prev_focusable_widget(anchor)
                if target is not None:
                    target.setFocus(Qt.BacktabFocusReason)
                    event.accept()
                    return True
            return False

        self.clear_pending()
        return False


PENDING_TAB_FILTER = PendingTabFocusFilter()


def ensure_pending_tab_filter() -> None:
    app = QApplication.instance()
    if app is not None and not getattr(app, "_postit_pending_tab_filter_installed", False):
        app.installEventFilter(PENDING_TAB_FILTER)
        app._postit_pending_tab_filter_installed = True


def next_focusable_widget(widget):
    current = widget
    visited = set()
    while current is not None:
        nxt = current.nextInFocusChain()
        if nxt is None or nxt is current or id(nxt) in visited:
            break
        visited.add(id(nxt))
        policy = getattr(nxt, "focusPolicy", lambda: Qt.NoFocus)()
        if isinstance(nxt, QWidget) and nxt.isVisible() and nxt.isEnabled() and policy != Qt.NoFocus:
            return nxt
        current = nxt
    return None


def prev_focusable_widget(widget):
    current = widget
    visited = set()
    while current is not None:
        prev = current.previousInFocusChain()
        if prev is None or prev is current or id(prev) in visited:
            break
        visited.add(id(prev))
        policy = getattr(prev, "focusPolicy", lambda: Qt.NoFocus)()
        if isinstance(prev, QWidget) and prev.isVisible() and prev.isEnabled() and policy != Qt.NoFocus:
            return prev
        current = prev
    return None


def make_down_icon(size: int = 12) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setPen(QPen(QColor(THEME.color_icon), 2))
    painter.drawLine(2, 4, size // 2, size - 4)
    painter.drawLine(size // 2, size - 4, size - 2, 4)
    painter.end()
    return QIcon(pm)


class InlineCalendarPopup(QDialog):
    datePicked = Signal(QDate)
    moveNextRequested = Signal()

    def __init__(self, initial: QDate, parent=None):
        super().__init__(parent, Qt.Popup)
        lay = QWidget(self)
        root = None
        from PySide6.QtWidgets import QVBoxLayout
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
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
